/**
 * Frontend Unit Tests — Vitest + @vue/test-utils
 * Run: npm run test:unit
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

// ─── Mock vue-router ──────────────────────────────────────────────────────────
vi.mock('vue-router', () => ({
  useRouter:       () => ({ push: vi.fn() }),
  useRoute:        () => ({ path: '/' }),
  createRouter:    () => ({ beforeEach: vi.fn(), push: vi.fn() }),
  createWebHistory: vi.fn(),
  RouterLink:      { template: '<a><slot /></a>' },
  RouterView:      { template: '<div />' },
}))

// ─── Mock API services ────────────────────────────────────────────────────────
vi.mock('@/services/api', () => ({
  authAPI:     { login: vi.fn() },
  teamsAPI:    { list: vi.fn(() => Promise.resolve({ data: [] })), create: vi.fn(), remove: vi.fn() },
  managersAPI: { list: vi.fn(() => Promise.resolve({ data: [] })), create: vi.fn(), update: vi.fn(), remove: vi.fn() },
  employeesAPI:{ list: vi.fn(() => Promise.resolve({ data: [] })), byManager: vi.fn(() => Promise.resolve({ data: [] })), create: vi.fn(), update: vi.fn(), remove: vi.fn() },
  default:     {},
}))

import LoginView    from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import TeamsView    from '@/views/TeamsView.vue'
import ManagersView from '@/views/ManagersView.vue'
import EmployeesView from '@/views/EmployeesView.vue'
import { useAuthStore } from '@/store/auth'
import { authAPI }      from '@/services/api'

// ─── Auth Store ───────────────────────────────────────────────────────────────
describe('Auth Store', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('starts with no token', () => {
    const store = useAuthStore()
    expect(store.token).toBeNull()
    expect(store.isLoggedIn).toBe(false)
  })

  it('sets token after successful login', async () => {
    authAPI.login.mockResolvedValueOnce({ data: { access_token: 'tok123', expires_in: 3600 } })
    const store = useAuthStore()
    const ok = await store.login('admin@sapsecops.in', 'Admin123')
    expect(ok).toBe(true)
    expect(store.isLoggedIn).toBe(true)
    expect(store.token).toBe('tok123')
  })

  it('sets error on failed login', async () => {
    authAPI.login.mockRejectedValueOnce({ response: { data: { detail: 'Invalid credentials' } } })
    const store = useAuthStore()
    const ok = await store.login('bad@email.com', 'wrong')
    expect(ok).toBe(false)
    expect(store.error).toBe('Invalid credentials')
  })

  it('clears state on logout', async () => {
    authAPI.login.mockResolvedValueOnce({ data: { access_token: 'tok', expires_in: 3600 } })
    const store = useAuthStore()
    await store.login('admin@sapsecops.in', 'Admin123')
    store.logout()
    expect(store.isLoggedIn).toBe(false)
    expect(store.token).toBeNull()
  })
})

// ─── LoginView ────────────────────────────────────────────────────────────────
describe('LoginView', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders email and password fields', () => {
    const w = mount(LoginView, { global: { plugins: [createPinia()] } })
    expect(w.find('input[type="email"]').exists()).toBe(true)
    expect(w.find('input[type="password"]').exists()).toBe(true)
  })

  it('renders sign-in button', () => {
    const w = mount(LoginView, { global: { plugins: [createPinia()] } })
    expect(w.find('button[type="submit"]').text()).toContain('Sign In')
  })

  it('shows error message when auth.error is set', async () => {
    const pinia = createPinia()
    const w     = mount(LoginView, { global: { plugins: [pinia] } })
    const store = useAuthStore()
    store.error = 'Invalid email or password'
    await w.vm.$nextTick()
    expect(w.find('.alert-error').text()).toContain('Invalid email or password')
  })
})

// ─── TeamsView ────────────────────────────────────────────────────────────────
describe('TeamsView', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders Create Team button', async () => {
    const w = mount(TeamsView, { global: { plugins: [createPinia()] } })
    await w.vm.$nextTick()
    expect(w.find('.btn-primary').text()).toContain('Create Team')
  })

  it('opens modal on button click', async () => {
    const w = mount(TeamsView, { global: { plugins: [createPinia()] } })
    await w.vm.$nextTick()
    await w.find('.btn-primary').trigger('click')
    expect(w.find('.modal').exists()).toBe(true)
  })

  it('shows empty state when no teams', async () => {
    const { teamsAPI } = await import('@/services/api')
    teamsAPI.list.mockResolvedValueOnce({ data: [] })
    const w = mount(TeamsView, { global: { plugins: [createPinia()] } })
    await new Promise(r => setTimeout(r, 20))
    await w.vm.$nextTick()
    expect(w.find('.empty').exists()).toBe(true)
  })
})

// ─── ManagersView ─────────────────────────────────────────────────────────────
describe('ManagersView', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders Add Manager button', async () => {
    const w = mount(ManagersView, { global: { plugins: [createPinia()] } })
    await w.vm.$nextTick()
    expect(w.find('.btn-primary').text()).toContain('Add Manager')
  })
})

// ─── EmployeesView ────────────────────────────────────────────────────────────
describe('EmployeesView', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  it('renders Add Employee button', async () => {
    const w = mount(EmployeesView, { global: { plugins: [createPinia()] } })
    await w.vm.$nextTick()
    expect(w.find('.btn-primary').text()).toContain('Add Employee')
  })
})
