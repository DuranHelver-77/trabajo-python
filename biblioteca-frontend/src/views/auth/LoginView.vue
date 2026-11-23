<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-12">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="text-5xl mb-4">📚</div>
        <h1 class="text-3xl font-bold text-gray-900">Bienvenido</h1>
        <p class="text-gray-500 mt-2">Inicia sesión en tu cuenta</p>
      </div>
      <div class="card">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div class="form-group">
            <label class="label-field">Email</label>
            <input v-model="form.email" type="email" class="input-field" placeholder="tu@email.com" required autofocus>
          </div>
          <div class="form-group">
            <label class="label-field">Contraseña</label>
            <input v-model="form.password" type="password" class="input-field" placeholder="••••••••" required>
          </div>
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {{ error }}
          </div>
          <button type="submit" :disabled="loading" class="btn btn-primary w-full justify-center">
            <span v-if="loading">Iniciando sesión…</span>
            <span v-else>Iniciar sesión</span>
          </button>
        </form>
        <div class="mt-4 text-center text-sm text-gray-500">
          ¿No tienes cuenta?
          <router-link to="/registro" class="text-blue-600 hover:text-blue-700 font-medium ml-1">Regístrate gratis</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = ref({ email: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value.email, form.value.password)
    router.push('/')
  } catch (e) {
    const msg = e.response?.data?.detail
    if (e.response?.status === 423) error.value = 'Cuenta bloqueada por demasiados intentos. Espera 15 minutos.'
    else error.value = msg || 'Credenciales incorrectas'
  } finally { loading.value = false }
}
</script>

