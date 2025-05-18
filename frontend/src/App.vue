<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from './services/api'

const router = useRouter()
const isAuthenticated = ref(false)
const user = ref(null)

const isAdmin = computed(() => {
  return user.value && user.value.is_admin
})

onMounted(async () => {
  checkAuth()
})

const checkAuth = async () => {
  const token = localStorage.getItem('token')
  if (token) {
    isAuthenticated.value = true
    try {
      // Fetch current user data
      const userData = await api.getProfile()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (error) {
      console.error('Error fetching user profile:', error)
      logout()
    }
  }
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  isAuthenticated.value = false
  user.value = null
  router.push('/login')
}
</script>

<template>
  <div class="app-container">
    <header class="header">
      <div class="logo">
        <router-link to="/">Community Pulse</router-link>
      </div>
      
      <nav class="nav">
        <router-link to="/">Home</router-link>
        <router-link to="/events">Browse Events</router-link>
        
        <template v-if="isAuthenticated">
          <router-link to="/create-event">Create Event</router-link>
          <router-link to="/my-events">My Events</router-link>
          <router-link to="/my-interests">My Interests</router-link>
          <router-link to="/profile">Profile</router-link>
          <router-link v-if="isAdmin" to="/admin">Admin Dashboard</router-link>
          <a href="#" @click.prevent="logout" class="logout-btn">Logout</a>
        </template>
        
        <template v-else>
          <router-link to="/login">Login</router-link>
          <router-link to="/register">Register</router-link>
        </template>
      </nav>
    </header>
    
    <main class="main-content">
      <router-view />
    </main>
    
    <footer class="footer">
      <div class="container">
        <p>&copy; {{ new Date().getFullYear() }} Community Pulse - Connect with your local community</p>
      </div>
    </footer>
  </div>
</template>

<style>
:root {
  --primary-color: #4a6fa5;
  --secondary-color: #f7c331;
  --accent-color: #e8871e;
  --text-color: #333;
  --bg-color: #f8f9fa;
  --light-gray: #e9ecef;
  --dark-gray: #6c757d;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: var(--text-color);
  background-color: var(--bg-color);
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  background-color: var(--primary-color);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo a {
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
}

.nav {
  display: flex;
  gap: 1.5rem;
}

.nav a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 0;
  transition: color 0.3s;
}

.nav a:hover,
.nav a.router-link-active {
  color: var(--secondary-color);
}

.logout-btn {
  cursor: pointer;
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.footer {
  background-color: var(--primary-color);
  color: white;
  text-align: center;
  padding: 1.5rem;
  margin-top: auto;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

/* Common UI Components */
.btn {
  display: inline-block;
  background-color: var(--primary-color);
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #3a5a8c;
}

.btn-secondary {
  background-color: var(--secondary-color);
  color: var(--text-color);
}

.btn-secondary:hover {
  background-color: #e8b429;
}

.btn-danger {
  background-color: #dc3545;
}

.btn-danger:hover {
  background-color: #c82333;
}

.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid var(--light-gray);
  border-radius: 4px;
}

.alert {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
}

/* Responsive styles */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    padding: 1rem;
  }
  
  .logo {
    margin-bottom: 1rem;
  }
  
  .nav {
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
  }
  
  .main-content {
    padding: 1rem;
  }
}
</style>
