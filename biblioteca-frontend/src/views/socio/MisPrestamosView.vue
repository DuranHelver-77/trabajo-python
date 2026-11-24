<template>
  <div class="max-w-6xl mx-auto px-4 py-10">
    <PageHeader title="Mis Préstamos" subtitle="Historial de préstamos de tu cuenta" />
    <div class="card mb-4 flex gap-4">
      <select v-model="estado" @change="cargar()" class="input-field max-w-xs">
        <option value="">Todos los estados</option>
        <option value="activo">Activo</option>
        <option value="devuelto">Devuelto</option>
        <option value="vencido">Vencido</option>
      </select>
    </div>
    <LoadingSpinner v-if="loading" />
    <EmptyState v-else-if="!prestamos.length" icon="📋" message="No tienes préstamos" sub="Visita el catálogo para explorar libros" />
    <template v-else>
      <div class="space-y-4">
        <div v-for="p in prestamos" :key="p.id" class="card flex flex-col md:flex-row md:items-center gap-4">
          <div class="w-16 h-20 rounded-lg overflow-hidden bg-blue-50 flex items-center justify-center flex-shrink-0">
            <img v-if="p.libro?.portada_url" :src="p.libro.portada_url" class="w-full h-full object-cover">
            <span v-else class="text-2xl">📖</span>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-gray-900 truncate">{{ p.libro?.titulo || `Libro #${p.libro_id}` }}</h3>
            <p class="text-sm text-gray-500">{{ p.libro?.autor?.nombre }}</p>
            <div class="flex flex-wrap gap-4 mt-2 text-xs text-gray-400">
              <span>📅 Préstamo: {{ p.fecha_prestamo }}</span>
              <span>⏰ Límite: {{ p.fecha_limite }}</span>
              <span v-if="p.fecha_devolucion">✅ Devuelto: {{ p.fecha_devolucion }}</span>
            </div>
          </div>
          <div class="flex flex-col items-end gap-2">
            <span :class="estadoBadge(p.estado)">{{ p.estado }}</span>
            <span v-if="p.multa > 0" :class="p.multa_pagada ? 'badge-green' : 'badge-red'">
              💰 Multa: ${{ p.multa }} {{ p.multa_pagada ? '(pagada)' : '(pendiente)' }}
            </span>
            <button 
              v-if="!p.fecha_devolucion" 
              @click="abrirDevolucion(p)" 
              class="btn btn-secondary btn-sm mt-1"
            >
              ↩️ Devolver libro
            </button>
          </div>
        </div>
      </div>
      <Pagination :page="page" :limit="limit" :total="total" :skip="skip" @change="cambiarPagina" />
    </template>

    <!-- Modal confirmar devolución -->
    <ModalBase v-if="modalDevolucion" title="Devolver libro" @close="modalDevolucion = false">
      <div class="space-y-4">
        <p class="text-sm text-gray-600">
          ¿Confirmas la entrega y devolución del libro <strong class="text-gray-900">{{ prestamoSeleccionado?.libro?.titulo }}</strong>?
        </p>
        <div v-if="errorDevolucion" class="bg-red-50 text-red-700 p-3 rounded-lg text-sm border border-red-200">
          {{ errorDevolucion }}
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" @click="modalDevolucion = false" class="btn btn-secondary">Cancelar</button>
          <button type="button" @click="confirmarDevolucion" :disabled="procesando" class="btn btn-primary">
            {{ procesando ? 'Devolviendo...' : 'Confirmar Devolución' }}
          </button>
        </div>
      </div>
    </ModalBase>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { sociosApi, prestamosApi, parseError } from '@/api/client'
import { useToastStore } from '@/stores/toast'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import Pagination from '@/components/Pagination.vue'
import ModalBase from '@/components/ModalBase.vue'

const toast = useToastStore()
const prestamos = ref([])
const estado = ref('')
const loading = ref(true)
const total = ref(0), page = ref(1), limit = 10, skip = ref(0)

const modalDevolucion = ref(false)
const prestamoSeleccionado = ref(null)
const procesando = ref(false)
const errorDevolucion = ref('')

const estadoBadge = (e) => ({ activo: 'badge-blue', devuelto: 'badge-green', vencido: 'badge-red' }[e] || 'badge-gray')

function abrirDevolucion(p) {
  prestamoSeleccionado.value = p
  errorDevolucion.value = ''
  modalDevolucion.value = true
}

async function confirmarDevolucion() {
  procesando.value = true
  errorDevolucion.value = ''
  try {
    await prestamosApi.devolver(prestamoSeleccionado.value.id, {})
    toast.success('¡Libro devuelto con éxito!')
    modalDevolucion.value = false
    cargar()
  } catch (err) {
    errorDevolucion.value = parseError(err)
  } finally {
    procesando.value = false
  }
}

async function cargar() {
  loading.value = true
  try {
    const { data } = await sociosApi.mePrestamos({ skip: skip.value, limit, ...(estado.value ? { estado: estado.value } : {}) })
    prestamos.value = data.items; total.value = data.total
  } finally { loading.value = false }
}

function cambiarPagina(p) { page.value = p; skip.value = (p - 1) * limit; cargar() }
onMounted(cargar)
</script>

