import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')

  const isLoggedIn = computed(() => !!accessToken.value && !!user.value)
  const rol = computed(() => user.value?.rol || 'anonimo')
  const isAdmin = computed(() => rol.value === 'admin')
  const isStaff = computed(() => rol.value === 'admin' || rol.value === 'bibliotecario')
  const isSocio = computed(() => rol.value === 'socio')

  async function login(email, password) {
    const { data } = await authApi.login(email, password)
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    await fetchMe()
  }

  async function fetchMe() {
    const { data } = await authApi.me()
    user.value = data
    localStorage.setItem('user', JSON.stringify(data))
  }

  async function logout() {
    try {
      if (refreshToken.value) await authApi.logout(refreshToken.value)
    } catch {}
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  async function register(datos) {
    const { data } = await authApi.registro(datos)
    return data
  }

  return { user, isLoggedIn, rol, isAdmin, isStaff, isSocio, login, logout, register, fetchMe }
})

