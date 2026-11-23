<template>
  <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2 font-bold text-xl text-blue-600">
          📚 Biblioteca
        </router-link>

        <!-- Nav Links escritorio -->
        <div class="hidden md:flex items-center gap-1">
          <router-link to="/libros" class="nav-link">Libros</router-link>
          <router-link to="/autores" class="nav-link">Autores</router-link>

          <!-- Socio -->
          <template v-if="auth.isSocio">
            <router-link to="/mis-prestamos" class="nav-link">Mis Préstamos</router-link>
            <router-link to="/mis-multas" class="nav-link">Mis Multas</router-link>
          </template>

          <!-- Staff dropdown -->
          <div v-if="auth.isStaff" class="relative group">
            <button class="nav-link flex items-center gap-1">
              Panel Admin <span class="text-xs">▾</span>
            </button>
            <div class="absolute top-full left-0 mt-1 w-48 bg-white border border-gray-200 rounded-xl shadow-lg py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150">
              <router-link to="/admin/libros"      class="dropdown-item">📚 Libros</router-link>
              <router-link to="/admin/autores"     class="dropdown-item">✍️ Autores</router-link>
              <router-link to="/admin/categorias"  class="dropdown-item">🏷️ Categorías</router-link>
              <router-link to="/admin/socios"      class="dropdown-item">👥 Socios</router-link>
              <router-link to="/admin/prestamos"   class="dropdown-item">📋 Préstamos</router-link>
              <router-link to="/admin/reportes"    class="dropdown-item">📊 Reportes</router-link>
              <router-link v-if="auth.isAdmin" to="/admin/usuarios" class="dropdown-item">🔑 Usuarios</router-link>
            </div>
          </div>
        </div>

        <!-- Auth buttons -->
        <div class="flex items-center gap-2">
          <template v-if="!auth.isLoggedIn">
            <router-link to="/login"   class="btn btn-secondary btn-sm">Entrar</router-link>
            <router-link to="/registro" class="btn btn-primary btn-sm">Registrarse</router-link>
          </template>
          <template v-else>
            <router-link to="/perfil" class="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition">
              <span class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm">
                {{ auth.user?.email?.[0]?.toUpperCase() }}
              </span>
              <span class="hidden md:block">{{ auth.user?.email }}</span>
            </router-link>
            <button @click="handleLogout" class="btn btn-secondary btn-sm">Salir</button>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-link      { @apply px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-blue-600 hover:bg-blue-50 transition; }
.dropdown-item { @apply block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition; }
</style>

