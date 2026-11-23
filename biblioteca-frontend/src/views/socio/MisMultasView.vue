<template>
  <div class="max-w-4xl mx-auto px-4 py-10">
    <PageHeader title="Mis Multas" subtitle="Multas pendientes de pago" />
    <LoadingSpinner v-if="loading" />
    <div v-else-if="datos">
      <div v-if="datos.total_adeudado > 0" class="card mb-6 flex items-center gap-4 border-red-200 bg-red-50">
        <div class="stat-icon bg-red-100">⚠️</div>
        <div>
          <p class="stat-value text-red-600">${{ datos.total_adeudado.toFixed(2) }}</p>
          <p class="stat-label">Total adeudado</p>
        </div>
      </div>
      <EmptyState v-if="!datos.items?.length" icon="🎉" message="¡Sin multas pendientes!" sub="Estás al día con tus devoluciones" />
      <div v-else class="space-y-4">
        <div v-for="m in datos.items" :key="m.prestamo_id" class="card flex items-center gap-4">
          <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center text-red-600 font-bold flex-shrink-0">⚠️</div>
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900">{{ m.libro_titulo }}</h3>
            <p class="text-sm text-gray-500">Fecha límite: {{ m.fecha_limite }}</p>
          </div>
          <span class="badge-red text-base font-bold">${{ m.multa }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { sociosApi } from '@/api/client'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'

const datos = ref(null)
const loading = ref(true)
onMounted(async () => {
  try { const { data } = await sociosApi.meMultas(); datos.value = data }
  finally { loading.value = false }
})
</script>

