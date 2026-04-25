<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Recommendations">
      <div class="flex items-center gap-2">
        <a
          v-if="recommendations.length"
          href="/api/recommendations/export"
          class="flex items-center gap-1.5 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-xs text-gray-400 hover:text-emerald-400 hover:border-emerald-500/30 transition-colors"
        >
          <i class="fa-solid fa-download"></i> Export CSV
        </a>
        <button
          class="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg text-sm font-medium transition-colors"
          :disabled="generating"
          @click="generateRecommendations"
        >
          <i :class="['fa-solid', generating ? 'fa-spinner fa-spin' : 'fa-wand-magic-sparkles']"></i>
          {{ generating ? 'Generating...' : 'Generate' }}
        </button>
      </div>
    </PageHeader>

    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div v-for="n in 6" :key="n" class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate-pulse">
          <div class="h-7 w-16 bg-gray-700 rounded mb-3"></div>
          <div class="space-y-2 mb-3">
            <div class="h-5 w-32 bg-gray-700 rounded"></div>
            <div class="h-3 w-24 bg-gray-700/50 rounded"></div>
          </div>
          <div class="h-8 bg-gray-700/50 rounded mb-3"></div>
          <div class="space-y-2">
            <div class="h-3 w-full bg-gray-700/50 rounded"></div>
            <div class="h-3 w-3/4 bg-gray-700/50 rounded"></div>
          </div>
        </div>
      </div>

      <div v-else-if="error" class="bg-rose-500/10 border border-rose-500/20 rounded-xl p-5 mb-6">
        <div class="flex items-start gap-3">
          <i class="fa-solid fa-circle-exclamation text-rose-400 text-xl mt-0.5"></i>
          <div>
            <div class="text-rose-400 font-medium mb-1">Failed to load recommendations</div>
            <div class="text-sm text-gray-400">{{ error }}</div>
            <button
              class="mt-3 px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 rounded-lg text-xs text-rose-400 transition-colors"
              @click="fetchRecommendations"
            >
              <i class="fa-solid fa-rotate-right mr-1"></i> Retry
            </button>
          </div>
        </div>
      </div>

      <div v-if="recommendations.length" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="rec in recommendations"
          :key="rec.symbol"
          class="bg-gray-800 border border-gray-700 rounded-xl p-5 hover:border-gray-600 transition-colors animate__animated animate__fadeInUp"
        >
          <div class="flex items-center justify-between mb-3">
            <span
              :class="[
                'px-2.5 py-1 rounded-md text-xs font-bold',
                actionClass(rec.action),
              ]"
            >
              <i :class="['fa-solid text-[10px] mr-0.5', actionIcon(rec.action)]"></i>
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
              <i class="fa-solid fa-bullseye text-emerald-600 mr-0.5"></i>
              <span class="text-gray-500">Target: </span>
              <span class="text-emerald-400 font-medium">₹{{ formatNum(rec.target_price) }}</span>
            </div>
            <div v-if="rec.stop_loss">
              <i class="fa-solid fa-shield-halved text-rose-600 mr-0.5"></i>
              <span class="text-gray-500">Stop Loss: </span>
              <span class="text-rose-400 font-medium">₹{{ formatNum(rec.stop_loss) }}</span>
            </div>
          </div>

          <p class="text-sm text-gray-400 leading-relaxed">{{ rec.rationale }}</p>
        </div>
      </div>

      <div v-else-if="!loading && !generating && !error" class="flex flex-col items-center justify-center py-20 text-center">
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

import { formatNum, actionClass } from '../utils/format'

const { recommendations, loading, generating, error, fetchRecommendations, generateRecommendations } = useRecommendations()

onMounted(fetchRecommendations)

function actionIcon(action) {
  switch (action) {
    case 'BUY': return 'fa-arrow-trend-up'
    case 'SELL': return 'fa-arrow-trend-down'
    default: return 'fa-minus'
  }
}

function confidenceColor(c) {
  if (c >= 0.7) return 'bg-emerald-500'
  if (c >= 0.4) return 'bg-amber-500'
  return 'bg-rose-500'
}
</script>