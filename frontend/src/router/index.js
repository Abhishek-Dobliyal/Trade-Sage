import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from '../views/Dashboard.vue'
import Chat from '../views/Chat.vue'
import Portfolio from '../views/Portfolio.vue'
import Recommendations from '../views/Recommendations.vue'
import Watchlist from '../views/Watchlist.vue'
import Market from '../views/Market.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/chat', name: 'Chat', component: Chat },
  { path: '/portfolio', name: 'Portfolio', component: Portfolio },
  { path: '/recommendations', name: 'Recommendations', component: Recommendations },
  { path: '/watchlist', name: 'Watchlist', component: Watchlist },
  { path: '/market', name: 'Market', component: Market },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
