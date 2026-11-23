<template>
  <div class="max-w-7xl mx-auto px-4 py-10">
    <PageHeader title="Gestión de Socios">
      <template #actions><button @click="abrirCrear" class="btn btn-primary">+ Nuevo socio</button></template>
    </PageHeader>
    <div class="card mb-6 flex gap-3">
      <select v-model="activo" @change="cargar()" class="input-field max-w-xs">
        <option value="">Todos</option><option :value="true">Activos</option><option :value="false">Inactivos</option>
      </select>
    </div>
    <LoadingSpinner v-if="loading" />
    <div v-else class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
      <table class="w-full">
        <thead class="bg-gray-50"><tr>
          <th class="table-head">Nombre</th><th class="table-head">Email</th><th class="table-head">Teléfono</th><th class="table-head">Alta</th><th class="table-head">Estado</th><th class="table-head">Acciones</th>
        </tr></thead>
        <tbody>
          <tr v-for="s in socios" :key="s.id" class="table-row">
            <td class="table-cell font-medium">{{ s.nombre }}</td>
            <td class="table-cell text-gray-500">{{ s.email }}</td>
            <td class="table-cell text-gray-500">{{ s.telefono || '—' }}</td>
            <td class="table-cell text-gray-400 text-xs">{{ new Date(s.fecha_alta).toLocaleDateString() }}</td>
            <td class="table-cell"><span :class="s.activo ? 'badge-green' : 'badge-red'">{{ s.activo ? 'Activo' : 'Inactivo' }}</span></td>
            <td class="table-cell"><div class="flex gap-2">
              <button @click="verPrestamos(s)" class="btn btn-secondary btn-sm">📋</button>
              <button @click="abrirEditar(s)" class="btn btn-secondary btn-sm">✏️</button>
              <button v-if="auth.isAdmin" @click="confirmarEliminar(s)" class="btn btn-danger btn-sm">🗑️</button>
            </div></td>
          </tr>
          <tr v-if="!socios.length"><td colspan="6"><EmptyState icon="👥" message="No hay socios registrados" /></td></tr>
        </tbody>
      </table>
    </div>
    <Pagination :page="page" :limit="limit" :total="total" :skip="skip" @change="cambiarPagina" />

    <ModalBase v-if="modal" :title="editando ? 'Editar socio' : 'Nuevo socio'" @close="modal = false">
      <form @submit.prevent="guardar" class="space-y-4">
        <div class="form-group"><label class="label-field">Nombre *</label><input v-model="form.nombre" class="input-field" required></div>
        <div class="form-group"><label class="label-field">Email *</label><input v-model="form.email" type="email" class="input-field" :disabled="!!editando" required></div>
        <div class="form-group"><label class="label-field">Teléfono</label><input v-model="form.telefono" type="tel" class="input-field"></div>
        <div v-if="formError" class="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm border border-red-200">{{ formError }}</div>
        <div class="flex gap-3 justify-end">
          <button type="button" @click="modal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" :disabled="formLoading" class="btn btn-primary">{{ formLoading ? 'Guardando…' : (editando ? 'Actualizar' : 'Crear') }}</button>
        </div>
      </form>
    </ModalBase>

    <ModalBase v-if="modalPrestamos" :title="`Préstamos de ${socioSeleccionado?.nombre}`" @close="modalPrestamos = false" maxWidth="720px">
      <LoadingSpinner v-if="prestamosLoading" />
      <EmptyState v-else-if="!prestamos.length" icon="📋" message="Sin préstamos" />
      <div v-else class="space-y-3 max-h-96 overflow-y-auto pr-1">
        <div v-for="p in prestamos" :key="p.id" class="card-sm flex items-center gap-3">
          <div class="flex-1">
            <p class="font-medium text-sm">{{ p.libro?.titulo }}</p>
            <p class="text-xs text-gray-400">{{ p.fecha_prestamo }} → {{ p.fecha_limite }}</p>
          </div>
          <span :class="{ activo: 'badge-blue', devuelto: 'badge-green', vencido: 'badge-red' }[p.estado] || 'badge-gray'">{{ p.estado }}</span>
          <span v-if="p.multa > 0" :class="p.multa_pagada ? 'badge-green' : 'badge-red'" class="text-xs">${{ p.multa }}</span>
        </div>
      </div>
    </ModalBase>

    <ModalBase v-if="confirmEliminar" title="Desactivar/Eliminar socio" @close="confirmEliminar = false">
      <p class="mb-6 text-gray-600">¿Eliminar al socio <strong>{{ socioAEliminar?.nombre }}</strong>?</p>
      <div class="flex gap-3 justify-end">
        <button @click="confirmEliminar = false" class="btn btn-secondary">Cancelar</button>
        <button @click="eliminar" :disabled="formLoading" class="btn btn-danger">Eliminar</button>
      </div>
    </ModalBase>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { sociosApi } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import Pagination from '@/components/Pagination.vue'
import ModalBase from '@/components/ModalBase.vue'

const auth = useAuthStore(); const toast = useToastStore()
const socios = ref([]), loading = ref(true), total = ref(0), page = ref(1), limit = 15, skip = ref(0), activo = ref('')
const modal = ref(false), editando = ref(null), confirmEliminar = ref(false), socioAEliminar = ref(null)
const modalPrestamos = ref(false), socioSeleccionado = ref(null), prestamos = ref([]), prestamosLoading = ref(false)
const form = ref({ nombre: '', email: '', telefono: '' }), formError = ref(''), formLoading = ref(false)

async function cargar() {
  loading.value = true
  try {
    const params = { skip: skip.value, limit }
    if (activo.value !== '') params.activo = activo.value
    const { data } = await sociosApi.listar(params); socios.value = data.items; total.value = data.total
  } finally { loading.value = false }
}
function cambiarPagina(p) { page.value = p; skip.value = (p-1)*limit; cargar() }
function abrirCrear() { editando.value = null; form.value = { nombre: '', email: '', telefono: '' }; formError.value = ''; modal.value = true }
function abrirEditar(s) { editando.value = s.id; form.value = { nombre: s.nombre, email: s.email, telefono: s.telefono || '' }; formError.value = ''; modal.value = true }
function confirmarEliminar(s) { socioAEliminar.value = s; confirmEliminar.value = true }
async function verPrestamos(s) {
  socioSeleccionado.value = s; prestamos.value = []; modalPrestamos.value = true; prestamosLoading.value = true
  try { const { data } = await sociosApi.prestamos(s.id, { limit: 50 }); prestamos.value = data.items }
  finally { prestamosLoading.value = false }
}
async function guardar() {
  formError.value = ''; formLoading.value = true
  try {
    if (editando.value) { await sociosApi.actualizar(editando.value, form.value); toast.success('Socio actualizado') }
    else { await sociosApi.crear(form.value); toast.success('Socio creado') }
    modal.value = false; cargar()
  } catch (e) { formError.value = e.response?.data?.detail || 'Error' }
  finally { formLoading.value = false }
}
async function eliminar() {
  formLoading.value = true
  try { await sociosApi.eliminar(socioAEliminar.value.id); toast.success('Socio eliminado'); confirmEliminar.value = false; cargar() }
  catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  finally { formLoading.value = false }
}
onMounted(cargar)
</script>

