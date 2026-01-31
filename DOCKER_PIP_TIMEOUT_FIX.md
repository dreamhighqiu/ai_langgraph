# Docker 构建 pip 超时问题修复

## 🔍 问题描述

在构建 Docker 镜像时，pip 下载 Python 包时出现超时错误：

```
ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.
```

**原因：**
- 网络连接慢或不稳定
- PyPI 官方源在国内访问速度慢
- 默认超时时间太短

---

## ✅ 已完成的修复

### 1. 配置 pip 使用国内镜像源

**已更新的文件：**
- `Dockerfile.backend`
- `anything-chat-rag/Dockerfile`

**修复内容：**
```dockerfile
# 配置 pip 使用清华大学镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.timeout 300 && \
    pip config set global.retries 5
```

### 2. 增加超时时间和重试次数

**修复内容：**
- 超时时间：300 秒（默认 15 秒）
- 重试次数：5 次
- 备用镜像源：阿里云

### 3. 添加备用安装方案

**修复内容：**
```dockerfile
# 优先使用 uv，失败则使用 pip，再失败则使用阿里云镜像
RUN pip install --no-cache-dir --timeout=300 uv || \
    (pip install --no-cache-dir --timeout=300 -i https://mirrors.aliyun.com/pypi/simple/ uv)
```

---

## 📊 镜像源选项

### 推荐的国内镜像源

1. **清华大学**（已配置）
   ```
   https://pypi.tuna.tsinghua.edu.cn/simple
   ```

2. **阿里云**（备用）
   ```
   https://mirrors.aliyun.com/pypi/simple
   ```

3. **中科大**（可选）
   ```
   https://pypi.mirrors.ustc.edu.cn/simple
   ```

4. **华为云**（可选）
   ```
   https://mirrors.huaweicloud.com/repository/pypi/simple
   ```

---

## 🔧 如果仍然失败

### 选项 1: 使用不同的镜像源

如果清华大学镜像源不可用，可以修改为：

```dockerfile
# 使用阿里云镜像源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
```

### 选项 2: 增加超时时间

```dockerfile
# 增加超时到 600 秒
RUN pip config set global.timeout 600
```

### 选项 3: 使用代理

如果有代理服务器：

```dockerfile
# 设置代理
ENV http_proxy=http://proxy.example.com:8080
ENV https_proxy=http://proxy.example.com:8080
```

### 选项 4: 分步安装

如果单个命令失败，可以分步安装：

```dockerfile
# 先安装 uv
RUN pip install --timeout=300 uv

# 再安装其他依赖
RUN uv pip install --system -r requirements.txt
```

---

## 🚀 验证修复

### 1. 重新构建

```bash
# 清除缓存并重新构建
docker compose build --no-cache lightrag

# 或构建所有服务
docker compose build --no-cache
```

### 2. 检查构建日志

```bash
# 查看详细构建日志
docker compose build --progress=plain lightrag 2>&1 | tee build.log
```

### 3. 如果仍然失败

**检查网络连接：**
```bash
# 在容器构建过程中测试
docker run -it --rm python:3.11-slim bash
pip install --timeout=300 uv
```

**检查镜像源可用性：**
```bash
curl -I https://pypi.tuna.tsinghua.edu.cn/simple/
curl -I https://mirrors.aliyun.com/pypi/simple/
```

---

## 📝 配置说明

### pip 配置位置

配置会写入：`/root/.pip/pip.conf`

**内容：**
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
timeout = 300
retries = 5
```

### 环境变量方式（备选）

如果不想修改 pip 配置，可以使用环境变量：

```dockerfile
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TIMEOUT=300
ENV PIP_RETRIES=5
```

---

## ✅ 总结

**已完成的修复：**
- ✅ 配置 pip 使用清华大学镜像源
- ✅ 增加超时时间到 300 秒
- ✅ 增加重试次数到 5 次
- ✅ 添加阿里云作为备用镜像源
- ✅ 所有 pip 安装命令都添加了超时和重试

**预期效果：**
- 下载速度更快
- 超时错误减少
- 构建成功率提高

**如果仍然失败：**
1. 检查服务器网络连接
2. 尝试其他镜像源
3. 使用代理（如果有）
4. 增加超时时间

