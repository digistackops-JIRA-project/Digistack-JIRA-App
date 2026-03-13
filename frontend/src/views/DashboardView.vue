<template>
  <div class="dashboard">
    <header class="page-header">
      <h2>Admin Dashboard</h2>
      <p>Welcome back, <strong>{{ auth.email }}</strong></p>
    </header>

    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-icon">👥</span>
        <div>
          <div class="stat-value">{{ stats.teams }}</div>
          <div class="stat-label">Teams</div>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">🧑‍💼</span>
        <div>
          <div class="stat-value">{{ stats.managers }}</div>
          <div class="stat-label">Managers</div>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">👤</span>
        <div>
          <div class="stat-value">{{ stats.employees }}</div>
          <div class="stat-label">Employees</div>
        </div>
      </div>
    </div>

    <div class="actions-grid">
      <div class="action-card" @click="router.push('/teams')">
        <span class="action-icon">👥</span>
        <h3>Create Team</h3>
        <p>Manage organisation teams</p>
        <span class="action-arrow">→</span>
      </div>
      <div class="action-card" @click="router.push('/managers')">
        <span class="action-icon">🧑‍💼</span>
        <h3>Add Manager</h3>
        <p>Assign managers to teams</p>
        <span class="action-arrow">→</span>
      </div>
      <div class="action-card" @click="router.push('/employees')">
        <span class="action-icon">👤</span>
        <h3>Add Employee</h3>
        <p>Onboard employees under managers</p>
        <span class="action-arrow">→</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { teamsAPI, managersAPI, employeesAPI } from '@/services/api'

const auth   = useAuthStore()
const router = useRouter()
const stats  = reactive({ teams: 0, managers: 0, employees: 0 })

onMounted(async () => {
  try {
    const [t, m, e] = await Promise.all([teamsAPI.list(), managersAPI.list(), employeesAPI.list()])
    stats.teams     = t.data.length
    stats.managers  = m.data.length
    stats.employees = e.data.length
  } catch { /* non-critical */ }
})
</script>

<style scoped>
.dashboard { max-width: 900px; }
.page-header { margin-bottom: 2rem; }
.page-header h2 { font-size: 1.6rem; color: #1e1b4b; }
.page-header p  { color: var(--text-muted); margin-top: .3rem; }
.stats-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; margin-bottom: 2rem; }
.stat-card { background: #fff; border-radius: var(--radius); padding: 1.2rem 1.5rem; display: flex; align-items: center; gap: 1rem; box-shadow: var(--shadow); }
.stat-icon { font-size: 2rem; }
.stat-value { font-size: 1.8rem; font-weight: 700; color: #1e1b4b; }
.stat-label { font-size: .8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .05em; }
.actions-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 1.2rem; }
.action-card {
  background: #fff; border-radius: 10px; padding: 1.8rem 1.5rem;
  cursor: pointer; box-shadow: var(--shadow); border: 2px solid transparent;
  transition: border-color .2s, transform .15s; position: relative;
}
.action-card:hover { border-color: var(--primary); transform: translateY(-3px); }
.action-icon { font-size: 2.5rem; }
.action-card h3 { margin: .8rem 0 .4rem; font-size: 1.05rem; color: #1e1b4b; }
.action-card p  { font-size: .85rem; color: var(--text-muted); }
.action-arrow { position: absolute; top: 1.2rem; right: 1.2rem; font-size: 1.2rem; color: var(--primary); opacity: 0; transition: opacity .2s; }
.action-card:hover .action-arrow { opacity: 1; }
</style>
