<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Dashboard" />
    <div class="flex-1 overflow-y-auto p-6 space-y-6">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <i class="fa-solid fa-spinner fa-spin text-2xl text-gray-500"></i>
      </div>
      <template v-else-if="data">
        <MarketPulse :indices="data.indices" />
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PortfolioSummary :portfolio="data.portfolio" />
          <RecentRecs :recommendations="data.recommendations" />
        </div>
        <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate__animated animate__fadeIn">
          <h3 class="text-sm font-medium text-gray-400 mb-4">Latest News</h3>
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
      <div v-else-if="error" class="text-rose-400 text-sm p-4 bg-rose-500/10 rounded-lg">
        <i class="fa-solid fa-circle-exclamation mr-2"></i>{{ error }}
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
