<template>
  <div v-if="totalPages > 1" class="flex items-center justify-between mt-6">
    <p class="text-sm text-gray-500">
      Mostrando {{ skip + 1 }}–{{ Math.min(skip + limit, total) }} de {{ total }}
    </p>
    <div class="flex gap-2">
      <button :disabled="page <= 1" @click="$emit('change', page - 1)" class="btn btn-secondary btn-sm">← Anterior</button>
      <span class="flex items-center px-3 text-sm font-medium text-gray-700">{{ page }} / {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="$emit('change', page + 1)" class="btn btn-secondary btn-sm">Siguiente →</button>
    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({ page: Number, limit: Number, total: Number, skip: Number })
defineEmits(['change'])
const totalPages = computed(() => Math.ceil(props.total / props.limit))
</script>

