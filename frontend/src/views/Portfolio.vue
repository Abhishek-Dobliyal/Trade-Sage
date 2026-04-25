<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Portfolio">
      <div class="flex items-center gap-3">
        <button
          v-if="holdings.length"
          class="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-xs text-gray-400 hover:text-emerald-400 hover:border-emerald-500/30 transition-colors"
          :disabled="valuationLoading"
          @click="fetchValuation"
        >
          <i :class="['fa-solid', valuationLoading ? 'fa-spinner fa-spin' : 'fa-arrow-rotate-right']"></i>
          Live P&L
        </button>
        <button
          v-if="holdings.length"
          class="text-gray-500 hover:text-gray-300 transition-colors"
          @click="toggle"
          :title="hidden ? 'Show values' : 'Hide values'"
        >
          <i :class="['fa-solid text-sm', hidden ? 'fa-eye-slash' : 'fa-eye']"></i>
        </button>
        <button
          v-if="holdings.length"
          class="text-sm text-rose-400 hover:text-rose-300 transition-colors"
          @click="handleClear"
        >
          <i class="fa-solid fa-trash mr-1"></i> Clear
        </button>
      </div>
    </PageHeader>

    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <div v-if="loading" class="animate-pulse space-y-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-for="n in 4" :key="n" class="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div class="h-3 w-16 bg-gray-700 rounded mb-2"></div>
            <div class="h-6 w-20 bg-gray-700 rounded"></div>
          </div>
        </div>
        <div class="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
          <div class="p-4 border-b border-gray-700">
            <div class="h-4 w-32 bg-gray-700 rounded"></div>
          </div>
          <div class="p-4 space-y-3">
            <div v-for="n in 6" :key="n" class="h-10 bg-gray-700/50 rounded-lg"></div>
          </div>
        </div>
        <div class="bg-gray-800 border border-gray-700 rounded-xl p-5">
          <div class="h-4 w-28 bg-gray-700 rounded mb-4"></div>
          <div class="h-64 bg-gray-700/50 rounded-lg"></div>
        </div>
      </div>

      <div v-else-if="error" class="bg-rose-500/10 border border-rose-500/20 rounded-xl p-5">
        <div class="flex items-start gap-3">
          <i class="fa-solid fa-circle-exclamation text-rose-400 text-xl mt-0.5"></i>
          <div>
            <div class="text-rose-400 font-medium mb-1">Failed to load portfolio</div>
            <div class="text-sm text-gray-400">{{ error }}</div>
            <button
              class="mt-3 px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 rounded-lg text-xs text-rose-400 transition-colors"
              @click="fetchHoldings"
            >
              <i class="fa-solid fa-rotate-right mr-1"></i> Retry
            </button>
          </div>
        </div>
      </div>

      <template v-else>
        <div
          v-if="valuation"
          class="grid grid-cols-2 md:grid-cols-4 gap-4 animate__animated animate__fadeIn"
        >
          <div class="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div class="text-xs text-gray-500 mb-1"><i class="fa-solid fa-coins mr-1"></i>Invested</div>
            <div class="text-lg font-bold text-gray-100">
              {{ hidden ? '₹••••••' : '₹' + formatNum(valuation.summary.total_invested) }}
            </div>
          </div>
          <div class="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div class="text-xs text-gray-500 mb-1"><i class="fa-solid fa-sack-dollar mr-1"></i>Current</div>
            <div class="text-lg font-bold text-gray-100">
              {{ hidden ? '₹••••••' : '₹' + formatNum(valuation.summary.total_current) }}
            </div>
          </div>
          <div class="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div class="text-xs text-gray-500 mb-1"><i class="fa-solid fa-chart-line mr-1"></i>P&L</div>
            <div :class="['text-lg font-bold', valuation.summary.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400']">
              {{ hidden ? '••••' : (valuation.summary.total_pnl >= 0 ? '+' : '') + '₹' + formatNum(Math.abs(valuation.summary.total_pnl)) }}
            </div>
          </div>
          <div class="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div class="text-xs text-gray-500 mb-1"><i class="fa-solid fa-percent mr-1"></i>Returns</div>
            <div :class="['text-lg font-bold', valuation.summary.total_pnl_pct >= 0 ? 'text-emerald-400' : 'text-rose-400']">
              {{ hidden ? '••%' : (valuation.summary.total_pnl_pct >= 0 ? '+' : '') + valuation.summary.total_pnl_pct + '%' }}
            </div>
          </div>
        </div>
        <div v-if="valuation && hasOnlyMF" class="text-xs text-gray-600 bg-gray-800/50 rounded-lg px-3 py-2 inline-block">
          <i class="fa-solid fa-circle-info mr-1"></i>
          Mutual Funds don't have live P&L — values shown are at NAV from last import. Live P&L only available for stocks.
        </div>

        <div
          class="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-emerald-500/30 transition-colors animate__animated animate__fadeIn"
          @dragover.prevent
          @drop.prevent="handleDrop"
        >
          <i class="fa-solid fa-cloud-arrow-up text-3xl text-gray-600 mb-3"></i>
          <p class="text-sm text-gray-400 mb-1">Drag & drop your portfolio CSV here</p>
          <p class="text-xs text-gray-600 mb-4">
            Required columns: symbol, name, type, quantity, avg_price
          </p>
          <label class="inline-flex items-center px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-300 hover:border-emerald-500/30 cursor-pointer transition-colors">
            <i class="fa-solid fa-file-csv mr-2"></i> Browse Files
            <input type="file" accept=".csv" class="hidden" @change="handleFileSelect" />
          </label>
          <div v-if="importStatus" :class="['text-sm mt-3 animate__animated animate__fadeIn', importStatus.ok ? 'text-emerald-400' : 'text-rose-400']">
            <i :class="['fa-solid mr-1', importStatus.ok ? 'fa-circle-check' : 'fa-circle-xmark']"></i>
            {{ importStatus.message }}
          </div>
        </div>

        <template v-if="displayHoldings.length">
          <div class="space-y-6">
            <div class="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden flex flex-col max-h-[28rem] animate__animated animate__fadeIn">
              <div class="p-4 border-b border-gray-700 shrink-0 flex items-center justify-between">
                <h3 class="text-sm font-medium text-gray-400">
                  <i class="fa-solid fa-table-list mr-1.5 text-gray-600"></i>Holdings ({{ displayHoldings.length }})
                </h3>
              </div>
              <div class="overflow-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="text-left text-xs text-gray-500 border-b border-gray-700">
                      <th class="px-4 py-3 font-medium">Symbol</th>
                      <th class="px-4 py-3 font-medium">Name</th>
                      <th class="px-4 py-3 font-medium">Type</th>
                      <th class="px-4 py-3 font-medium text-right">Qty</th>
                      <th class="px-4 py-3 font-medium text-right">Avg Price</th>
                      <th class="px-4 py-3 font-medium text-right">Invested</th>
                      <th v-if="valuation" class="px-4 py-3 font-medium text-right">CMP</th>
                      <th v-if="valuation" class="px-4 py-3 font-medium text-right">P&L</th>
                      <th v-if="valuation" class="px-4 py-3 font-medium text-right">Day %</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="h in displayHoldings"
                      :key="h.id || h.symbol"
                      class="border-b border-gray-700/50 hover:bg-gray-700/20 transition-colors cursor-pointer"
                      @click="openDrillDown(h.symbol)"
                    >
                      <td class="px-4 py-3 font-medium text-gray-200">{{ h.symbol }}</td>
                      <td class="px-4 py-3 text-gray-400 truncate max-w-48">{{ h.name }}</td>
                      <td class="px-4 py-3">
                        <span
                          :class="[
                            'px-2 py-0.5 rounded text-xs font-medium',
                            h.asset_type === 'STOCK' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400',
                          ]"
                        >
                          <i :class="['fa-solid text-[10px] mr-0.5', h.asset_type === 'STOCK' ? 'fa-chart-simple' : 'fa-building-columns']"></i>
                          {{ h.asset_type }}
                        </span>
                      </td>
                      <td class="px-4 py-3 text-right text-gray-300">{{ hidden ? '••' : h.quantity }}</td>
                      <td class="px-4 py-3 text-right text-gray-300">{{ hidden ? '₹••••' : '₹' + formatNum(h.avg_price) }}</td>
                      <td class="px-4 py-3 text-right text-gray-200 font-medium">
                        {{ hidden ? '₹••••••' : '₹' + formatNum(h.invested || h.quantity * h.avg_price) }}
                      </td>
                      <template v-if="valuation">
                        <td class="px-4 py-3 text-right text-gray-300">
                          {{ h.current_price ? '₹' + formatNum(h.current_price) : '—' }}
                        </td>
                        <td class="px-4 py-3 text-right font-medium" :class="h.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'">
                          {{ hidden ? '••' : (h.pnl >= 0 ? '+' : '') + '₹' + formatNum(Math.abs(h.pnl || 0)) }}
                        </td>
                        <td class="px-4 py-3 text-right text-xs" :class="(h.day_change_pct || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'">
                          {{ h.day_change_pct != null ? (h.day_change_pct >= 0 ? '+' : '') + h.day_change_pct + '%' : '—' }}
                        </td>
                      </template>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate__animated animate__fadeIn">
              <h3 class="text-sm font-medium text-gray-400 mb-4">
                <i class="fa-solid fa-chart-pie mr-1.5 text-gray-600"></i>Sector Allocation
              </h3>
              <div v-if="sectorEntries.length" class="h-64">
                <Bar :data="barData" :options="barOptions" />
              </div>
              <div v-else class="text-gray-500 text-sm text-center py-8">
                No sector data available
              </div>
            </div>
          </div>
        </template>
      </template>
    </div>

    <div
      v-if="drillDown"
      class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-6"
      @click.self="drillDown = null"
    >
      <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-auto animate__animated animate__fadeIn">
        <div class="flex items-center justify-between p-5 border-b border-gray-700">
          <h2 class="text-lg font-semibold text-gray-100">
            <i class="fa-solid fa-chart-line mr-2 text-emerald-500"></i>{{ drillDown.symbol }}
          </h2>
          <button class="text-gray-500 hover:text-gray-300" @click="drillDown = null">
            <i class="fa-solid fa-xmark text-lg"></i>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div v-if="drillDownLoading" class="flex items-center justify-center py-10">
            <i class="fa-solid fa-spinner fa-spin text-2xl text-gray-500"></i>
          </div>
          <div v-else-if="drillDownError" class="text-rose-400 text-sm p-3 bg-rose-500/10 rounded-lg">
            <i class="fa-solid fa-circle-exclamation mr-1"></i>{{ drillDownError }}
          </div>
          <template v-else-if="drillDownQuote">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <div class="text-xs text-gray-500">Current Price</div>
                <div class="text-lg font-semibold text-gray-100">₹{{ formatNum(drillDownQuote.current_price) }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-500">Prev Close</div>
                <div class="text-lg font-semibold text-gray-300">₹{{ formatNum(drillDownQuote.previous_close) }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-500">Day Change</div>
                <div :class="['text-lg font-semibold', drillDownQuote.day_change >= 0 ? 'text-emerald-400' : 'text-rose-400']">
                  {{ drillDownQuote.day_change >= 0 ? '+' : '' }}{{ formatNum(drillDownQuote.day_change) }}
                </div>
              </div>
              <div>
                <div class="text-xs text-gray-500">Change %</div>
                <div :class="['text-lg font-semibold', drillDownQuote.day_change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400']">
                  {{ drillDownQuote.day_change_pct >= 0 ? '+' : '' }}{{ drillDownQuote.day_change_pct }}%
                </div>
              </div>
            </div>
            <div v-if="drillDownHistory.length" class="h-52">
              <Line :data="drillDownChartData" :options="drillDownChartOptions" />
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <i class="fa-solid fa-chart-line text-3xl mb-2 opacity-50"></i>
              <div class="text-sm">No historical data available</div>
            </div>
          </template>
          <template v-else>
            <div class="text-center py-8 text-gray-500">
              <i class="fa-solid fa-chart-simple text-3xl mb-2 opacity-50"></i>
              <div class="text-sm">Market data not available for this holding</div>
              <div class="text-xs text-gray-600 mt-1">MFs and some stocks may not have real-time data</div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, computed, onMounted, onUnmounted } from 'vue'
import { Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Filler,
  Tooltip,
} from 'chart.js'
import PageHeader from '../components/layout/PageHeader.vue'
import { usePortfolio } from '../composables/usePortfolio'
import { usePrivacy } from '../composables/usePrivacy'
import { formatNum } from '../utils/format'
import api from '../api/client'

ChartJS.register(BarElement, CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip)

const { holdings, valuation, loading, valuationLoading, error, fetchHoldings, fetchValuation, importCsv, clearHoldings } = usePortfolio()
const { hidden, toggle } = usePrivacy()
const importStatus = ref(null)

const drillDown = shallowRef(null)
const drillDownQuote = shallowRef(null)
const drillDownHistory = shallowRef([])
const drillDownLoading = shallowRef(false)
const drillDownError = shallowRef(null)

onMounted(fetchHoldings)

function handleKeydown(e) {
  if (e.key === 'Escape' && drillDown.value) drillDown.value = null
}
onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))

