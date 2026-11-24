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
          <span :class="libro.disponibles > 0 ? 'badge-green' : 'badge-red'" class="w-full justify-center py-2 text-sm flex items-center">
            {{ libro.disponibles > 0 ? `✅ ${libro.disponibles} ejemplares disponibles` : '❌ Sin ejemplares disponibles' }}
          </span>

          <!-- Botón de solicitar préstamo para socios -->
          <button 
            v-if="auth.isSocio && libro.disponibles > 0" 
            @click="abrirModalSolicitud" 
            class="btn btn-primary w-full shadow-sm hover:shadow py-2.5 flex items-center justify-center gap-2 mt-3"
          >
            📖 Solicitar Préstamo
          </button>
          <div v-else-if="!auth.isLoggedIn" class="p-3 bg-blue-50 text-blue-700 text-xs rounded-lg text-center mt-3">
            Inicia sesión como socio para solicitar este libro.
          </div>
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

    <!-- Modal Solicitar Préstamo -->
    <ModalBase v-if="modalSolicitud" title="Confirmar solicitud de préstamo" @close="modalSolicitud = false">
      <div class="space-y-4">
        <p class="text-sm text-gray-600">
          ¿Deseas solicitar en préstamo el libro <strong class="text-gray-900">{{ libro?.titulo }}</strong>?
        </p>
        <div class="form-group">
          <label class="label-field">Días de préstamo (1 a 30):</label>
          <input v-model.number="diasPrestamo" type="number" min="1" max="30" class="input-field" />
        </div>
        <div v-if="errorSolicitud" class="bg-red-50 text-red-700 p-3 rounded-lg text-sm border border-red-200">
          {{ errorSolicitud }}
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" @click="modalSolicitud = false" class="btn btn-secondary">Cancelar</button>
          <button type="button" @click="confirmarSolicitud" :disabled="solicitando" class="btn btn-primary">
            {{ solicitando ? 'Solicitando...' : 'Confirmar Préstamo' }}
          </button>
        </div>
      </div>
    </ModalBase>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { librosApi, prestamosApi, parseError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ModalBase from '@/components/ModalBase.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()
const libro = ref(null)
const loading = ref(true)

const modalSolicitud = ref(false)
const diasPrestamo = ref(14)
const solicitando = ref(false)
const errorSolicitud = ref('')

function abrirModalSolicitud() {
  diasPrestamo.value = 14
  errorSolicitud.value = ''
  modalSolicitud.value = true
}

async function confirmarSolicitud() {
  solicitando.value = true
  errorSolicitud.value = ''
  try {
    await prestamosApi.solicitar({
      libro_id: libro.value.id,
      dias: diasPrestamo.value || 14
    })
    toast.success('¡Préstamo realizado con éxito!')
    modalSolicitud.value = false
    router.push('/mis-prestamos')
  } catch (err) {
    errorSolicitud.value = parseError(err)
  } finally {
    solicitando.value = false
  }
}

onMounted(async () => {
  try { const { data } = await librosApi.obtener(route.params.id); libro.value = data }
  finally { loading.value = false }
})
</script>

