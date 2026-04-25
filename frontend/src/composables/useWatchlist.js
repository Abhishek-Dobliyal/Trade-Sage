import { shallowRef } from 'vue'
import api from '../api/client'

const items = shallowRef([])
const loading = shallowRef(false)
const adding = shallowRef(false)
const error = shallowRef(null)

export function useWatchlist() {
  async function fetchWatchlist() {
    loading.value = true
    error.value = null
    try {
      const res = await api.get('/watchlist')
      items.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
    } finally {
      loading.value = false
    }
  }

  async function addItem(symbol, name) {
    adding.value = true
    error.value = null
    try {
      await api.post('/watchlist', { symbol, name })
      await fetchWatchlist()
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
    } finally {
      adding.value = false
    }
  }

  async function removeItem(symbol) {
    try {
      await api.delete(`/watchlist/${symbol}`)
      items.value = items.value.filter(i => i.symbol !== symbol)
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
    }
  }

  return { items, loading, adding, error, fetchWatchlist, addItem, removeItem }
}