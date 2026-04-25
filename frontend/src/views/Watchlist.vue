<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Watchlist" />

    <div class="flex-1 overflow-y-auto p-6 space-y-6">
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

      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div v-for="n in 6" :key="n" class="bg-gray-800 border border-gray-700 rounded-xl p-4 animate-pulse">
          <div class="h-5 w-20 bg-gray-700 rounded mb-2"></div>
          <div class="h-3 w-36 bg-gray-700/50 rounded mb-4"></div>
          <div class="flex justify-between">
            <div class="h-6 w-24 bg-gray-700 rounded"></div>
            <div class="h-4 w-12 bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>

      <div v-else-if="error" class="bg-rose-500/10 border border-rose-500/20 rounded-xl p-5 animate__animated animate__fadeIn">
        <div class="flex items-start gap-3">
          <i class="fa-solid fa-circle-exclamation text-rose-400 text-xl mt-0.5"></i>
          <div>
            <div class="text-rose-400 font-medium mb-1">Failed to load watchlist</div>
            <div class="text-sm text-gray-400">{{ error }}</div>
            <button
              class="mt-3 px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 rounded-lg text-xs text-rose-400 transition-colors"
              @click="fetchWatchlist"
            >
              <i class="fa-solid fa-rotate-right mr-1"></i> Retry
            </button>
          </div>
        </div>
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
import PageHeader from '../components/layout/PageHeader.vue'
import { useWatchlist } from '../composables/useWatchlist'

import { formatNum } from '../utils/format'

const { items, loading, adding, error, fetchWatchlist, addItem, removeItem } = useWatchlist()

const newSymbol = ref('')
const newName = ref('')

async function handleAdd() {
  if (!newSymbol.value.trim() || !newName.value.trim()) return
  const sym = newSymbol.value.trim()
  const name = newName.value.trim()
  newSymbol.value = ''
  newName.value = ''
  await addItem(sym, name)
}

async function handleRemove(symbol) {
  await removeItem(symbol)
}

onMounted(fetchWatchlist)
</script>