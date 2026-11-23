<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box" :style="{ maxWidth: maxWidth }">
      <div class="flex items-center justify-between p-6 border-b border-gray-100">
        <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition text-xl leading-none">✕</button>
      </div>
      <div class="p-6">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ title: String, maxWidth: { default: '540px' } })
defineEmits(['close'])
</script>

