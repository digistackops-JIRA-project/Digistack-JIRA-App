<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Teams</h2>
        <p>{{ teams.length }} team(s) registered</p>
      </div>
      <button class="btn-primary" @click="openModal">+ Create Team</button>
    </div>

    <div v-if="loading" class="loading">Loading…</div>

    <div v-else-if="teams.length === 0" class="empty">
      No teams yet. Create your first team.
    </div>

    <table v-else class="data-table">
      <thead>
        <tr><th>#</th><th>Team Name</th><th>Created At</th><th>Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="(t, i) in teams" :key="t.id">
          <td>{{ i + 1 }}</td>
          <td><strong>{{ t.team_name }}</strong></td>
          <td>{{ formatDate(t.created_at) }}</td>
          <td>
            <button class="btn-danger-sm" @click="removeTeam(t)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Create Team Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Create Team</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <form @submit.prevent="submitCreate">
          <div class="field">
            <label>Team Name *</label>
            <input v-model="form.team_name" type="text" placeholder="e.g. Backend Engineering" required />
          </div>
          <div v-if="errorMsg" class="alert-error">{{ errorMsg }}</div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Saving…' : 'Create Team' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { teamsAPI } from '@/services/api'

const teams     = ref([])
const loading   = ref(true)
const saving    = ref(false)
const showModal = ref(false)
const errorMsg  = ref('')
const form      = reactive({ team_name: '' })

async function fetchTeams() {
  loading.value = true
  const { data } = await teamsAPI.list()
  teams.value = data
  loading.value = false
}

function openModal()  { form.team_name = ''; errorMsg.value = ''; showModal.value = true }
function closeModal() { showModal.value = false }

async function submitCreate() {
  saving.value = true; errorMsg.value = ''
  try {
    await teamsAPI.create({ team_name: form.team_name })
    await fetchTeams()
    closeModal()
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || 'Failed to create team'
  } finally {
    saving.value = false
  }
}

async function removeTeam(t) {
  if (!confirm(`Delete team "${t.team_name}"?`)) return
  try {
    await teamsAPI.remove(t.id)
    await fetchTeams()
  } catch (err) {
    alert(err.response?.data?.detail || 'Cannot delete team')
  }
}

const formatDate = (d) => new Date(d).toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })

onMounted(fetchTeams)
</script>

<style scoped>
@import '@/assets/shared-page.css';
</style>
