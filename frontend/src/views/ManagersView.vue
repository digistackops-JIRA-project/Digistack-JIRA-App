<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Managers</h2>
        <p>{{ managers.length }} manager(s) registered</p>
      </div>
      <button class="btn-primary" @click="openModal()">+ Add Manager</button>
    </div>

    <div v-if="loading" class="loading">Loading…</div>

    <div v-else-if="managers.length === 0" class="empty">
      No managers yet. Add your first manager.
    </div>

    <table v-else class="data-table">
      <thead>
        <tr><th>#</th><th>Name</th><th>Email</th><th>Phone</th><th>Team</th><th>Created</th><th>Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="(m, i) in managers" :key="m.id">
          <td>{{ i + 1 }}</td>
          <td><strong>{{ m.name }}</strong></td>
          <td>{{ m.email }}</td>
          <td>{{ m.phone || '—' }}</td>
          <td><span class="badge">{{ m.team_name }}</span></td>
          <td>{{ formatDate(m.created_at) }}</td>
          <td>
            <button class="btn-primary-sm" @click="openModal(m)">Edit</button>
            <button class="btn-danger-sm"  @click="removeMgr(m)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Add / Edit Manager Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editing ? 'Edit Manager' : 'Add Manager' }}</h3>
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
              <input v-model="form.email" type="email" placeholder="manager@company.com" required />
            </div>
            <div class="field">
              <label>Password *</label>
              <input v-model="form.password" type="password" placeholder="Min 8 chars, 1 uppercase, 1 number" required />
            </div>
          </div>
          <div class="field">
            <label>Team *</label>
            <select v-model="form.team_id" required>
              <option value="" disabled>— Select a team —</option>
              <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.team_name }}</option>
            </select>
          </div>
          <div v-if="errorMsg" class="alert-error">{{ errorMsg }}</div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Saving…' : (editing ? 'Update' : 'Add Manager') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { managersAPI, teamsAPI } from '@/services/api'

const managers  = ref([])
const teams     = ref([])
const loading   = ref(true)
const saving    = ref(false)
const showModal = ref(false)
const editing   = ref(null)   // manager object when editing
const errorMsg  = ref('')

const form = reactive({ name: '', email: '', password: '', phone: '', team_id: '' })

async function fetchAll() {
  loading.value = true
  const [m, t] = await Promise.all([managersAPI.list(), teamsAPI.list()])
  managers.value = m.data
  teams.value    = t.data
  loading.value  = false
}

function openModal(mgr = null) {
  editing.value = mgr
  errorMsg.value = ''
  if (mgr) {
    Object.assign(form, { name: mgr.name, email: mgr.email, password: '', phone: mgr.phone || '', team_id: mgr.team_id })
  } else {
    Object.assign(form, { name: '', email: '', password: '', phone: '', team_id: '' })
  }
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function submitForm() {
  saving.value = true; errorMsg.value = ''
  const payload = { name: form.name, email: form.email, password: form.password, phone: form.phone || null, team_id: form.team_id }
  try {
    editing.value
      ? await managersAPI.update(editing.value.id, payload)
      : await managersAPI.create(payload)
    await fetchAll()
    closeModal()
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || 'Operation failed'
  } finally {
    saving.value = false
  }
}

async function removeMgr(m) {
  if (!confirm(`Delete manager "${m.name}"?`)) return
  try {
    await managersAPI.remove(m.id)
    await fetchAll()
  } catch (err) {
    alert(err.response?.data?.detail || 'Cannot delete manager')
  }
}

const formatDate = (d) => new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })

onMounted(fetchAll)
</script>

<style scoped>
@import '@/assets/shared-page.css';
</style>
