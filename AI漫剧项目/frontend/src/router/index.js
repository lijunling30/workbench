import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/projects' },
  { path: '/login', component: () => import('../views/LoginView.vue') },
  { path: '/projects', component: () => import('../views/ProjectsView.vue') },
  { path: '/workbench/:projectId', component: () => import('../views/WorkbenchView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/projects' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('manju_token')
  if (!token && to.path !== '/login') return '/login'
  if (token && to.path === '/login') return '/projects'
})

export default router
