<template>
  <aside
    :class="[
      'fixed top-0 left-0 h-screen bg-gray-900 border-r border-gray-800 flex flex-col transition-all duration-300 z-50',
      collapsed ? 'w-16' : 'w-56',
    ]"
  >
    <div class="flex items-center h-14 px-4 border-b border-gray-800">
      <i class="fa-solid fa-chart-trending-up text-emerald-500 text-xl"></i>
      <span v-if="!collapsed" class="ml-3 font-bold text-lg text-gray-100 whitespace-nowrap">
        TradeSage
      </span>
    </div>

    <nav class="flex-1 py-4 space-y-1 px-2">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        :class="[
          'flex items-center px-3 py-2.5 rounded-lg transition-colors group',
          isActive(item.path)
            ? 'bg-emerald-500/10 text-emerald-400'
            : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200',
        ]"
      >
        <i :class="[item.icon, 'w-5 text-center text-base']"></i>
        <span v-if="!collapsed" class="ml-3 text-sm font-medium whitespace-nowrap">
          {{ item.label }}
        </span>
      </router-link>
    </nav>

    <div class="px-2 py-4 border-t border-gray-800">
      <button
        class="flex items-center px-3 py-2 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors w-full"
        @click="collapsed = !collapsed"
      >
        <i :class="['fa-solid', collapsed ? 'fa-angles-right' : 'fa-angles-left', 'w-5 text-center']"></i>
        <span v-if="!collapsed" class="ml-3 text-sm">Collapse</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const collapsed = ref(false)

const navItems = [
  { path: '/', label: 'Dashboard', icon: 'fa-solid fa-gauge-high' },
  { path: '/chat', label: 'Chat', icon: 'fa-solid fa-comments' },
  { path: '/portfolio', label: 'Portfolio', icon: 'fa-solid fa-briefcase' },
  { path: '/recommendations', label: 'Recommendations', icon: 'fa-solid fa-lightbulb' },
  { path: '/watchlist', label: 'Watchlist', icon: 'fa-solid fa-binoculars' },
  { path: '/market', label: 'Market', icon: 'fa-solid fa-chart-line' },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

defineExpose({ collapsed })
</script>
