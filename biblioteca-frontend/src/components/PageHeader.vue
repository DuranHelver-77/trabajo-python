<template>
  <div class="flex items-center justify-between mb-6">
    <div>
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="subtitle" class="text-gray-500 text-sm mt-1">{{ subtitle }}</p>
    </div>
    <slot name="actions" />
  </div>
</template>
<script setup>
defineProps({ title: String, subtitle: String })
</script>

