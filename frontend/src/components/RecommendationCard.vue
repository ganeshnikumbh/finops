<template>
  <div class="card hover:shadow-lg transition-shadow duration-200">
    <div class="flex justify-between items-start mb-4">
      <div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ recommendation.title }}</h3>
        <p class="text-sm text-gray-600 mb-3">{{ recommendation.description }}</p>
      </div>
      <div class="flex flex-col items-end">
        <span 
          :class="[
            'status-badge',
            {
              'status-ok': recommendation.status === 'ok',
              'status-warning': recommendation.status === 'warning',
              'status-error': recommendation.status === 'error',
              'status-not-available': recommendation.status === 'not_available'
            }
          ]"
        >
          {{ recommendation.status }}
        </span>
        <span class="text-xs text-gray-500 mt-1">{{ recommendation.category }}</span>
      </div>
    </div>

    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-4">
        <div v-if="recommendation.estimated_savings" class="text-sm">
          <span class="text-gray-500">Estimated Savings:</span>
          <span class="font-semibold text-green-600 ml-1">${{ recommendation.estimated_savings.toFixed(2) }}/month</span>
        </div>
        <div v-if="recommendation.affected_resources && recommendation.affected_resources.length > 0" class="text-sm">
          <span class="text-gray-500">Affected Resources:</span>
          <span class="font-semibold text-blue-600 ml-1">{{ recommendation.affected_resources.length }}</span>
        </div>
      </div>
    </div>

    <div class="flex justify-between items-center">
      <div class="text-xs text-gray-400">
        Last updated: {{ formatDate(recommendation.last_updated) }}
      </div>
      <div class="flex space-x-2">
        <button
          v-if="recommendation.can_implement"
          @click="handleImplement"
          :disabled="implementing"
          class="btn-primary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="implementing">Implementing...</span>
          <span v-else>Implement</span>
        </button>
        <button
          v-if="recommendation.can_implement"
          @click="handleDryRun"
          :disabled="implementing"
          class="btn-secondary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Dry Run
        </button>
        <span v-else class="text-xs text-gray-500 italic">Manual implementation required</span>
      </div>
    </div>

    <!-- Implementation Result -->
    <div v-if="implementationResult" class="mt-4 p-3 rounded-lg" :class="resultClasses">
      <div class="flex items-center">
        <div v-if="implementationResult.success" class="text-green-600 mr-2">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <div v-else class="text-red-600 mr-2">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div>
          <p class="font-medium">{{ implementationResult.message }}</p>
          <p v-if="implementationResult.savings" class="text-sm">
            Savings: ${{ implementationResult.savings.toFixed(2) }}/month
          </p>
          <p v-if="implementationResult.affected_resources && implementationResult.affected_resources.length > 0" class="text-sm">
            Affected: {{ implementationResult.affected_resources.length }} resources
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'RecommendationCard',
  props: {
    recommendation: {
      type: Object,
      required: true
    }
  },
  emits: ['implementation-completed'],
  setup(props, { emit }) {
    const implementing = ref(false)
    const implementationResult = ref(null)

    const resultClasses = computed(() => {
      if (!implementationResult.value) return ''
      return implementationResult.value.success
        ? 'bg-green-50 border border-green-200'
        : 'bg-red-50 border border-red-200'
    })

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown'
      const date = new Date(dateString)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
    }

    const handleImplement = async () => {
      await implementRecommendation(false)
    }

    const handleDryRun = async () => {
      await implementRecommendation(true)
    }

    const implementRecommendation = async (dryRun) => {
      implementing.value = true
      implementationResult.value = null

      try {
        const result = await apiService.implementRecommendation(props.recommendation.check_id, {
          dryRun: dryRun
        })
        
        implementationResult.value = result
        emit('implementation-completed', {
          checkId: props.recommendation.check_id,
          success: result.success,
          savings: result.savings
        })
      } catch (error) {
        console.error('Implementation failed:', error)
        implementationResult.value = {
          success: false,
          message: error.response?.data?.detail || 'Implementation failed'
        }
      } finally {
        implementing.value = false
      }
    }

    return {
      implementing,
      implementationResult,
      resultClasses,
      formatDate,
      handleImplement,
      handleDryRun
    }
  }
}
</script> 