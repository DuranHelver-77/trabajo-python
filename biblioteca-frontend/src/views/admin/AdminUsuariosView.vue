<template>
  <div class="max-w-6xl mx-auto px-4 py-10">
    <PageHeader title="Gestión de Usuarios" subtitle="Administra roles y accesos del sistema">
      <template #actions><button @click="abrirCrear" class="btn btn-primary">+ Crear staff</button></template>
    </PageHeader>
    <div class="card mb-6 flex gap-3">
      <select v-model="filtroRol" @change="cargar()" class="input-field max-w-xs">
        <option value="">Todos los roles</option>
        <option value="admin">Admin</option><option value="bibliotecario">Bibliotecario</option><option value="socio">Socio</option>
      </select>
      <select v-model="filtroActivo" @change="cargar()" class="input-field max-w-xs">
        <option value="">Todos</option><option :value="true">Activos</option><option :value="false">Inactivos</option>
      </select>
    </div>

    <LoadingSpinner v-if="loading" />
    <div v-else class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
      <table class="w-full">
        <thead class="bg-gray-50"><tr>
          <th class="table-head">Email</th><th class="table-head">Rol</th><th class="table-head">Estado</th><th class="table-head">Acciones</th>
        </tr></thead>
        <tbody>
          <tr v-for="u in usuarios" :key="u.id" class="table-row">
            <td class="table-cell font-medium">{{ u.email }}</td>
            <td class="table-cell"><span :class="rolBadge(u.rol)">{{ u.rol }}</span></td>
            <td class="table-cell"><span :class="u.activo ? 'badge-green' : 'badge-red'">{{ u.activo ? 'Activo' : 'Inactivo' }}</span></td>
            <td class="table-cell">
              <div class="flex gap-2" v-if="u.id !== auth.user?.id">
                <button @click="abrirCambiarRol(u)" class="btn btn-secondary btn-sm">🔑 Rol</button>
                <button @click="toggleActivo(u)" class="btn btn-sm" :class="u.activo ? 'btn-danger' : 'btn-success'">
                  {{ u.activo ? 'Desactivar' : 'Activar' }}
                </button>
              </div>
              <span v-else class="text-xs text-gray-400">Tu cuenta</span>
            </td>
          </tr>
          <tr v-if="!usuarios.length"><td colspan="4"><EmptyState icon="👤" message="No hay usuarios" /></td></tr>
        </tbody>
      </table>
    </div>
    <Pagination :page="page" :limit="limit" :total="total" :skip="skip" @change="cambiarPagina" />

    <!-- Modal crear staff -->
    <ModalBase v-if="modal" title="Crear usuario staff" @close="modal = false">
      <form @submit.prevent="guardar" class="space-y-4">
        <div class="form-group"><label class="label-field">Nombre *</label><input v-model="form.nombre" type="text" class="input-field" placeholder="Nombre completo" required></div>
        <div class="form-group"><label class="label-field">Email *</label><input v-model="form.email" type="email" class="input-field" required></div>
        <div class="form-group"><label class="label-field">Contraseña *</label><input v-model="form.password" type="password" class="input-field" required></div>
        <div class="form-group">
          <label class="label-field">Rol *</label>
          <select v-model="form.rol" class="input-field" required>
            <option value="bibliotecario">Bibliotecario</option><option value="admin">Admin</option>
          </select>
        </div>
        <div v-if="formError" class="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm border border-red-200">{{ formError }}</div>
        <div class="flex gap-3 justify-end">
          <button type="button" @click="modal = false" class="btn btn-secondary">Cancelar</button>
          <button type="submit" :disabled="formLoading" class="btn btn-primary">{{ formLoading ? 'Creando…' : 'Crear' }}</button>
        </div>
      </form>
    </ModalBase>

    <!-- Modal cambiar rol -->
    <ModalBase v-if="modalRol" title="Cambiar rol" @close="modalRol = false">
      <div class="mb-4 p-4 bg-blue-50 rounded-xl text-blue-900 font-medium text-sm">{{ usuarioRol?.email }}</div>
      <div class="form-group">
        <label class="label-field">Nuevo rol</label>
        <select v-model="nuevoRol" class="input-field">
          <option value="socio">Socio</option><option value="bibliotecario">Bibliotecario</option><option value="admin">Admin</option>
        </select>
      </div>
      <div class="flex gap-3 justify-end mt-4">
        <button @click="modalRol = false" class="btn btn-secondary">Cancelar</button>
        <button @click="confirmarRol" :disabled="formLoading" class="btn btn-primary">{{ formLoading ? 'Cambiando…' : 'Confirmar' }}</button>
      </div>
    </ModalBase>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usuariosApi, parseError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import PageHeader from '@/components/PageHeader.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import EmptyState from '@/components/EmptyState.vue'
import Pagination from '@/components/Pagination.vue'
import ModalBase from '@/components/ModalBase.vue'

const auth = useAuthStore(); const toast = useToastStore()
const usuarios = ref([]), loading = ref(true), total = ref(0), page = ref(1), limit = 20, skip = ref(0)
const filtroRol = ref(''), filtroActivo = ref('')
const modal = ref(false), form = ref({ email: '', nombre: '', password: '', rol: 'bibliotecario' }), formError = ref(''), formLoading = ref(false)
const modalRol = ref(false), usuarioRol = ref(null), nuevoRol = ref('')

const rolBadge = (r) => ({ admin: 'badge-red', bibliotecario: 'badge-blue', socio: 'badge-green' }[r] || 'badge-gray')

async function cargar() {
  loading.value = true
  try {
    const params = { skip: skip.value, limit }
    if (filtroRol.value) params.rol = filtroRol.value
    if (filtroActivo.value !== '') params.activo = filtroActivo.value
    const { data } = await usuariosApi.listar(params); usuarios.value = data.items; total.value = data.total
  } finally { loading.value = false }
}
function cambiarPagina(p) { page.value = p; skip.value = (p-1)*limit; cargar() }
function abrirCrear() { form.value = { email: '', nombre: '', password: '', rol: 'bibliotecario' }; formError.value = ''; modal.value = true }
function abrirCambiarRol(u) { usuarioRol.value = u; nuevoRol.value = u.rol; modalRol.value = true }

async function guardar() {
  formError.value = ''; formLoading.value = true
  try { await usuariosApi.crear(form.value); toast.success('Usuario creado'); modal.value = false; cargar() }
  catch (e) { formError.value = parseError(e) }
  finally { formLoading.value = false }
}
async function confirmarRol() {
  formLoading.value = true
  try { await usuariosApi.cambiarRol(usuarioRol.value.id, nuevoRol.value); toast.success('Rol actualizado'); modalRol.value = false; cargar() }
  catch (e) { toast.error(e.response?.data?.detail || 'Error') }
  finally { formLoading.value = false }
}
async function toggleActivo(u) {
  try { await usuariosApi.cambiarActivo(u.id, !u.activo); toast.success(`Usuario ${u.activo ? 'desactivado' : 'activado'}`); cargar() }
  catch (e) { toast.error(e.response?.data?.detail || 'Error') }
}
onMounted(cargar)
</script>

