<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import request from '../api/request'
import MarkdownIt from 'markdown-it'
import markdownItMark from 'markdown-it-mark'
import markdownItSub from 'markdown-it-sub'
import markdownItSup from 'markdown-it-sup'
import markdownItTaskLists from 'markdown-it-task-lists'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import NavBar from '../components/NavBar.vue'
import { ElImageViewer } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const doc = ref<any>(null)
const tree = ref<any[]>([])
const loading = ref(true)
const permissionDenied = ref(false)

// Image Viewer State
const showViewer = ref(false)
const previewImageList = ref<string[]>([])
const initialIndex = ref(0)

// Table of Contents State
const toc = ref<{ id: string, text: string, level: number }[]>([])
const activeHeaderId = ref('')
let observer: IntersectionObserver | null = null

const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true, // Enable hard line breaks
  typographer: true,
  highlight: function (str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code class="language-' + lang + '">' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>';
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
  }
})
.use(markdownItMark)
.use(markdownItSub)
.use(markdownItSup)
.use(markdownItTaskLists)

const handleImageClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  if (target.tagName === 'IMG') {
    const img = target as HTMLImageElement
    // 获取文章内所有图片，实现相册浏览体验
    const allImages = Array.from(document.querySelectorAll('.prose img'))
    const urls = allImages.map(i => (i as HTMLImageElement).src)
    
    previewImageList.value = urls
    initialIndex.value = urls.indexOf(img.src)
    showViewer.value = true
  }
}

const enhanceCodeBlocks = () => {
  const blocks = document.querySelectorAll('.prose pre');
  
  blocks.forEach((pre) => {
    // 1. 避免重复处理
    if (pre.querySelector('.code-enhancement')) return;

    const code = pre.querySelector('code');
    if (!code) return;

    // 2. 提取语言
    const classNameStr = (code.className || '') + ' ' + (pre.className || '');
    const match = /language-([a-zA-Z0-9]+)/.exec(classNameStr);
    const langName = (match && match[1]) ? match[1].toUpperCase() : null;

    // 3. 创建顶部容器 (为了布局整齐)
    const header = document.createElement('div');
    header.className = 'code-enhancement absolute top-3 right-3 flex items-center space-x-3 z-10';
    
    // 4. 添加语言标签
    if (langName) {
      const langSpan = document.createElement('span');
      langSpan.className = 'text-xs text-gray-400 font-mono select-none mr-2';
      langSpan.innerText = langName;
      header.appendChild(langSpan);
    }

    // 5. 添加复制按钮
    const copyBtn = document.createElement('button');
    copyBtn.className = 'text-gray-400 hover:text-white transition-colors p-1 rounded';
    copyBtn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>`;
    
    copyBtn.onclick = async () => {
        try {
            await navigator.clipboard.writeText(code.innerText);
            // 切换为对勾图标
            copyBtn.innerHTML = `<svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`;
            setTimeout(() => {
                // 2秒后恢复
                copyBtn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>`;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy', err);
        }
    };
    
    header.appendChild(copyBtn);
    pre.appendChild(header); // 将控制栏添加到代码块中
  });
};

const generateTOC = () => {
  toc.value = []
  const article = document.querySelector('.prose')
  if (!article) return

  const headers = article.querySelectorAll('h1, h2, h3, h4')
  headers.forEach((header, index) => {
    if (!header.id) {
      header.id = `heading-${index}`
    }
    toc.value.push({
      id: header.id,
      text: header.textContent || '',
      level: parseInt(header.tagName.substring(1))
    })
  })

  setupIntersectionObserver(headers)
}

const setupIntersectionObserver = (headers: NodeListOf<Element>) => {
  if (observer) observer.disconnect()
  
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        activeHeaderId.value = entry.target.id
      }
    })
  }, {
    rootMargin: '-80px 0px -80% 0px' // Adjust trigger area
  })

  headers.forEach(header => observer?.observe(header))
}

const scrollToHeader = (id: string) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
    activeHeaderId.value = id
  }
}

const fetchTree = async () => {
  try {
    const response = await request.get('/api/structure/tree')
    tree.value = response.data
  } catch (error) {
    console.error('Failed to fetch structure tree:', error)
  }
}

