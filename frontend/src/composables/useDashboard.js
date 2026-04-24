import { ref } from 'vue'
import api from '../api/client'

const data = ref(null)
const loading = ref(false)
const error = ref(null)

export function useDashboard() {
  async function fetchDashboard() {
    loading.value = true
    error.value = null
    try {
      const res = await api.get('/dashboard')
      data.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, fetchDashboard }
}
