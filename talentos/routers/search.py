"""人材検索（Dify連携 / モック対応）"""

import json
import os
import re
from fastapi import APIRouter, Request
from pydantic import BaseModel

from db.database import get_connection

router = APIRouter(prefix="/api/search", tags=["search"])

DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "")


class SearchRequest(BaseModel):
    query: str


def _use_dify() -> bool:
    return bool(DIFY_API_KEY and DIFY_BASE_URL)


def _extract_keywords(query: str) -> list:
    known = [
        "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C#", "PHP", "Ruby", "Swift",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Linux",
        "React", "Vue", "Angular", "Next.js", "Node.js", "FastAPI", "Django", "Flask", "Spring",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
        "GitHub", "GitHub Actions", "CI/CD", "Git",
    ]
    found = []
    q_upper = query.upper()
    for k in known:
        if k.upper() in q_upper:
            found.append(k)
    if not found:
        words = re.findall(r'[A-Za-z#.+]+', query)
        found = [w for w in words if len(w) >= 2]
    return found


def _search_engineers(keywords: list) -> list:
    conn = get_connection()
    engineers = conn.execute(
        "SELECT u.user_id, u.name, e.specialty "
        "FROM users u LEFT JOIN engineers e ON u.user_id = e.engineer_id "
        "WHERE u.role = 'engineer'"
    ).fetchall()

    results = []
    for eng in engineers:
        eid = eng["user_id"]
        sheets = conn.execute(
            "SELECT theme, raw_data FROM skill_sheets WHERE engineer_id = ?", (eid,)
        ).fetchall()

        all_skills = []
        latest_role = ""
        exp_summary = ""
        for s in sheets:
            raw = json.loads(s["raw_data"]) if s["raw_data"] else {}
            if s["theme"] == "career":
                ts = raw.get("tech_stack", [])
                if isinstance(ts, list):
                    all_skills.extend(ts)
                latest_role = raw.get("role_title", "")
                exp_summary = raw.get("description", "")
            elif s["theme"] == "skills":
                for key in ("tools", "certifications"):
                    items = raw.get(key, [])
                    if isinstance(items, list):
                        all_skills.extend(items)

        exps = conn.execute(
            "SELECT role_title, tech_stack, description FROM experiences "
            "WHERE engineer_id = ? ORDER BY period_start DESC LIMIT 1",
            (eid,),
        ).fetchall()
        for e in exps:
            ts = json.loads(e["tech_stack"]) if e["tech_stack"] else []
            all_skills.extend(ts)
            if not latest_role:
                latest_role = e["role_title"] or ""
            if not exp_summary:
                exp_summary = e["description"] or ""

        unique_skills = list(dict.fromkeys(all_skills))

        matched = []
        for kw in keywords:
            for sk in unique_skills:
                if kw.upper() in sk.upper():
                    matched.append(sk)
                    break

        if keywords and not matched:
            continue

        results.append({
            "engineer_id": eid,
            "name": eng["name"],
            "specialty": eng["specialty"] or "",
            "matched_skills": matched,
            "top_skills": unique_skills[:6],
            "latest_role": latest_role,
            "experience_summary": exp_summary[:100] if exp_summary else "",
        })

    conn.close()
    return results


@router.post("")
async def do_search(body: SearchRequest, request: Request):
    query = body.query.strip()

    if _use_dify():
        return await _dify_search(query, request)

    keywords = _extract_keywords(query)
    results = _search_engineers(keywords)
    kw_text = "・".join(keywords) if keywords else query
    ai_insight = (
        kw_text + "に関連するエンジニアを検索しました。"
        + str(len(results)) + "件の結果が見つかりました。"
    )
    return {"ai_insight": ai_insight, "results": results}


async def _dify_search(query: str, request: Request):
    import httpx

    user = request.state.user
    payload = {
        "inputs": {"search_query": query},
        "response_mode": "blocking",
        "user": user["user_id"],
    }
    headers = {"Authorization": "Bearer " + DIFY_API_KEY}

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                DIFY_BASE_URL + "/v1/workflows/run", json=payload, headers=headers
            )
            data = resp.json()

        outputs = data.get("data", {}).get("outputs", {})
        conditions = outputs.get("conditions", {})
        ai_insight = outputs.get("ai_insight", "検索結果です。")
        keywords = conditions.get("skills", [])
        results = _search_engineers(keywords)
        return {"ai_insight": ai_insight, "results": results}
    except Exception:
        keywords = _extract_keywords(query)
        results = _search_engineers(keywords)
        return {
            "ai_insight": "検索結果です（" + str(len(results)) + "件）。",
            "results": results,
        }
