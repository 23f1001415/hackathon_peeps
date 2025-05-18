import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/events',
      name: 'events',
      component: () => import('../views/EventsView.vue')
    },
    {
      path: '/events/:id',
      name: 'event-details',
      component: () => import('../views/EventDetailsView.vue'),
      props: true
    },
    {
      path: '/create-event',
      name: 'create-event',
      component: () => import('../views/CreateEventView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/edit-event/:id',
      name: 'edit-event',
      component: () => import('../views/EditEventView.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/my-events',
      name: 'my-events',
      component: () => import('../views/MyEventsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/my-interests',
      name: 'my-interests',
      component: () => import('../views/MyInterestsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/AdminDashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: 'pending-events',
          name: 'admin-pending-events',
          component: () => import('../views/admin/PendingEventsView.vue')
        },
        {
          path: 'flagged-events',
          name: 'admin-flagged-events',
          component: () => import('../views/admin/FlaggedEventsView.vue')
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('../views/admin/UserManagementView.vue')
        },
        {
          path: 'analytics',
          name: 'admin-analytics',
          component: () => import('../views/admin/AnalyticsView.vue')
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue')
    }
  ]
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token')
  const userData = JSON.parse(localStorage.getItem('user') || '{}')
  const isAdmin = userData.is_admin
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAdmin && !isAdmin) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router