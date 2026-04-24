<template>
  <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate__animated animate__fadeIn">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-medium text-gray-400">
        <i class="fa-solid fa-wallet mr-1.5 text-emerald-500/60"></i>Portfolio Summary
      </h3>
      <button
        v-if="portfolio"
        class="text-gray-500 hover:text-gray-300 transition-colors"
        @click="toggle"
        :title="hidden ? 'Show values' : 'Hide values'"
      >
        <i :class="['fa-solid text-sm', hidden ? 'fa-eye-slash' : 'fa-eye']"></i>
      </button>
    </div>
    <div v-if="portfolio" class="space-y-4">
      <div>
        <div class="text-3xl font-bold text-gray-100">
          {{ hidden ? '₹••••••' : '₹' + formatNum(portfolio.total_invested) }}
        </div>
        <div class="text-sm text-gray-500 mt-1">Total Invested</div>
      </div>
      <div class="grid grid-cols-3 gap-3 pt-3 border-t border-gray-700">
        <div>
          <div class="text-lg font-semibold text-gray-200">
            <i class="fa-solid fa-layer-group text-xs text-gray-600 mr-1"></i>{{ portfolio.holdings_count }}
          </div>
          <div class="text-xs text-gray-500">Holdings</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-emerald-400">
            <i class="fa-solid fa-chart-simple text-xs text-emerald-600 mr-1"></i>{{ portfolio.stocks_count }}
          </div>
          <div class="text-xs text-gray-500">Stocks</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-blue-400">
            <i class="fa-solid fa-building-columns text-xs text-blue-600 mr-1"></i>{{ portfolio.mf_count }}
          </div>
          <div class="text-xs text-gray-500">Mutual Funds</div>
        </div>
      </div>
    </div>
    <div v-else class="text-gray-500 text-sm py-4 text-center">
      <i class="fa-solid fa-cloud-arrow-up mr-2"></i>
      Import your portfolio to see summary
    </div>
  </div>
</template>

<script setup>
import { formatNum } from '../../utils/format'
import { usePrivacy } from '../../composables/usePrivacy'

const { hidden, toggle } = usePrivacy()

defineProps({
  portfolio: { type: Object, default: null },
})
</script>