const displayHoldings = computed(() => {
  if (valuation.value) return valuation.value.holdings
  return holdings.value
})

const hasOnlyMF = computed(() => {
  const src = displayHoldings.value
  if (!src.length) return false
  return src.every(h => h.asset_type !== 'STOCK')
})

async function openDrillDown(symbol) {
  if (!symbol) return
  drillDown.value = { symbol }
  drillDownQuote.value = null
  drillDownHistory.value = []
  drillDownError.value = null
  drillDownLoading.value = true
  try {
    const [quoteRes, histRes] = await Promise.all([
      api.get(`/market/quote/${symbol}`),
      api.get(`/market/history/${symbol}`),
    ])
    drillDownQuote.value = quoteRes.data
    drillDownHistory.value = histRes.data
  } catch (err) {
    drillDownError.value = err.response?.data?.detail || err.message || 'Failed to load stock data'
  } finally {
    drillDownLoading.value = false
  }
}

const drillDownChartData = computed(() => ({
  labels: drillDownHistory.value.map(d => {
    const dt = new Date(d.date)
    return dt.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
  }),
  datasets: [{
    data: drillDownHistory.value.map(d => d.close),
    borderColor: '#10b981',
    backgroundColor: 'rgba(16, 185, 129, 0.08)',
    borderWidth: 1.5,
    pointRadius: 0,
    pointHitRadius: 10,
    fill: true,
    tension: 0.3,
  }],
}))

const drillDownChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: { ticks: { color: '#6b7280', maxTicksLimit: 6, font: { size: 10 } }, grid: { display: false } },
    y: { ticks: { color: '#6b7280', font: { size: 10 } }, grid: { color: 'rgba(75, 85, 99, 0.3)' } },
  },
  plugins: { legend: { display: false } },
}

const CHART_COLORS = [
  '#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
]

const sectorEntries = computed(() => {
  const source = displayHoldings.value
  const sectorMap = {}
  let total = 0
  for (const h of source) {
    const sector = h.sector || 'Uncategorized'
    const value = h.invested || h.quantity * h.avg_price
    sectorMap[sector] = (sectorMap[sector] || 0) + value
    total += value
  }
  return Object.entries(sectorMap)
    .map(([sector, value]) => ({
      sector,
      value: Math.round(value),
      pct: total > 0 ? (value / total) * 100 : 0,
    }))
    .sort((a, b) => b.value - a.value)
})

const barData = computed(() => ({
  labels: sectorEntries.value.map(e => e.sector),
  datasets: [{
    data: sectorEntries.value.map(e => e.pct),
    backgroundColor: sectorEntries.value.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]),
    borderWidth: 0,
    borderRadius: 4,
    barThickness: 22,
  }],
}))

const barOptions = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      ticks: { color: '#6b7280', font: { size: 10 }, callback: (v) => v + '%' },
      grid: { color: 'rgba(75, 85, 99, 0.2)' },
    },
    y: {
      ticks: { color: '#9ca3af', font: { size: 11 } },
      grid: { display: false },
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
      callbacks: { label: (ctx) => `${ctx.parsed.x.toFixed(1)}%` },
    },
  },
}

async function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (file) await uploadFile(file)
}

async function handleDrop(e) {
  const file = e.dataTransfer.files?.[0]
  if (file) await uploadFile(file)
}

async function uploadFile(file) {
  importStatus.value = null
  try {
    const result = await importCsv(file)
    importStatus.value = { ok: true, message: `Imported ${result.imported} holdings.` }
  } catch (err) {
    importStatus.value = { ok: false, message: err.response?.data?.detail || err.message }
  }
}

async function handleClear() {
  await clearHoldings()
  importStatus.value = null
}
</script>