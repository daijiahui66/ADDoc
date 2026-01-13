/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'markdown-it-mark';
declare module 'markdown-it-sub';
declare module 'markdown-it-sup';
declare module 'markdown-it-task-lists';
declare module 'vue3-emoji-picker';
declare module 'vue3-emoji-picker/css';
