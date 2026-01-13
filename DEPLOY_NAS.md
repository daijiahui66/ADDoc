# ADDoc 绿联 NAS (UGREEN UGOS) 部署指南

本指南将帮助你将 ADDoc 部署到绿联 NAS 上。由于 NAS 的 80 端口通常被系统占用，我们默认使用 **8090** 端口。

## 1. 准备工作

### 1.1 打包项目
在项目根目录下（Windows）运行提供的打包脚本：

```powershell
.\package.ps1
```

这将生成一个 `addoc_deploy.zip` 文件，其中包含了所有部署所需的源码和配置。

### 1.2 开启 NAS SSH
1. 登录绿联 NAS 网页管理界面。
2. 打开 **控制面板** -> **终端**。
3. 勾选 **开启 SSH**，记下端口（默认 22）和用户名。

## 2. 上传与部署

### 2.1 上传文件
1. 使用绿联客户端或 SMB/文件共享，在 NAS 的 Docker 共享文件夹下创建一个新目录，例如 `addoc`。
2. 将 `addoc_deploy.zip` 上传到该目录。

### 2.2 通过 SSH 部署
使用终端工具（如 PowerShell, PuTTY, CMD）连接到 NAS：

```bash
# 替换 username 为你的 NAS 用户名，nas_ip 为 NAS 的 IP 地址
ssh username@nas_ip -p 22
```

连接成功后，执行以下命令：

```bash
# 1. 切换到 root 权限 (通常需要，如果当前用户有 docker 权限可跳过)
sudo -i

# 2. 进入上传目录 (假设你上传到了 Docker/addoc)
# 注意：绿联 NAS 的存储卷路径通常在 /mnt/dm-0, /mnt/dm-1 等，或者 /volume1
# 你可以使用 `ls /mnt` 查看
cd /mnt/dm-0/Docker/addoc  # 请根据实际路径修改

# 3. 解压文件 (如果系统没有 unzip，可能需要用 python 解压或在电脑解压好传文件夹)
# 推荐：在电脑上解压好，直接传文件夹 `addoc_deploy` 里的内容到 NAS，这样更简单。
# 如果你上传的是 zip 且 NAS 有 unzip：
unzip addoc_deploy.zip

# 4. 启动服务
docker-compose up -d --build
```

> **注意：** 第一次构建需要下载 Python 和 Node.js 镜像并安装依赖，可能需要几分钟时间，请耐心等待。

## 3. 验证与访问

部署完成后，打开浏览器访问：

**http://NAS_IP:8090**

*   **NAS_IP**: 你 NAS 的局域网 IP 地址。
*   **8090**: 我们在 docker-compose.yml 中配置的端口。

### 数据备份
所有重要数据都已挂载到当前目录下的 `backend/data` (数据库) 和 `backend/uploads` (上传文件)。请定期备份这些目录。

## 常见问题

**Q: 8090 端口也被占用了怎么办？**
A: 修改 `docker-compose.yml` 文件，找到 `frontend` 服务下的 `ports`，将 `"8090:80"` 修改为其他端口，如 `"18080:80"`，然后重新执行 `docker-compose up -d`。

**Q: 构建速度慢？**
A: `Dockerfile` 中已配置阿里云镜像源用于 Python 包安装，npm 安装也建议在构建前配置淘宝源，或者耐心等待。
