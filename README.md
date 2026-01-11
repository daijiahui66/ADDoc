# ADDoc 个人知识库系统

<p align="center">
  <img src="./frontend/public/favicon.svg" width="100" height="100" alt="ADDoc Logo">
</p>

<p align="center">
  <strong>极简 · 高效 · 现代化</strong><br>
  专为开发者打造的第二大脑，专注于纯粹的记录与极致的阅读体验。
</p>

<p align="center">
  <a href="https://gitee.com/"><img src="https://img.shields.io/badge/Frontend-Vue3-4FC08D?style=flat-square&logo=vue.js" alt="Vue 3"></a>
  <a href="https://gitee.com/"><img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi" alt="FastAPI"></a>
  <a href="https://gitee.com/"><img src="https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite" alt="SQLite"></a>
  <a href="https://gitee.com/"><img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="License"></a>
</p>

---

## 📖 项目简介

**ADDoc** 诞生于对“纯粹记录”的追求。厌倦了繁杂的商业笔记软件，我决定手搓一套符合自己需求的知识库系统。它摒弃了冗余的功能，专注于 Markdown 的极致渲染、代码片段的优雅展示以及流畅的阅读体验。

无论你是需要整理技术文档、记录学习笔记，还是构建个人 Wiki，ADDoc 都能为你提供一个安静、专注的书写空间。

## ✨ 核心特性

- **💻 现代化技术栈**：采用 Vue 3 + TypeScript + Vite 构建前端，FastAPI 驱动后端，兼顾开发体验与运行性能。
- **🎨 Mac 风格代码块**：集成 Highlight.js，定制化 macOS 窗口风格代码块，支持语言自动识别与一键复制。
- **🔍 智能全文检索**：内置 KWIC (Key Word In Context) 算法，支持关键词高亮与上下文智能截取，毫秒级响应。
- **📂 拖拽式管理**：所见即所得的分类与文档管理，支持层级结构拖拽排序。
- **🖼️ 沉浸式阅读**：深度优化的排版细节，支持图片点击灯箱放大预览。
- **💾 数据安全**：基于 SQLite 单文件数据库，支持一键全量备份导出（ZIP格式，包含图片资源）。
- **🚀 离线部署友好**：支持前后端一体化打包，可在无外网的 Windows 服务器上轻松运行。

## 🛠️ 技术栈

| 模块 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **Frontend** | Vue 3 + TypeScript | 核心前端框架 |
| **Build Tool** | Vite | 极速构建工具 |
| **UI Framework** | Tailwind CSS + Element Plus | 原子化 CSS 与组件库 |
| **Backend** | FastAPI (Python) | 高性能异步 Web 框架 |
| **Database** | SQLite + SQLAlchemy | 轻量级嵌入式数据库与 ORM |
| **Auth** | OAuth2 + JWT | 标准身份验证与权限控制 |

## 📸 系统预览

> *请在此处替换为您实际的运行截图，建议上传至 Gitee 仓库的 assets 目录或图床*

| 首页 | 文档编辑 |
| :---: | :---: |
| ![Dashboard](https://gitee.com/daijiahui/addoc/raw/master/assets/%E9%A6%96%E9%A1%B5.png) | ![Editor](https://gitee.com/daijiahui/addoc/raw/master/assets/%E6%96%87%E6%A1%A3%E7%BC%96%E8%BE%91.png) |

| 文档阅读 | 后台首页 |
| :---: | :---: |
| ![Reading](https://gitee.com/daijiahui/addoc/raw/master/assets/%E6%96%87%E6%A1%A3%E9%98%85%E8%AF%BB.png) | ![About](https://gitee.com/daijiahui/addoc/raw/master/assets/%E5%90%8E%E5%8F%B0%E9%A6%96%E9%A1%B5.png) |

## 🚀 快速开始 (开发模式)

### 环境要求
- Node.js >= 16
- Python >= 3.10

### 1. 后端启动
```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活环境 (Windows)
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务 (默认端口 8000)
uvicorn main:app --reload

```

### 2. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

```

访问 `http://localhost:5173` 即可看到系统界面。


## 🤝 贡献与反馈

如果你觉得这个项目对你有帮助，欢迎 Star ⭐️ 或 Fork。
如果有任何问题或建议，请提交 Issue。

## 👤 作者

**饿死小胖子**

* 💻 Role: 医疗行业信息工程师 / 业余全栈开发者

## 🚀 特别致谢

* **Gemini & Trae**: 感谢 AI 提供的强力代码辅助与架构建议。
* **Open Source**: 感谢所有开源社区的贡献者。

## 🙏 感谢打赏
| 微信 | 支付宝 |
| :---: | :---: |
| ![Dashboard](https://gitee.com/daijiahui/addoc/raw/master/assets/wechat.png) | ![Editor](https://gitee.com/daijiahui/addoc/raw/master/assets/alipay.png) |
---

<p align="center">Copyright © 2026 ADDoc. Powered by Coffee & Bugs ☕🐛</p>

```
