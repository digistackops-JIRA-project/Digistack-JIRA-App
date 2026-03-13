import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  { path: '/',          redirect: '/dashboard' },
  { path: '/login',     component: () => import('@/views/LoginView.vue'),      meta: { public: true } },
  { path: '/dashboard', component: () => import('@/views/DashboardView.vue'),  meta: { requiresAuth: true } },
  { path: '/teams',     component: () => import('@/views/TeamsView.vue'),      meta: { requiresAuth: true } },
  { path: '/managers',  component: () => import('@/views/ManagersView.vue'),   meta: { requiresAuth: true } },
  { path: '/employees', component: () => import('@/views/EmployeesView.vue'),  meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return '/login'
  if (to.path === '/login' && auth.isLoggedIn) return '/dashboard'
})

export default router
