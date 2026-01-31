# LightRAG WebUI 远程访问配置完整指南

## ✅ 问题已修复

### 原问题
Docker 部署时，前端配置 `localhost` 导致远程访问失败：
```
用户浏览器 → http://192.168.1.100:5173 (服务器 WebUI)
             ↓ 前端请求
         http://localhost:9621 ❌ (用户电脑的 localhost，不是服务器!)
```

### 解决方案：自动检测服务器地址

修改了 `lightrag_webui/src/lib/constants.ts`，实现智能检测：

```typescript
const getBackendBaseUrl = () => {
  // 1. 优先使用环境变量 (VITE_API_BASE_URL)
  const envUrl = import.meta.env.VITE_API_BASE_URL
  if (envUrl) {
    return envUrl
  }
  
  // 2. 自动检测：使用当前访问的主机地址
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location
    return `${protocol}//${hostname}:9621`
  }
  
  return ''
}
```

## 🎯 工作原理

### 本地访问
```
用户访问: http://localhost:5173
自动检测: http://localhost:9621 ✅
```

### 远程访问（局域网）
```
用户访问: http://192.168.1.100:5173
自动检测: http://192.168.1.100:9621 ✅
```

### 远程访问（公网）
```
用户访问: http://your-domain.com:5173
自动检测: http://your-domain.com:9621 ✅
```

### HTTPS 部署
```
用户访问: https://your-domain.com:5173
自动检测: https://your-domain.com:9621 ✅
```

## 🚀 部署方式

### 方式 1: 自动检测（推荐）✅
```yaml
# docker-compose.yml
lightrag-webui:
  environment:
    - VITE_API_BASE_URL=  # 留空，自动检测
```

**优点**:
- ✅ 自动适配本地和远程访问
- ✅ 无需手动配置 IP
- ✅ 支持任何域名和 IP

### 方式 2: 手动指定 ✅
```yaml
# docker-compose.yml
lightrag-webui:
  environment:
    - VITE_API_BASE_URL=http://192.168.1.100:9621
```

**适用场景**:
- API 端口不是 9621
- 使用特殊域名
- 需要指定完整 URL

### 方式 3: 使用 .env 文件 ✅
```bash
# .env
LIGHTRAG_API_URL=http://your-server-ip:9621
```

```yaml
# docker-compose.yml
lightrag-webui:
  environment:
    - VITE_API_BASE_URL=${LIGHTRAG_API_URL:-}
```

## 📋 部署示例

### 本地开发
```bash
# 不需要任何配置，自动使用 localhost
docker compose up -d

# 访问
http://localhost:5173
```

### 局域网部署
```bash
# 服务器 IP: 192.168.1.100

# 不需要配置，自动检测
docker compose up -d

# 用户从任何局域网设备访问
http://192.168.1.100:5173
# 前端自动请求: http://192.168.1.100:9621 ✅
```

### 公网部署（域名）
```bash
# 域名: rag.example.com

# 不需要配置，自动检测
docker compose up -d

# 用户访问
https://rag.example.com:5173
# 前端自动请求: https://rag.example.com:9621 ✅
```

### 特殊端口（需要手动配置）
```bash
# API 端口改为 9999
# .env
LIGHTRAG_API_URL=http://192.168.1.100:9999

docker compose up -d
```

## 🔍 验证配置

### 1. 查看前端实际使用的 API 地址
打开浏览器开发者工具（F12）:
```javascript
// Console 中输入
console.log(window.location)
// 查看前端会请求的地址
```

### 2. 检查网络请求
开发者工具 → Network 标签:
- 查看请求是否发送到正确的服务器地址
- 确认没有 CORS 错误

### 3. 测试健康检查
```bash
# 在浏览器中访问
http://your-server-ip:9621/docs

# 应该能看到 API 文档
```

## ⚙️ 高级配置

### 使用 Nginx 反向代理（生产推荐）
```nginx
server {
    listen 80;
    server_name rag.example.com;
    
    # WebUI
    location / {
        proxy_pass http://localhost:5173;
    }
    
    # API
    location /api/ {
        proxy_pass http://localhost:9621/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

配置环境变量：
```yaml
lightrag-webui:
  environment:
    - VITE_API_BASE_URL=/api
```

### 使用不同端口
```yaml
# docker-compose.yml
lightrag:
  ports:
    - "9999:9621"  # 外部端口 9999

lightrag-webui:
  environment:
    - VITE_API_BASE_URL=http://your-server:9999
```

## 🐛 故障排查

### 问题 1: 无法连接 API
**症状**: 前端显示连接错误

**检查**:
```bash
# 1. 确认 LightRAG API 正常运行
curl http://localhost:9621/docs

# 2. 检查防火墙
sudo ufw status
sudo ufw allow 9621

# 3. 查看日志
docker compose logs lightrag
```

### 问题 2: CORS 错误
**症状**: 浏览器控制台显示 CORS 错误

**解决**: LightRAG API 需要配置 CORS
```python
# LightRAG 服务器配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题 3: 使用了错误的地址
**症状**: 请求发送到 `localhost` 而不是服务器 IP

**检查**:
1. 清除浏览器缓存
2. 重新构建前端镜像:
```bash
docker compose build --no-cache lightrag-webui
docker compose up -d lightrag-webui
```

## 📊 配置对比表

| 访问方式 | 配置 | 前端检测结果 |
|---------|------|------------|
| 本地 | 留空 | http://localhost:9621 ✅ |
| 局域网 (192.168.1.100) | 留空 | http://192.168.1.100:9621 ✅ |
| 域名 (rag.example.com) | 留空 | http://rag.example.com:9621 ✅ |
| HTTPS | 留空 | https://rag.example.com:9621 ✅ |
| 自定义端口 | 手动设置 | 使用设置的值 ✅ |

## 🎉 总结

### 现在的配置
✅ **自动检测服务器地址**
- 修改了 `constants.ts` 实现智能检测
- Docker 环境变量留空即可
- 支持本地、局域网、公网访问
- 无需手动配置 IP

### 使用建议
1. **默认配置**: 不设置 `VITE_API_BASE_URL`，让前端自动检测
2. **特殊需求**: 通过 `.env` 文件设置 `LIGHTRAG_API_URL`
3. **生产环境**: 使用 Nginx 反向代理，统一端口

---

**现在远程访问完全没问题了！** ✅
