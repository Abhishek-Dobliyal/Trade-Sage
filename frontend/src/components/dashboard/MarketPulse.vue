<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div
      v-for="idx in indices"
      :key="idx.name"
      class="bg-gray-800 border border-gray-700 rounded-xl p-4 animate__animated animate__fadeIn"
    >
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-400 font-medium">{{ idx.name }}</span>
        <i
          :class="[
            'fa-solid text-xs',
            idx.change >= 0 ? 'fa-caret-up text-emerald-400' : 'fa-caret-down text-rose-400',
          ]"
        ></i>
      </div>
      <div class="text-2xl font-bold text-gray-100">
        {{ formatNum(idx.value) }}
      </div>
      <div
        :class="[
          'text-sm font-medium mt-1',
          idx.change >= 0 ? 'text-emerald-400' : 'text-rose-400',
        ]"
      >
        {{ idx.change >= 0 ? '+' : '' }}{{ formatNum(idx.change) }}
        ({{ idx.change_pct >= 0 ? '+' : '' }}{{ idx.change_pct }}%)
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  indices: { type: Array, default: () => [] },
})

function formatNum(n) {
  if (n == null) return '—'
  return n.toLocaleString('en-IN', { maximumFractionDigits: 2 })
}
</script>
