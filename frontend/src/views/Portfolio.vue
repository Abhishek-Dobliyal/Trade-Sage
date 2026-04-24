<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Portfolio">
      <button
        v-if="holdings.length"
        class="text-sm text-rose-400 hover:text-rose-300 transition-colors"
        @click="handleClear"
      >
        <i class="fa-solid fa-trash mr-1"></i> Clear
      </button>
    </PageHeader>

    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <!-- CSV Upload -->
      <div
        class="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-emerald-500/30 transition-colors"
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
        <div v-if="importStatus" :class="['text-sm mt-3', importStatus.ok ? 'text-emerald-400' : 'text-rose-400']">
          {{ importStatus.message }}
        </div>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-10">
        <i class="fa-solid fa-spinner fa-spin text-2xl text-gray-500"></i>
      </div>

      <template v-if="holdings.length">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Holdings Table -->
          <div class="lg:col-span-2 bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
            <div class="p-4 border-b border-gray-700">
              <h3 class="text-sm font-medium text-gray-400">Holdings ({{ holdings.length }})</h3>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="text-left text-xs text-gray-500 border-b border-gray-700">
                    <th class="px-4 py-3 font-medium">Symbol</th>
                    <th class="px-4 py-3 font-medium">Name</th>
                    <th class="px-4 py-3 font-medium">Type</th>
                    <th class="px-4 py-3 font-medium text-right">Qty</th>
                    <th class="px-4 py-3 font-medium text-right">Avg Price</th>
                    <th class="px-4 py-3 font-medium text-right">Invested</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="h in holdings"
                    :key="h.id"
                    class="border-b border-gray-700/50 hover:bg-gray-700/20 transition-colors"
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
                        {{ h.asset_type }}
                      </span>
                    </td>
                    <td class="px-4 py-3 text-right text-gray-300">{{ h.quantity }}</td>
                    <td class="px-4 py-3 text-right text-gray-300">₹{{ formatNum(h.avg_price) }}</td>
                    <td class="px-4 py-3 text-right text-gray-200 font-medium">
                      ₹{{ formatNum(h.quantity * h.avg_price) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Sector Pie Chart -->
          <div class="bg-gray-800 border border-gray-700 rounded-xl p-5">
            <h3 class="text-sm font-medium text-gray-400 mb-4">Sector Allocation</h3>
            <Pie v-if="sectorData" :data="sectorData" :options="chartOptions" />
            <div v-else class="text-gray-500 text-sm text-center py-8">
              No sector data available
            </div>
          </div>
        </div>
      </template>

      <div v-else-if="error" class="text-rose-400 text-sm p-4 bg-rose-500/10 rounded-lg">
        <i class="fa-solid fa-circle-exclamation mr-2"></i>{{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import PageHeader from '../components/layout/PageHeader.vue'
import { usePortfolio } from '../composables/usePortfolio'

ChartJS.register(ArcElement, Tooltip, Legend)

const { holdings, loading, error, fetchHoldings, importCsv, clearHoldings } = usePortfolio()
const importStatus = ref(null)

onMounted(fetchHoldings)

const CHART_COLORS = [
  '#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
]

const sectorData = computed(() => {
  const sectorMap = {}
  for (const h of holdings.value) {
    const sector = h.sector || 'Uncategorized'
    sectorMap[sector] = (sectorMap[sector] || 0) + h.quantity * h.avg_price
  }
  const labels = Object.keys(sectorMap)
  if (!labels.length) return null
  return {
    labels,
    datasets: [{
      data: Object.values(sectorMap).map(v => Math.round(v)),
      backgroundColor: CHART_COLORS.slice(0, labels.length),
      borderWidth: 0,
    }],
  }
})

const chartOptions = {
  responsive: true,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#9ca3af', font: { size: 11 }, padding: 12 },
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

function formatNum(n) {
  if (n == null) return '—'
  return n.toLocaleString('en-IN', { maximumFractionDigits: 2 })
}
</script>
