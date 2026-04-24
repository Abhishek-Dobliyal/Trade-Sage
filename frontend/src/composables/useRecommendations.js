import { ref } from 'vue'
import api from '../api/client'

const recommendations = ref([])
const loading = ref(false)
const generating = ref(false)
const error = ref(null)

export function useRecommendations() {
  async function fetchRecommendations() {
    loading.value = true
    error.value = null
    try {
      const res = await api.get('/recommendations')
      recommendations.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
    } finally {
      loading.value = false
    }
  }

  async function generateRecommendations() {
    generating.value = true
    error.value = null
    try {
      const res = await api.post('/recommendations/generate')
      recommendations.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
    } finally {
      generating.value = false
    }
  }

  return { recommendations, loading, generating, error, fetchRecommendations, generateRecommendations }
}
