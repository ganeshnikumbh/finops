<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">AWS Trusted Advisor Recommendations</h2>
        <p class="text-gray-600 mt-1">Optimize your AWS infrastructure and reduce costs</p>
      </div>
      <div class="flex items-center space-x-4">
        <div class="text-right">
          <p class="text-sm text-gray-500">Total Savings</p>
          <p class="text-2xl font-bold text-green-600">${{ totalSavings.toFixed(2) }}/month</p>
        </div>
        <button
          @click="refreshRecommendations"
          :disabled="loading"
          class="btn-secondary"
        >
          <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="card">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Total Recommendations</p>
            <p class="text-2xl font-bold text-gray-900">{{ recommendations.length }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Warnings</p>
            <p class="text-2xl font-bold text-gray-900">{{ warningCount }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Auto-Implementable</p>
            <p class="text-2xl font-bold text-gray-900">{{ autoImplementableCount }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 rounded-lg">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Errors</p>
            <p class="text-2xl font-bold text-gray-900">{{ errorCount }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-4 items-center">
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium text-gray-700">Filter by:</label>
        <select v-model="statusFilter" class="border border-gray-300 rounded-md px-3 py-1 text-sm">
          <option value="">All Status</option>
          <option value="warning">Warnings</option>
          <option value="error">Errors</option>
          <option value="ok">OK</option>
        </select>
      </div>
      <div class="flex items-center space-x-2">
        <select v-model="categoryFilter" class="border border-gray-300 rounded-md px-3 py-1 text-sm">
          <option value="">All Categories</option>
          <option value="cost_optimization">Cost Optimization</option>
          <option value="security">Security</option>
          <option value="fault_tolerance">Fault Tolerance</option>
          <option value="performance">Performance</option>
        </select>
      </div>
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium text-gray-700">Show:</label>
        <select v-model="implementationFilter" class="border border-gray-300 rounded-md px-3 py-1 text-sm">
          <option value="">All</option>
          <option value="auto">Auto-Implementable</option>
          <option value="manual">Manual Only</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <LoadingSpinner message="Loading recommendations..." />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card bg-red-50 border-red-200">
      <div class="flex items-center">
        <svg class="w-6 h-6 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div>
          <h3 class="text-lg font-medium text-red-800">Error Loading Recommendations</h3>
          <p class="text-red-600">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredRecommendations.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No recommendations found</h3>
      <p class="mt-1 text-sm text-gray-500">Try adjusting your filters or refresh the data.</p>
    </div>

    <!-- Recommendations Grid -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <RecommendationCard
        v-for="recommendation in filteredRecommendations"
        :key="recommendation.check_id"
        :recommendation="recommendation"
        @implementation-completed="handleImplementationCompleted"
      />
    </div>

    <!-- Implementation Summary -->
    <div v-if="implementationSummary.length > 0" class="card bg-blue-50 border-blue-200">
      <h3 class="text-lg font-medium text-blue-800 mb-3">Recent Implementations</h3>
      <div class="space-y-2">
        <div v-for="summary in implementationSummary" :key="summary.checkId" class="flex justify-between items-center">
          <span class="text-sm text-blue-700">{{ summary.message }}</span>
          <span v-if="summary.savings" class="text-sm font-medium text-green-600">
            +${{ summary.savings.toFixed(2) }}/month
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/api.js'
import LoadingSpinner from './LoadingSpinner.vue'
import RecommendationCard from './RecommendationCard.vue'

export default {
  name: 'RecommendationList',
  components: {
    LoadingSpinner,
    RecommendationCard
  },
  setup() {
    const recommendations = ref([])
    const loading = ref(false)
    const error = ref(null)
    const statusFilter = ref('')
    const categoryFilter = ref('')
    const implementationFilter = ref('')
    const implementationSummary = ref([])

    const filteredRecommendations = computed(() => {
      return recommendations.value.filter(rec => {
        // Status filter
        if (statusFilter.value && rec.status !== statusFilter.value) {
          return false
        }
        
        // Category filter
        if (categoryFilter.value && rec.category !== categoryFilter.value) {
          return false
        }
        
        // Implementation filter
        if (implementationFilter.value === 'auto' && !rec.can_implement) {
          return false
        }
        if (implementationFilter.value === 'manual' && rec.can_implement) {
          return false
        }
        
        return true
      })
    })

    const totalSavings = computed(() => {
      return recommendations.value.reduce((total, rec) => {
        return total + (rec.estimated_savings || 0)
      }, 0)
    })

    const warningCount = computed(() => {
      return recommendations.value.filter(rec => rec.status === 'warning').length
    })

    const errorCount = computed(() => {
      return recommendations.value.filter(rec => rec.status === 'error').length
    })

    const autoImplementableCount = computed(() => {
      return recommendations.value.filter(rec => rec.can_implement).length
    })

    const refreshRecommendations = async () => {
      loading.value = true
      error.value = null

      try {
        const data = await apiService.getRecommendations()
        recommendations.value = data.recommendations
      } catch (err) {
        console.error('Failed to fetch recommendations:', err)
        error.value = err.response?.data?.detail || 'Failed to load recommendations'
      } finally {
        loading.value = false
      }
    }

    const handleImplementationCompleted = (result) => {
      // Add to implementation summary
      implementationSummary.value.unshift({
        checkId: result.checkId,
        message: `Implementation ${result.success ? 'succeeded' : 'failed'}`,
        savings: result.savings || 0
      })

      // Keep only last 5 implementations
      if (implementationSummary.value.length > 5) {
        implementationSummary.value = implementationSummary.value.slice(0, 5)
      }

      // Update the recommendation in the list
      const index = recommendations.value.findIndex(r => r.check_id === result.checkId)
      if (index !== -1) {
        recommendations.value[index] = {
          ...recommendations.value[index],
          status: result.success ? 'ok' : 'error'
        }
      }
    }

    onMounted(() => {
      refreshRecommendations()
    })

    return {
      recommendations,
      loading,
      error,
      statusFilter,
      categoryFilter,
      implementationFilter,
      implementationSummary,
      filteredRecommendations,
      totalSavings,
      warningCount,
      errorCount,
      autoImplementableCount,
      refreshRecommendations,
      handleImplementationCompleted
    }
  }
}
</script> 