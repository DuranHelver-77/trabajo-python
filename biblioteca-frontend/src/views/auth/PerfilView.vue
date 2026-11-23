<template>
  <div class="max-w-2xl mx-auto px-4 py-10">
    <PageHeader title="Mi Perfil" subtitle="Gestiona tu información personal y seguridad" />
    <div v-if="auth.user" class="space-y-6">
      <!-- Info principal -->
      <div class="card">
        <h2 class="section-title">Información de cuenta</h2>
        <div class="space-y-3 text-sm">
          <div class="flex items-center gap-3 py-2 border-b border-gray-100">
            <span class="text-gray-500 w-32">Email:</span>
            <span class="font-medium">{{ auth.user.email }}</span>
          </div>
          <div class="flex items-center gap-3 py-2 border-b border-gray-100">
            <span class="text-gray-500 w-32">Rol:</span>
            <span :class="rolBadge(auth.user.rol)">{{ auth.user.rol }}</span>
          </div>
          <div class="flex items-center gap-3 py-2">
            <span class="text-gray-500 w-32">Estado:</span>
            <span :class="auth.user.activo ? 'badge-green' : 'badge-red'">{{ auth.user.activo ? 'Activo' : 'Inactivo' }}</span>
          </div>
        </div>
      </div>

      <!-- Cambiar contraseña -->
      <div class="card">
        <h2 class="section-title">Cambiar contraseña</h2>
        <form @submit.prevent="cambiarPass" class="space-y-4">
          <div class="form-group">
            <label class="label-field">Contraseña actual</label>
            <input v-model="passForm.password_actual" type="password" class="input-field" required>
          </div>
          <div class="form-group">
            <label class="label-field">Nueva contraseña</label>
            <input v-model="passForm.password_nuevo" type="password" class="input-field" required>
          </div>
          <div class="form-group">
            <label class="label-field">Confirmar nueva contraseña</label>
            <input v-model="passForm.password_nuevo2" type="password" class="input-field" required>
          </div>
          <div v-if="passError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{{ passError }}</div>
          <div v-if="passOk" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">Contraseña actualizada exitosamente.</div>
          <button type="submit" :disabled="passLoading || passForm.password_nuevo !== passForm.password_nuevo2" class="btn btn-primary">
            {{ passLoading ? 'Guardando…' : 'Actualizar contraseña' }}
          </button>
        </form>
      </div>

      <!-- Perfil de socio -->
      <div v-if="auth.isSocio && socio" class="card">
        <h2 class="section-title">Perfil de socio</h2>
        <form @submit.prevent="actualizarSocio" class="space-y-4">
          <div class="form-group">
            <label class="label-field">Nombre</label>
            <input v-model="socioForm.nombre" type="text" class="input-field">
          </div>
          <div class="form-group">
            <label class="label-field">Teléfono</label>
            <input v-model="socioForm.telefono" type="tel" class="input-field">
          </div>
          <button type="submit" :disabled="socioLoading" class="btn btn-primary">{{ socioLoading ? 'Guardando…' : 'Actualizar perfil' }}</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { authApi, sociosApi } from '@/api/client'
import PageHeader from '@/components/PageHeader.vue'

const auth = useAuthStore()
const toast = useToastStore()

const passForm = ref({ password_actual: '', password_nuevo: '', password_nuevo2: '' })
const passError = ref(''), passOk = ref(false), passLoading = ref(false)

const socio = ref(null)
const socioForm = ref({ nombre: '', telefono: '' })
const socioLoading = ref(false)

const rolBadge = (r) => ({ admin: 'badge-red', bibliotecario: 'badge-blue', socio: 'badge-green' }[r] || 'badge-gray')

onMounted(async () => {
  if (auth.isSocio) {
    try {
      const { data } = await sociosApi.mePerfil()
      socio.value = data
      socioForm.value = { nombre: data.nombre, telefono: data.telefono || '' }
    } catch {}
  }
})

async function cambiarPass() {
  if (passForm.value.password_nuevo !== passForm.value.password_nuevo2) { passError.value = 'Las contraseñas no coinciden'; return }
  passError.value = ''; passOk.value = false; passLoading.value = true
  try {
    await authApi.cambiarPassword({ password_actual: passForm.value.password_actual, password_nuevo: passForm.value.password_nuevo, password_nuevo2: passForm.value.password_nuevo2 })
    passOk.value = true
    passForm.value = { password_actual: '', password_nuevo: '', password_nuevo2: '' }
  } catch (e) { passError.value = e.response?.data?.detail || 'Error al cambiar contraseña' }
  finally { passLoading.value = false }
}

async function actualizarSocio() {
  socioLoading.value = true
  try {
    const { data } = await sociosApi.meActualizar(socioForm.value)
    socio.value = data
    toast.success('Perfil actualizado')
  } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  finally { socioLoading.value = false }
}
</script>

