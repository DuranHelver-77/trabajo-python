import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Adjuntar token en cada petición
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Manejar 401 → intentar renovar token
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) throw new Error('No refresh token')
        const { data } = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refresh })
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        original.headers.Authorization = `Bearer ${data.access_token}`
        return api(original)
      } catch {
        const auth = useAuthStore()
        auth.logout()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export function parseError(e) {
  const detail = e.response?.data?.detail
  if (!detail) return e.message || 'Ocurrió un error inesperado'
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map(err => {
      const campo = err.loc ? err.loc[err.loc.length - 1] : ''
      return `${campo ? campo + ': ' : ''}${err.msg}`
    }).join('. ')
  }
  return JSON.stringify(detail)
}

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (username, password) => {
    const form = new URLSearchParams({ username, password })
    return api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
  },
  registro: (datos) => api.post('/auth/registro', datos),
  me: () => api.get('/auth/me'),
  logout: (refresh_token) => api.post('/auth/logout', { refresh_token }),
  cambiarPassword: (datos) => api.patch('/auth/me/password', datos),
}

// ── Libros ───────────────────────────────────────────────────────────────────
export const librosApi = {
  listar: (params) => api.get('/libros', { params }),
  obtener: (id) => api.get(`/libros/${id}`),
  crear: (datos) => api.post('/libros', datos),
  actualizar: (id, datos) => api.patch(`/libros/${id}`, datos),
  eliminar: (id) => api.delete(`/libros/${id}`),
  subirPortada: (id, file) => {
    const fd = new FormData()
    fd.append('archivo', file)
    return api.post(`/libros/${id}/portada`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  eliminarPortada: (id) => api.delete(`/libros/${id}/portada`),
}

// ── Autores ──────────────────────────────────────────────────────────────────
export const autoresApi = {
  listar: (params) => api.get('/autores/', { params }),
  obtener: (id) => api.get(`/autores/${id}`),
  crear: (datos) => api.post('/autores/', datos),
  actualizar: (id, datos) => api.patch(`/autores/${id}`, datos),
  eliminar: (id) => api.delete(`/autores/${id}`),
}

// ── Categorías ────────────────────────────────────────────────────────────────
export const categoriasApi = {
  listar: (params) => api.get('/categorias/', { params }),
  obtener: (id) => api.get(`/categorias/${id}`),
  crear: (datos) => api.post('/categorias/', datos),
  actualizar: (id, datos) => api.patch(`/categorias/${id}`, datos),
  eliminar: (id) => api.delete(`/categorias/${id}`),
}

// ── Socios ───────────────────────────────────────────────────────────────────
export const sociosApi = {
  listar: (params) => api.get('/socios/', { params }),
  obtener: (id) => api.get(`/socios/${id}`),
  crear: (datos) => api.post('/socios/', datos),
  actualizar: (id, datos) => api.patch(`/socios/${id}`, datos),
  eliminar: (id) => api.delete(`/socios/${id}`),
  mePerfil: () => api.get('/socios/me'),
  meActualizar: (datos) => api.patch('/socios/me', datos),
  mePrestamos: (params) => api.get('/socios/me/prestamos', { params }),
  meMultas: () => api.get('/socios/me/multas'),
  prestamos: (id, params) => api.get(`/socios/${id}/prestamos`, { params }),
}

// ── Préstamos ─────────────────────────────────────────────────────────────────
export const prestamosApi = {
  listar: (params) => api.get('/prestamos/', { params }),
  obtener: (id) => api.get(`/prestamos/${id}`),
  crear: (datos) => api.post('/prestamos/', datos),
  solicitar: (datos) => api.post('/prestamos/solicitar', datos),
  aprobar: (id) => api.post(`/prestamos/${id}/aprobar`),
  rechazar: (id) => api.post(`/prestamos/${id}/rechazar`),
  devolver: (id, datos) => api.post(`/prestamos/${id}/devolucion`, datos),
  pagarMulta: (id) => api.post(`/prestamos/${id}/pago-multa`),
}

// ── Reportes ──────────────────────────────────────────────────────────────────
export const reportesApi = {
  librosMasPrestados: (limite = 10) => api.get('/reportes/libros-mas-prestados', { params: { limite } }),
  categorias: () => api.get('/reportes/categorias'),
  prestamosVencidos: () => api.get('/reportes/prestamos-vencidos'),
  sociosConMultas: () => api.get('/reportes/socios-con-multas'),
  autores: () => api.get('/reportes/autores'),
  resumen: () => api.get('/reportes/resumen'),
}

// ── Usuarios (admin) ──────────────────────────────────────────────────────────
export const usuariosApi = {
  listar: (params) => api.get('/usuarios', { params }),
  crear: (datos) => api.post('/usuarios', datos),
  cambiarRol: (id, rol) => api.patch(`/usuarios/${id}/rol`, { rol }),
  cambiarActivo: (id, activo) => api.patch(`/usuarios/${id}/activo`, { activo }),
}

