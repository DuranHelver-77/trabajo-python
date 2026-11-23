<template>
  <div class="flex items-center justify-center py-20 text-blue-500">
    <svg class="animate-spin w-8 h-8" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z"/>
    </svg>
    <span class="ml-3 text-gray-500 font-medium">{{ text }}</span>
  </div>
</template>
<script setup>
defineProps({ text: { default: 'Cargando...' } })
</script>

