import { defineStore } from 'pinia'
import request from '../api/request'

interface User {
  id: number
  username: string
  role: string
  avatar?: string
  created_at: string
  last_login?: string
}

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('token'),
    user: null,
    isAuthenticated: !!localStorage.getItem('token'),
  }),
  actions: {
    async login(username: string, password: string) {      
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const response = await request.post('/api/token', params, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      this.token = response.data.access_token;
      this.isAuthenticated = true;
      localStorage.setItem('token', this.token as string);
      
      await this.fetchUser();
    },
    async fetchUser() {
      try {
        const response = await request.get('/api/users/me');
        this.user = response.data;
      } catch (error) {
        this.logout();
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      this.isAuthenticated = false;
      localStorage.removeItem('token');
      window.location.href = '/login';
    },
  },
})
