<template>
  <div class="flex flex-col items-center justify-center py-20 text-gray-400">
    <span class="text-5xl mb-4">{{ icon }}</span>
    <p class="text-gray-500 font-medium">{{ message }}</p>
    <p v-if="sub" class="text-sm text-gray-400 mt-1">{{ sub }}</p>
  </div>
</template>
<script setup>
defineProps({
  icon:    { default: '📭' },
  message: { default: 'No hay resultados' },
  sub:     String,
})
</script>

