<template>
  <div id="app">
    <!-- Sidebar nav shown only when logged in -->
    <aside v-if="auth.isLoggedIn" class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">🎫</span>
        <span>SapSecOps</span>
      </div>
      <nav>
        <router-link to="/dashboard">🏠 Dashboard</router-link>
        <router-link to="/teams">👥 Teams</router-link>
        <router-link to="/managers">🧑‍💼 Managers</router-link>
        <router-link to="/employees">👤 Employees</router-link>
      </nav>
      <div class="sidebar-footer">
        <span class="user-email">{{ auth.email }}</span>
        <button class="btn-logout" @click="logout">Logout</button>
      </div>
    </aside>

    <main :class="auth.isLoggedIn ? 'content-with-sidebar' : 'content-full'">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'

const auth   = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
#app { display: flex; min-height: 100vh; }
.sidebar {
  width: 220px; background: #1e1b4b; color: #c7d2fe;
  display: flex; flex-direction: column; padding: 1.5rem 0;
  position: fixed; top: 0; left: 0; bottom: 0; z-index: 100;
}
.sidebar-brand { display: flex; align-items: center; gap: .6rem; padding: 0 1.2rem 1.5rem; font-size: 1.1rem; font-weight: 700; color: #fff; }
.brand-icon { font-size: 1.5rem; }
nav { display: flex; flex-direction: column; flex: 1; }
nav a { padding: .75rem 1.2rem; color: #a5b4fc; font-size: .92rem; transition: background .2s; }
nav a:hover, nav a.router-link-active { background: #312e81; color: #fff; }
.sidebar-footer { padding: 1rem 1.2rem; border-top: 1px solid #312e81; }
.user-email { display: block; font-size: .78rem; color: #818cf8; margin-bottom: .5rem; overflow: hidden; text-overflow: ellipsis; }
.btn-logout { width: 100%; padding: .5rem; background: #dc2626; color: #fff; border: none; border-radius: var(--radius); font-size: .85rem; }
.content-with-sidebar { margin-left: 220px; flex: 1; padding: 2rem; }
.content-full { flex: 1; }
</style>
