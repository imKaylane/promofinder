/**
 * GestãoPro — Módulo API cliente (EX6)
 * Funções de alto nível para cada entidade do ERP.
 * Usa Auth.fetchWithAuth internamente.
 * Depende de: config.js, auth.js
 */

const API = (() => {

  // ── Helper interno ─────────────────────────────────────
  function _url(path) {
    const cfg = window.GestaoConfig;
    return cfg ? `${cfg.API_BASE}${path}` : path;
  }

  function _qs(params) {
    const q = Object.entries(params)
      .filter(([, v]) => v !== '' && v !== null && v !== undefined)
      .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
      .join('&');
    return q ? `?${q}` : '';
  }

  // ── Produtos ──────────────────────────────────────────
  const Products = {
    list:   (params = {}) => Auth.fetchWithAuth(_url(`/api/v1/products${_qs(params)}`)),
    get:    (id)          => Auth.fetchWithAuth(_url(`/api/v1/products/${id}`)),
    create: (data)        => Auth.fetchWithAuth(_url('/api/v1/products'), { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data)    => Auth.fetchWithAuth(_url(`/api/v1/products/${id}`), { method: 'PUT', body: JSON.stringify(data) }),
    remove: (id)          => Auth.fetchWithAuth(_url(`/api/v1/products/${id}`), { method: 'DELETE' }),
  };

  // ── Clientes ──────────────────────────────────────────
  const Customers = {
    list:   (params = {}) => Auth.fetchWithAuth(_url(`/api/v1/customers${_qs(params)}`)),
    get:    (id)          => Auth.fetchWithAuth(_url(`/api/v1/customers/${id}`)),
    create: (data)        => Auth.fetchWithAuth(_url('/api/v1/customers'), { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data)    => Auth.fetchWithAuth(_url(`/api/v1/customers/${id}`), { method: 'PUT', body: JSON.stringify(data) }),
    remove: (id)          => Auth.fetchWithAuth(_url(`/api/v1/customers/${id}`), { method: 'DELETE' }),
  };

  // ── Fornecedores ──────────────────────────────────────
  const Suppliers = {
    list:   (params = {}) => Auth.fetchWithAuth(_url(`/api/v1/suppliers${_qs(params)}`)),
    get:    (id)          => Auth.fetchWithAuth(_url(`/api/v1/suppliers/${id}`)),
    create: (data)        => Auth.fetchWithAuth(_url('/api/v1/suppliers'), { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data)    => Auth.fetchWithAuth(_url(`/api/v1/suppliers/${id}`), { method: 'PUT', body: JSON.stringify(data) }),
    patch:  (id, data)    => Auth.fetchWithAuth(_url(`/api/v1/suppliers/${id}`), { method: 'PATCH', body: JSON.stringify(data) }),
    remove: (id)          => Auth.fetchWithAuth(_url(`/api/v1/suppliers/${id}`), { method: 'DELETE' }),
  };

  // ── Usuários ──────────────────────────────────────────
  const Users = {
    list:  (params = {}) => Auth.fetchWithAuth(_url(`/api/v1/admin/users${_qs(params)}`)),
    audit: (params = {}) => Auth.fetchWithAuth(_url(`/api/v1/audit${_qs(params)}`)),
  };

  // ── ViaCEP ────────────────────────────────────────────
  /**
   * Consulta o ViaCEP e preenche campos de endereço.
   *
   * @param {string} cep - CEP a consultar
   * @param {object} fieldMap - mapeamento { campo: seletor }
   *   Ex: { logradouro: '#address', localidade: '#city', uf: '#state' }
   * @returns {object|null} dados do endereço ou null em caso de erro
   */
  async function lookupCEP(cep, fieldMap = {}) {
    const digits = (cep || '').replace(/\D/g, '');
    if (digits.length !== 8) return null;

    try {
      const url = window.GestaoConfig
        ? window.GestaoConfig.VIACEP_URL(digits)
        : `https://viacep.com.br/ws/${digits}/json/`;

      const res = await fetch(url);
      if (!res.ok) return null;
      const data = await res.json();
      if (data.erro) return null;

      // Preenche campos automaticamente
      const mappings = {
        logradouro: fieldMap.logradouro || fieldMap.address,
        bairro:     fieldMap.bairro || fieldMap.neighborhood,
        localidade: fieldMap.localidade || fieldMap.city,
        uf:         fieldMap.uf || fieldMap.state,
        cep:        fieldMap.cep || fieldMap.zip_code,
      };

      for (const [apiField, selector] of Object.entries(mappings)) {
        if (!selector || !data[apiField]) continue;
        const el = typeof selector === 'string'
          ? document.querySelector(selector)
          : selector;
        if (el) el.value = data[apiField];
      }

      return data;
    } catch (err) {
      console.warn('[ViaCEP] Erro ao consultar CEP:', err);
      return null;
    }
  }

  /**
   * Ativa consulta automática de CEP em um campo <input>.
   * Ao perder o foco (blur), consulta o ViaCEP e preenche campos.
   *
   * @param {string|HTMLElement} cepInput  - seletor ou elemento do campo CEP
   * @param {object}            fieldMap  - mapeamento de campos (ver lookupCEP)
   * @param {Function}          [onFound] - callback opcional com os dados retornados
   */
  function bindCEPLookup(cepInput, fieldMap = {}, onFound = null) {
    const el = typeof cepInput === 'string'
      ? document.querySelector(cepInput)
      : cepInput;
    if (!el) return;

    el.addEventListener('blur', async () => {
      const data = await lookupCEP(el.value, fieldMap);
      if (data && typeof onFound === 'function') onFound(data);
    });
  }

  return { Products, Customers, Suppliers, Users, lookupCEP, bindCEPLookup };
})();

window.GestaoAPI = API;
