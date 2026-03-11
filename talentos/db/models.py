"""テーブル定義 SQL"""

TABLES = [
    # ユーザー管理
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id       TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        name          TEXT NOT NULL,
        role          TEXT NOT NULL CHECK(role IN ('engineer','sales','admin'))
    )
    """,
    # エンジニア基本情報
    """
    CREATE TABLE IF NOT EXISTS engineers (
        engineer_id        TEXT PRIMARY KEY REFERENCES users(user_id),
        specialty          TEXT,
        relocation_ok      INTEGER DEFAULT 0,
        work_location      TEXT,
        nearest_station    TEXT,
        education_level    TEXT,
        school_name        TEXT,
        faculty_name       TEXT,
        department_name    TEXT,
        self_pr            TEXT,
        hobbies            TEXT,
        skill_level        TEXT,
        language_skills    TEXT,
        tool_info          TEXT,
        certifications     TEXT,
        updated_at         TEXT
    )
    """,
    # スキルシート
    """
    CREATE TABLE IF NOT EXISTS skill_sheets (
        sheet_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        engineer_id    TEXT NOT NULL REFERENCES users(user_id),
        theme          TEXT NOT NULL CHECK(theme IN ('basic','career','skills')),
        raw_data       TEXT,
        optimized_data TEXT,
        created_at     TEXT NOT NULL,
        updated_at     TEXT NOT NULL
    )
    """,
    # 職務経歴
    """
    CREATE TABLE IF NOT EXISTS experiences (
        exp_id         INTEGER PRIMARY KEY AUTOINCREMENT,
        engineer_id    TEXT NOT NULL REFERENCES users(user_id),
        project_name   TEXT,
        period_start   TEXT,
        period_end     TEXT,
        team_size      INTEGER,
        role_title     TEXT,
        tech_stack     TEXT,
        description    TEXT,
        created_at     TEXT
    )
    """,
    # ヒアリングログ
    """
    CREATE TABLE IF NOT EXISTS hearing_logs (
        log_id         INTEGER PRIMARY KEY AUTOINCREMENT,
        engineer_id    TEXT NOT NULL REFERENCES users(user_id),
        theme          TEXT NOT NULL,
        messages       TEXT NOT NULL,
        completed      INTEGER DEFAULT 0,
        completed_at   TEXT,
        dify_conversation_id TEXT
    )
    """,
]
