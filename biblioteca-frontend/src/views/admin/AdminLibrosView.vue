<template>
  <div class="max-w-7xl mx-auto px-4 py-10">
    <PageHeader title="Gestión de Libros">
      <template #actions>
        <button @click="abrirCrear" class="btn btn-primary">+ Nuevo libro</button>
      </template>
    </PageHeader>

    <!-- Filtros -->
    <div class="card mb-6 flex gap-3">
      <input v-model="buscar" @input="debouncedSearch" placeholder="🔍 Buscar..." class="input-field">
      <button @click="cargar()" class="btn btn-primary">Buscar</button>
    </div>

    <LoadingSpinner v-if="loading" />
    <div v-else class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="table-head">Portada</th>
            <th class="table-head">Título</th>
            <th class="table-head">Autor</th>
            <th class="table-head">ISBN</th>
            <th class="table-head">Año</th>
            <th class="table-head">Disponibles</th>
            <th class="table-head">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in libros" :key="l.id" class="table-row">
            <td class="table-cell">
              <div class="w-10 h-14 rounded overflow-hidden bg-blue-50 flex items-center justify-center">
                <img v-if="l.portada_url" :src="l.portada_url" class="w-full h-full object-cover">
                <span v-else class="text-lg">📖</span>
              </div>
            </td>
            <td class="table-cell font-medium max-w-xs truncate">{{ l.titulo }}</td>
            <td class="table-cell text-gray-500">{{ l.autor?.nombre }}</td>
            <td class="table-cell font-mono text-xs">{{ l.isbn }}</td>
            <td class="table-cell">{{ l.anio_publicacion }}</td>
            <td class="table-cell">
              <span :class="l.disponibles > 0 ? 'badge-green' : 'badge-red'">{{ l.disponibles }}/{{ l.ejemplares }}</span>
            </td>
            <td class="table-cell">
              <div class="flex gap-2">
                <button @click="abrirPortada(l)" class="btn btn-secondary btn-sm">🖼️</button>
                <button @click="abrirEditar(l)" class="btn btn-secondary btn-sm">✏️</button>
                <button v-if="auth.isAdmin" @click="confirmarEliminar(l)" class="btn btn-danger btn-sm">🗑️</button>
              </div>
            </td>
          </tr>
          <tr v-if="!libros.length"><td colspan="7"><EmptyState icon="📚" message="No hay libros registrados" /></td></tr>
        </tbody>
      </table>
    </div>
    <Pagination :page="page" :limit="limit" :total="total" :skip="skip" @change="cambiarPagina" />

    <!-- Modal crear/editar -->
    <ModalBase v-if="modal" :title="editando ? 'Editar libro' : 'Nuevo libro'" @close="modal = false" maxWidth="600px">
      <form @submit.prevent="guardar" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div class="form-group col-span-2">
            <label class="label-field">Título *</label>
            <input v-model="form.titulo" class="input-field" required>
          </div>
          <div class="form-group">
            <label class="label-field">ISBN (13 dígitos) *</label>
            <input v-model="form.isbn" class="input-field" :disabled="editando" required>
          </div>
          <div class="form-group">
            <label class="label-field">Año de publicación *</label>
            <input v-model.number="form.anio_publicacion" type="number" class="input-field" required>
          </div>
          <div class="form-group">
            <label class="label-field">Ejemplares *</label>
            <input v-model.number="form.ejemplares" type="number" min="1" max="50" class="input-field" required>
          </div>
          <div class="form-group">
            <label class="label-field">Autor *</label>
            <select v-model.number="form.autor_id" class="input-field" required>
              <option value="">Seleccionar autor</option>
              <option v-for="a in autores" :key="a.id" :value="a.id">{{ a.nombre }}</option>
            </select>
          </div>
          <div class="form-group col-span-2">
            <label class="label-field">Categorías</label>
            <div class="flex flex-wrap gap-2 p-2 border border-gray-300 rounded-lg min-h-10">
              <label v-for="c in categorias" :key="c.id" class="flex items-center gap-1 text-sm cursor-pointer">
                <input type="checkbox" :value="c.id" v-model="form.categoria_ids" class="rounded">
                {{ c.nombre }}
              </label>
            </div>
          </div>
        </div>
        <div v-if="formError" class="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm border border-red-200">{{ formError }}</div>
        <div class="flex gap-3 justify-end">
          <button type="button" @click="modal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" :disabled="formLoading" class="btn btn-primary">{{ formLoading ? 'Guardando…' : (editando ? 'Actualizar' : 'Crear') }}</button>
        </div>
      </form>
    </ModalBase>

    <!-- Modal portada -->
    <ModalBase v-if="modalPortada" title="Gestionar portada" @close="modalPortada = false">
      <div class="space-y-4">
        <div class="aspect-video bg-blue-50 rounded-xl overflow-hidden flex items-center justify-center max-h-64">
          <img v-if="libroSeleccionado?.portada_url" :src="libroSeleccionado.portada_url" class="max-h-64 object-contain">
          <span v-else class="text-5xl">📖</span>
        </div>
        <div>
          <label class="label-field">Subir nueva portada (JPG, PNG o WEBP · máx. 5 MB)</label>
          <input type="file" @change="e => portadaFile = e.target.files[0]" accept="image/jpeg,image/png,image/webp" class="input-field">
        </div>
        <div class="flex gap-3 justify-end">
          <button v-if="libroSeleccionado?.portada_url" @click="eliminarPortada" :disabled="portadaLoading" class="btn btn-danger">🗑️ Eliminar</button>
          <button @click="subirPortada" :disabled="!portadaFile || portadaLoading" class="btn btn-primary">{{ portadaLoading ? 'Subiendo…' : '☁️ Subir' }}</button>
        </div>
      </div>
    </ModalBase>

    <!-- Confirm eliminar -->
    <ModalBase v-if="confirmEliminar" title="Confirmar eliminación" @close="confirmEliminar = false">
      <p class="text-gray-600 mb-6">¿Eliminar el libro <strong>{{ libroAEliminar?.titulo }}</strong>? Esta acción no se puede deshacer.</p>
      <div class="flex gap-3 justify-end">
        <button @click="confirmEliminar = false" class="btn btn-secondary">Cancelar</button>
        <button @click="eliminarLibro" :disabled="formLoading" class="btn btn-danger">{{ formLoading ? 'Eliminando…' : 'Eliminar' }}</button>
      </div>
    </ModalBase>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { librosApi, autoresApi, categoriasApi } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import Pagination from '@/components/Pagination.vue'
