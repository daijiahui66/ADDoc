<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import request from '../api/request'
import MarkdownIt from 'markdown-it'
import markdownItMark from 'markdown-it-mark'
import markdownItSub from 'markdown-it-sub'
import markdownItSup from 'markdown-it-sup'
import markdownItTaskLists from 'markdown-it-task-lists'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { ElMessage } from 'element-plus'
import EmojiPicker from 'vue3-emoji-picker'
import 'vue3-emoji-picker/css'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const docId = route.params.id as string
const isEditMode = !!docId && docId !== 'new'

const form = ref({
  title: '',
  category_id: null as number | null,
  sub_category_id: null as number | null,
  content: '',
  is_public: true
})

const categories = ref<any[]>([])
const subCategories = ref<any[]>([])
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const previewRef = ref<HTMLElement | null>(null)
const emojiContainerRef = ref<HTMLElement | null>(null)
const isScrolling = ref(false)
const showEmojiPicker = ref(false)

const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true, // Enable hard line breaks
  typographer: true,
  highlight: function (str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
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

const previewContent = computed(() => {
  return md.render(form.value.content || '')
})

const fetchCategories = async () => {
  try {
    const treeResponse = await request.get('/api/structure/tree')
    categories.value = treeResponse.data
  } catch (error) {
    console.error('Failed to fetch categories', error)
  }
}

const handleCategoryChange = () => {
  const selectedCat = categories.value.find(c => c.id === form.value.category_id)
  subCategories.value = selectedCat ? selectedCat.sub_categories : []
  if (!subCategories.value.find(s => s.id === form.value.sub_category_id)) {
      form.value.sub_category_id = null
  }
}

const fetchDoc = async () => {
  if (!isEditMode) return
  try {
    const response = await request.get(`/api/docs/${docId}`)
    const doc = response.data
    form.value = {
      title: doc.title,
      category_id: null,
      sub_category_id: doc.sub_category_id,
      content: doc.content,
      is_public: doc.is_public
    }
    
    for (const cat of categories.value) {
        if (cat.sub_categories.find((s: any) => s.id === doc.sub_category_id)) {
            form.value.category_id = cat.id
            subCategories.value = cat.sub_categories
            break
        }
    }
  } catch (error) {
    console.error('Failed to fetch doc', error)
    ElMessage.error('加载文档失败')
  }
}

const handleSave = async () => {
  if (!form.value.title || !form.value.sub_category_id || !form.value.content) {
      ElMessage.warning('请填写完整信息')
      return
  }

  try {
    if (isEditMode) {
      await request.put(`/api/docs/${docId}`, form.value)
      ElMessage.success('更新成功')
      router.push(`/docs/${docId}`)
    } else {
      const response = await request.post('/api/docs', form.value)
      ElMessage.success('创建成功')
      const newId = response.data?.id
      router.push(newId ? `/docs/${newId}` : '/')
    }
  } catch (error) {
    console.error('Save failed', error)
    ElMessage.error('保存失败')
  }
}

const handleCancel = () => {
  router.back()
}

// Emoji Selection
const onSelectEmoji = (emoji: any) => {
  insertText(emoji.i)
  showEmojiPicker.value = false
}

// Toolbar Logic
const insertText = (before: string, after: string = '') => {
  if (!textareaRef.value) return
  
  const start = textareaRef.value.selectionStart
  const end = textareaRef.value.selectionEnd
  const text = form.value.content
  
  const selection = text.substring(start, end)
  const replacement = before + selection + after
  
  form.value.content = text.substring(0, start) + replacement + text.substring(end)
  
  nextTick(() => {
    if (textareaRef.value) {
        textareaRef.value.focus()
        textareaRef.value.setSelectionRange(start + before.length, end + before.length)
    }
  })
}

const handleScroll = (source: 'editor' | 'preview') => {
  if (isScrolling.value) return
  isScrolling.value = true

  const editor = textareaRef.value
  const preview = previewRef.value

  if (editor && preview) {
    if (source === 'editor') {
      const percentage = editor.scrollTop / (editor.scrollHeight - editor.clientHeight)
      preview.scrollTop = percentage * (preview.scrollHeight - preview.clientHeight)
    } else {
      const percentage = preview.scrollTop / (preview.scrollHeight - preview.clientHeight)
      editor.scrollTop = percentage * (editor.scrollHeight - editor.clientHeight)
    }
  }

  setTimeout(() => {
    isScrolling.value = false
  }, 50)
}

const uploadImage = async (file: File) => {
  const placeholder = `![图片上传中...]()`
  insertText(placeholder)
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await request.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    // Assume backend returns { url: '...' } or just the url string
    const url = response.data.url || response.data
    
    // Replace placeholder with real image
    form.value.content = form.value.content.replace(placeholder, `![image](${url})`)
    ElMessage.success('图片上传成功')
  } catch (error) {
    console.error('Upload failed', error)
    form.value.content = form.value.content.replace(placeholder, `![上传失败]()`)
    ElMessage.error('图片上传失败')
  }
}

