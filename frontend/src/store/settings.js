// Store centralizado de configurações do sistema
// -------------------------------------------------------------
// Objetivo: prover um único ponto de leitura/escrita das
// configurações da aplicação (geral, rede, etc.), com
// persistência simples em localStorage até existir API.
// -------------------------------------------------------------

import { defineStore } from 'pinia'

// Chave única para persistência local
const STORAGE_KEY = 'system_settings'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    // Estrutura única que pode crescer ao longo do projeto
    settings: {
      general: {
        company_name: '',
        cnpj: '',
        phone: '',
        // Endereço
        address: '',
        number: '',
        district: '',
        city: '',
        state: '',
        cep: '',
        // Para simplificar, armazenamos o preview da logo como DataURL
        // (até termos upload/backend real)
        logo_data_url: null,          // Logo principal (relatórios etc.)
        logo_sidebar_data_url: null,  // Logo para Sidebar
        logo_sidebar_mini_data_url: null, // Logo para Sidebar recolhida (mini)
        favicon_data_url: null,       // Ícone do navegador
        logo_login_data_url: null,    // Logo para modal de Login
      },
      network: {
        dynamic_compression: true,
        enable_rewards: true,
        max_commission_levels: 5,
      },
      // Configurações de pagamentos/saques
      payments: {
        withdraw_min_value: 100,     // Valor mínimo para saque (R$)
        withdraw_fee_percent: 5,     // Taxa % deduzida do valor do saque
        request_deadline_day: 10,    // Dia limite para solicitar saque
        payment_deadline_day: 20,    // Dia limite para realizar o pagamento
      },
    },
  }),

  actions: {
    // Carrega do localStorage. Se não existir, mantém defaults.
    loadFromStorage() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (!raw) return
        const parsed = JSON.parse(raw)
        // Faz merge raso para manter defaults de novos campos
        this.settings = {
          ...this.settings,
          ...parsed,
          general: { ...this.settings.general, ...(parsed.general || {}) },
          network: { ...this.settings.network, ...(parsed.network || {}) },
          payments: { ...this.settings.payments, ...(parsed.payments || {}) },
        }
      } catch (e) {
        console.error('[settings] Falha ao carregar do storage', e)
      }
    },

    // Salva toda a estrutura.
    saveToStorage() {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.settings))
      } catch (e) {
        console.error('[settings] Falha ao gravar no storage', e)
      }
    },

    // Atualiza parcialmente o bloco "general"
    setGeneral(partial) {
      this.settings.general = { ...this.settings.general, ...partial }
    },

    // Atualiza parcialmente o bloco "network"
    setNetwork(partial) {
      this.settings.network = { ...this.settings.network, ...partial }
    },

    // Atualiza parcialmente o bloco "payments"
    setPayments(partial) {
      this.settings.payments = { ...this.settings.payments, ...partial }
    },
  },
})


