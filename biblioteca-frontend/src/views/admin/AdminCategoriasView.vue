<template>
  <div class="max-w-4xl mx-auto px-4 py-10">
    <PageHeader title="Gestión de Categorías">
      <template #actions><button @click="abrirCrear" class="btn btn-primary">+ Nueva categoría</button></template>
    </PageHeader>
    <LoadingSpinner v-if="loading" />
    <div v-else class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
      <table class="w-full">
        <thead class="bg-gray-50"><tr><th class="table-head">Nombre</th><th class="table-head">Descripción</th><th class="table-head">Acciones</th></tr></thead>
        <tbody>
          <tr v-for="c in categorias" :key="c.id" class="table-row">
            <td class="table-cell font-medium">{{ c.nombre }}</td>
            <td class="table-cell text-gray-500">{{ c.descripcion || '—' }}</td>
            <td class="table-cell"><div class="flex gap-2">
              <button @click="abrirEditar(c)" class="btn btn-secondary btn-sm">✏️</button>
              <button v-if="auth.isAdmin" @click="confirmarEliminar(c)" class="btn btn-danger btn-sm">🗑️</button>
            </div></td>
          </tr>
          <tr v-if="!categorias.length"><td colspan="3"><EmptyState icon="🏷️" message="No hay categorías" /></td></tr>
        </tbody>
      </table>
    </div>
    <Pagination :page="page" :limit="limit" :total="total" :skip="skip" @change="cambiarPagina" />

    <ModalBase v-if="modal" :title="editando ? 'Editar categoría' : 'Nueva categoría'" @close="modal = false">
      <form @submit.prevent="guardar" class="space-y-4">
        <div class="form-group"><label class="label-field">Nombre *</label><input v-model="form.nombre" class="input-field" required></div>
        <div class="form-group"><label class="label-field">Descripción</label><textarea v-model="form.descripcion" class="input-field" rows="3"></textarea></div>
        <div v-if="formError" class="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm border border-red-200">{{ formError }}</div>
        <div class="flex gap-3 justify-end">
          <button type="button" @click="modal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" :disabled="formLoading" class="btn btn-primary">{{ formLoading ? 'Guardando…' : (editando ? 'Actualizar' : 'Crear') }}</button>
        </div>
      </form>
    </ModalBase>
    <ModalBase v-if="confirmEliminar" title="Confirmar eliminación" @close="confirmEliminar = false">
      <p class="mb-6 text-gray-600">¿Eliminar la categoría <strong>{{ catAEliminar?.nombre }}</strong>?</p>
      <div class="flex gap-3 justify-end">
        <button @click="confirmEliminar = false" class="btn btn-secondary">Cancelar</button>
        <button @click="eliminar" :disabled="formLoading" class="btn btn-danger">Eliminar</button>
      </div>
    </ModalBase>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { categoriasApi } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import Pagination from '@/components/Pagination.vue'
import ModalBase from '@/components/ModalBase.vue'

const auth = useAuthStore(); const toast = useToastStore()
const categorias = ref([]), loading = ref(true), total = ref(0), page = ref(1), limit = 20, skip = ref(0)
const modal = ref(false), editando = ref(null), confirmEliminar = ref(false), catAEliminar = ref(null)
const form = ref({ nombre: '', descripcion: '' }), formError = ref(''), formLoading = ref(false)

async function cargar() {
  loading.value = true
  try { const { data } = await categoriasApi.listar({ skip: skip.value, limit }); categorias.value = data.items; total.value = data.total }
  finally { loading.value = false }
}
function cambiarPagina(p) { page.value = p; skip.value = (p-1)*limit; cargar() }
function abrirCrear() { editando.value = null; form.value = { nombre: '', descripcion: '' }; formError.value = ''; modal.value = true }
function abrirEditar(c) { editando.value = c.id; form.value = { nombre: c.nombre, descripcion: c.descripcion || '' }; formError.value = ''; modal.value = true }
function confirmarEliminar(c) { catAEliminar.value = c; confirmEliminar.value = true }
async function guardar() {
  formError.value = ''; formLoading.value = true
  try {
    if (editando.value) { await categoriasApi.actualizar(editando.value, form.value); toast.success('Categoría actualizada') }
    else { await categoriasApi.crear(form.value); toast.success('Categoría creada') }
    modal.value = false; cargar()
  } catch (e) { formError.value = e.response?.data?.detail || 'Error' }
  finally { formLoading.value = false }
}
async function eliminar() {
  formLoading.value = true
  try { await categoriasApi.eliminar(catAEliminar.value.id); toast.success('Categoría eliminada'); confirmEliminar.value = false; cargar() }
  catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  finally { formLoading.value = false }
}
onMounted(cargar)
</script>

