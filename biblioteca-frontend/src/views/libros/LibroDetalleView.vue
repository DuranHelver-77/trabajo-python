<template>
  <div class="max-w-4xl mx-auto px-4 py-10">
    <router-link to="/libros" class="text-sm text-blue-600 hover:text-blue-700 mb-6 inline-flex items-center gap-1">← Volver al catálogo</router-link>
    <LoadingSpinner v-if="loading" />
    <div v-else-if="libro" class="grid md:grid-cols-3 gap-8">
      <!-- Portada -->
      <div class="md:col-span-1">
        <div class="aspect-[3/4] bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl overflow-hidden shadow-md flex items-center justify-center">
          <img v-if="libro.portada_url" :src="libro.portada_url" :alt="libro.titulo" class="w-full h-full object-cover">
          <span v-else class="text-7xl">📖</span>
        </div>
        <div class="mt-4 space-y-2">
          <span :class="libro.disponibles > 0 ? 'badge-green' : 'badge-red'" class="w-full justify-center py-2 text-sm">
            {{ libro.disponibles > 0 ? `✅ ${libro.disponibles} ejemplares disponibles` : '❌ Sin ejemplares disponibles' }}
          </span>
        </div>
      </div>
      <!-- Info -->
      <div class="md:col-span-2">
        <div class="flex items-start justify-between gap-4 mb-2">
          <h1 class="text-3xl font-bold text-gray-900">{{ libro.titulo }}</h1>
          <router-link v-if="auth.isStaff" :to="`/admin/libros`" class="btn btn-secondary btn-sm flex-shrink-0">✏️ Editar</router-link>
        </div>
        <p class="text-lg text-gray-600 mb-6">{{ libro.autor?.nombre }}
          <span v-if="libro.autor?.nacionalidad" class="text-sm text-gray-400">({{ libro.autor.nacionalidad }})</span>
        </p>
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="card-sm">
            <p class="text-xs text-gray-400 mb-1">ISBN</p>
            <p class="font-mono font-semibold text-sm">{{ libro.isbn }}</p>
          </div>
          <div class="card-sm">
            <p class="text-xs text-gray-400 mb-1">Año de publicación</p>
            <p class="font-semibold">{{ libro.anio_publicacion }}</p>
          </div>
          <div class="card-sm">
            <p class="text-xs text-gray-400 mb-1">Total de ejemplares</p>
            <p class="font-semibold">{{ libro.ejemplares }}</p>
          </div>
          <div class="card-sm">
            <p class="text-xs text-gray-400 mb-1">Disponibles</p>
            <p class="font-semibold" :class="libro.disponibles > 0 ? 'text-green-600' : 'text-red-600'">{{ libro.disponibles }}</p>
          </div>
        </div>
        <div v-if="libro.categorias?.length" class="mb-6">
          <p class="text-xs text-gray-400 mb-2">Categorías</p>
          <div class="flex flex-wrap gap-2">
            <span v-for="c in libro.categorias" :key="c.id" class="badge-blue">{{ c.nombre }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="text-center py-20 text-gray-500">Libro no encontrado</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { librosApi } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const route = useRoute()
const auth = useAuthStore()
const libro = ref(null)
const loading = ref(true)

onMounted(async () => {
  try { const { data } = await librosApi.obtener(route.params.id); libro.value = data }
  finally { loading.value = false }
})
</script>

