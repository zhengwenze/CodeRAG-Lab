import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/views/layout/index.vue'),
    redirect: '/chat',
    children: [
      {
        path: '/chat',
        name: 'Chat',
        component: () => import('@/views/chat/index.vue'),
      },
      {
        path: '/datasets',
        name: 'Datasets',
        component: () => import('@/views/dataset/index.vue'),
      },
      {
        path: '/datasets/:id',
        name: 'DatasetDetail',
        component: () => import('@/views/dataset/detail.vue'),
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
