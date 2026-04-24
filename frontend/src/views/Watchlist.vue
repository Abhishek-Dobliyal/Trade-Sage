<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Watchlist" />

    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- Add to watchlist -->
      <form class="flex gap-3" @submit.prevent="handleAdd">
        <input
          v-model="newSymbol"
          type="text"
          placeholder="Symbol (e.g. RELIANCE)"
          class="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-emerald-500 transition-colors w-40"
        />
        <input
          v-model="newName"
          type="text"
          placeholder="Company name"
          class="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-emerald-500 transition-colors"
        />
        <button
          type="submit"
          :disabled="!newSymbol.trim() || !newName.trim() || adding"
          class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <i :class="['fa-solid', adding ? 'fa-spinner fa-spin' : 'fa-plus']"></i>
        </button>
      </form>

      <div v-if="error" class="text-rose-400 text-sm p-3 bg-rose-500/10 rounded-lg animate__animated animate__fadeIn">
        <i class="fa-solid fa-circle-exclamation mr-1"></i>{{ error }}
      </div>

      <div v-if="loading" class="flex items-center justify-center py-20">
        <i class="fa-solid fa-spinner fa-spin text-2xl text-gray-500"></i>
      </div>

      <div v-else-if="items.length" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="item in items"
          :key="item.id"
          class="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-gray-600 transition-colors animate__animated animate__fadeIn"
        >
          <div class="flex items-center justify-between mb-2">
            <div>
              <div class="text-base font-semibold text-gray-200">{{ item.symbol }}</div>
              <div class="text-xs text-gray-500 truncate max-w-48">{{ item.name }}</div>
            </div>
            <button
              class="text-gray-600 hover:text-rose-400 transition-colors"
              @click="handleRemove(item.symbol)"
            >
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
          <div v-if="item.current_price" class="flex items-center justify-between mt-3">
            <div class="text-lg font-bold text-gray-100">₹{{ formatNum(item.current_price) }}</div>
            <div
              :class="['text-sm font-medium', (item.day_change_pct || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400']"
            >
              <i :class="['fa-solid text-xs mr-0.5', (item.day_change_pct || 0) >= 0 ? 'fa-caret-up' : 'fa-caret-down']"></i>
              {{ (item.day_change_pct || 0) >= 0 ? '+' : '' }}{{ item.day_change_pct }}%
            </div>
          </div>
          <div v-else class="text-xs text-gray-600 mt-3">
            <i class="fa-solid fa-clock mr-1"></i>Price unavailable
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="flex flex-col items-center justify-center py-20 text-center">
        <i class="fa-solid fa-binoculars text-4xl text-gray-700 mb-4"></i>
        <p class="text-gray-400 mb-2">Your watchlist is empty</p>
        <p class="text-sm text-gray-600">Add stocks you want to track above</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/client'
import PageHeader from '../components/layout/PageHeader.vue'
import { formatNum } from '../utils/format'

const items = ref([])
const loading = ref(false)
const adding = ref(false)
const error = ref(null)
const newSymbol = ref('')
const newName = ref('')

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

async function handleAdd() {
  if (!newSymbol.value.trim() || !newName.value.trim()) return
  adding.value = true
  error.value = null
  try {
    await api.post('/watchlist', {
      symbol: newSymbol.value.trim(),
      name: newName.value.trim(),
    })
    newSymbol.value = ''
    newName.value = ''
    await fetchWatchlist()
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
  } finally {
    adding.value = false
  }
}

async function handleRemove(symbol) {
  try {
    await api.delete(`/watchlist/${symbol}`)
    items.value = items.value.filter(i => i.symbol !== symbol)
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
  }
}

onMounted(fetchWatchlist)
</script>
