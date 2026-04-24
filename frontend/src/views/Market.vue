<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Market & News" />
    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- Indices -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="idx in indices"
          :key="idx.name"
          class="bg-gray-800 border border-gray-700 rounded-xl p-4"
        >
          <div class="text-sm text-gray-400 mb-1">{{ idx.name }}</div>
          <div class="text-2xl font-bold text-gray-100">{{ formatNum(idx.value) }}</div>
          <div
            :class="['text-sm font-medium mt-1', idx.change >= 0 ? 'text-emerald-400' : 'text-rose-400']"
          >
            {{ idx.change >= 0 ? '+' : '' }}{{ formatNum(idx.change) }}
            ({{ idx.change_pct >= 0 ? '+' : '' }}{{ idx.change_pct }}%)
          </div>
        </div>
      </div>

      <!-- Stock Lookup -->
      <div class="bg-gray-800 border border-gray-700 rounded-xl p-5">
        <h3 class="text-sm font-medium text-gray-400 mb-4">Stock Lookup</h3>
        <form class="flex gap-3 mb-4" @submit.prevent="handleSearch">
          <input
            v-model="searchSymbol"
            type="text"
            placeholder="Enter symbol (e.g. RELIANCE)"
            class="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-emerald-500 transition-colors"
          />
          <button
            type="submit"
            :disabled="!searchSymbol.trim() || searchLoading"
            class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg text-sm font-medium transition-colors"
          >
            <i :class="['fa-solid', searchLoading ? 'fa-spinner fa-spin' : 'fa-magnifying-glass']"></i>
          </button>
        </form>

        <div v-if="searchError" class="text-rose-400 text-sm mb-4">
          <i class="fa-solid fa-circle-exclamation mr-1"></i>{{ searchError }}
        </div>

        <div v-if="quote" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <div class="text-xs text-gray-500">Current Price</div>
            <div class="text-lg font-semibold text-gray-100">₹{{ formatNum(quote.current_price) }}</div>
          </div>
          <div>
            <div class="text-xs text-gray-500">Previous Close</div>
            <div class="text-lg font-semibold text-gray-300">₹{{ formatNum(quote.previous_close) }}</div>
          </div>
          <div>
            <div class="text-xs text-gray-500">Day Change</div>
            <div :class="['text-lg font-semibold', quote.day_change >= 0 ? 'text-emerald-400' : 'text-rose-400']">
              {{ quote.day_change >= 0 ? '+' : '' }}{{ formatNum(quote.day_change) }}
            </div>
          </div>
          <div>
            <div class="text-xs text-gray-500">Change %</div>
            <div :class="['text-lg font-semibold', quote.day_change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400']">
              {{ quote.day_change_pct >= 0 ? '+' : '' }}{{ quote.day_change_pct }}%
            </div>
          </div>
        </div>

        <div v-if="history.length" class="h-64">
          <Line :data="chartData" :options="chartOptions" />
        </div>
      </div>

      <!-- News -->
      <div class="bg-gray-800 border border-gray-700 rounded-xl p-5">
        <h3 class="text-sm font-medium text-gray-400 mb-4">Market News</h3>
        <div v-if="news.length" class="space-y-3">
          <a
            v-for="(item, i) in news"
            :key="i"
            :href="item.link"
            target="_blank"
            rel="noopener"
            class="flex items-start gap-3 p-3 bg-gray-900/50 rounded-lg hover:bg-gray-900 transition-colors group"
          >
            <i class="fa-solid fa-newspaper text-gray-600 mt-0.5"></i>
            <div class="flex-1 min-w-0">
              <div class="text-sm text-gray-200 group-hover:text-emerald-400 transition-colors">
                {{ item.title }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ item.source }} &middot; {{ formatTime(item.published) }}
              </div>
            </div>
            <i class="fa-solid fa-arrow-up-right-from-square text-xs text-gray-600 group-hover:text-gray-400"></i>
          </a>
        </div>
        <div v-else class="text-gray-500 text-sm">
          <i class="fa-solid fa-spinner fa-spin mr-2"></i>Loading news...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Filler,
} from 'chart.js'
import PageHeader from '../components/layout/PageHeader.vue'
import { useMarket } from '../composables/useMarket'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler)

import { formatNum, formatTime } from '../utils/format'

const { indices, news, quote, history, loading: searchLoading, error: searchError, fetchIndices, fetchNews, fetchQuote, fetchHistory } = useMarket()
const searchSymbol = ref('')

onMounted(() => {
  fetchIndices()
  fetchNews()
})

async function handleSearch() {
  const sym = searchSymbol.value.trim().toUpperCase()
  if (!sym) return
  await Promise.all([fetchQuote(sym), fetchHistory(sym)])
}

const chartData = computed(() => ({
  labels: history.value.map(d => {
    const dt = new Date(d.date)
    return dt.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
  }),
  datasets: [{
    label: 'Close Price',
    data: history.value.map(d => d.close),
    borderColor: '#10b981',
    backgroundColor: 'rgba(16, 185, 129, 0.08)',
    borderWidth: 1.5,
    pointRadius: 0,
    pointHitRadius: 10,
    fill: true,
    tension: 0.3,
  }],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      ticks: { color: '#6b7280', maxTicksLimit: 8, font: { size: 10 } },
      grid: { display: false },
    },
    y: {
      ticks: { color: '#6b7280', font: { size: 10 } },
      grid: { color: 'rgba(75, 85, 99, 0.3)' },
    },
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1f2937',
      titleColor: '#e5e7eb',
      bodyColor: '#9ca3af',
      borderColor: '#374151',
      borderWidth: 1,
    },
  },
}


</script>
