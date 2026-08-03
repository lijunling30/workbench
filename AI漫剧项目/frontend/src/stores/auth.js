import { defineStore } from 'pinia'
import { api, getToken, setToken, clearToken } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken() || '',
    user: null,
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
  },
  actions: {
    async login(phone, password) {
      const r = await api.post('/auth/login', { phone, password })
      this.token = r.access_token
      setToken(r.access_token)
      await this.fetchMe()
    },
    async register(phone, password) {
      const r = await api.post('/auth/register', { phone, password })
      this.token = r.access_token
      setToken(r.access_token)
      await this.fetchMe()
    },
    async fetchMe() {
      this.user = await api.get('/auth/me')
    },
    logout() {
      this.token = ''
      this.user = null
      clearToken()
    },
  },
})
