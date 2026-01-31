# LightRAG WebUI API 配置说明

## 问题：Docker 环境中前端如何连接后端？

### ❌ 错误配置
```yaml
environment:
  - VITE_API_BASE_URL=http://lightrag:9621  # 浏览器无法解析 Docker 内部服务名
```

### 方案对比

#### 方案 1: 使用空值（推荐） ✅
```yaml
environment:
  - VITE_API_BASE_URL=
```
- **前端行为**: 使用相对路径，自动使用浏览器当前域名
- **实际请求**: `http://localhost:5173/api/...` → 需要配置反向代理
- **优点**: 生产环境友好，自动适配域名
- **缺点**: 需要 Nginx 反向代理

#### 方案 2: 使用 localhost ✅
```yaml
environment:
  - VITE_API_BASE_URL=http://localhost:9621
```
- **前端行为**: 直接请求 `http://localhost:9621/api/...`
- **优点**: 本地开发简单，无需配置
- **缺点**: 
  - 只适用于本地开发
  - 远程访问时无法工作
  - 跨域问题（需要 LightRAG 配置 CORS）

#### 方案 3: 使用动态检测 ✅✅ (最佳)
```yaml
environment:
  - VITE_API_BASE_URL=auto
```
前端代码检测：
```typescript
const baseUrl = import.meta.env.VITE_API_BASE_URL === 'auto' 
  ? `${window.location.protocol}//${window.location.hostname}:9621`
  : import.meta.env.VITE_API_BASE_URL
```
- **优点**: 自动适配本地和远程访问
- **缺点**: 需要修改前端代码

## 推荐配置

### Docker Compose 部署
```yaml
lightrag-webui:
  environment:
    # 方案 A: 直接连接（简单，适合开发）
    - VITE_API_BASE_URL=http://localhost:9621
    
    # 方案 B: 通过 Nginx 代理（推荐生产环境）
    - VITE_API_BASE_URL=/api
```

### 本地 PowerShell 启动
```powershell
$env:VITE_API_BASE_URL = "http://localhost:9621"
npm run dev-no-bun
```

## 当前代码检查

根据 `src/lib/constants.ts`:
```typescript
export const backendBaseUrl = ''  // 空字符串，使用相对路径
```

这意味着：
- 前端会请求 `http://localhost:5173/openapi.json` 等相对路径
- **需要配置反向代理** 或 **修改为绝对路径**

## 建议修改

### 选项 1: 修改 constants.ts（推荐）
```typescript
// src/lib/constants.ts
export const backendBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:9621'
```

### 选项 2: 添加 Nginx 反向代理
```nginx
location /api/ {
    proxy_pass http://lightrag:9621/;
}
```

### 选项 3: 使用 Vite 代理（开发环境）
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:9621',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

## 最终推荐

**Docker 部署**:
```yaml
environment:
  - VITE_API_BASE_URL=http://localhost:9621
```

**本地开发**:
```powershell
$env:VITE_API_BASE_URL = "http://localhost:9621"
```

这样配置：
- ✅ 本地和 Docker 都能工作
- ✅ 无需修改代码
- ✅ 无需配置反向代理
- ⚠️ 仅适用于同一台机器访问

如需远程访问，建议使用 Nginx 反向代理方案。

