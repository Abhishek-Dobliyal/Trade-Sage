<template>
  <header class="flex items-center justify-between h-14 px-6 border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
    <h1 class="text-lg font-semibold text-gray-100">{{ title }}</h1>
    <slot />
  </header>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
})
</script>