import ModalBase from '@/components/ModalBase.vue'

const auth = useAuthStore()
const toast = useToastStore()
const libros = ref([]), autores = ref([]), categorias = ref([])
const loading = ref(true)
const total = ref(0), page = ref(1), limit = 15, skip = ref(0)
const buscar = ref(''), modal = ref(false), editando = ref(null)
const modalPortada = ref(false), libroSeleccionado = ref(null), portadaFile = ref(null), portadaLoading = ref(false)
const confirmEliminar = ref(false), libroAEliminar = ref(null)
const form = ref(formVacio()), formError = ref(''), formLoading = ref(false)
let timer = null

function formVacio() { return { titulo: '', isbn: '', anio_publicacion: new Date().getFullYear(), ejemplares: 1, autor_id: '', categoria_ids: [] } }
function debouncedSearch() { clearTimeout(timer); timer = setTimeout(cargar, 400) }

async function cargar() {
  loading.value = true
  try {
    const { data } = await librosApi.listar({ skip: skip.value, limit, ...(buscar.value ? { buscar: buscar.value } : {}) })
    libros.value = data.items; total.value = data.total
  } finally { loading.value = false }
}

function cambiarPagina(p) { page.value = p; skip.value = (p - 1) * limit; cargar() }

function abrirCrear() { editando.value = null; form.value = formVacio(); formError.value = ''; modal.value = true }
function abrirEditar(l) {
  editando.value = l.id
  form.value = { titulo: l.titulo, isbn: l.isbn, anio_publicacion: l.anio_publicacion, ejemplares: l.ejemplares, autor_id: l.autor_id || l.autor?.id, categoria_ids: l.categorias?.map(c => c.id) || [] }
  formError.value = ''; modal.value = true
}

function abrirPortada(l) { libroSeleccionado.value = l; portadaFile.value = null; modalPortada.value = true }
function confirmarEliminar(l) { libroAEliminar.value = l; confirmEliminar.value = true }

async function guardar() {
  formError.value = ''; formLoading.value = true
  try {
    if (editando.value) {
      const { titulo, anio_publicacion, ejemplares, categoria_ids } = form.value
      await librosApi.actualizar(editando.value, { titulo, anio_publicacion, ejemplares, categoria_ids })
      toast.success('Libro actualizado')
    } else {
      await librosApi.crear(form.value)
      toast.success('Libro creado')
    }
    modal.value = false; cargar()
  } catch (e) { formError.value = e.response?.data?.detail || 'Error al guardar' }
  finally { formLoading.value = false }
}

async function subirPortada() {
  portadaLoading.value = true
  try {
    const { data } = await librosApi.subirPortada(libroSeleccionado.value.id, portadaFile.value)
    libroSeleccionado.value = data
    libros.value = libros.value.map(l => l.id === data.id ? data : l)
    toast.success('Portada actualizada')
  } catch (e) { toast.error(e.response?.data?.detail || 'Error al subir portada') }
  finally { portadaLoading.value = false }
}

async function eliminarPortada() {
  portadaLoading.value = true
  try {
    const { data } = await librosApi.eliminarPortada(libroSeleccionado.value.id)
    libroSeleccionado.value = data
    libros.value = libros.value.map(l => l.id === data.id ? data : l)
    toast.success('Portada eliminada')
  } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  finally { portadaLoading.value = false }
}

async function eliminarLibro() {
  formLoading.value = true
  try {
    await librosApi.eliminar(libroAEliminar.value.id)
    toast.success('Libro eliminado')
    confirmEliminar.value = false; cargar()
  } catch (e) { toast.error(e.response?.data?.detail || 'Error al eliminar') }
  finally { formLoading.value = false }
}

onMounted(async () => {
  const [, a, c] = await Promise.all([cargar(), autoresApi.listar({ limit: 200 }), categoriasApi.listar({ limit: 100 })])
  autores.value = a.data.items; categorias.value = c.data.items
})
</script>

