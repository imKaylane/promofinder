// =========================================================
// GestãoPro — Módulo de Internacionalização (EX2)
// BUG FIX: usa /frontend/i18n/ (absoluto) em vez de ../i18n/
// Suporta pt-BR, en, es
// =========================================================

const I18N = (() => {
  const STORAGE_KEY = 'gestaopro_lang';

  // Base sempre /frontend/i18n/ independente de onde a página está
  const I18N_BASE = '/frontend/i18n/';

  let _lang = localStorage.getItem(STORAGE_KEY) || _detectLang();
  let _translations = {};

  function _detectLang() {
    const nav = (navigator.language || navigator.userLanguage || 'pt-BR').toLowerCase();
    if (nav.startsWith('pt')) return 'pt-BR';
    if (nav.startsWith('es')) return 'es';
    return 'en';
  }

  async function load(lang) {
    const url = `${I18N_BASE}${lang}.json`;
    try {
      const res = await fetch(url);
      // Validar content-type — evitar receber HTML do index
      const ct = res.headers.get('content-type') || '';
      if (!res.ok || !ct.includes('json')) {
        console.warn('[i18n] Falha ao carregar', lang, res.status, ct);
        if (lang !== 'pt-BR') return load('pt-BR');
        return;
      }
      _translations = await res.json();
      _lang = lang;
      localStorage.setItem(STORAGE_KEY, lang);
      document.documentElement.lang = lang;
      applyAll();
      // Sync language selector if present
      const sel = document.getElementById('lang-select');
      if (sel) sel.value = lang;
    } catch (e) {
      console.warn('[i18n] Erro ao carregar', lang, e);
    }
  }

  function t(key, vars = {}) {
    const val = key.split('.').reduce((obj, k) => (obj && obj[k] !== undefined ? obj[k] : null), _translations);
    if (val === null) return key;
    return val.replace(/\{\{(\w+)\}\}/g, (_, k) => vars[k] ?? '');
  }

  function applyAll() {
    // Textos simples
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key  = el.getAttribute('data-i18n');
      const text = t(key);
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.placeholder = text;
      } else {
        el.textContent = text;
      }
    });

    // Placeholders explícitos
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
    });

    // title="..."
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      el.title = t(el.getAttribute('data-i18n-title'));
    });

    // aria-label="..."
    document.querySelectorAll('[data-i18n-aria]').forEach(el => {
      el.setAttribute('aria-label', t(el.getAttribute('data-i18n-aria')));
    });

    // <option> com data-i18n
    document.querySelectorAll('option[data-i18n]').forEach(el => {
      el.textContent = t(el.getAttribute('data-i18n'));
    });

    // <title> da página
    const titleKey = document.documentElement.getAttribute('data-page-title');
    if (titleKey) document.title = `GestãoPro — ${t(titleKey)}`;

    // Disparar evento para código externo se registrar
    document.dispatchEvent(new CustomEvent('i18n:applied', { detail: { lang: _lang } }));
  }

  function getLang() { return _lang; }

  function formatCurrency(value, currency) {
    const cur = currency || (_lang === 'pt-BR' ? 'BRL' : _lang === 'es' ? 'EUR' : 'USD');
    return new Intl.NumberFormat(_lang, { style: 'currency', currency: cur }).format(value);
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    if (isNaN(d)) return dateStr;
    return new Intl.DateTimeFormat(_lang, { day: '2-digit', month: '2-digit', year: 'numeric' }).format(d);
  }

  function formatDatetime(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    if (isNaN(d)) return dateStr;
    return new Intl.DateTimeFormat(_lang, {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    }).format(d);
  }

  function formatNumber(n) {
    return new Intl.NumberFormat(_lang).format(n);
  }

  // ── Decimal separator for the current locale ──────────────
  function decimalSeparator() {
    return _lang === 'pt-BR' || _lang === 'es' ? ',' : '.';
  }

  return { load, t, applyAll, getLang, formatCurrency, formatDate, formatDatetime, formatNumber, decimalSeparator };
})();

// Auto-load on page start
document.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('gestaopro_lang');
  const nav   = (navigator.language || 'pt-BR').toLowerCase();
  const lang  = saved || (nav.startsWith('pt') ? 'pt-BR' : nav.startsWith('es') ? 'es' : 'en');
  I18N.load(lang);
});
