<template>
  <div class="max-w-7xl mx-auto px-4 py-10">
    <PageHeader title="Reportes" subtitle="Estadísticas y análisis de la biblioteca" />

    <!-- Resumen general -->
    <div v-if="resumen" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
      <div class="stat-card"><div class="stat-icon bg-blue-100">📚</div><div><p class="stat-value">{{ resumen.total_libros }}</p><p class="stat-label">Total libros</p></div></div>
      <div class="stat-card"><div class="stat-icon bg-green-100">👥</div><div><p class="stat-value">{{ resumen.total_socios }}</p><p class="stat-label">Socios activos</p></div></div>
      <div class="stat-card"><div class="stat-icon bg-yellow-100">📋</div><div><p class="stat-value">{{ resumen.prestamos_activos }}</p><p class="stat-label">Préstamos activos</p></div></div>
      <div class="stat-card"><div class="stat-icon bg-red-100">⚠️</div><div><p class="stat-value">{{ resumen.prestamos_vencidos }}</p><p class="stat-label">Vencidos</p></div></div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Top libros -->
      <div class="card">
        <h2 class="section-title">📈 Top libros más prestados</h2>
        <LoadingSpinner v-if="loadingLibros" text="Cargando..." />
        <div v-else-if="topLibros.length" class="space-y-3">
          <div v-for="(l, i) in topLibros" :key="l.libro_id" class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0"
              :class="i === 0 ? 'bg-yellow-100 text-yellow-700' : i === 1 ? 'bg-gray-200 text-gray-600' : i === 2 ? 'bg-orange-100 text-orange-700' : 'bg-blue-50 text-blue-600'">
              {{ i + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-sm truncate">{{ l.titulo }}</p>
              <p class="text-xs text-gray-400">{{ l.autor }}</p>
            </div>
            <span class="badge-blue font-bold">{{ l.total_prestamos }}</span>
          </div>
        </div>
        <EmptyState v-else icon="📊" message="Sin datos" />
      </div>

      <!-- Categorías -->
      <div class="card">
        <h2 class="section-title">🏷️ Libros por categoría</h2>
        <LoadingSpinner v-if="loadingCats" />
        <div v-else-if="cats.length" class="space-y-2">
          <div v-for="c in cats" :key="c.categoria" class="flex items-center gap-3">
            <div class="flex-1">
              <div class="flex justify-between mb-1">
                <span class="text-sm font-medium">{{ c.categoria }}</span>
                <span class="text-sm font-bold text-blue-600">{{ c.total_libros }}</span>
              </div>
              <div class="bg-gray-100 rounded-full h-2">
                <div class="bg-blue-500 h-2 rounded-full transition-all" :style="{ width: `${(c.total_libros / maxCat) * 100}%` }"></div>
              </div>
            </div>
          </div>
        </div>
        <EmptyState v-else icon="🏷️" message="Sin datos" />
      </div>

      <!-- Préstamos vencidos -->
      <div class="card lg:col-span-2">
        <h2 class="section-title text-red-700">⚠️ Préstamos vencidos</h2>
        <LoadingSpinner v-if="loadingVencidos" />
        <EmptyState v-else-if="!vencidos.length" icon="🎉" message="No hay préstamos vencidos" />
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead><tr>
              <th class="table-head">Libro</th><th class="table-head">Socio</th><th class="table-head">Límite</th><th class="table-head">Días vencido</th><th class="table-head">Multa</th>
            </tr></thead>
            <tbody>
              <tr v-for="p in vencidos" :key="p.prestamo_id" class="table-row">
                <td class="table-cell font-medium">{{ p.titulo }}</td>
                <td class="table-cell text-gray-500">{{ p.socio }}</td>
                <td class="table-cell text-red-600">{{ p.fecha_limite }}</td>
                <td class="table-cell"><span class="badge-red">{{ p.dias_vencido }} días</span></td>
                <td class="table-cell font-bold text-red-600">${{ p.multa }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Socios con multas -->
      <div class="card">
        <h2 class="section-title text-yellow-700">💰 Socios con multas pendientes</h2>
        <LoadingSpinner v-if="loadingMultas" />
        <EmptyState v-else-if="!sociosMultas.length" icon="🎉" message="Sin multas pendientes" />
        <div v-else class="space-y-3">
          <div v-for="s in sociosMultas" :key="s.socio_id" class="flex items-center gap-3 p-3 bg-yellow-50 rounded-xl">
            <div class="flex-1">
              <p class="font-medium text-sm">{{ s.nombre }}</p>
              <p class="text-xs text-gray-500">{{ s.prestamos_con_multa }} préstamo(s)</p>
            </div>
            <span class="badge-red font-bold">${{ s.total_multas }}</span>
          </div>
        </div>
      </div>

      <!-- Autores más activos -->
      <div class="card">
        <h2 class="section-title">✍️ Autores más activos</h2>
        <LoadingSpinner v-if="loadingAutores" />
        <div v-else-if="autoresData.length" class="space-y-3">
          <div v-for="a in autoresData.slice(0,8)" :key="a.autor_id" class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-sm flex-shrink-0">{{ a.nombre?.[0] }}</div>
            <div class="flex-1">
              <p class="font-medium text-sm">{{ a.nombre }}</p>
              <p class="text-xs text-gray-400">{{ a.total_libros }} libros · {{ a.total_prestamos }} préstamos</p>
            </div>
          </div>
        </div>
        <EmptyState v-else icon="✍️" message="Sin datos" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { reportesApi } from '@/api/client'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'

const resumen = ref(null), topLibros = ref([]), cats = ref([]), vencidos = ref([]), sociosMultas = ref([]), autoresData = ref([])
const loadingLibros = ref(true), loadingCats = ref(true), loadingVencidos = ref(true), loadingMultas = ref(true), loadingAutores = ref(true)
const maxCat = computed(() => Math.max(...cats.value.map(c => c.total_libros), 1))

onMounted(async () => {
  const [r, l, c, v, m, a] = await Promise.all([
    reportesApi.resumen(),
    reportesApi.librosMasPrestados(10),
    reportesApi.categorias(),
    reportesApi.prestamosVencidos(),
    reportesApi.sociosConMultas(),
    reportesApi.autores(),
  ])
  resumen.value = r.data
  topLibros.value = l.data; loadingLibros.value = false
  cats.value = c.data; loadingCats.value = false
  vencidos.value = v.data; loadingVencidos.value = false
  sociosMultas.value = m.data; loadingMultas.value = false
  autoresData.value = a.data; loadingAutores.value = false
})
</script>

