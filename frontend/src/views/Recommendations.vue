<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Recommendations">
      <button
        class="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg text-sm font-medium transition-colors"
        :disabled="generating"
        @click="generateRecommendations"
      >
        <i :class="['fa-solid', generating ? 'fa-spinner fa-spin' : 'fa-wand-magic-sparkles']"></i>
        {{ generating ? 'Generating...' : 'Generate' }}
      </button>
    </PageHeader>

    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <i class="fa-solid fa-spinner fa-spin text-2xl text-gray-500"></i>
      </div>

      <div v-else-if="error" class="text-rose-400 text-sm p-4 bg-rose-500/10 rounded-lg mb-6">
        <i class="fa-solid fa-circle-exclamation mr-2"></i>{{ error }}
      </div>

      <div v-if="recommendations.length" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="rec in recommendations"
          :key="rec.symbol"
          class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate__animated animate__fadeInUp"
        >
          <div class="flex items-center justify-between mb-3">
            <span
              :class="[
                'px-2.5 py-1 rounded-md text-xs font-bold',
                actionClass(rec.action),
              ]"
            >
              {{ rec.action }}
            </span>
            <div class="flex items-center gap-1.5">
              <div class="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <div
                  :class="['h-full rounded-full', confidenceColor(rec.confidence)]"
                  :style="{ width: (rec.confidence * 100) + '%' }"
                ></div>
              </div>
              <span class="text-xs text-gray-500">{{ Math.round(rec.confidence * 100) }}%</span>
            </div>
          </div>

          <div class="mb-3">
            <div class="text-base font-semibold text-gray-200">{{ rec.symbol }}</div>
            <div class="text-xs text-gray-500 truncate">{{ rec.name }}</div>
          </div>

          <div v-if="rec.target_price || rec.stop_loss" class="flex gap-4 mb-3 text-xs">
            <div v-if="rec.target_price">
              <span class="text-gray-500">Target: </span>
              <span class="text-emerald-400 font-medium">₹{{ formatNum(rec.target_price) }}</span>
            </div>
            <div v-if="rec.stop_loss">
              <span class="text-gray-500">Stop Loss: </span>
              <span class="text-rose-400 font-medium">₹{{ formatNum(rec.stop_loss) }}</span>
            </div>
          </div>

          <p class="text-sm text-gray-400 leading-relaxed">{{ rec.rationale }}</p>
        </div>
      </div>

      <div v-else-if="!loading && !generating" class="flex flex-col items-center justify-center py-20 text-center">
        <i class="fa-solid fa-lightbulb text-4xl text-gray-700 mb-4"></i>
        <p class="text-gray-400 mb-2">No recommendations yet</p>
        <p class="text-sm text-gray-600">
          Click Generate to get AI-powered buy/sell/hold recommendations
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import PageHeader from '../components/layout/PageHeader.vue'
import { useRecommendations } from '../composables/useRecommendations'

const { recommendations, loading, generating, error, fetchRecommendations, generateRecommendations } = useRecommendations()

onMounted(fetchRecommendations)

function actionClass(action) {
  switch (action) {
    case 'BUY': return 'bg-emerald-500/20 text-emerald-400'
    case 'SELL': return 'bg-rose-500/20 text-rose-400'
    default: return 'bg-amber-500/20 text-amber-400'
  }
}

function confidenceColor(c) {
  if (c >= 0.7) return 'bg-emerald-500'
  if (c >= 0.4) return 'bg-amber-500'
  return 'bg-rose-500'
}

function formatNum(n) {
  if (n == null) return '—'
  return n.toLocaleString('en-IN', { maximumFractionDigits: 2 })
}
</script>
