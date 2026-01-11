<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '../api/request'
import NavBar from '../components/NavBar.vue'

const route = useRoute()
const router = useRouter()
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const loading = ref(false)

const performSearch = async () => {
    if (!searchQuery.value.trim()) return
    
    loading.value = true
    try {
        const response = await request.get('/api/search', { params: { q: searchQuery.value } })
        
        // Filter unique docs (if needed, though backend search usually returns unique docs, but assuming it might return fragments)
        const uniqueDocs = new Map()
        response.data.forEach((item: any) => {
            if (!uniqueDocs.has(item.id)) {
                uniqueDocs.set(item.id, item)
            }
        })
        searchResults.value = Array.from(uniqueDocs.values())
        
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const generateSnippet = (content: string, query: string) => {
  if (!content) return '';
  
  // 1. 简单去除 Markdown 标记
  const plainText = content
    .replace(/[#*`]/g, '') // 去除 # * `
    .replace(/!\[.*?\]\(.*?\)/g, '[图片]') // 替换图片
    .replace(/\[.*?\]\(.*?\)/g, '$1'); // 替换链接显示文本

  if (!query) return plainText.substring(0, 100) + '...';

  // 2. 查找关键词位置 (忽略大小写)
  const index = plainText.toLowerCase().indexOf(query.toLowerCase());
  
  let snippet = '';
  if (index === -1) {
    // 没找到（可能在标题里），只展示开头
    snippet = plainText.substring(0, 120);
  } else {
    // 3. 截取上下文 (前30，后60)
    const start = Math.max(0, index - 30);
    const end = Math.min(plainText.length, index + query.length + 60);
    snippet = (start > 0 ? '...' : '') + 
              plainText.substring(start, end) + 
              (end < plainText.length ? '...' : '');
  }

  // 4. 高亮替换 (保留原大小写，添加样式)
  const reg = new RegExp(`(${query})`, 'gi');
  return snippet.replace(reg, '<span class="text-blue-600 bg-yellow-100 font-bold px-0.5 rounded">$1</span>');
}

watch(() => route.query.q, (newQ) => {
    if (newQ) {
        searchQuery.value = newQ as string
        performSearch()
    }
}, { immediate: true })

</script>

<template>
  <div class="bg-gray-50 text-slate-800 font-sans min-h-screen flex flex-col">
    <NavBar />

    <main class="flex-grow max-w-4xl mx-auto w-full px-4 py-12 pt-24 fade-in">
        <div class="mb-8">
            <h1 class="text-2xl font-bold text-slate-800">搜索结果</h1>
            <p class="text-gray-500 mt-2">关键词 "<span class="font-bold text-slate-900">{{ searchQuery }}</span>" 共找到 {{ searchResults.length }} 条相关结果</p>
        </div>

        <div v-if="loading" class="flex justify-center py-20">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>

        <div v-else class="space-y-6">
            <div v-if="searchResults.length === 0" class="text-center py-10 bg-white rounded-2xl border border-gray-100 shadow-sm">
                <svg class="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                <p class="text-gray-500">没有找到相关文档，换个关键词试试？</p>
            </div>

            <div 
                v-for="res in searchResults" 
                :key="res.id"
                class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-all cursor-pointer group"
                @click="router.push(`/docs/${res.id}`)"
            >
                <div v-if="res.category_name" class="flex items-center text-xs text-gray-400 mb-2 space-x-2">
                    <span class="bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">{{ res.category_name }}</span>
                    <span v-if="res.sub_category_name">/</span>
                    <span v-if="res.sub_category_name">{{ res.sub_category_name }}</span>
                </div>
                <h2 class="text-xl font-bold text-blue-600 mb-2 group-hover:underline" v-html="generateSnippet(res.title, searchQuery)"></h2>
                <p class="text-sm text-gray-500 leading-relaxed" v-html="generateSnippet(res.content, searchQuery)"></p>
            </div>
        </div>
    </main>
  </div>
</template>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
