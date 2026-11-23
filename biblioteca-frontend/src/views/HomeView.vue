<template>
  <div class="max-w-7xl mx-auto px-4 py-10">
    <!-- Hero -->
    <div class="text-center py-16 px-4">
      <h1 class="text-5xl font-bold text-gray-900 mb-4">📚 Biblioteca Digital</h1>
      <p class="text-xl text-gray-500 mb-8 max-w-2xl mx-auto">Gestiona libros, autores, préstamos y más desde una plataforma completa y fácil de usar.</p>
      <div class="flex justify-center gap-4">
        <router-link to="/libros" class="btn btn-primary">Explorar Libros</router-link>
        <router-link v-if="!auth.isLoggedIn" to="/registro" class="btn btn-secondary">Registrarse Gratis</router-link>
      </div>
    </div>

    <!-- Stats cards (solo staff) -->
    <div v-if="auth.isStaff && resumen" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
      <div class="stat-card"><div class="stat-icon bg-blue-100">📚</div><div><p class="stat-value">{{ resumen.total_libros }}</p><p class="stat-label">Libros</p></div></div>
      <div class="stat-card"><div class="stat-icon bg-green-100">👥</div><div><p class="stat-value">{{ resumen.total_socios }}</p><p class="stat-label">Socios</p></div></div>
      <div class="stat-card"><div class="stat-icon bg-yellow-100">📋</div><div><p class="stat-value">{{ resumen.prestamos_activos }}</p><p class="stat-label">Préstamos activos</p></div></div>
      <div class="stat-card"><div class="stat-icon bg-red-100">⚠️</div><div><p class="stat-value">{{ resumen.prestamos_vencidos }}</p><p class="stat-label">Vencidos</p></div></div>
    </div>

    <!-- Últimos libros -->
    <div class="mb-10">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold text-gray-900">Libros recientes</h2>
        <router-link to="/libros" class="text-sm text-blue-600 hover:text-blue-700 font-medium">Ver todos →</router-link>
      </div>
      <LoadingSpinner v-if="loading" />
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <router-link
          v-for="libro in libros"
          :key="libro.id"
          :to="`/libros/${libro.id}`"
          class="card hover:shadow-md transition group"
        >
          <div class="aspect-[3/4] bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg mb-4 overflow-hidden flex items-center justify-center">
            <img v-if="libro.portada_url" :src="libro.portada_url" :alt="libro.titulo" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
            <span v-else class="text-5xl">📖</span>
          </div>
          <h3 class="font-semibold text-gray-900 text-sm leading-tight mb-1 line-clamp-2">{{ libro.titulo }}</h3>
          <p class="text-xs text-gray-500">{{ libro.autor?.nombre }}</p>
          <div class="flex items-center justify-between mt-3">
            <span class="text-xs text-gray-400">{{ libro.anio_publicacion }}</span>
            <span :class="libro.disponibles > 0 ? 'badge-green' : 'badge-red'">
              {{ libro.disponibles > 0 ? `${libro.disponibles} disponibles` : 'Sin stock' }}
            </span>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Features -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 py-10">
      <div class="card text-center">
        <div class="text-4xl mb-4">🔍</div>
        <h3 class="font-semibold text-gray-900 mb-2">Búsqueda avanzada</h3>
        <p class="text-sm text-gray-500">Filtra por título, autor, categoría y año.</p>
      </div>
      <div class="card text-center">
        <div class="text-4xl mb-4">🔒</div>
        <h3 class="font-semibold text-gray-900 mb-2">Gestión segura</h3>
        <p class="text-sm text-gray-500">Sistema de roles: admin, bibliotecario y socio.</p>
      </div>
      <div class="card text-center">
        <div class="text-4xl mb-4">📊</div>
        <h3 class="font-semibold text-gray-900 mb-2">Reportes detallados</h3>
        <p class="text-sm text-gray-500">Estadísticas en tiempo real para el equipo.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { librosApi, reportesApi } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const libros = ref([])
const resumen = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await librosApi.listar({ limit: 8, skip: 0 })
    libros.value = data.items
    if (auth.isStaff) {
      const r = await reportesApi.resumen()
      resumen.value = r.data
    }
  } finally { loading.value = false }
})
</script>

