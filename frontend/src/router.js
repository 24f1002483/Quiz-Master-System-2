// router.js - Vue 3 compatible

import { createRouter, createWebHistory } from 'vue-router'
import Welcome from './components/Welcome.vue'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import AdminLayout from './components/AdminLayout.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import ExportDashboard from './components/ExportDashboard.vue'
import SubjectManagement from './components/SubjectManagement.vue'
import ChapterManagement from './components/ChapterManagement.vue'
import QuizManagement from './components/QuizManagement.vue'
import QuestionManagement from './components/QuestionManagement.vue'
import UserManagement from './components/UserManagement.vue'
import UserDashboard from './components/UserDashboard.vue'
import UserSummary from './components/UserSummary.vue'
import AvailableQuizzes from './components/AvailableQuizzes.vue'
import QuizTaking from './components/QuizTaking.vue'
import ScoreSummary from './components/ScoreSummary.vue'
import QuizSummary from './components/QuizSummary.vue'
import { checkAuth } from './services/authService.js'

const routes = [
  {
    path: '/',
    name: 'Welcome',
    component: Welcome,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard
      },
      {
        path: 'subjects',
        name: 'SubjectsManagement',
        component: SubjectManagement
      },
      {
        path: 'chapters',
        name: 'ChaptersManagement',
        component: ChapterManagement
      },
      {
        path: 'quizzes',
        name: 'QuizzesManagement',
        component: QuizManagement
      },
      {
        path: 'questions',
        name: 'QuestionsManagement',
        component: QuestionManagement
      },
      {
        path: 'users',
        name: 'UsersManagement',
        component: UserManagement
      },
      {
        path: 'export',
        name: 'AdminExport',
        component: ExportDashboard
      },
      {
        path: 'summary',
        name: 'AdminSummary',
        component: QuizSummary
      },
      {
        path: '',
        redirect: 'dashboard'
      }
    ]
  },
  {
    path: '/dashboard',
    name: 'UserDashboard',
    component: UserDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/user',
    name: 'UserHome',
    component: UserDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/user/scores',
    name: 'UserScores',
    component: ScoreSummary,
    meta: { requiresAuth: true }
  },
  {
    path: '/user/summary',
    name: 'UserSummary',
    component: UserSummary,
    meta: { requiresAuth: true }
  },
  {
    path: '/quizzes',
    name: 'AvailableQuizzes',
    component: AvailableQuizzes,
    meta: { requiresAuth: true }
  },
  {
    path: '/quiz/:id',
    name: 'QuizTaking',
    component: QuizTaking,
    meta: { requiresAuth: true }
  },
  {
    path: '/score-summary',
    name: 'ScoreSummary',
    component: ScoreSummary,
    meta: { requiresAuth: true }
  },
  
  {
    path: '/:pathMatch(.*)*',
    redirect: '/' // <-- Redirect unknown routes to Welcome
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Vue 3 navigation guard
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    try {
      const user = await checkAuth()
      if (to.meta.requiresAdmin && user.role !== 'admin') {
        next('/login')
      } else {
        next()
      }
    } catch (error) {
      next('/login')
    }
  } else {
    next()
  }
})

export default router