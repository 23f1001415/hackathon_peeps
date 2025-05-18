import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add authentication token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor to handle errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default {
  // Auth services
  async login(credentials) {
    const response = await api.post('/auth/login', credentials)
    return response.data
  },
  
  async register(userData) {
    const response = await api.post('/auth/register', userData)
    return response.data
  },
  
  async getProfile() {
    const response = await api.get('/auth/profile')
    return response.data
  },
  
  async updateProfile(userData) {
    const response = await api.put('/auth/profile', userData)
    return response.data
  },
  
  // Event services
  async getEvents(params = {}) {
    const response = await api.get('/events', { params })
    return response.data
  },
  
  async getEvent(id) {
    const response = await api.get(`/events/${id}`)
    return response.data
  },
  
  async createEvent(eventData) {
    const response = await api.post('/events', eventData)
    return response.data
  },
  
  async updateEvent(id, eventData) {
    const response = await api.put(`/events/${id}`, eventData)
    return response.data
  },
  
  async deleteEvent(id) {
    const response = await api.delete(`/events/${id}`)
    return response.data
  },
  
  async getUserEvents() {
    const response = await api.get('/events/my-events')
    return response.data
  },
  
  // Interest services
  async registerInterest(eventId, interestData) {
    const response = await api.post(`/interests/${eventId}`, interestData)
    return response.data
  },
  
  async getUserInterests() {
    const response = await api.get('/interests/my-interests')
    return response.data
  },
  
  async getEventInterests(eventId) {
    const response = await api.get(`/interests/${eventId}`)
    return response.data
  },
  
  async cancelInterest(interestId) {
    const response = await api.delete(`/interests/${interestId}`)
    return response.data
  },
  
  // Admin services
  async getPendingEvents() {
    const response = await api.get('/admin/events/pending')
    return response.data
  },
  
  async getFlaggedEvents() {
    const response = await api.get('/admin/events/flagged')
    return response.data
  },
  
  async approveEvent(id) {
    const response = await api.patch(`/admin/events/${id}/approve`)
    return response.data
  },
  
  async rejectEvent(id) {
    const response = await api.patch(`/admin/events/${id}/reject`)
    return response.data
  },
  
  async flagEvent(id) {
    const response = await api.patch(`/admin/events/${id}/flag`)
    return response.data
  },
  
  async getUsers() {
    const response = await api.get('/admin/users')
    return response.data
  },
  
  async getUserEventHistory(userId) {
    const response = await api.get(`/admin/users/${userId}/events`)
    return response.data
  },
  
  async verifyUser(userId) {
    const response = await api.patch(`/admin/users/${userId}/verify`)
    return response.data
  },
  
  async banUser(userId) {
    const response = await api.patch(`/admin/users/${userId}/ban`)
    return response.data
  },
  
  async unbanUser(userId) {
    const response = await api.patch(`/admin/users/${userId}/unban`)
    return response.data
  },
  
  async getEventAnalytics() {
    const response = await api.get('/admin/analytics/events')
    return response.data
  },
  
  async getUserAnalytics() {
    const response = await api.get('/admin/analytics/users')
    return response.data
  }
}