<template>
  <div class="max-w-7xl mx-auto px-4 py-10">
    <PageHeader title="Autores" subtitle="Conoce a los autores de nuestra colección">
      <template #actions>
        <router-link v-if="auth.isStaff" to="/admin/autores" class="btn btn-primary">⚙️ Gestionar</router-link>
      </template>
    </PageHeader>

    <div class="card mb-6 flex gap-4">
      <input v-model="buscar" @input="debouncedSearch" placeholder="🔍 Buscar autor..." class="input-field">
    </div>

    <LoadingSpinner v-if="loading" />
    <EmptyState v-else-if="!autores.length" icon="✍️" message="No se encontraron autores" />
    <template v-else>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        <div v-for="a in autores" :key="a.id" class="card hover:shadow-md transition">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center text-2xl font-bold text-blue-600">
              {{ a.nombre?.[0] }}
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">{{ a.nombre }}</h3>
              <p class="text-sm text-gray-500">{{ a.nacionalidad || '—' }}</p>
            </div>
          </div>
          <div class="text-sm text-gray-500">
            <span v-if="a.anio_nacimiento">Nacido en {{ a.anio_nacimiento }}</span>
          </div>
          <router-link :to="`/libros?autor=${encodeURIComponent(a.nombre)}`" class="mt-3 inline-flex text-xs text-blue-600 hover:text-blue-700 font-medium">
            Ver libros →
          </router-link>
        </div>
      </div>
      <Pagination :page="page" :limit="limit" :total="total" :skip="skip" @change="cambiarPagina" />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { autoresApi } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import Pagination from '@/components/Pagination.vue'

const auth = useAuthStore()
const autores = ref([])
const buscar = ref('')
const loading = ref(true)
const total = ref(0)
const page = ref(1)
const limit = 12
const skip = ref(0)
let timer = null

function debouncedSearch() { clearTimeout(timer); timer = setTimeout(cargar, 400) }

async function cargar() {
  loading.value = true
  try {
    const { data } = await autoresApi.listar({ skip: skip.value, limit, ...(buscar.value ? { nacionalidad: buscar.value } : {}) })
    autores.value = data.items; total.value = data.total
  } finally { loading.value = false }
}

function cambiarPagina(p) { page.value = p; skip.value = (p - 1) * limit; cargar() }
onMounted(cargar)
</script>

