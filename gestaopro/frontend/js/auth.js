// =========================================================
// GestãoPro — Módulo de Autenticação
// Portado de: backend/app/core/security.py (lógica JWT)
//             frontend/src/hooks/useAuth.tsx (fluxo)
//             frontend/src/services/api.ts (interceptors)
// =========================================================

const Auth = (() => {
  const API = window.GestaoAPI;
  const STORAGE_USER = 'gestaopro_user';

  function getAccessToken() { return localStorage.getItem('gestaopro_access'); }
  function getRefreshToken() { return localStorage.getItem('gestaopro_refresh'); }
  function isAuthenticated() { return !!getAccessToken(); }
  function getUser() {
    const s = sessionStorage.getItem(STORAGE_USER);
    return s ? JSON.parse(s) : null;
  }

  async function login(email, password) {
    const body = new URLSearchParams({ username: email, password });
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body
    });
    if (!res.ok) throw new Error(res.status);
    const data = await res.json();
    localStorage.setItem('gestaopro_access', data.access_token);
    localStorage.setItem('gestaopro_refresh', data.refresh_token);
    // fetch user profile
    const me = await fetchWithAuth('/api/v1/users/me');
    sessionStorage.setItem(STORAGE_USER, JSON.stringify(me));
    return me;
  }

  async function logout() {
    const rt = getRefreshToken();
    if (rt) {
      try {
        await fetchWithAuth('/api/v1/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: rt })
        });
      } catch (_) {}
    }
    _clearStorage();
    window.location.href = '../index.html';
  }

  function _clearStorage() {
    localStorage.removeItem('gestaopro_access');
    localStorage.removeItem('gestaopro_refresh');
    sessionStorage.removeItem(STORAGE_USER);
  }

  async function _refresh() {
    const rt = getRefreshToken();
    if (!rt) throw new Error('no_refresh');
    const res = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: rt })
    });
    if (!res.ok) throw new Error('refresh_failed');
    const data = await res.json();
    localStorage.setItem('gestaopro_access', data.access_token);
    localStorage.setItem('gestaopro_refresh', data.refresh_token);
    return data.access_token;
  }

  // ── Fetch with auth + automatic token refresh ──────────────────────────
  async function fetchWithAuth(url, opts = {}) {
    const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
    const token = getAccessToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    let res = await fetch(url, { ...opts, headers });

    if (res.status === 401) {
      try {
        const newToken = await _refresh();
        headers['Authorization'] = `Bearer ${newToken}`;
        res = await fetch(url, { ...opts, headers });
      } catch (_) {
        _clearStorage();
        window.location.href = '../index.html';
        throw new Error('session_expired');
      }
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw Object.assign(new Error(err.detail || 'request_error'), { status: res.status, data: err });
    }
    if (res.status === 204) return null;
    return res.json();
  }

  function requireAuth() {
    if (!isAuthenticated()) {
      window.location.href = '../index.html';
      return false;
    }
    return true;
  }

  return { login, logout, fetchWithAuth, getUser, isAuthenticated, requireAuth, getAccessToken };
})();
