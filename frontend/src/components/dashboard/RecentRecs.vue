<template>
  <div class="bg-gray-800 border border-gray-700 rounded-xl p-5 animate__animated animate__fadeIn">
    <h3 class="text-sm font-medium text-gray-400 mb-4">
      <i class="fa-solid fa-lightbulb mr-1.5 text-amber-500/60"></i>Recent Recommendations
    </h3>
    <div v-if="recommendations.length" class="space-y-3">
      <div
        v-for="rec in recommendations"
        :key="rec.symbol"
        class="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg hover:bg-gray-900/80 transition-colors"
      >
        <div class="flex items-center gap-3">
          <span
            :class="[
              'px-2 py-0.5 rounded text-xs font-bold',
              actionClass(rec.action),
            ]"
          >
            {{ rec.action }}
          </span>
          <div>
            <div class="text-sm font-medium text-gray-200">{{ rec.symbol }}</div>
            <div class="text-xs text-gray-500 truncate max-w-48">{{ rec.name }}</div>
          </div>
        </div>
        <div class="text-xs text-gray-500">
          {{ Math.round(rec.confidence * 100) }}%
        </div>
      </div>
    </div>
    <div v-else class="text-gray-500 text-sm">
      <i class="fa-solid fa-lightbulb mr-2"></i>
      No recommendations yet
    </div>
  </div>
</template>

<script setup>
import { actionClass } from '../../utils/format'

defineProps({
  recommendations: { type: Array, default: () => [] },
})
</script>
