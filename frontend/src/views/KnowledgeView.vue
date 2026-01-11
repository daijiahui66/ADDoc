<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../api/request'
import NavBar from '../components/NavBar.vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const categories = ref<any[]>([])
const loading = ref(true)

const fetchCategories = async () => {
    try {
        const response = await request.get('/structure/tree')
        categories.value = response.data.map((cat: any) => {
            // Calculate total docs
            let docCount = 0
            const subNames: string[] = []
            
            cat.sub_categories.forEach((sub: any) => {
                docCount += sub.documents?.length || 0
                subNames.push(`${sub.name} (${sub.documents?.length || 0})`)
            })

            return {
                ...cat,
                docCount,
                subNames: subNames.slice(0, 3) // Show first 3 subcategories
            }
        })
    } catch (error) {
        console.error('Failed to fetch structure tree:', error)
        ElMessage.error('获取知识库结构失败')
    } finally {
        loading.value = false
    }
}

const handleCategoryClick = (category: any) => {
    // Find first document
    for (const sub of category.sub_categories) {
        if (sub.documents && sub.documents.length > 0) {
            router.push(`/docs/${sub.documents[0].id}`)
            return
        }
    }
    ElMessage.info('该分类下暂无文档')
}

onMounted(() => {
    fetchCategories()
})
</script>

<template>
  <div class="bg-gray-50 text-slate-800 font-sans min-h-screen flex flex-col">
    
    <NavBar />

    <main class="flex-grow max-w-7xl mx-auto w-full px-4 py-12 pt-24">
        
        <div class="text-center mb-12 fade-in">
            <h1 class="text-3xl font-extrabold text-slate-900 mb-4">探索知识库</h1>
            <p class="text-gray-500 max-w-2xl mx-auto">这里汇集了团队积累的所有技术文档，按照领域分类。选择一个感兴趣的主题开始阅读吧。</p>
        </div>

        <div v-if="loading" class="flex justify-center py-20">
            <p class="text-gray-400">加载中...</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 fade-in" style="animation-delay: 0.1s;">
            
            <div 
                v-for="(category, index) in categories" 
                :key="category.id"
                @click="handleCategoryClick(category)"
                class="bg-white rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer group h-full flex flex-col"
            >
                <div class="p-6 flex-grow">
                    <div class="flex items-center justify-between mb-4">
                        <div 
                            class="w-12 h-12 rounded-xl flex items-center justify-center transition-colors"
                            :class="[
                                index % 3 === 0 ? 'bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white' : 
                                index % 3 === 1 ? 'bg-purple-50 text-purple-600 group-hover:bg-purple-600 group-hover:text-white' : 
                                'bg-orange-50 text-orange-600 group-hover:bg-orange-600 group-hover:text-white'
                            ]"
                        >
                            <svg v-if="index % 3 === 0" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"></path></svg>
                            <svg v-else-if="index % 3 === 1" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
                            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                        </div>
                        <span class="bg-gray-50 text-gray-600 text-xs font-bold px-2 py-1 rounded-full border border-gray-200">{{ category.docCount }} 篇文章</span>
                    </div>
                    <h3 
                        class="text-xl font-bold text-slate-800 mb-3 transition-colors"
                        :class="[
                            index % 3 === 0 ? 'group-hover:text-blue-600' : 
                            index % 3 === 1 ? 'group-hover:text-purple-600' : 
                            'group-hover:text-orange-600'
                        ]"
                    >
                        {{ category.name }}
                    </h3>
                    <div class="space-y-2">
                        <div v-for="name in category.subNames" :key="name" class="flex items-center text-sm text-gray-500">
                            <span 
                                class="w-1.5 h-1.5 rounded-full mr-2"
                                :class="[
                                    index % 3 === 0 ? 'bg-blue-400' : 
                                    index % 3 === 1 ? 'bg-purple-400' : 
                                    'bg-orange-400'
                                ]"
                            ></span>
                            {{ name }}
                        </div>
                    </div>
                </div>
                <div 
                    class="px-6 py-4 bg-gray-50 rounded-b-2xl border-t border-gray-100 flex items-center justify-between text-sm font-medium transition-colors"
                    :class="[
                        index % 3 === 0 ? 'text-blue-600 group-hover:bg-blue-50' : 
                        index % 3 === 1 ? 'text-purple-600 group-hover:bg-purple-50' : 
                        'text-orange-600 group-hover:bg-orange-50'
                    ]"
                >
                    开始阅读
                    <svg class="w-4 h-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                </div>
            </div>

        </div>
    </main>
  </div>
</template>

<style scoped>
.fade-in { animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
