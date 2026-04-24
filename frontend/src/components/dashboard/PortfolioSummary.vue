<template>
  <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate__animated animate__fadeIn">
    <h3 class="text-sm font-medium text-gray-400 mb-4">Portfolio Summary</h3>
    <div v-if="portfolio" class="space-y-4">
      <div>
        <div class="text-3xl font-bold text-gray-100">
          ₹{{ formatNum(portfolio.total_invested) }}
        </div>
        <div class="text-sm text-gray-500 mt-1">Total Invested</div>
      </div>
      <div class="grid grid-cols-3 gap-3 pt-3 border-t border-gray-700">
        <div>
          <div class="text-lg font-semibold text-gray-200">{{ portfolio.holdings_count }}</div>
          <div class="text-xs text-gray-500">Holdings</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-emerald-400">{{ portfolio.stocks_count }}</div>
          <div class="text-xs text-gray-500">Stocks</div>
        </div>
        <div>
          <div class="text-lg font-semibold text-blue-400">{{ portfolio.mf_count }}</div>
          <div class="text-xs text-gray-500">Mutual Funds</div>
        </div>
      </div>
    </div>
    <div v-else class="text-gray-500 text-sm">
      <i class="fa-solid fa-upload mr-2"></i>
      Import your portfolio to see summary
    </div>
  </div>
</template>

<script setup>
import { formatNum } from '../../utils/format'

defineProps({
  portfolio: { type: Object, default: null },
})
</script>
