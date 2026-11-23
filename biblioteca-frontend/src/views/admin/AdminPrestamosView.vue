<template>
  <div class="max-w-7xl mx-auto px-4 py-10">
    <PageHeader title="Gestión de Préstamos">
      <template #actions><button @click="abrirCrear" class="btn btn-primary">+ Nuevo préstamo</button></template>
    </PageHeader>
    <div class="card mb-6 flex flex-wrap gap-3">
      <select v-model="filtroEstado" @change="cargar()" class="input-field max-w-xs">
        <option value="">Todos los estados</option>
        <option value="activo">Activo</option><option value="devuelto">Devuelto</option><option value="vencido">Vencido</option>
      </select>
    </div>

    <LoadingSpinner v-if="loading" />
    <div v-else class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
      <table class="w-full">
        <thead class="bg-gray-50"><tr>
          <th class="table-head">Libro</th><th class="table-head">Socio</th><th class="table-head">Préstamo</th><th class="table-head">Límite</th><th class="table-head">Devolución</th><th class="table-head">Estado</th><th class="table-head">Multa</th><th class="table-head">Acciones</th>
        </tr></thead>
        <tbody>
          <tr v-for="p in prestamos" :key="p.id" class="table-row">
            <td class="table-cell font-medium max-w-xs truncate text-sm">{{ p.libro?.titulo }}</td>
            <td class="table-cell text-gray-500 text-sm">{{ p.socio?.nombre }}</td>
            <td class="table-cell text-sm">{{ p.fecha_prestamo }}</td>
            <td class="table-cell text-sm">{{ p.fecha_limite }}</td>
            <td class="table-cell text-sm">{{ p.fecha_devolucion || '—' }}</td>
            <td class="table-cell"><span :class="{ activo: 'badge-blue', devuelto: 'badge-green', vencido: 'badge-red' }[p.estado] || 'badge-gray'">{{ p.estado }}</span></td>
            <td class="table-cell">
              <div v-if="p.multa > 0">
                <span :class="p.multa_pagada ? 'badge-green' : 'badge-red'">${{ p.multa }}</span>
                <button v-if="!p.multa_pagada" @click="pagarMulta(p)" class="btn btn-success btn-sm ml-2">Pagar</button>
              </div>
              <span v-else class="text-gray-400 text-xs">—</span>
            </td>
            <td class="table-cell">
              <button v-if="!p.fecha_devolucion" @click="abrirDevolucion(p)" class="btn btn-secondary btn-sm">↩️ Devolver</button>
            </td>
          </tr>
          <tr v-if="!prestamos.length"><td colspan="8"><EmptyState icon="📋" message="No hay préstamos" /></td></tr>
        </tbody>
      </table>
    </div>
    <Pagination :page="page" :limit="limit" :total="total" :skip="skip" @change="cambiarPagina" />

    <!-- Modal nuevo préstamo -->
    <ModalBase v-if="modal" title="Nuevo préstamo" @close="modal = false">
      <form @submit.prevent="guardar" class="space-y-4">
        <div class="form-group">
          <label class="label-field">Socio *</label>
          <select v-model.number="form.socio_id" class="input-field" required>
            <option value="">Seleccionar socio</option>
            <option v-for="s in socios" :key="s.id" :value="s.id">{{ s.nombre }} ({{ s.email }})</option>
          </select>
        </div>
        <div class="form-group">
          <label class="label-field">Libro *</label>
          <select v-model.number="form.libro_id" class="input-field" required>
            <option value="">Seleccionar libro</option>
            <option v-for="l in librosList" :key="l.id" :value="l.id" :disabled="l.disponibles === 0">{{ l.titulo }} ({{ l.disponibles }} disp.)</option>
          </select>
        </div>
        <div class="form-group">
          <label class="label-field">Días (1–30)</label>
          <input v-model.number="form.dias" type="number" min="1" max="30" class="input-field">
        </div>
        <div v-if="formError" class="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm border border-red-200">{{ formError }}</div>
        <div class="flex gap-3 justify-end">
          <button type="button" @click="modal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" :disabled="formLoading" class="btn btn-primary">{{ formLoading ? 'Registrando…' : 'Registrar préstamo' }}</button>
        </div>
      </form>
    </ModalBase>

    <!-- Modal devolución -->
    <ModalBase v-if="modalDevolucion" title="Registrar devolución" @close="modalDevolucion = false">
      <div class="mb-4 p-4 bg-blue-50 rounded-xl">
        <p class="font-medium text-blue-900">{{ prestamoDevolucion?.libro?.titulo }}</p>
        <p class="text-sm text-blue-700">Socio: {{ prestamoDevolucion?.socio?.nombre }}</p>
        <p class="text-sm text-blue-700">Límite: {{ prestamoDevolucion?.fecha_limite }}</p>
      </div>
      <div class="form-group">
        <label class="label-field">Fecha de devolución (opcional)</label>
        <input v-model="fechaDevolucion" type="date" class="input-field">
        <p class="text-xs text-gray-400 mt-1">Si no se especifica, se usa la fecha de hoy.</p>
      </div>
      <div class="flex gap-3 justify-end">
        <button @click="modalDevolucion = false" class="btn btn-secondary">Cancelar</button>
        <button @click="confirmarDevolucion" :disabled="formLoading" class="btn btn-success">{{ formLoading ? 'Procesando…' : '✅ Confirmar devolución' }}</button>
      </div>
    </ModalBase>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { prestamosApi, sociosApi, librosApi } from '@/api/client'
