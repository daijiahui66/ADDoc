<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import request from '../api/request'

const router = useRouter()
const authStore = useAuthStore()
const showMenu = ref(false)
const showSearchDropdown = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
let debounceTimeout: any = null

defineProps<{
  transparent?: boolean
}>()

const handleLogout = () => {
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/')
}

// Search Logic
const highlightText = (text: string, keyword: string) => {
    if (!text || !keyword) return text
    const regex = new RegExp(`(${keyword})`, 'gi')
    return text.replace(regex, '<span class="bg-yellow-200 text-yellow-900 rounded px-0.5 font-medium">$1</span>')
}

const performSearch = async () => {
    if (!searchQuery.value.trim()) {
        searchResults.value = []
        showSearchDropdown.value = false
        return
    }
    
    try {
        const response = await request.get('/api/search', { params: { q: searchQuery.value } })
        searchResults.value = response.data.slice(0, 5) // Limit to 5 for dropdown
        showSearchDropdown.value = searchResults.value.length > 0
    } catch (e) {
        console.error(e)
    }
}

const onSearchInput = () => {
    if (debounceTimeout) clearTimeout(debounceTimeout)
    debounceTimeout = setTimeout(performSearch, 300)
}

const goToDoc = (id: number) => {
    showSearchDropdown.value = false
    searchQuery.value = ''
    router.push(`/docs/${id}`)
}

const goToFullSearch = () => {
    if (searchQuery.value.trim()) {
        showSearchDropdown.value = false
        router.push({ path: '/search', query: { q: searchQuery.value } })
    }
}

// Close dropdown on click outside logic is handled by blur event usually, 
// but for simplicity we use a simple directive or just mouseleave on the container if acceptable,
// or better: utilize focus/blur on input with delay to allow clicking items.
const handleBlur = () => {
    setTimeout(() => {
        showSearchDropdown.value = false
    }, 200)
}
</script>

<template>
    <nav class="fixed top-0 left-0 right-0 z-50 h-16 transition-colors duration-300" :class="transparent ? 'bg-white/80 backdrop-blur-md border-b border-gray-200' : 'bg-white border-b border-gray-200'">
        <div class="max-w-[1440px] mx-auto px-4 h-full flex justify-between items-center">
            <div class="flex items-center space-x-2 cursor-pointer w-64" @click="router.push('/')">
                <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">A</div>
                <span class="text-xl font-bold tracking-tight text-slate-900">ADDoc</span>
            </div>

            <!-- Search Bar Area -->
            <div class="flex-grow max-w-lg relative mx-4">
                <div class="relative">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    </span>
                    <input 
                        type="text" 
                        v-model="searchQuery"
                        @input="onSearchInput"
                        @keydown.enter="goToFullSearch"
                        @focus="searchResults.length > 0 && (showSearchDropdown = true)"
                        @blur="handleBlur"
                        class="w-full bg-gray-100 text-sm rounded-lg py-2.5 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder-gray-500 border border-transparent focus:bg-white focus:border-blue-500/20" 
                        placeholder="搜索文档..."
                    >
                    <button v-if="searchQuery" @click="searchQuery = ''; showSearchDropdown = false" class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>

                <!-- Dropdown Results -->
                <div v-if="showSearchDropdown" class="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50">
                    <div class="px-4 py-2 text-xs font-semibold text-gray-400 bg-gray-50 border-b border-gray-50">
                        找到相关结果
                    </div>
                    
                    <div 
                        v-for="res in searchResults" 
                        :key="res.id"
                        @click="goToDoc(res.id)"
                        class="block px-4 py-3 hover:bg-blue-50 transition-colors border-b border-gray-50 group cursor-pointer"
                    >
                        <div class="text-sm font-medium text-slate-800 group-hover:text-blue-600 truncate" v-html="highlightText(res.title, searchQuery)"></div>
                        <div class="text-xs text-gray-400 mt-0.5 truncate" v-html="highlightText(res.content?.substring(0, 60) + '...', searchQuery)"></div>
                    </div>

                    <div @click="goToFullSearch" class="block px-4 py-3 text-center text-sm font-bold text-blue-600 hover:bg-gray-50 transition-colors cursor-pointer">
                        查看所有结果 (Enter) &rarr;
                    </div>
                </div>
            </div>

            <div class="flex items-center space-x-4 justify-end w-64">
                <slot name="right-start"></slot>

                <template v-if="!authStore.isAuthenticated">
                    <button @click="router.push('/login')" class="text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors px-3 whitespace-nowrap">登录</button>
                </template>
                <template v-else>
                    <div class="relative ml-3" @mouseenter="showMenu = true" @mouseleave="showMenu = false">
                        <div class="flex items-center space-x-2 cursor-pointer py-2">
                            <img :src="authStore.user?.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix'" class="w-8 h-8 rounded-full bg-slate-100 border border-slate-200">
                            <span class="text-sm font-medium text-slate-700 hidden sm:block">{{ authStore.user?.username }}</span>
                        </div>

                        <transition name="fade">
                            <div v-show="showMenu" class="absolute right-0 top-full mt-1 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-50">
                                <div class="px-4 py-3 border-b border-gray-50">
                                    <p class="text-xs text-gray-400">Signed in as</p>
                                    <p class="text-sm font-bold text-slate-800 truncate">{{ authStore.user?.username }}</p>
                                </div>
                                
                                <a v-if="authStore.user?.role === 'admin'" @click="router.push('/admin')" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-blue-600 cursor-pointer transition-colors">
                                    后台管理
                                </a>
                                <a @click="handleLogout" class="block px-4 py-2 text-sm text-red-600 hover:bg-red-50 cursor-pointer transition-colors border-t border-gray-50 mt-1">
                                    退出登录
                                </a>
                            </div>
                        </transition>
                    </div>
                </template>
                
                <slot name="right-end"></slot>
            </div>
        </div>
    </nav>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
