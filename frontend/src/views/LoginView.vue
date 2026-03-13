<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <span class="logo">🎫</span>
        <h1>SapSecOps Admin</h1>
        <p>Sign in to the Admin Portal</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="field">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="admin@sapsecops.in"
            autocomplete="username"
            required
          />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <div v-if="auth.error" class="alert-error">{{ auth.error }}</div>

        <button type="submit" class="btn-primary" :disabled="auth.loading">
          {{ auth.loading ? 'Signing in…' : 'Sign In' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const auth   = useAuthStore()
const router = useRouter()
const form   = reactive({ email: '', password: '' })

async function handleLogin() {
  const ok = await auth.login(form.email, form.password)
  if (ok) router.push('/dashboard')
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: grid; place-items: center; background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); }
.login-card { background: #fff; border-radius: 12px; padding: 2.5rem; width: 100%; max-width: 400px; box-shadow: 0 20px 60px rgba(0,0,0,.3); }
.login-header { text-align: center; margin-bottom: 2rem; }
.logo { font-size: 3rem; }
h1 { margin: .5rem 0 .3rem; font-size: 1.4rem; color: #1e1b4b; }
p { color: var(--text-muted); font-size: .9rem; }
.field { margin-bottom: 1.2rem; }
label { display: block; margin-bottom: .4rem; font-size: .85rem; font-weight: 600; color: #374151; }
input { width: 100%; padding: .65rem .9rem; border: 1px solid var(--border); border-radius: var(--radius); font-size: .95rem; transition: border-color .2s; }
input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(79,70,229,.15); }
.btn-primary { width: 100%; padding: .75rem; background: var(--primary); color: #fff; border: none; border-radius: var(--radius); font-size: 1rem; font-weight: 600; margin-top: .5rem; transition: background .2s; }
.btn-primary:hover:not(:disabled) { background: var(--primary-dark); }
.btn-primary:disabled { opacity: .6; cursor: not-allowed; }
.alert-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; border-radius: var(--radius); padding: .6rem .9rem; margin-bottom: 1rem; font-size: .88rem; }
</style>
