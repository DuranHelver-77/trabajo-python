<template>
  <div class="max-w-7xl mx-auto px-4 py-10">
    <PageHeader title="Catálogo de Libros" subtitle="Explora nuestra colección">
      <template #actions>
        <router-link v-if="auth.isStaff" to="/admin/libros" class="btn btn-primary">⚙️ Gestionar</router-link>
      </template>
    </PageHeader>

    <!-- Filtros -->
    <div class="card mb-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <input v-model="filtros.buscar" @input="debouncedSearch" placeholder="🔍 Buscar por título..." class="input-field">
        <input v-model="filtros.autor" @input="debouncedSearch" placeholder="✍️ Por autor..." class="input-field">
        <select v-model="filtros.categoria_id" @change="cargar()" class="input-field">
          <option value="">🏷️ Todas las categorías</option>
          <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
        </select>
        <select v-model="filtros.orden" @change="cargar()" class="input-field">
          <option value="">Ordenar por título</option>
          <option value="anio">Ordenar por año</option>
        </select>
      </div>
      <div class="flex gap-4 mt-3">
        <input v-model.number="filtros.desde" type="number" placeholder="Año desde" class="input-field flex-1">
        <input v-model.number="filtros.hasta" type="number" placeholder="Año hasta" class="input-field flex-1">
        <button @click="limpiarFiltros" class="btn btn-secondary">Limpiar</button>
        <button @click="cargar()" class="btn btn-primary">Buscar</button>
      </div>
    </div>

    <LoadingSpinner v-if="loading" />
    <EmptyState v-else-if="!libros.length" icon="📚" message="No se encontraron libros" sub="Intenta con otros filtros" />
    <template v-else>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <router-link v-for="libro in libros" :key="libro.id" :to="`/libros/${libro.id}`" class="card hover:shadow-md transition group cursor-pointer">
          <div class="aspect-[3/4] bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg mb-4 overflow-hidden flex items-center justify-center">
            <img v-if="libro.portada_url" :src="libro.portada_url" :alt="libro.titulo" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
            <span v-else class="text-5xl">📖</span>
          </div>
          <h3 class="font-semibold text-gray-900 text-sm leading-tight mb-1 line-clamp-2">{{ libro.titulo }}</h3>
          <p class="text-xs text-gray-500 mb-1">{{ libro.autor?.nombre }}</p>
          <div class="flex items-center justify-between mt-2">
            <span class="text-xs text-gray-400">{{ libro.anio_publicacion }}</span>
            <span :class="libro.disponibles > 0 ? 'badge-green' : 'badge-red'">
              {{ libro.disponibles > 0 ? `${libro.disponibles} disp.` : 'Sin stock' }}
            </span>
          </div>
        </router-link>
      </div>
      <Pagination :page="page" :limit="limit" :total="total" :skip="skip" @change="cambiarPagina" />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { librosApi, categoriasApi } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import Pagination from '@/components/Pagination.vue'

const auth = useAuthStore()
const libros = ref([])
const categorias = ref([])
const loading = ref(true)
const total = ref(0)
const page = ref(1)
const limit = 12
const skip = ref(0)

const filtros = ref({ buscar: '', autor: '', categoria_id: '', orden: '', desde: null, hasta: null })
let searchTimer = null

function debouncedSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => cargar(), 500)
}

async function cargar() {
  loading.value = true
  try {
    const params = { skip: skip.value, limit }
    if (filtros.value.buscar) params.buscar = filtros.value.buscar
    if (filtros.value.autor) params.autor = filtros.value.autor
    if (filtros.value.categoria_id) params.categoria_id = filtros.value.categoria_id
    if (filtros.value.orden) params.orden = filtros.value.orden
    if (filtros.value.desde) params.desde = filtros.value.desde
    if (filtros.value.hasta) params.hasta = filtros.value.hasta
    const { data } = await librosApi.listar(params)
    libros.value = data.items
    total.value = data.total
  } finally { loading.value = false }
}

function cambiarPagina(p) {
  page.value = p
  skip.value = (p - 1) * limit
  cargar()
}

function limpiarFiltros() {
  filtros.value = { buscar: '', autor: '', categoria_id: '', orden: '', desde: null, hasta: null }
  page.value = 1; skip.value = 0
  cargar()
}

onMounted(async () => {
  const [, { data }] = await Promise.all([cargar(), categoriasApi.listar({ limit: 100 })])
  categorias.value = data.items
})
</script>

