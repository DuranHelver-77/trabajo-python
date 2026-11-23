<template>
  <div class="max-w-5xl mx-auto px-4 py-10">
    <PageHeader title="Gestión de Autores">
      <template #actions>
        <button @click="abrirCrear" class="btn btn-primary">+ Nuevo autor</button>
      </template>
    </PageHeader>
    <div class="card mb-6"><input v-model="buscar" @input="debouncedSearch" placeholder="🔍 Buscar..." class="input-field"></div>

    <LoadingSpinner v-if="loading" />
    <div v-else class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
      <table class="w-full">
        <thead class="bg-gray-50"><tr>
          <th class="table-head">Nombre</th><th class="table-head">Nacionalidad</th><th class="table-head">Nacimiento</th><th class="table-head">Acciones</th>
        </tr></thead>
        <tbody>
          <tr v-for="a in autores" :key="a.id" class="table-row">
            <td class="table-cell font-medium">{{ a.nombre }}</td>
            <td class="table-cell text-gray-500">{{ a.nacionalidad || '—' }}</td>
            <td class="table-cell text-gray-500">{{ a.anio_nacimiento || '—' }}</td>
            <td class="table-cell"><div class="flex gap-2">
              <button @click="abrirEditar(a)" class="btn btn-secondary btn-sm">✏️</button>
              <button v-if="auth.isAdmin" @click="confirmarEliminar(a)" class="btn btn-danger btn-sm">🗑️</button>
            </div></td>
          </tr>
          <tr v-if="!autores.length"><td colspan="4"><EmptyState icon="✍️" message="No hay autores" /></td></tr>
        </tbody>
      </table>
    </div>
    <Pagination :page="page" :limit="limit" :total="total" :skip="skip" @change="cambiarPagina" />

    <ModalBase v-if="modal" :title="editando ? 'Editar autor' : 'Nuevo autor'" @close="modal = false">
      <form @submit.prevent="guardar" class="space-y-4">
        <div class="form-group"><label class="label-field">Nombre *</label><input v-model="form.nombre" class="input-field" required></div>
        <div class="form-group"><label class="label-field">Nacionalidad</label><input v-model="form.nacionalidad" class="input-field"></div>
        <div class="form-group"><label class="label-field">Año nacimiento</label><input v-model.number="form.anio_nacimiento" type="number" class="input-field"></div>
        <div v-if="formError" class="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm border border-red-200">{{ formError }}</div>
        <div class="flex gap-3 justify-end">
          <button type="button" @click="modal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" :disabled="formLoading" class="btn btn-primary">{{ formLoading ? 'Guardando…' : (editando ? 'Actualizar' : 'Crear') }}</button>
        </div>
      </form>
    </ModalBase>

    <ModalBase v-if="confirmEliminar" title="Confirmar eliminación" @close="confirmEliminar = false">
      <p class="mb-6 text-gray-600">¿Eliminar al autor <strong>{{ autoAEliminar?.nombre }}</strong>?</p>
      <div class="flex gap-3 justify-end">
        <button @click="confirmEliminar = false" class="btn btn-secondary">Cancelar</button>
        <button @click="eliminar" :disabled="formLoading" class="btn btn-danger">Eliminar</button>
      </div>
    </ModalBase>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { autoresApi } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import Pagination from '@/components/Pagination.vue'
import ModalBase from '@/components/ModalBase.vue'

const auth = useAuthStore(); const toast = useToastStore()
const autores = ref([]), loading = ref(true), total = ref(0), page = ref(1), limit = 15, skip = ref(0)
const buscar = ref(''), modal = ref(false), editando = ref(null), autoAEliminar = ref(null), confirmEliminar = ref(false)
const form = ref({ nombre: '', nacionalidad: '', anio_nacimiento: null }), formError = ref(''), formLoading = ref(false)
let timer = null

function debouncedSearch() { clearTimeout(timer); timer = setTimeout(cargar, 400) }
async function cargar() {
  loading.value = true
  try { const { data } = await autoresApi.listar({ skip: skip.value, limit }); autores.value = data.items; total.value = data.total }
  finally { loading.value = false }
}
function cambiarPagina(p) { page.value = p; skip.value = (p-1)*limit; cargar() }
function abrirCrear() { editando.value = null; form.value = { nombre: '', nacionalidad: '', anio_nacimiento: null }; formError.value = ''; modal.value = true }
function abrirEditar(a) { editando.value = a.id; form.value = { nombre: a.nombre, nacionalidad: a.nacionalidad || '', anio_nacimiento: a.anio_nacimiento }; formError.value = ''; modal.value = true }
function confirmarEliminar(a) { autoAEliminar.value = a; confirmEliminar.value = true }
async function guardar() {
  formError.value = ''; formLoading.value = true
  try {
    if (editando.value) { await autoresApi.actualizar(editando.value, form.value); toast.success('Autor actualizado') }
    else { await autoresApi.crear(form.value); toast.success('Autor creado') }
    modal.value = false; cargar()
  } catch (e) { formError.value = e.response?.data?.detail || 'Error' }
  finally { formLoading.value = false }
}
async function eliminar() {
  formLoading.value = true
  try { await autoresApi.eliminar(autoAEliminar.value.id); toast.success('Autor eliminado'); confirmEliminar.value = false; cargar() }
  catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  finally { formLoading.value = false }
}
onMounted(cargar)
</script>

