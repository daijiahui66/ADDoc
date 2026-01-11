import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import DocView from '../views/DocView.vue'
import EditorView from '../views/EditorView.vue'
import AdminView from '../views/AdminView.vue'
import KnowledgeView from '../views/KnowledgeView.vue'
import SearchView from '../views/SearchView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: '首页' }
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: KnowledgeView,
      meta: { title: '知识库' }
    },
    {
      path: '/search',
      name: 'search',
      component: SearchView,
      meta: { title: '搜索' }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { title: '登录' }
    },
    {
      path: '/docs/:id',
      name: 'doc',
      component: DocView,
      meta: { title: '文档详情' }
    },
    {
      path: '/editor/:id?',
      name: 'editor',
      component: EditorView,
      meta: { requiresAuth: true, title: '编辑器' }
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true, requiresAdmin: true, title: '管理后台' }
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
      next('/')
  } else if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
      // Redirect non-admin users trying to access admin page
      next('/') 
  } else {
    next()
  }
})

router.afterEach((to) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} | ADDoc`
  } else {
    document.title = 'ADDoc'
  }
})

export default router
