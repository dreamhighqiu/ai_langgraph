# LightRAG WebUI 远程访问配置指南

## ⚠️ 重要：Docker 远程部署配置

### 问题诊断

如果你的 Docker 是在**远程服务器**上部署，使用 `localhost` 是错误的！

```
❌ 错误场景：
服务器 IP: 192.168.1.100
浏览器访问: http://192.168.1.100:5173
前端配置: VITE_API_BASE_URL=http://localhost:9621
结果: 前端会尝试连接浏览器所在电脑的 localhost，而不是服务器！
```

### ✅ 正确配置方案

#### 方案 1: 使用环境变量（推荐）

**1. 编辑 .env 文件**
```bash
# 本地开发
PUBLIC_API_URL=http://localhost:9621

# 局域网部署
PUBLIC_API_URL=http://192.168.1.100:9621

# 公网部署
PUBLIC_API_URL=http://your-domain.com:9621
```

**2. 启动服务**
```bash
docker compose up -d --build
```

**docker-compose.yml 已配置**:
```yaml
environment:
  - VITE_API_BASE_URL=${PUBLIC_API_URL:-http://localhost:9621}
```

#### 方案 2: 命令行指定（适合不同环境）

```bash
# 本地开发
PUBLIC_API_URL=http://localhost:9621 docker compose up -d

# 远程服务器（替换为实际 IP）
PUBLIC_API_URL=http://192.168.1.100:9621 docker compose up -d

# 生产环境
PUBLIC_API_URL=https://api.your-domain.com docker compose up -d --build
```

#### 方案 3: 使用 Nginx 反向代理（生产推荐）⭐

**优点**：
- 统一入口，前端和后端用同一域名
- 支持 HTTPS
- 解决跨域问题
- 更专业的生产部署

**配置示例**：

**1. 创建 nginx.conf**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://lightrag-webui:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # LightRAG API
    location /api/ {
        proxy_pass http://lightrag:9621/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**2. 修改 docker-compose.yml**
```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - lightrag
      - lightrag-webui
    networks:
      - ai_network

  lightrag-webui:
    # 不暴露端口，通过 nginx 访问
    # ports:
    #   - "5173:5173"
    environment:
      - VITE_API_BASE_URL=/api  # 使用相对路径
```

**3. 启动**
```bash
docker compose up -d --build
```

**访问**：http://your-domain.com

### 🎯 不同场景配置对照表

| 场景 | PUBLIC_API_URL 配置 | 访问地址 |
|------|-------------------|---------|
| 本地开发 | `http://localhost:9621` | http://localhost:5173 |
| 同一台电脑 | `http://127.0.0.1:9621` | http://127.0.0.1:5173 |
| 局域网服务器 | `http://192.168.1.100:9621` | http://192.168.1.100:5173 |
| 公网服务器 | `http://公网IP:9621` | http://公网IP:5173 |
| 域名（无 Nginx） | `http://your-domain.com:9621` | http://your-domain.com:5173 |
| 域名（有 Nginx）⭐ | `/api` | http://your-domain.com |

### 📝 快速配置步骤

#### 场景 A: 本地开发
```bash
# 1. 复制环境变量
cp env.docker.example .env

# 2. 使用默认配置即可
# PUBLIC_API_URL=http://localhost:9621

# 3. 启动
docker compose up -d
```

#### 场景 B: 远程服务器（例如 192.168.1.100）
```bash
# 1. 编辑 .env
nano .env

# 2. 修改配置
PUBLIC_API_URL=http://192.168.1.100:9621

# 3. 重新构建并启动
docker compose down
docker compose up -d --build

# 4. 访问
# http://192.168.1.100:5173
```

#### 场景 C: 生产环境（推荐 Nginx）
```bash
# 1. 创建 nginx.conf（见上面示例）

# 2. 编辑 .env
PUBLIC_API_URL=/api

# 3. 启动
docker compose up -d --build

# 4. 配置域名解析

# 5. 访问
# http://your-domain.com
```

### 🔍 验证配置

**检查前端 API 地址**：
1. 访问 http://YOUR_SERVER:5173
2. 打开浏览器开发者工具（F12）
3. 查看 Network 标签
4. 刷新页面
5. 查看 API 请求的地址是否正确

### ⚠️ 常见问题

#### 1. 跨域错误（CORS）
**问题**: 前端访问后端时出现 CORS 错误

**解决方案 A**: 使用 Nginx 反向代理（推荐）

**解决方案 B**: 配置 LightRAG 允许跨域
```python
# lightrag/api/lightrag_server.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. 防火墙问题
确保服务器防火墙开放端口：
```bash
# Ubuntu/Debian
sudo ufw allow 5173
sudo ufw allow 9621

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5173/tcp
sudo firewall-cmd --permanent --add-port=9621/tcp
sudo firewall-cmd --reload
```

#### 3. 构建缓存问题
如果修改了 `PUBLIC_API_URL`，需要重新构建：
```bash
docker compose down
docker compose build --no-cache lightrag-webui
docker compose up -d
```

### 📚 推荐阅读顺序

1. 确定部署场景（本地/远程/生产）
2. 选择配置方案（环境变量/Nginx）
3. 修改 .env 文件
4. 重新构建并启动
5. 验证访问

---

## 总结

| 方案 | 适用场景 | 配置难度 | 推荐度 |
|------|---------|---------|--------|
| 环境变量 | 本地/远程开发 | ⭐ 简单 | ⭐⭐⭐⭐ |
| Nginx 代理 | 生产环境 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐⭐ |
| 硬编码 | 不推荐 | ⭐ 简单 | ⭐ |

**当前项目已配置**: 环境变量方案（灵活，易用）

**生产部署建议**: 添加 Nginx 反向代理

