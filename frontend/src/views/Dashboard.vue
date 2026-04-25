<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Dashboard" />
    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <div v-if="loading">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="n in 3" :key="n" class="bg-gray-800 border border-gray-700 rounded-xl p-4 animate-pulse">
            <div class="h-4 w-20 bg-gray-700 rounded mb-3"></div>
            <div class="h-7 w-28 bg-gray-700 rounded mb-2"></div>
            <div class="h-4 w-24 bg-gray-700 rounded"></div>
          </div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate-pulse">
            <div class="h-4 w-32 bg-gray-700 rounded mb-4"></div>
            <div class="space-y-3">
              <div v-for="n in 4" :key="n" class="h-4 bg-gray-700 rounded"></div>
            </div>
          </div>
          <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate-pulse">
            <div class="h-4 w-40 bg-gray-700 rounded mb-4"></div>
            <div class="space-y-3">
              <div v-for="n in 3" :key="n" class="h-16 bg-gray-700 rounded-lg"></div>
            </div>
          </div>
        </div>
        <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 mt-6 animate-pulse">
          <div class="h-4 w-24 bg-gray-700 rounded mb-4"></div>
          <div class="space-y-3">
            <div v-for="n in 4" :key="n" class="h-12 bg-gray-700 rounded-lg"></div>
          </div>
        </div>
      </div>
      <template v-else-if="data">
        <MarketPulse :indices="data.indices" />
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PortfolioSummary :portfolio="data.portfolio" />
          <RecentRecs :recommendations="data.recommendations" />
        </div>
        <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate__animated animate__fadeIn">
          <h3 class="text-sm font-medium text-gray-400 mb-4">
            <i class="fa-solid fa-rss mr-1.5 text-orange-500/60"></i>Latest News
          </h3>
          <div v-if="data.news.length" class="space-y-3">
            <a
              v-for="(item, i) in data.news"
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
          <div v-else class="text-gray-500 text-sm">No news available</div>
        </div>
      </template>
      <div v-else-if="error" class="bg-rose-500/10 border border-rose-500/20 rounded-xl p-5">
        <div class="flex items-start gap-3">
          <i class="fa-solid fa-circle-exclamation text-rose-400 text-xl mt-0.5"></i>
          <div>
            <div class="text-rose-400 font-medium mb-1">Failed to load dashboard</div>
            <div class="text-sm text-gray-400">{{ error }}</div>
            <button
              class="mt-3 px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 rounded-lg text-xs text-rose-400 transition-colors"
              @click="fetchDashboard"
            >
              <i class="fa-solid fa-rotate-right mr-1"></i> Retry
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import PageHeader from '../components/layout/PageHeader.vue'
import MarketPulse from '../components/dashboard/MarketPulse.vue'
import PortfolioSummary from '../components/dashboard/PortfolioSummary.vue'
import RecentRecs from '../components/dashboard/RecentRecs.vue'
import { useDashboard } from '../composables/useDashboard'

import { formatTime } from '../utils/format'

const { data, loading, error, fetchDashboard } = useDashboard()

onMounted(fetchDashboard)
</script>