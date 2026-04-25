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

    <div class="px-2 py-4 border-t border-gray-800 space-y-1">
      <div
        class="group relative flex items-center px-3 py-2 rounded-lg text-gray-600 hover:text-gray-500 transition-colors cursor-help"
        title="Keyboard shortcuts"
      >
        <i class="fa-solid fa-keyboard w-5 text-center text-xs"></i>
        <span v-if="!collapsed" class="ml-3 text-xs">Shortcuts</span>
        <div
          class="absolute bottom-full left-4 mb-2 w-64 bg-gray-800 border border-gray-700 rounded-xl p-3 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50"
        >
          <div class="text-xs text-gray-400 font-medium mb-2">Keyboard Shortcuts</div>
          <div class="space-y-1.5">
            <div class="flex justify-between text-xs">
              <span class="text-gray-500">Command palette</span>
              <span class="flex gap-1">
                <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">Ctrl</kbd>
                <span class="text-gray-600">+</span>
                <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">K</kbd>
              </span>
            </div>
            <div class="flex justify-between text-xs">
              <span class="text-gray-500">Close modal</span>
              <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">ESC</kbd>
            </div>
            <div class="border-t border-gray-700 pt-1.5 mt-1.5 space-y-1.5">
              <div class="flex justify-between text-xs">
                <span class="text-gray-500">Dashboard</span>
                <span class="flex gap-1">
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">Alt</kbd>
                  <span class="text-gray-600">+</span>
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">1</kbd>
                </span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-gray-500">Market</span>
                <span class="flex gap-1">
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">Alt</kbd>
                  <span class="text-gray-600">+</span>
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">2</kbd>
                </span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-gray-500">Portfolio</span>
                <span class="flex gap-1">
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">Alt</kbd>
                  <span class="text-gray-600">+</span>
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">3</kbd>
                </span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-gray-500">Recommendations</span>
                <span class="flex gap-1">
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">Alt</kbd>
                  <span class="text-gray-600">+</span>
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">4</kbd>
                </span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-gray-500">Watchlist</span>
                <span class="flex gap-1">
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">Alt</kbd>
                  <span class="text-gray-600">+</span>
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">5</kbd>
                </span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-gray-500">Chat</span>
                <span class="flex gap-1">
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">Alt</kbd>
                  <span class="text-gray-600">+</span>
                  <kbd class="bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded text-[10px]">6</kbd>
                </span>
              </div>
            </div>
          </div>
          <div class="absolute -bottom-1.5 left-6 w-3 h-3 bg-gray-800 border-r border-b border-gray-700 rotate-45"></div>
        </div>
      </div>
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
