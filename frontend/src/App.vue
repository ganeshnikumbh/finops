<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-8 w-8 text-aws-orange" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
            </div>
            <div class="ml-4">
              <h1 class="text-2xl font-bold text-gray-900">AWS FinOps</h1>
              <p class="text-sm text-gray-500">Trusted Advisor Automation</p>
            </div>
          </div>
          
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 rounded-full" :class="healthStatusClass"></div>
              <span class="text-sm text-gray-500">{{ healthStatusText }}</span>
            </div>
            <button
              @click="refreshHealth"
              :disabled="healthLoading"
              class="text-sm text-gray-500 hover:text-gray-700"
            >
              <svg v-if="healthLoading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <RecommendationList />
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex justify-between items-center">
          <div class="text-sm text-gray-500">
            AWS FinOps Application v1.0.0
          </div>
          <div class="flex items-center space-x-4 text-sm text-gray-500">
            <a href="https://docs.aws.amazon.com/awssupport/latest/user/trusted-advisor.html" target="_blank" class="hover:text-gray-700">
              AWS Trusted Advisor
            </a>
            <a href="https://aws.amazon.com/finops/" target="_blank" class="hover:text-gray-700">
              AWS FinOps
            </a>
          </div>
        </div>
      </div>
    </footer>

    <!-- Health Status Modal -->
    <div v-if="showHealthModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-center w-12 h-12 mx-auto bg-blue-100 rounded-full">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div class="mt-3 text-center">
            <h3 class="text-lg font-medium text-gray-900">System Health</h3>
            <div class="mt-2 px-7 py-3">
              <div class="space-y-2 text-sm text-gray-500">
                <div class="flex justify-between">
                  <span>Backend Status:</span>
                  <span :class="healthStatusClass">{{ healthStatusText }}</span>
                </div>
                <div class="flex justify-between">
                  <span>AWS Connection:</span>
                  <span :class="awsConnectionClass">{{ awsConnectionText }}</span>
                </div>
                <div class="flex justify-between">
                  <span>Last Check:</span>
                  <span>{{ lastHealthCheck }}</span>
                </div>
              </div>
            </div>
            <div class="items-center px-4 py-3">
              <button
                @click="showHealthModal = false"
                class="px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from './services/api.js'
import RecommendationList from './components/RecommendationList.vue'

export default {
  name: 'App',
  components: {
    RecommendationList
  },
  setup() {
    const healthStatus = ref('unknown')
    const awsConnection = ref(false)
    const healthLoading = ref(false)
    const lastHealthCheck = ref('Never')
    const showHealthModal = ref(false)

    const healthStatusClass = computed(() => {
      switch (healthStatus.value) {
        case 'healthy':
          return 'bg-green-500'
        case 'unhealthy':
          return 'bg-red-500'
        default:
          return 'bg-yellow-500'
      }
    })

    const healthStatusText = computed(() => {
      switch (healthStatus.value) {
        case 'healthy':
          return 'Healthy'
        case 'unhealthy':
          return 'Unhealthy'
        default:
          return 'Unknown'
      }
    })

    const awsConnectionClass = computed(() => {
      return awsConnection.value ? 'text-green-600' : 'text-red-600'
    })

    const awsConnectionText = computed(() => {
      return awsConnection.value ? 'Connected' : 'Disconnected'
    })

    const checkHealth = async () => {
      healthLoading.value = true
      
      try {
        const health = await apiService.healthCheck()
        healthStatus.value = health.status
        awsConnection.value = health.aws_connection
        lastHealthCheck.value = new Date(health.timestamp).toLocaleString()
      } catch (error) {
        console.error('Health check failed:', error)
        healthStatus.value = 'unhealthy'
        awsConnection.value = false
        lastHealthCheck.value = new Date().toLocaleString()
      } finally {
        healthLoading.value = false
      }
    }

    const refreshHealth = () => {
      checkHealth()
    }

    onMounted(() => {
      checkHealth()
      
      // Check health every 30 seconds
      setInterval(checkHealth, 30000)
    })

    return {
      healthStatus,
      awsConnection,
      healthLoading,
      lastHealthCheck,
      showHealthModal,
      healthStatusClass,
      healthStatusText,
      awsConnectionClass,
      awsConnectionText,
      refreshHealth
    }
  }
}
</script> 