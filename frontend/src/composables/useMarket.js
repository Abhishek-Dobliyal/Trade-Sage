import { shallowRef } from 'vue'
import api from '../api/client'

const indices = shallowRef([])
const news = shallowRef([])
const quote = shallowRef(null)
const history = shallowRef([])
const loading = shallowRef(false)
const error = shallowRef(null)

export function useMarket() {
  async function fetchIndices() {
    try {
      const res = await api.get('/market/indices')
      indices.value = res.data
    } catch (err) {
      console.error('Failed to fetch indices:', err)
    }
  }

  async function fetchNews(limit = 20) {
    try {
      const res = await api.get('/news', { params: { limit } })
      news.value = res.data
    } catch (err) {
      console.error('Failed to fetch news:', err)
    }
  }

  async function fetchQuote(symbol) {
    loading.value = true
    error.value = null
    quote.value = null
    try {
      const res = await api.get(`/market/quote/${symbol}`)
      quote.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(symbol, period = '6mo') {
    try {
      const res = await api.get(`/market/history/${symbol}`, { params: { period } })
      history.value = res.data
    } catch (err) {
      console.error('Failed to fetch history:', err)
      history.value = []
    }
  }

  return { indices, news, quote, history, loading, error, fetchIndices, fetchNews, fetchQuote, fetchHistory }
}