const handlePaste = (event: ClipboardEvent) => {
  const items = event.clipboardData?.items
  if (!items) return
  
  for (const item of items) {
    if (item.type.indexOf('image') !== -1) {
      event.preventDefault()
      const file = item.getAsFile()
      if (file) uploadImage(file)
      return
    }
  }
}

const handleDrop = (event: DragEvent) => {
  const files = event.dataTransfer?.files
  if (!files) return
  
  for (const file of files) {
    if (file.type.indexOf('image') !== -1) {
      uploadImage(file)
      // Only upload the first image found to avoid chaos, or loop for multiple
      return 
    }
  }
}

const handleClickOutside = (event: MouseEvent) => {
  if (showEmojiPicker.value && emojiContainerRef.value && !emojiContainerRef.value.contains(event.target as Node)) {
    showEmojiPicker.value = false
  }
}

onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  await fetchCategories()
  if (isEditMode) {
    await fetchDoc()
  } else if (route.query.sub_category_id) {
    const subId = Number(route.query.sub_category_id)
    form.value.sub_category_id = subId
    
    for (const cat of categories.value) {
        if (cat.sub_categories.find((s: any) => s.id === subId)) {
            form.value.category_id = cat.id
            subCategories.value = cat.sub_categories
            break
        }
    }
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="bg-gray-50 h-screen flex flex-col overflow-hidden text-slate-800 font-sans">
    
    <!-- Header -->
    <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 flex-none z-20">
        <div class="flex items-center">
            <button @click="handleCancel" class="text-gray-400 hover:text-slate-800 transition-colors mr-4 flex items-center">
                <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                返回
            </button>
        </div>

        <div class="flex items-center space-x-6">
            <div class="flex items-center">
                <span class="text-sm text-gray-500 mr-3 font-medium">文档状态</span>
                <button 
                    @click="form.is_public = !form.is_public" 
                    :class="form.is_public ? 'bg-blue-600' : 'bg-gray-200'" 
                    class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none mr-2"
                >
                    <span 
                        :class="form.is_public ? 'translate-x-6' : 'translate-x-1'" 
                        class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform" 
                    />
                </button>
                <span class="text-sm text-slate-700 font-bold cursor-pointer" @click="form.is_public = !form.is_public">{{ form.is_public ? '公开' : '保密' }}</span>
            </div>

            <button @click="handleSave" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-bold shadow-md shadow-blue-200 transition-all flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg>
                保存文档
            </button>

            <div class="flex items-center ml-4 pl-4 border-l border-gray-200 space-x-3">
                <div class="text-right hidden sm:block">
                    <div class="text-sm font-bold text-gray-700">
                        {{ authStore.user?.username || 'User' }}
                    </div>
                    <div class="text-xs text-gray-400">
                        {{ authStore.user?.role === 'admin' ? '管理员' : '编辑者' }}
                    </div>
                </div>
                <img 
                    :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=${authStore.user?.username || 'user'}`" 
                    class="w-8 h-8 rounded-full bg-gray-100 border border-gray-200" 
                    alt="Avatar" 
                >
            </div>
        </div>
    </header>

    <main class="flex-1 flex flex-col w-[95%] max-w-[1800px] mx-auto px-4 py-6 overflow-hidden">
        
        <div class="flex-none mb-4 space-y-4">
            <input v-model="form.title" type="text" class="w-full text-4xl font-extrabold text-slate-900 placeholder-gray-300 border-none focus:ring-0 bg-transparent p-0" placeholder="请输入文档标题...">
            
            <div class="flex items-center space-x-4">
                <div class="relative">
                    <select v-model="form.category_id" @change="handleCategoryChange" class="appearance-none bg-white border border-gray-200 text-slate-700 text-sm rounded-lg pl-3 pr-8 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm cursor-pointer hover:border-blue-300 transition-colors">
                         <option :value="null" disabled>选择大类</option>
                        <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                    </select>
                    <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                    </div>
                </div>

                <div class="relative">
                    <select v-model="form.sub_category_id" class="appearance-none bg-white border border-gray-200 text-slate-700 text-sm rounded-lg pl-3 pr-8 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm cursor-pointer hover:border-blue-300 transition-colors">
                        <option :value="null" disabled>选择子类</option>
                        <option v-for="sub in subCategories" :key="sub.id" :value="sub.id">{{ sub.name }}</option>
                    </select>
                    <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                    </div>
                </div>
            </div>
        </div>

        <div class="flex-1 bg-white rounded-xl shadow-lg border border-gray-200 flex flex-col overflow-hidden">
            
            <div class="h-10 border-b border-gray-100 bg-gray-50 flex items-center px-3 space-x-1 flex-none select-none flex-wrap z-20">
                <button @click="insertText('**', '**')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="加粗">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 4h8a4 4 0 014 4 4 4 0 01-4 4H6V4zm0 8h9a4 4 0 014 4 4 4 0 01-4 4H6v-8z"></path></svg>
                </button>
                <button @click="insertText('*', '*')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="斜体">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
                </button>
                <button @click="insertText('~~', '~~')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="删除线">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                </button>
                <div class="w-px h-4 bg-gray-300 mx-1 flex-shrink-0"></div>
                <button @click="insertText('# ')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors font-bold text-xs flex-shrink-0">H1</button>
                <button @click="insertText('## ')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors font-bold text-xs flex-shrink-0">H2</button>
                <button @click="insertText('### ')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors font-bold text-xs flex-shrink-0">H3</button>
                <div class="w-px h-4 bg-gray-300 mx-1 flex-shrink-0"></div>
                <button @click="insertText('- ')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="无序列表">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </button>
                <button @click="insertText('1. ')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="有序列表">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h12M7 12h12M7 17h12M3 7h.01M3 12h.01M3 17h.01"></path></svg>
                </button>
                <button @click="insertText('- [ ] ')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="任务列表">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                </button>
                <button @click="insertText('> ')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="引用">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"></path></svg>
                </button>
                <div class="w-px h-4 bg-gray-300 mx-1 flex-shrink-0"></div>
                <button @click="insertText('\n---\n')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="分割线">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path></svg>
                </button>
                <button @click="insertText('[', '](url)')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="链接">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                </button>
                <button @click="insertText('\n| Header | Header |\n| --- | --- |\n| Cell | Cell |', '')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="表格">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7-8h14a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v2a2 2 0 002 2zm0 8h14a2 2 0 002-2v-2a2 2 0 00-2-2H6a2 2 0 00-2 2v2a2 2 0 002 2z"></path></svg>
                </button>
                <div class="w-px h-4 bg-gray-300 mx-1 flex-shrink-0"></div>
                <button @click="insertText('```\n', '\n```')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="代码块">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
                </button>
                <button @click="insertText('![Image](', ')')" class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" title="图片">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                </button>
                
                <div class="w-px h-4 bg-gray-300 mx-1 flex-shrink-0"></div>
                
                <!-- Emoji Picker Button -->
                <div class="relative" ref="emojiContainerRef">
                    <button 
                        @click.stop="showEmojiPicker = !showEmojiPicker" 
                        class="p-1.5 rounded hover:bg-gray-200 text-gray-600 transition-colors" 
                        title="表情"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </button>
                    
                    <!-- Emoji Picker Popover -->
                    <div v-if="showEmojiPicker" class="absolute right-0 z-50 shadow-xl rounded-lg" style="top: 100%; margin-top: 0.5rem; min-width: 300px;">
                        <div class="relative z-50">
                            <EmojiPicker :native="true" @select="onSelectEmoji" />
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex-1 flex overflow-hidden">
                <textarea 
                    ref="textareaRef"
                    v-model="form.content"
                    @scroll="handleScroll('editor')"
                    @paste="handlePaste"
                    @dragover.prevent
                    @drop.prevent="handleDrop"
                    class="w-1/2 h-full bg-gray-50 p-6 overflow-y-auto border-r border-gray-100 font-mono text-sm leading-relaxed text-slate-700 outline-none resize-none focus:ring-0 focus:border-blue-200 transition-colors" 
                    style="font-family: 'Menlo', 'Monaco', 'Courier New', monospace; line-height: 1.6;"
                    placeholder="在此输入 Markdown 内容..."
                ></textarea>
                <div 
                    ref="previewRef"
                    @scroll="handleScroll('preview')"
                    class="w-1/2 h-full bg-white p-8 overflow-y-auto prose prose-sm max-w-none" 
                    v-html="previewContent"
                >
                </div>
            </div>
            <div class="h-6 bg-white border-t border-gray-100 flex items-center px-4 justify-between text-[10px] text-gray-400 select-none">
                <div class="flex space-x-3"><span>{{ form.content.length }} Chars</span></div>
                <div>Markdown Mode</div>
            </div>
        </div>
    </main>
  </div>
</template>


