<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')

const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    await authStore.login(username.value, password.value)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    console.error(error)
    let msg = error.response?.data?.detail || '登录失败，请检查用户名或密码'
    if (msg === 'Incorrect username or password') {
        msg = '用户名或密码错误'
    }
    errorMessage.value = msg
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-gray-50 flex items-center justify-center h-screen font-sans selection:bg-blue-100">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl border border-gray-100 p-10 transform transition-all hover:scale-[1.01]">
        
        <div class="text-center mb-10">
            <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-600 text-white font-bold text-2xl shadow-lg shadow-blue-200 mb-4">
                A
            </div>
            <h1 class="text-2xl font-bold text-slate-800">欢迎回来</h1>
            <p class="text-sm text-gray-500 mt-2">请登录 ADDoc 知识库管理系统</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-6">
            <div v-if="errorMessage" class="text-red-500 text-sm text-center bg-red-50 py-2 rounded-lg border border-red-100">
                {{ errorMessage }}
            </div>

            <div>
                <label class="block text-sm font-bold text-slate-700 mb-2 ml-1">用户名</label>
                <input 
                    v-model="username" 
                    type="text" 
                    class="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all placeholder-gray-400" 
                    placeholder="请输入用户名 "
                >
            </div>

            <div>
                <label class="block text-sm font-bold text-slate-700 mb-2 ml-1">密码</label>
                <input 
                    v-model="password" 
                    type="password" 
                    class="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all placeholder-gray-400" 
                    placeholder="请输入密码"
                >
            </div>

            <button 
                type="submit"
                :disabled="loading"
                class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3.5 rounded-xl shadow-lg shadow-blue-200 transition-all active:scale-95 flex justify-center items-center"
            >
                <span v-if="loading">登录中...</span>
                <span v-else>登 录</span>
            </button>
        </form>

        <div class="mt-8 text-center">
            <p class="text-xs text-gray-400">
                游客请直接 <router-link to="/" class="text-blue-600 hover:underline font-medium">返回首页</router-link>
            </p>
        </div>
    </div>
  </div>
</template>
