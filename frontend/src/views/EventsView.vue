<template>
  <div class="events-page">
    <header class="events-header">
      <h1>Community Events</h1>
      <div class="filter-controls">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search events..." 
            @input="filterEvents"
          >
        </div>
        <div class="category-filter">
          <select v-model="selectedCategory" @change="filterEvents">
            <option value="">All Categories</option>
            <option value="garage_sale">Garage Sale</option>
            <option value="sports">Sports Match</option>
            <option value="community_class">Community Class</option>
            <option value="volunteer">Volunteer Opportunity</option>
            <option value="exhibition">Exhibition</option>
            <option value="festival">Festival or Celebration</option>
          </select>
        </div>
        <div class="date-filter">
          <select v-model="dateFilter" @change="filterEvents">
            <option value="all">All Dates</option>
            <option value="today">Today</option>
            <option value="tomorrow">Tomorrow</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
        </div>
      </div>
    </header>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading events...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="fetchEvents" class="retry-button">Try Again</button>
    </div>

    <div v-else-if="!filteredEvents.length" class="no-events">
      <p>No events found matching your criteria.</p>
      <button @click="resetFilters" class="reset-button">Reset Filters</button>
    </div>

    <div v-else class="events-grid">
      <div 
        v-for="event in filteredEvents" 
        :key="event.id" 
        class="event-card"
        @click="navigateToEvent(event.id)"
      >
        <div class="event-image" :style="event.image_url ? `background-image: url(${event.image_url})` : ''">
          <div class="event-category">{{ formatCategory(event.category) }}</div>
        </div>
        <div class="event-details">
          <h2 class="event-title">{{ event.title }}</h2>
          <p class="event-date">{{ formatDate(event.date) }}</p>
          <p class="event-location">{{ event.location }}</p>
          <p class="event-description">{{ truncateDescription(event.description) }}</p>
        </div>
      </div>
    </div>

    <div class="create-event-button" v-if="isAuthenticated">
      <router-link to="/create-event" class="create-button">
        <span>+</span> Create Event
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { format, parseISO, isToday, isTomorrow, isThisWeek, isThisMonth } from 'date-fns'
import api from '@/services/api'

const router = useRouter()
const events = ref([])
const filteredEvents = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const selectedCategory = ref('')
const dateFilter = ref('all')
const isAuthenticated = ref(!!localStorage.getItem('token'))

const formatDate = (dateString) => {
  const date = parseISO(dateString)
  return format(date, 'EEEE, MMMM d, yyyy h:mm a')
}

const formatCategory = (category) => {
  if (!category) return ''
  return category.replace('_', ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const truncateDescription = (description, maxLength = 100) => {
  if (!description) return ''
  if (description.length <= maxLength) return description
  return description.substring(0, maxLength) + '...'
}

const navigateToEvent = (eventId) => {
  router.push({ name: 'event-details', params: { id: eventId } })
}

const fetchEvents = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await api.getEvents()
    events.value = response.events || []
    filterEvents()
  } catch (err) {
    console.error('Error fetching events:', err)
    error.value = 'Failed to load events. Please try again later.'
  } finally {
    loading.value = false
  }
}

const filterEvents = () => {
  let filtered = [...events.value]
  
  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(event => 
      event.title.toLowerCase().includes(query) || 
      event.description.toLowerCase().includes(query) ||
      event.location.toLowerCase().includes(query)
    )
  }
  
  // Apply category filter
  if (selectedCategory.value) {
    filtered = filtered.filter(event => event.category === selectedCategory.value)
  }
  
  // Apply date filter
  if (dateFilter.value !== 'all') {
    filtered = filtered.filter(event => {
      const eventDate = parseISO(event.date)
      
      if (dateFilter.value === 'today') {
        return isToday(eventDate)
      } else if (dateFilter.value === 'tomorrow') {
        return isTomorrow(eventDate)
      } else if (dateFilter.value === 'week') {
        return isThisWeek(eventDate)
      } else if (dateFilter.value === 'month') {
        return isThisMonth(eventDate)
      }
      
      return true
    })
  }
  
  filteredEvents.value = filtered
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  dateFilter.value = 'all'
  filterEvents()
}

onMounted(() => {
  fetchEvents()
})
</script>

<style scoped>
.events-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  min-height: calc(100vh - 100px);
}

.events-header {
  margin-bottom: 2rem;
}

.events-header h1 {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  color: #333;
}

.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.search-box {
  flex: 1;
  min-width: 200px;
}

.search-box input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.category-filter, .date-filter {
  min-width: 150px;
}

.category-filter select, .date-filter select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  background-color: white;
}

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.event-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-color: white;
  cursor: pointer;
}

.event-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.event-image {
  height: 180px;
  background-color: #f0f0f0;
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
  padding: 1.5rem;
}

.event-title {
  font-size: 1.4rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.event-date, .event-location {
  margin-bottom: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.event-description {
  color: #777;
  font-size: 0.9rem;
  line-height: 1.4;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 50vh;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container, .no-events {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.retry-button, .reset-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.create-event-button {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
}

.create-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #4CAF50;
  color: white;
  border-radius: 30px;
  text-decoration: none;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.create-button:hover {
  background-color: #388E3C;
  transform: scale(1.05);
}

.create-button span {
  font-size: 1.5rem;
  font-weight: bold;
}

@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
  }
  
  .search-box, .category-filter, .date-filter {
    width: 100%;
  }
  
  .events-grid {
    grid-template-columns: 1fr;
  }
}
</style>