import { useToastStore } from '@/stores/toast'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import Pagination from '@/components/Pagination.vue'
import ModalBase from '@/components/ModalBase.vue'

const toast = useToastStore()
const prestamos = ref([]), socios = ref([]), librosList = ref([])
const loading = ref(true), total = ref(0), page = ref(1), limit = 15, skip = ref(0), filtroEstado = ref('')
const modal = ref(false), form = ref({ socio_id: '', libro_id: '', dias: 14 }), formError = ref(''), formLoading = ref(false)
const modalDevolucion = ref(false), prestamoDevolucion = ref(null), fechaDevolucion = ref('')

async function cargar() {
  loading.value = true
  try {
    const params = { skip: skip.value, limit }
    if (filtroEstado.value) params.estado = filtroEstado.value
    const { data } = await prestamosApi.listar(params); prestamos.value = data.items; total.value = data.total
  } finally { loading.value = false }
}
function cambiarPagina(p) { page.value = p; skip.value = (p-1)*limit; cargar() }
function abrirCrear() { form.value = { socio_id: '', libro_id: '', dias: 14 }; formError.value = ''; modal.value = true }
function abrirDevolucion(p) { prestamoDevolucion.value = p; fechaDevolucion.value = ''; modalDevolucion.value = true }

async function guardar() {
  formError.value = ''; formLoading.value = true
  try { await prestamosApi.crear(form.value); toast.success('Préstamo registrado'); modal.value = false; cargar() }
  catch (e) { formError.value = e.response?.data?.detail || 'Error' }
  finally { formLoading.value = false }
}
async function confirmarDevolucion() {
  formLoading.value = true
  try {
    await prestamosApi.devolver(prestamoDevolucion.value.id, { fecha_devolucion: fechaDevolucion.value || null })
    toast.success('Devolución registrada'); modalDevolucion.value = false; cargar()
  } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  finally { formLoading.value = false }
}
async function pagarMulta(p) {
  try { await prestamosApi.pagarMulta(p.id); toast.success('Multa registrada como pagada'); cargar() }
  catch (e) { toast.error(e.response?.data?.detail || 'Error') }
}
onMounted(async () => {
  const [, s, l] = await Promise.all([cargar(), sociosApi.listar({ limit: 200 }), librosApi.listar({ limit: 200 })])
  socios.value = s.data.items; librosList.value = l.data.items
})
</script>

