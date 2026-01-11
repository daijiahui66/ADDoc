<script setup lang="ts">
import { useAuthStore } from './stores/auth'
import { onMounted } from 'vue'

const authStore = useAuthStore()

onMounted(() => {
    // Check auth on mount, though router guard handles most
    if (authStore.isAuthenticated && !authStore.user) {
        authStore.fetchUser()
    }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- NavBar is now handled individually in each view for better control (AdminView has sidebar, HomeView has transparent nav, etc.) -->
    <!-- We removed the global header here to avoid duplication and layout issues in AdminView/LoginView -->
    
    <router-view />
  </div>
</template>
