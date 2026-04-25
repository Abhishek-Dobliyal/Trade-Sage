<template>
  <div class="flex min-h-screen">
    <Sidebar ref="sidebarRef" />
    <main
      :class="[
        'flex-1 flex flex-col transition-all duration-300',
        sidebarCollapsed ? 'ml-16' : 'ml-56',
      ]"
    >
      <router-view />

      <div
        v-if="showCmdk"
        class="fixed inset-0 bg-black/60 z-[100] flex items-start justify-center pt-32"
        @click.self="showCmdk = false"
        @keydown.escape="showCmdk = false"
      >
        <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-lg shadow-2xl animate__animated animate__fadeIn">
          <div class="p-4 border-b border-gray-700 flex items-center gap-3">
            <i class="fa-solid fa-magnifying-glass text-gray-500"></i>
            <input
              ref="cmdkInput"
              v-model="cmdkQuery"
              type="text"
              placeholder="Search symbols, actions..."
              class="flex-1 bg-transparent text-gray-100 placeholder-gray-500 focus:outline-none text-sm"
              @keydown.escape="showCmdk = false"
              @keydown.enter="executeCmdk"
            />
            <kbd class="text-xs text-gray-600 bg-gray-700 px-1.5 py-0.5 rounded">ESC</kbd>
          </div>
          <div class="p-2 max-h-80 overflow-y-auto">
            <div v-if="!cmdkResults.length && cmdkQuery" class="text-center py-8 text-gray-500 text-sm">
              No results for "{{ cmdkQuery }}"
            </div>
            <button
              v-for="(r, i) in cmdkResults"
              :key="i"
              class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-700/50 transition-colors text-left"
              @click="navigateTo(r)"
            >
              <i :class="['fa-solid w-5 text-center', r.icon, r.iconColor]"></i>
              <div>
                <div class="text-sm text-gray-200">{{ r.label }}</div>
                <div class="text-xs text-gray-500">{{ r.sub }}</div>
              </div>
            </button>
            <div v-if="!cmdkQuery" class="py-2">
              <div class="text-xs text-gray-600 px-3 py-1 mb-1">Navigation</div>
              <button
                v-for="r in navItems"
                :key="r.path"
                class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-700/50 transition-colors text-left"
                @click="navigateTo(r)"
              >
                <i :class="['fa-solid w-5 text-center', r.icon, r.iconColor]"></i>
                <div>
                  <div class="text-sm text-gray-200">{{ r.label }}</div>
                  <div class="text-xs text-gray-500">{{ r.sub }}</div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from './components/layout/Sidebar.vue'

const router = useRouter()
const sidebarRef = ref(null)
const sidebarCollapsed = computed(() => sidebarRef.value?.collapsed ?? false)

const showCmdk = ref(false)
const cmdkInput = ref(null)
const cmdkQuery = ref('')
const holdings = ref([])

const navItems = [
  { path: '/', label: 'Dashboard', sub: 'Overview & market pulse', icon: 'fa-gauge-high', iconColor: 'text-emerald-400' },
  { path: '/market', label: 'Market', sub: 'Indices & stock lookup', icon: 'fa-chart-line', iconColor: 'text-blue-400' },
  { path: '/portfolio', label: 'Portfolio', sub: 'Holdings & CSV import', icon: 'fa-briefcase', iconColor: 'text-amber-400' },
  { path: '/recommendations', label: 'Recommendations', sub: 'AI-powered insights', icon: 'fa-wand-magic-sparkles', iconColor: 'text-purple-400' },
  { path: '/watchlist', label: 'Watchlist', sub: 'Tracked stocks', icon: 'fa-binoculars', iconColor: 'text-cyan-400' },
  { path: '/chat', label: 'Chat', sub: 'Talk to TradeSage AI', icon: 'fa-comments', iconColor: 'text-teal-400' },
]

const cmdkResults = computed(() => {
  const q = cmdkQuery.value.toLowerCase().trim()
  if (!q) return []
  return holdings.value
    .filter(h => h.symbol.toLowerCase().includes(q) || h.name.toLowerCase().includes(q))
    .slice(0, 8)
    .map(h => ({
      ...h,
      label: h.symbol,
      sub: h.name,
      icon: 'fa-chart-simple',
      iconColor: 'text-emerald-400',
      action: 'drilldown',
    }))
})

async function loadHoldings() {
  try {
    const res = await fetch('/api/portfolio', { credentials: 'include' })
    if (res.ok) {
      const data = await res.json()
      holdings.value = data.holdings || []
    }
  } catch {}
}

function navigateTo(item) {
  showCmdk.value = false
  cmdkQuery.value = ''
  router.push(item.path)
}

function executeCmdk() {
  if (cmdkResults.value.length) {
    navigateTo(cmdkResults.value[0])
  }
}

function handleKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    showCmdk.value = true
    nextTick(() => cmdkInput.value?.focus())
    return
  }
  if (e.key === 'Escape' && showCmdk.value) {
    showCmdk.value = false
    return
  }
  if (showCmdk.value) return
  if (e.key === 'Escape') {
    const modals = document.querySelectorAll('[class*="fixed inset-0"]')
    if (modals.length) return
  }
  if (e.altKey && e.key === '1') { e.preventDefault(); router.push('/') }
  if (e.altKey && e.key === '2') { e.preventDefault(); router.push('/market') }
  if (e.altKey && e.key === '3') { e.preventDefault(); router.push('/portfolio') }
  if (e.altKey && e.key === '4') { e.preventDefault(); router.push('/recommendations') }
  if (e.altKey && e.key === '5') { e.preventDefault(); router.push('/watchlist') }
  if (e.altKey && e.key === '6') { e.preventDefault(); router.push('/chat') }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  loadHoldings()
})
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>