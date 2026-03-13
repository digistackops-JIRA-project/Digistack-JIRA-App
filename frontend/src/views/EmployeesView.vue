<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Employees</h2>
        <p>{{ totalEmployees }} employee(s) registered</p>
      </div>
      <button class="btn-primary" @click="openModal()">+ Add Employee</button>
    </div>

    <div v-if="loading" class="loading">Loading…</div>

    <div v-else-if="groups.length === 0" class="empty">
      No employees yet. Add your first employee.
    </div>

    <!-- Grouped by Manager -->
    <div v-else>
      <div v-for="group in groups" :key="group.manager_id" class="manager-group">
        <div class="group-header">
          <span class="group-icon">🧑‍💼</span>
          <strong>{{ group.manager_name }}</strong>
          <span class="badge">{{ group.employees.length }} employee(s)</span>
        </div>
        <table class="data-table" v-if="group.employees.length > 0">
          <thead>
            <tr><th>#</th><th>Name</th><th>Email</th><th>Phone</th><th>Team</th><th>Created</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="(e, i) in group.employees" :key="e.id">
              <td>{{ i + 1 }}</td>
              <td><strong>{{ e.name }}</strong></td>
              <td>{{ e.email }}</td>
              <td>{{ e.phone || '—' }}</td>
              <td><span class="badge">{{ e.team_name }}</span></td>
              <td>{{ formatDate(e.created_at) }}</td>
              <td>
                <button class="btn-primary-sm" @click="openModal(e)">Edit</button>
                <button class="btn-danger-sm"  @click="removeEmp(e)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-emp">No employees assigned to this manager yet.</p>
      </div>
    </div>

    <!-- Add / Edit Employee Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h3>{{ editing ? 'Edit Employee' : 'Add Employee' }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <form @submit.prevent="submitForm">
          <div class="field-row">
            <div class="field">
              <label>Name *</label>
              <input v-model="form.name" type="text" placeholder="Full name" required />
            </div>
            <div class="field">
              <label>Phone</label>
              <input v-model="form.phone" type="tel" placeholder="+91-XXXXXXXXXX" />
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label>Email *</label>
              <input v-model="form.email" type="email" required />
            </div>
            <div class="field">
              <label>Password *</label>
              <input v-model="form.password" type="password" placeholder="Min 8 chars, 1 uppercase, 1 number" required />
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label>Team *</label>
              <select v-model="form.team_id" required>
                <option value="" disabled>— Select Team —</option>
                <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.team_name }}</option>
              </select>
            </div>
            <div class="field">
              <label>Manager *</label>
              <select v-model="form.manager_id" required>
                <option value="" disabled>— Select Manager —</option>
                <option v-for="m in managers" :key="m.id" :value="m.id">{{ m.name }}</option>
              </select>
            </div>
          </div>
          <div v-if="errorMsg" class="alert-error">{{ errorMsg }}</div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Saving…' : (editing ? 'Update' : 'Add Employee') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { employeesAPI, teamsAPI, managersAPI } from '@/services/api'

const groups    = ref([])
const teams     = ref([])
const managers  = ref([])
const loading   = ref(true)
const saving    = ref(false)
const showModal = ref(false)
const editing   = ref(null)
const errorMsg  = ref('')

const totalEmployees = computed(() => groups.value.reduce((s, g) => s + g.employees.length, 0))
const form = reactive({ name: '', email: '', password: '', phone: '', team_id: '', manager_id: '' })

async function fetchAll() {
  loading.value = true
  const [g, t, m] = await Promise.all([employeesAPI.byManager(), teamsAPI.list(), managersAPI.list()])
  groups.value   = g.data
  teams.value    = t.data
  managers.value = m.data
  loading.value  = false
}

function openModal(emp = null) {
  editing.value = emp; errorMsg.value = ''
  if (emp) {
    Object.assign(form, { name: emp.name, email: emp.email, password: '', phone: emp.phone || '', team_id: emp.team_id, manager_id: emp.manager_id })
  } else {
    Object.assign(form, { name: '', email: '', password: '', phone: '', team_id: '', manager_id: '' })
  }
  showModal.value = true
}
function closeModal() { showModal.value = false }

async function submitForm() {
  saving.value = true; errorMsg.value = ''
  const payload = { name: form.name, email: form.email, password: form.password, phone: form.phone || null, team_id: form.team_id, manager_id: form.manager_id }
  try {
    editing.value
      ? await employeesAPI.update(editing.value.id, payload)
      : await employeesAPI.create(payload)
    await fetchAll()
    closeModal()
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || 'Operation failed'
  } finally {
    saving.value = false
  }
}

async function removeEmp(e) {
  if (!confirm(`Delete employee "${e.name}"?`)) return
  try { await employeesAPI.remove(e.id); await fetchAll() }
  catch (err) { alert(err.response?.data?.detail || 'Cannot delete') }
}

const formatDate = (d) => new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })

onMounted(fetchAll)
</script>

<style scoped>
@import '@/assets/shared-page.css';
.manager-group { background: #fff; border-radius: var(--radius); margin-bottom: 1.5rem; box-shadow: var(--shadow); overflow: hidden; }
.group-header { padding: 1rem 1.5rem; background: #f8fafc; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: .8rem; }
.group-icon { font-size: 1.3rem; }
.no-emp { padding: 1rem 1.5rem; color: var(--text-muted); font-size: .9rem; }
</style>
