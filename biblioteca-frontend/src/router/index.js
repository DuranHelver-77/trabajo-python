import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/views/HomeView.vue') },
  { path: '/login', name: 'Login', component: () => import('@/views/auth/LoginView.vue'), meta: { guest: true } },
  { path: '/registro', name: 'Registro', component: () => import('@/views/auth/RegistroView.vue'), meta: { guest: true } },
  { path: '/perfil', name: 'Perfil', component: () => import('@/views/auth/PerfilView.vue'), meta: { requiresAuth: true } },

  // Libros (públicos para ver, staff para gestionar)
  { path: '/libros', name: 'Libros', component: () => import('@/views/libros/LibrosView.vue') },
  { path: '/libros/:id', name: 'LibroDetalle', component: () => import('@/views/libros/LibroDetalleView.vue') },

  // Autores (público)
  { path: '/autores', name: 'Autores', component: () => import('@/views/autores/AutoresView.vue') },

  // Área de Socio
  { path: '/mis-prestamos', name: 'MisPrestamos', component: () => import('@/views/socio/MisPrestamosView.vue'), meta: { requiresAuth: true, rol: 'socio' } },
  { path: '/mis-multas', name: 'MisMultas', component: () => import('@/views/socio/MisMultasView.vue'), meta: { requiresAuth: true, rol: 'socio' } },

  // Panel Staff
  { path: '/admin/libros', name: 'AdminLibros', component: () => import('@/views/admin/AdminLibrosView.vue'), meta: { requiresAuth: true, staff: true } },
  { path: '/admin/autores', name: 'AdminAutores', component: () => import('@/views/admin/AdminAutoresView.vue'), meta: { requiresAuth: true, staff: true } },
  { path: '/admin/categorias', name: 'AdminCategorias', component: () => import('@/views/admin/AdminCategoriasView.vue'), meta: { requiresAuth: true, staff: true } },
  { path: '/admin/socios', name: 'AdminSocios', component: () => import('@/views/admin/AdminSociosView.vue'), meta: { requiresAuth: true, staff: true } },
  { path: '/admin/prestamos', name: 'AdminPrestamos', component: () => import('@/views/admin/AdminPrestamosView.vue'), meta: { requiresAuth: true, staff: true } },
  { path: '/admin/reportes', name: 'AdminReportes', component: () => import('@/views/admin/AdminReportesView.vue'), meta: { requiresAuth: true, staff: true } },
  { path: '/admin/usuarios', name: 'AdminUsuarios', component: () => import('@/views/admin/AdminUsuariosView.vue'), meta: { requiresAuth: true, admin: true } },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return next('/login')
  if (to.meta.guest && auth.isLoggedIn) return next('/')
  if (to.meta.staff && !auth.isStaff) return next('/')
  if (to.meta.admin && !auth.isAdmin) return next('/')
  next()
})

export default router

