import { shallowRef } from 'vue'
import api from '../api/client'

const holdings = shallowRef([])
const valuation = shallowRef(null)
const loading = shallowRef(false)
const valuationLoading = shallowRef(false)
const error = shallowRef(null)

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

  async function fetchValuation() {
    valuationLoading.value = true
    error.value = null
    try {
      const res = await api.get('/portfolio/valuation')
      valuation.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
    } finally {
      valuationLoading.value = false
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
    valuation.value = null
  }

  async function fetchCsvSchema() {
    const res = await api.get('/portfolio/csv-schema')
    return res.data
  }

  return {
    holdings, valuation, loading, valuationLoading, error,
    fetchHoldings, fetchValuation, importCsv, clearHoldings, fetchCsvSchema,
  }
}