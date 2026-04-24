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
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Sidebar from './components/layout/Sidebar.vue'

const sidebarRef = ref(null)
const sidebarCollapsed = computed(() => sidebarRef.value?.collapsed ?? false)
</script>
