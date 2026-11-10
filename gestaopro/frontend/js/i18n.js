// =========================================================
// GestãoPro — Módulo de Internacionalização (EX2)
// =========================================================

const I18N = (() => {
  const STORAGE_KEY = 'gestaopro_lang';
  let _lang = localStorage.getItem(STORAGE_KEY) || 'pt-BR';
  let _translations = {};

  async function load(lang) {
    const url = `../i18n/${lang}.json`;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      _translations = await res.json();
      _lang = lang;
      localStorage.setItem(STORAGE_KEY, lang);
      document.documentElement.lang = lang;
      applyAll();
    } catch (e) {
      console.warn('[i18n] Could not load', lang, e);
    }
  }

  function t(key, vars = {}) {
    const val = key.split('.').reduce((obj, k) => (obj && obj[k] !== undefined ? obj[k] : null), _translations);
    if (val === null) return key;
    return val.replace(/\{\{(\w+)\}\}/g, (_, k) => vars[k] ?? '');
  }

  function applyAll() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const text = t(key);
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.placeholder = text;
      } else {
        el.textContent = text;
      }
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      el.title = t(el.getAttribute('data-i18n-title'));
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
    });
    // Update language selector buttons
    document.querySelectorAll('.lang-selector').forEach(el => {
      el.textContent = _lang === 'pt-BR' ? '🇧🇷 PT' : '🇺🇸 EN';
    });
  }

  function getLang() { return _lang; }

  function toggle() {
    load(_lang === 'pt-BR' ? 'en' : 'pt-BR');
  }

  function formatCurrency(value, currency) {
    const cur = currency || (_lang === 'pt-BR' ? 'BRL' : 'USD');
    return new Intl.NumberFormat(_lang, { style: 'currency', currency: cur }).format(value);
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return new Intl.DateTimeFormat(_lang, { day: '2-digit', month: '2-digit', year: 'numeric' }).format(d);
  }

  function formatNumber(n) {
    return new Intl.NumberFormat(_lang).format(n);
  }

  return { load, t, applyAll, getLang, toggle, formatCurrency, formatDate, formatNumber };
})();

// Auto-load on page start
document.addEventListener('DOMContentLoaded', () => {
  I18N.load(localStorage.getItem('gestaopro_lang') || 'pt-BR');
});
