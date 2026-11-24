<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-12">
    <div class="w-full max-w-lg">
      <div class="text-center mb-6">
        <div class="text-5xl mb-3">📚</div>
        <h1 class="text-3xl font-bold text-gray-900">Iniciar Sesión</h1>
        <p class="text-gray-500 mt-1">Selecciona el rol con el que deseas ingresar al sistema</p>
      </div>

      <div class="card shadow-lg border border-gray-200">
        <!-- Selector de Rol -->
        <div class="mb-5">
          <label class="label-field mb-2 text-xs uppercase tracking-wider text-gray-500 font-semibold">
            ¿Con cuál rol vas a ingresar?
          </label>
          <div class="grid grid-cols-3 gap-2.5">
            <!-- Botón Admin -->
            <button
              type="button"
              @click="seleccionarRol('admin')"
              :class="[
                'flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-semibold transition-all cursor-pointer',
                rolSeleccionado === 'admin'
                  ? 'border-red-500 bg-red-50 text-red-800 shadow-sm ring-2 ring-red-300'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-600'
              ]"
            >
              <span class="text-2xl mb-1">👑</span>
              <span class="font-bold">Admin</span>
              <span class="text-[10px] text-gray-400 font-normal mt-0.5">Control total</span>
            </button>

            <!-- Botón Bibliotecario -->
            <button
              type="button"
              @click="seleccionarRol('bibliotecario')"
              :class="[
                'flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-semibold transition-all cursor-pointer',
                rolSeleccionado === 'bibliotecario'
                  ? 'border-blue-500 bg-blue-50 text-blue-800 shadow-sm ring-2 ring-blue-300'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-600'
              ]"
            >
              <span class="text-2xl mb-1">📖</span>
              <span class="font-bold">Bibliotecario</span>
              <span class="text-[10px] text-gray-400 font-normal mt-0.5">Operación / Staff</span>
            </button>

            <!-- Botón Socio -->
            <button
              type="button"
              @click="seleccionarRol('socio')"
              :class="[
                'flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-semibold transition-all cursor-pointer',
                rolSeleccionado === 'socio'
                  ? 'border-green-500 bg-green-50 text-green-800 shadow-sm ring-2 ring-green-300'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-600'
              ]"
            >
              <span class="text-2xl mb-1">👤</span>
              <span class="font-bold">Socio</span>
              <span class="text-[10px] text-gray-400 font-normal mt-0.5">Lector / Cliente</span>
            </button>
          </div>

          <!-- Banner informativo del rol seleccionado -->
          <div v-if="rolInfo" class="mt-3 p-3 rounded-xl text-xs flex items-center justify-between border" :class="rolInfo.bannerClass">
            <div class="pr-2">
              <p class="font-bold text-sm">{{ rolInfo.titulo }}</p>
              <p class="opacity-90 mt-0.5">{{ rolInfo.descripcion }}</p>
            </div>
            <span class="badge flex-shrink-0" :class="rolInfo.badgeClass">{{ rolInfo.tag }}</span>
          </div>
        </div>

        <div class="relative flex py-2 items-center mb-4">
          <div class="flex-grow border-t border-gray-200"></div>
          <span class="flex-shrink mx-4 text-xs uppercase tracking-wider text-gray-400 font-medium">Credenciales de Acceso</span>
          <div class="flex-grow border-t border-gray-200"></div>
        </div>

        <!-- Formulario -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div class="form-group">
            <label class="label-field">Correo electrónico</label>
            <input
              v-model="form.email"
              type="email"
              class="input-field"
              placeholder="tu@email.com"
              required
            >
          </div>

          <div class="form-group">
            <label class="label-field">Contraseña</label>
            <input
              v-model="form.password"
              type="password"
              class="input-field"
              placeholder="••••••••"
              required
            >
          </div>

          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="btn btn-primary w-full justify-center py-2.5 text-sm font-semibold shadow-md"
          >
            <span v-if="loading">Iniciando sesión…</span>
            <span v-else>
              Iniciar sesión como {{ rolInfo ? rolInfo.nombre : 'Usuario' }}
            </span>
          </button>
        </form>

        <div class="mt-5 text-center text-sm text-gray-500">
          ¿No tienes cuenta de socio?
          <router-link to="/registro" class="text-blue-600 hover:text-blue-700 font-medium ml-1">Regístrate gratis</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { parseError } from '@/api/client'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ email: 'admin@biblioteca.com', password: 'Admin1234*' })
const rolSeleccionado = ref('admin')
const error = ref('')
const loading = ref(false)

const rolesConfig = {
  admin: {
    nombre: 'Administrador',
    titulo: '👑 Rol: Administrador',
    descripcion: 'Control total del sistema: usuarios, roles, reportes, libros y préstamos.',
    tag: 'ADMIN',
    bannerClass: 'bg-red-50 border-red-200 text-red-900',
    badgeClass: 'badge-red',
    email: 'admin@biblioteca.com',
    password: 'Admin1234*',
  },
  bibliotecario: {
    nombre: 'Bibliotecario',
    titulo: '📖 Rol: Bibliotecario',
    descripcion: 'Personal operativo: registrar préstamos, devoluciones, cobrar multas y editar libros.',
    tag: 'STAFF',
    bannerClass: 'bg-blue-50 border-blue-200 text-blue-900',
    badgeClass: 'badge-blue',
    email: 'biblio@biblioteca.com',
    password: 'Biblio1234*',
  },
  socio: {
    nombre: 'Socio',
    titulo: '👤 Rol: Socio (Lector)',
    descripcion: 'Usuario lector: consultar catálogo, revisar sus propios préstamos y multas.',
    tag: 'SOCIO',
    bannerClass: 'bg-green-50 border-green-200 text-green-900',
    badgeClass: 'badge-green',
    email: 'user@example.com',
    password: 'Socio1234*',
  },
}

const rolInfo = computed(() => rolesConfig[rolSeleccionado.value] || null)

function seleccionarRol(rol) {
  rolSeleccionado.value = rol
  error.value = ''
  if (rolesConfig[rol]) {
    form.value.email = rolesConfig[rol].email
    form.value.password = rolesConfig[rol].password
  }
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value.email, form.value.password)
    router.push('/')
  } catch (e) {
    if (e.response?.status === 423) {
      error.value = 'Cuenta bloqueada por demasiados intentos. Espera 15 minutos.'
    } else {
      error.value = parseError(e) || 'Credenciales incorrectas'
    }
  } finally {
    loading.value = false
  }
}
</script>
