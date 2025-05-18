<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { format } from 'date-fns'

const router = useRouter()
const events = ref([])
const loading = ref(true)
const error = ref(null)
const isAuthenticated = ref(!!localStorage.getItem('token'))

const formatDate = (dateString) => {
  return format(new Date(dateString), 'MMM d, yyyy h:mm a')
}

const formatCategory = (category) => {
  if (!category) return ''
  return category.replace('_', ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const navigateToEvent = (eventId) => {
  router.push({ name: 'event-details', params: { id: eventId } })
}

onMounted(async () => {
  try {
    // Get upcoming events, limited to 6
    const response = await api.getEvents({ limit: 6 })
    events.value = response.events
  } catch (err) {
    console.error('Error fetching events:', err)
    error.value = 'Failed to load events. Please try again later.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="home">
    <section class="hero">
      <div class="hero-content">
        <h1>Welcome to Community Pulse</h1>
        <p>Discover local events and connect with your community</p>
        <div class="hero-actions">
          <router-link to="/events" class="btn btn-primary">Browse Events</router-link>
          <router-link v-if="!isAuthenticated" to="/register" class="btn btn-secondary">Sign Up</router-link>
          <router-link v-else to="/create-event" class="btn btn-secondary">Create Event</router-link>
        </div>
      </div>
    </section>

    <section class="featured-events">
      <h2>Upcoming Events</h2>
      <div v-if="loading" class="loading">Loading events...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="!events.length" class="no-events">No upcoming events found.</div>
      <div v-else class="events-grid">
        <div v-for="event in events" :key="event.id" class="event-card">
          <div class="event-image" :style="event.image_url ? `background-image: url(${event.image_url})` : ''">
            <div class="event-category">{{ formatCategory(event.category) }}</div>
          </div>
          <div class="event-details">
            <h3 class="event-title">{{ event.title }}</h3>
            <p class="event-date">{{ formatDate(event.date) }}</p>
            <p class="event-location">{{ event.location }}</p>
            <router-link :to="`/events/${event.id}`" class="btn btn-sm">View Details</router-link>
          </div>
        </div>
      </div>
      <div class="view-all">
        <router-link to="/events" class="btn btn-outline">View All Events</router-link>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.hero {
  background-color: #f9f9f9;
  border-radius: 12px;
  padding: 3rem 2rem;
  margin-bottom: 3rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.hero h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  color: #666;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #388E3C;
}

.btn-secondary {
  background-color: #2196F3;
  color: white;
}

.btn-secondary:hover {
  background-color: #1565C0;
}

.btn-outline {
  border: 2px solid #4CAF50;
  color: #4CAF50;
  background: transparent;
}

.btn-outline:hover {
  background-color: #4CAF50;
  color: white;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.featured-events {
  margin-bottom: 3rem;
}

.featured-events h2 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  color: #333;
  text-align: center;
}

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.event-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.event-card:hover {
  transform: translateY(-5px);
}

.event-image {
  height: 160px;
  background-color: #ddd;
  background-size: cover;
  background-position: center;
  position: relative;
}

.event-category {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.event-details {
  padding: 1rem;
  background: white;
}

.event-title {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.event-date, .event-location {
  margin-bottom: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.view-all {
  text-align: center;
  margin-top: 1rem;
}

.loading, .error, .no-events {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #D32F2F;
}
</style>