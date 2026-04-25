import { shallowRef } from 'vue'
import api from '../api/client'

const recommendations = shallowRef([])
const loading = shallowRef(false)
const generating = shallowRef(false)
const error = shallowRef(null)

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