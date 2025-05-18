<template>
  <div class="register">
    <div class="register-container">
      <h1>Create an Account</h1>
      <form @submit.prevent="registerUser" class="register-form">
        <div class="form-group">
          <label for="name">Full Name</label>
          <input 
            type="text" 
            id="name" 
            v-model="user.name" 
            required 
            placeholder="Enter your full name"
          >
        </div>
        
        <div class="form-group">
          <label for="email">Email Address</label>
          <input 
            type="email" 
            id="email" 
            v-model="user.email" 
            required 
            placeholder="Enter your email address"
          >
        </div>

        <div class="form-group">
          <label for="phone">Phone Number</label>
          <input 
            type="tel" 
            id="phone" 
            v-model="user.phone" 
            required 
            placeholder="Enter your phone number"
          >
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password" 
            v-model="user.password" 
            required 
            placeholder="Create a password"
            minlength="6"
          >
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input 
            type="password" 
            id="confirmPassword" 
            v-model="confirmPassword" 
            required 
            placeholder="Confirm your password"
            minlength="6"
          >
          <div v-if="passwordMismatch" class="error-message">
            Passwords don't match
          </div>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <button 
          type="submit" 
          class="btn-register" 
          :disabled="loading || passwordMismatch"
        >
          <span v-if="loading">Registering...</span>
          <span v-else>Register</span>
        </button>
      </form>
      
      <div class="login-link">
        Already have an account? <router-link to="/login">Login here</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const user = ref({
  name: '',
  email: '',
  phone: '',
  password: ''
})
const confirmPassword = ref('')
const loading = ref(false)
const error = ref(null)

const passwordMismatch = computed(() => {
  return user.value.password && confirmPassword.value && 
    user.value.password !== confirmPassword.value
})

watch(user, () => {
  error.value = null
})

watch(confirmPassword, () => {
  error.value = null
})

const registerUser = async () => {
  if (passwordMismatch.value) {
    error.value = 'Passwords do not match'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    const response = await api.register(user.value)
    localStorage.setItem('token', response.token)
    localStorage.setItem('user', JSON.stringify(response.user))
    
    router.push('/events')
  } catch (err) {
    console.error('Registration error:', err)
    if (err.response && err.response.data && err.response.data.error) {
      error.value = err.response.data.error
    } else {
      error.value = 'Registration failed. Please try again later.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 100px);
  padding: 2rem;
  background-color: #f9f9f9;
}

.register-container {
  width: 100%;
  max-width: 500px;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  margin-bottom: 1.5rem;
  color: #333;
  text-align: center;
  font-size: 1.8rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}

input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.btn-register {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-register:hover:not(:disabled) {
  background-color: #388E3C;
}

.btn-register:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #D32F2F;
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

.login-link {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.9rem;
  color: #666;
}

.login-link a {
  color: #4CAF50;
  text-decoration: none;
  font-weight: 600;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>