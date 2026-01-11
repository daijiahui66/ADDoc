import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const service = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000,
});

service.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

service.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Check if the request config has a custom property to skip global error handling
    if (error.config && error.config.skipGlobalErrorHandler) {
      return Promise.reject(error);
    }

    const authStore = useAuthStore();
    if (error.response && error.response.status === 401) {
      // Don't redirect if already on login page
      if (window.location.pathname !== '/login') {
        authStore.logout();
      }
    }
    return Promise.reject(error);
  }
);

export default service;
