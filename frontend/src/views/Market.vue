<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Market" />
    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- Indices -->
      <div v-if="!indices.length" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="n in 3" :key="n" class="bg-gray-800 border border-gray-700 rounded-xl p-4 animate-pulse">
          <div class="h-4 w-20 bg-gray-700 rounded mb-3"></div>
          <div class="h-7 w-28 bg-gray-700 rounded mb-2"></div>
          <div class="h-4 w-24 bg-gray-700 rounded"></div>
        </div>
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="(idx, i) in indices"
          :key="idx.name"
          class="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-gray-600 transition-colors animate__animated animate__fadeInUp"
          :style="{ animationDelay: i * 100 + 'ms' }"
        >
          <div class="flex items-center justify-between mb-1">
            <span class="text-sm text-gray-400">{{ idx.name }}</span>
            <i :class="['fa-solid text-xs', idx.change >= 0 ? 'fa-caret-up text-emerald-400' : 'fa-caret-down text-rose-400']"></i>
          </div>
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
      <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate__animated animate__fadeIn">
        <h3 class="text-sm font-medium text-gray-400 mb-4">
          <i class="fa-solid fa-magnifying-glass-chart mr-1.5 text-gray-600"></i>Stock Lookup
        </h3>
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

        <div v-if="quote" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 animate__animated animate__fadeIn">
          <div class="animate__animated animate__fadeInUp" style="animation-delay: 0ms">
            <div class="text-xs text-gray-500"><i class="fa-solid fa-indian-rupee-sign mr-1 text-gray-600"></i>Current Price</div>
            <div class="text-lg font-semibold text-gray-100">₹{{ formatNum(quote.current_price) }}</div>
          </div>
          <div class="animate__animated animate__fadeInUp" style="animation-delay: 50ms">
            <div class="text-xs text-gray-500"><i class="fa-solid fa-clock-rotate-left mr-1 text-gray-600"></i>Previous Close</div>
            <div class="text-lg font-semibold text-gray-300">₹{{ formatNum(quote.previous_close) }}</div>
          </div>
          <div class="animate__animated animate__fadeInUp" style="animation-delay: 100ms">
            <div class="text-xs text-gray-500"><i class="fa-solid fa-arrow-right-arrow-left mr-1 text-gray-600"></i>Day Change</div>
            <div :class="['text-lg font-semibold', quote.day_change >= 0 ? 'text-emerald-400' : 'text-rose-400']">
              {{ quote.day_change >= 0 ? '+' : '' }}{{ formatNum(quote.day_change) }}
            </div>
          </div>
          <div class="animate__animated animate__fadeInUp" style="animation-delay: 150ms">
            <div class="text-xs text-gray-500"><i class="fa-solid fa-percent mr-1 text-gray-600"></i>Change %</div>
            <div :class="['text-lg font-semibold', quote.day_change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400']">
              {{ quote.day_change_pct >= 0 ? '+' : '' }}{{ quote.day_change_pct }}%
            </div>
          </div>
        </div>

        <div v-if="history.length" class="h-64 animate__animated animate__fadeIn">
          <Line :data="chartData" :options="chartOptions" />
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

import { formatNum } from '../utils/format'

const { indices, quote, history, loading: searchLoading, error: searchError, fetchIndices, fetchQuote, fetchHistory } = useMarket()
const searchSymbol = ref('')

onMounted(fetchIndices)

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
