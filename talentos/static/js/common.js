/**
 * 共通関数
 */

/** fetch ラッパー（JSON） */
async function apiFetch(url, options = {}) {
  const defaults = {
    headers: { 'Content-Type': 'application/json' },
  };
  const res = await fetch(url, { ...defaults, ...options });
  if (res.redirected) {
    window.location.href = res.url;
    return null;
  }
  return res.json();
}

/** ログアウト */
async function doLogout() {
  await fetch('/api/auth/logout', { method: 'POST' });
  window.location.href = '/login';
}

/** サイドナビのアクティブ状態を設定 */
function setActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.sidenav a[data-path]').forEach(a => {
    if (a.dataset.path === path) {
      a.classList.add('active');
    }
  });
}

document.addEventListener('DOMContentLoaded', setActiveNav);