const fetchDoc = async (id: string) => {
  loading.value = true
  permissionDenied.value = false
  doc.value = null
  try {
    // Pass custom config to skip global 401 redirect
    const response = await request.get(`/api/docs/${id}`, { skipGlobalErrorHandler: true } as any)
    doc.value = response.data
    nextTick(() => {
        generateTOC()
        enhanceCodeBlocks()
    })
  } catch (error: any) {
    console.error('Failed to fetch document:', error)
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
       permissionDenied.value = true
    }
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const pad = (n: number) => n < 10 ? '0' + n : n
  return `${date.getFullYear()}/${pad(date.getMonth() + 1)}/${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

// Watch for route changes to refetch doc
watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchDoc(newId as string)
  }
})

onMounted(() => {
  fetchTree()
  if (route.params.id) {
    fetchDoc(route.params.id as string)
  }
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<template>
  <div class="bg-white text-slate-800 font-sans flex flex-col h-screen overflow-hidden">
    
    <NavBar />

    <div class="flex flex-1 pt-16 max-w-[1440px] mx-auto w-full h-full">
        
        <aside class="w-[280px] flex-none border-r border-gray-200 overflow-y-auto no-scrollbar py-6 pl-6 pr-3 hidden lg:block">
            
            <div class="mb-6 pr-3" v-if="authStore.isAuthenticated">
                <button @click="router.push('/editor')" class="w-full flex items-center justify-center py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-bold shadow-md shadow-blue-200 transition-all active:scale-95">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                    新建文档
                </button>
            </div>

            <!-- Tree Rendering -->
            <div v-for="category in tree" :key="category.id" class="mb-8">
                <h3 class="font-bold text-slate-900 mb-3 text-sm uppercase tracking-wider px-2">{{ category.name }}</h3>
                
                <div v-for="sub in category.sub_categories" :key="sub.id" class="mb-2">
                    <div class="flex items-center text-sm font-medium text-slate-900 px-2 py-2 cursor-pointer hover:bg-gray-50 rounded-md">
                        <svg class="w-3 h-3 mr-2 transform rotate-90 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                        {{ sub.name }}
                    </div>
                    <div class="space-y-0.5 mt-1 relative">
                        <div class="absolute left-3.5 top-0 bottom-0 w-px bg-gray-100"></div>
                        
                        <template v-if="sub.documents && sub.documents.length">
                            <router-link 
                                v-for="d in sub.documents" 
                                :key="d.id" 
                                :to="'/docs/' + d.id"
                                class="flex items-center text-[13px] py-2 pl-9 pr-3 transition-colors relative"
                                :class="[
                                    d.id === parseInt(route.params.id as string) 
                                    ? 'active-sidebar-item rounded-r-md' 
                                    : 'text-slate-600 hover:text-blue-600'
                                ]"
                            >
                                <span class="truncate flex-1">{{ d.title }}</span>
                                <svg v-if="!d.is_public" class="w-3 h-3 ml-2 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                                </svg>
                                <svg v-if="d.id === parseInt(route.params.id as string)" class="w-3 h-3 ml-2 text-blue-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            </router-link>
                        </template>
                        <div v-else class="text-[13px] text-gray-400 py-2 pl-9 italic">
                            暂无文档
                        </div>
                    </div>
                </div>
            </div>
        </aside>

        <main class="flex-1 overflow-y-auto px-8 py-10 md:px-16 scroll-smooth">
            <div v-if="permissionDenied" class="flex flex-col items-center justify-center py-20 fade-in">
                <div class="w-24 h-24 bg-orange-50 rounded-full flex items-center justify-center mb-6">
                    <svg class="w-12 h-12 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                </div>
                <h2 class="text-2xl font-bold text-slate-800 mb-2">该文档为私密内容</h2>
                <p class="text-gray-500 mb-8 text-center max-w-md">您当前的身份（访客）无法查看此文档。<br>请联系管理员或登录后查看。</p>
                
                <div class="flex space-x-4">
                    <button @click="router.push('/')" class="px-6 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 font-medium transition-colors">
                        回到首页
                    </button>
                    <button @click="router.push('/login')" class="px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-medium transition-colors shadow-lg shadow-blue-200">
                        去登录
                    </button>
                </div>
            </div>

            <div v-else-if="doc" class="max-w-3xl mx-auto pb-24">
                
                <div class="flex items-center text-xs font-medium text-gray-400 mb-8 uppercase tracking-wide">
                    <span 
                        class="hover:text-slate-700 cursor-pointer transition-colors" 
                        @click="router.push('/')"
                    >
                        {{ doc.category_name || '文档库' }}
                    </span>

                    <span v-if="doc.sub_category_name" class="mx-2 text-gray-300">/</span>

                    <span 
                        v-if="doc.sub_category_name" 
                        class="hover:text-slate-700 cursor-pointer transition-colors"
                    >
                        {{ doc.sub_category_name }}
                    </span>
                </div>

                <h1 class="text-4xl font-extrabold text-slate-900 mb-6 tracking-tight leading-tight">{{ doc.title }}</h1>
                <div class="flex items-center space-x-6 text-sm text-gray-500 mb-10 border-b border-gray-100 pb-8">
                    <div class="flex items-center">
                        <img :src="doc.author?.avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix'" class="w-5 h-5 rounded-full mr-2">
                        {{ doc.author?.username || 'Unknown' }}
                    </div>
                    <span>•</span>
                    <div>{{ formatDate(doc.created_at) }}</div>
                    <span>•</span>
                    <div v-if="!doc.is_public" class="flex items-center text-orange-600 bg-orange-50 px-2 py-0.5 rounded text-xs font-semibold">
                        保密
                    </div>
                    <div v-else class="flex items-center text-green-600 bg-green-50 px-2 py-0.5 rounded text-xs font-semibold">
                        公开
                    </div>
                    
                    <button 
                        v-if="authStore.user && (authStore.user.id === doc.author_id || authStore.user.role === 'admin')"
                        @click="router.push(`/editor/${doc.id}`)"
                        class="ml-auto text-blue-600 hover:text-blue-800 font-medium"
                    >
                        编辑
                    </button>
                </div>

                <article class="prose max-w-none text-slate-600" v-html="md.render(doc.content || '')" @click="handleImageClick"></article>

                <div class="mt-20 pt-8 border-t border-gray-100 flex items-center justify-between">
                    <span class="text-sm text-gray-400">最后更新: {{ formatDate(doc.updated_at) }}</span>
                </div>
            </div>
            <div v-else-if="loading" class="flex justify-center items-center h-64">
                <p class="text-gray-500">加载中...</p>
            </div>
            <div v-else class="flex justify-center items-center h-64">
                <p class="text-gray-500">未找到文档</p>
            </div>
        </main>

        <aside class="w-[240px] flex-none hidden xl:block pt-10 pr-8">
            <div class="fixed w-[240px]">
                <h5 class="text-[11px] font-bold text-slate-900 uppercase tracking-widest mb-4 pl-4 opacity-40">On This Page</h5>
                
                <nav v-if="toc.length > 0" class="max-h-[calc(100vh-200px)] overflow-y-auto pr-2 custom-scrollbar">
                    <ul class="space-y-1">
                        <li v-for="item in toc" :key="item.id">
                            <a 
                                href="#" 
                                @click.prevent="scrollToHeader(item.id)"
                                class="block text-[13px] py-1.5 transition-all border-l-2 hover:text-slate-900 truncate"
                                :class="[
                                    activeHeaderId === item.id 
                                    ? 'text-blue-600 border-blue-600 font-medium' 
                                    : 'text-gray-500 border-transparent hover:border-gray-300',
                                    item.level === 1 ? 'pl-0 font-semibold text-slate-800' : '',
                                    item.level === 2 ? 'pl-4 text-slate-600' : '',
                                    item.level === 3 ? 'pl-8 text-xs text-slate-500' : '',
                                    item.level === 4 ? 'pl-12 text-xs text-slate-400' : ''
                                ]"
                            >
                                {{ item.text }}
                            </a>
                        </li>
                    </ul>
                </nav>
                <p v-else class="text-xs text-gray-400 pl-4 italic">本文无目录</p>
            </div>
        </aside>

    </div>

    <el-image-viewer 
      v-if="showViewer" 
      :url-list="previewImageList" 
      :initial-index="initialIndex"
      @close="showViewer = false"
      :hide-on-click-modal="true" 
    />
  </div>
</template>

<style>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
