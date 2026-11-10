/**
 * GestãoPro — Configuração central do frontend (EX6)
 * Centraliza a base URL da API e configurações globais.
 * Carregue este arquivo ANTES de auth.js e ui.js.
 */

const GestaoConfig = (() => {
  // Em produção, substitua pelo domínio real (ex: https://erp.empresa.com)
  const API_BASE = window.__GESTAOPRO_API_BASE__ || '';

  return {
    API_BASE,
    API_URL: (path) => `${API_BASE}/api/v1${path}`,

    // Endpoints da API
    ENDPOINTS: {
      // Auth
      LOGIN:    '/api/v1/auth/login',
      REGISTER: '/api/v1/auth/register',
      REFRESH:  '/api/v1/auth/refresh',
      LOGOUT:   '/api/v1/auth/logout',
      ME:       '/api/v1/auth/me',

      // Entidades
      PRODUCTS:   '/api/v1/products',
      CUSTOMERS:  '/api/v1/customers',
      SUPPLIERS:  '/api/v1/suppliers',
      USERS:      '/api/v1/admin/users',
      AUDIT:      '/api/v1/audit',
    },

    // ViaCEP — consulta gratuita de CEP (sem chave)
    VIACEP_URL: (cep) => `https://viacep.com.br/ws/${cep.replace(/\D/g, '')}/json/`,

    // Paginação padrão
    PAGE_SIZE: 20,

    // Timeout de requisições (ms)
    REQUEST_TIMEOUT: 15000,
  };
})();

// Exporta para uso global — compatível com scripts sem módulo ES
window.GestaoConfig = GestaoConfig;
