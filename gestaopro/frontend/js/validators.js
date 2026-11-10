/**
 * GestãoPro — Módulo de validação frontend (EX3)
 * Espelha validators.py no lado cliente.
 * Sem dependências externas — JS puro.
 */

// ── E-mail ────────────────────────────────────────────────────────────────────
const _EMAIL_RE = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

export function validateEmail(value) {
  return _EMAIL_RE.test((value || "").trim());
}

// ── CPF ───────────────────────────────────────────────────────────────────────
export function validateCPF(cpf) {
  const digits = (cpf || "").replace(/\D/g, "");
  if (digits.length !== 11 || new Set(digits).size === 1) return false;
  for (let i = 9; i <= 10; i++) {
    let total = 0;
    for (let j = 0; j < i; j++) total += parseInt(digits[j]) * (i + 1 - j);
    const expected = (total * 10 % 11) % 10;
    if (expected !== parseInt(digits[i])) return false;
  }
  return true;
}

// ── CNPJ ──────────────────────────────────────────────────────────────────────
export function validateCNPJ(cnpj) {
  const digits = (cnpj || "").replace(/\D/g, "");
  if (digits.length !== 14 || new Set(digits).size === 1) return false;
  const w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  const w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  for (const [w, pos] of [[w1, 12], [w2, 13]]) {
    const total = w.reduce((s, v, i) => s + parseInt(digits[i]) * v, 0);
    const rem = total % 11;
    const expected = rem < 2 ? 0 : 11 - rem;
    if (expected !== parseInt(digits[pos])) return false;
  }
  return true;
}

// ── CEP ───────────────────────────────────────────────────────────────────────
const _CEP_RE = /^\d{5}-?\d{3}$/;

export function validateCEP(cep) {
  return _CEP_RE.test((cep || "").trim());
}

// ── Telefone (Brasil) ─────────────────────────────────────────────────────────
export function validatePhoneBR(phone) {
  const digits = (phone || "").replace(/\D/g, "");
  return digits.length === 10 || digits.length === 11;
}

// ── UF ────────────────────────────────────────────────────────────────────────
const _UFS = new Set([
  "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS",
  "MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC",
  "SP","SE","TO",
]);

export function validateUF(uf) {
  return _UFS.has((uf || "").toUpperCase());
}

// ── Data ISO YYYY-MM-DD ───────────────────────────────────────────────────────
export function validateDateISO(value) {
  if (!value) return true;  // datas são opcionais
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value.trim())) return false;
  const d = new Date(value.trim());
  return !isNaN(d.getTime());
}

// ── Número decimal não-negativo ───────────────────────────────────────────────
export function validatePositiveDecimal(value) {
  if (value === null || value === undefined || value === "") return false;
  const n = parseFloat(String(value).replace(",", "."));
  return !isNaN(n) && n >= 0;
}

// ── Documento (CPF / CNPJ) ────────────────────────────────────────────────────
export function validateDocument(document, personType = "PF") {
  return personType === "PJ" ? validateCNPJ(document) : validateCPF(document);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
/**
 * Aplica validação a um <input> ou <select>:
 * - adiciona/remove a classe "is-invalid"
 * - preenche o elemento de feedback (data-feedback="fieldName")
 * Retorna true se válido.
 */
export function setFieldValidity(fieldEl, errorMsg, formEl = null) {
  const isValid = !errorMsg;
  fieldEl.classList.toggle("is-invalid", !isValid);
  fieldEl.classList.toggle("is-valid", isValid);

  // busca o elemento de feedback pelo data-feedback ou pelo nome do campo
  const feedbackSel = `[data-feedback="${fieldEl.name || fieldEl.id}"]`;
  const container = formEl || fieldEl.closest("form") || document;
  const fb = container.querySelector(feedbackSel);
  if (fb) fb.textContent = errorMsg || "";

  return isValid;
}

/**
 * Limpa todos os estados de validação de um formulário.
 */
export function clearFormValidation(formEl) {
  formEl.querySelectorAll(".is-invalid, .is-valid").forEach((el) => {
    el.classList.remove("is-invalid", "is-valid");
  });
  formEl.querySelectorAll("[data-feedback]").forEach((el) => {
    el.textContent = "";
  });
}
