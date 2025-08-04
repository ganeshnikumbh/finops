import axios from 'axios'

// Create axios instance with default configuration
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API service methods
export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  },

  // Get recommendations
  async getRecommendations() {
    const response = await api.get('/recommendations')
    return response.data
  },

  // Implement recommendation
  async implementRecommendation(checkId, options = {}) {
    const response = await api.post(`/implement/${checkId}`, {
      dry_run: options.dryRun || false,
      force: options.force || false,
    })
    return response.data
  },

  // Get implementation status
  async getImplementationStatus(checkId) {
    const response = await api.get(`/implementations/${checkId}/status`)
    return response.data
  },

  // Get available automations
  async getAvailableAutomations() {
    const response = await api.get('/automations/available')
    return response.data
  },

  // Execute automation
  async executeAutomation(automationId, options = {}) {
    const response = await api.post(`/automations/${automationId}/execute`, {
      dry_run: options.dryRun || false,
      force: options.force || false,
    })
    return response.data
  },
}

export default apiService 