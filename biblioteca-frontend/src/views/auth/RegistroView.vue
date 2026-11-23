<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-12">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="text-5xl mb-4">📚</div>
        <h1 class="text-3xl font-bold text-gray-900">Crear cuenta</h1>
        <p class="text-gray-500 mt-2">Únete a la biblioteca</p>
      </div>
      <div class="card">
        <form @submit.prevent="handleRegistro" class="space-y-4">
          <div class="form-group">
            <label class="label-field">Email</label>
            <input v-model="form.email" type="email" class="input-field" placeholder="tu@email.com" required autofocus>
          </div>
          <div class="form-group">
            <label class="label-field">Nombre completo</label>
            <input v-model="form.nombre" type="text" class="input-field" placeholder="Juan García" required>
          </div>
          <div class="form-group">
            <label class="label-field">Contraseña</label>
            <input v-model="form.password" type="password" class="input-field" placeholder="Mínimo 8 caracteres con mayúscula" required>
            <p class="error-text">Debe tener al menos 8 caracteres y una mayúscula.</p>
          </div>
          <div class="form-group">
            <label class="label-field">Confirmar contraseña</label>
            <input v-model="form.password2" type="password" class="input-field" placeholder="Repite la contraseña" required>
            <p v-if="form.password !== form.password2 && form.password2" class="error-text">Las contraseñas no coinciden</p>
          </div>
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{{ error }}</div>
          <div v-if="ok" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
            ¡Cuenta creada! <router-link to="/login" class="font-medium underline">Inicia sesión</router-link>
          </div>
          <button type="submit" :disabled="loading || form.password !== form.password2" class="btn btn-primary w-full justify-center">
            <span v-if="loading">Creando cuenta…</span>
            <span v-else>Crear cuenta</span>
          </button>
        </form>
        <div class="mt-4 text-center text-sm text-gray-500">
          ¿Ya tienes cuenta?
          <router-link to="/login" class="text-blue-600 hover:text-blue-700 font-medium ml-1">Inicia sesión</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const form = ref({ email: '', nombre: '', password: '', password2: '' })
const error = ref('')
const loading = ref(false)
const ok = ref(false)

async function handleRegistro() {
  if (form.value.password !== form.value.password2) return
  error.value = ''
  loading.value = true
  try {
    await auth.register({ email: form.value.email, nombre: form.value.nombre, password: form.value.password, password2: form.value.password2 })
    ok.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al crear la cuenta'
  } finally { loading.value = false }
}
</script>

