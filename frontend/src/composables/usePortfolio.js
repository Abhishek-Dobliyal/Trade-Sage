import { ref } from 'vue'
import api from '../api/client'

const holdings = ref([])
const loading = ref(false)
const error = ref(null)

export function usePortfolio() {
  async function fetchHoldings() {
    loading.value = true
    error.value = null
    try {
      const res = await api.get('/portfolio/holdings')
      holdings.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
    } finally {
      loading.value = false
    }
  }

  async function importCsv(file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/portfolio/import', formData)
    await fetchHoldings()
    return res.data
  }

  async function clearHoldings() {
    await api.delete('/portfolio/holdings')
    holdings.value = []
  }

  async function fetchCsvSchema() {
    const res = await api.get('/portfolio/csv-schema')
    return res.data
  }

  return { holdings, loading, error, fetchHoldings, importCsv, clearHoldings, fetchCsvSchema }
}
