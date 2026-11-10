// =========================================================
// GestãoPro — Utilitários de UI
// Toast, Modal, confirmação, loading
// =========================================================

const UI = (() => {

  // ── Toast ──────────────────────────────────────────────
  function toast(message, type = 'info', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const el = document.createElement('div');
    const icons = { success: '✓', error: '✕', info: 'ℹ' };
    el.className = `toast ${type}`;
    el.innerHTML = `<span>${icons[type] || icons.info}</span><span>${message}</span>`;
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity .3s'; }, duration);
    setTimeout(() => el.remove(), duration + 350);
  }

  // ── Loading overlay ────────────────────────────────────
  function showLoading(target) {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) return;
    el.dataset.prevContent = el.innerHTML;
    el.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;padding:24px"><div class="spinner"></div></div>`;
  }
  function hideLoading(target, html) {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) return;
    el.innerHTML = html !== undefined ? html : (el.dataset.prevContent || '');
  }

  // ── Button spinner ─────────────────────────────────────
  function btnLoading(btn, yes) {
    if (yes) {
      btn.dataset.origText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<span class="spinner" style="width:14px;height:14px;border-width:2px"></span>`;
    } else {
      btn.disabled = false;
      btn.innerHTML = btn.dataset.origText || '';
    }
  }

  // ── Modal ──────────────────────────────────────────────
  function openModal(id) {
    const m = document.getElementById(id);
    if (m) { m.classList.add('open'); document.body.style.overflow = 'hidden'; }
  }
  function closeModal(id) {
    const m = document.getElementById(id);
    if (m) { m.classList.remove('open'); document.body.style.overflow = ''; }
  }
  function closeAllModals() {
    document.querySelectorAll('.modal-overlay.open').forEach(m => {
      m.classList.remove('open');
    });
    document.body.style.overflow = '';
  }

  // Close modal on overlay click
  document.addEventListener('click', e => {
    if (e.target.classList.contains('modal-overlay')) closeAllModals();
  });
  // Close modal on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeAllModals();
  });

  // ── Confirm dialog ─────────────────────────────────────
  function confirm(message, onConfirm) {
    let overlay = document.getElementById('confirm-modal');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'confirm-modal';
      overlay.className = 'modal-overlay';
      overlay.innerHTML = `
        <div class="modal" style="max-width:380px">
          <div class="modal-header">
            <span class="modal-title" id="confirm-title">Confirmar</span>
            <button class="modal-close" onclick="UI.closeModal('confirm-modal')">✕</button>
          </div>
          <div class="modal-body"><p id="confirm-msg" style="font-size:14px;color:#475569"></p></div>
          <div class="modal-footer">
            <button class="btn btn-secondary btn-sm" onclick="UI.closeModal('confirm-modal')" data-i18n="actions.cancel"></button>
            <button class="btn btn-danger btn-sm" id="confirm-ok" data-i18n="actions.confirm"></button>
          </div>
        </div>`;
      document.body.appendChild(overlay);
    }
    document.getElementById('confirm-msg').textContent = message;
    document.getElementById('confirm-ok').onclick = () => { closeModal('confirm-modal'); onConfirm(); };
    openModal('confirm-modal');
    // Re-apply i18n
    I18N.applyAll();
  }

  // ── Form validation ────────────────────────────────────
  function validateForm(form) {
    let valid = true;
    form.querySelectorAll('[data-required]').forEach(input => {
      const err = input.closest('.form-group')?.querySelector('.form-error');
      if (!input.value.trim()) {
        input.classList.add('error');
        if (err) err.textContent = I18N.t('validation.required');
        valid = false;
      } else {
        input.classList.remove('error');
        if (err) err.textContent = '';
      }
    });
    return valid;
  }

  return { toast, showLoading, hideLoading, btnLoading, openModal, closeModal, closeAllModals, confirm, validateForm };
})();
