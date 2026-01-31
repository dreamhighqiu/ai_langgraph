# Docker 构建 uv 卡顿问题修复

## 🔍 问题描述

Docker 构建时，`uv pip install` 命令卡住，没有响应。

**可能原因：**
- uv 在处理某些依赖时可能卡住
- 网络连接问题
- uv 的某些内部问题

---

## ✅ 已完成的修复

### 修复策略

**优先使用 pip，uv 作为备用：**

1. **anything-chat-rag/Dockerfile** - 已更新
2. **Dockerfile.backend** - 已更新

**修复内容：**
- 优先使用 `pip install`（已配置镜像源和超时）
- uv 作为备用方案
- 添加了多个备用镜像源

---

## 📊 修复前后对比

### 修复前

```dockerfile
# 优先使用 uv，可能卡住
RUN uv pip install --system -r requirements.txt || \
    (pip install ...)
```

### 修复后

```dockerfile
# 优先使用 pip（已配置镜像源），uv 作为备用
RUN pip install --timeout=300 --retries=5 -r requirements.txt || \
    (pip install --timeout=300 --retries=5 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt) || \
    (echo "尝试使用 uv..." && uv pip install --system -r requirements.txt)
```

---

## 🚀 如果仍然卡住

### 选项 1: 完全移除 uv

如果不需要 uv，可以完全移除：

```dockerfile
# 移除 uv 安装
# RUN pip install --no-cache-dir --timeout=300 uv

# 直接使用 pip
RUN pip install --timeout=300 --retries=5 -r requirements.txt
```

### 选项 2: 增加超时时间

```dockerfile
# 增加超时到 600 秒
RUN pip install --timeout=600 --retries=10 -r requirements.txt
```

### 选项 3: 分步安装

如果单个命令失败，可以分步安装：

```dockerfile
# 先安装核心依赖
RUN pip install --timeout=300 --retries=5 -r requirements.txt || true

# 再安装其他依赖
RUN pip install --timeout=300 --retries=5 some-package
```

### 选项 4: 使用构建缓存

```bash
# 使用构建缓存加速
docker compose build --progress=plain lightrag
```

---

## 🔧 调试建议

### 1. 查看详细日志

```bash
# 查看详细构建日志
docker compose build --progress=plain lightrag 2>&1 | tee build.log
```

### 2. 测试单个命令

```bash
# 进入临时容器测试
docker run -it --rm python:3.11-slim bash
pip install --timeout=300 -r requirements.txt
```

### 3. 检查网络连接

```bash
# 测试镜像源连接
curl -I https://pypi.tuna.tsinghua.edu.cn/simple/
curl -I https://mirrors.aliyun.com/pypi/simple/
```

---

## 📝 当前配置

### pip 配置

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
timeout = 300
retries = 5
```

### 安装顺序

1. **pip + 清华大学镜像源**（主要）
2. **pip + 阿里云镜像源**（备用）
3. **uv**（最后备用）

---

## ✅ 总结

**已完成的修复：**
- ✅ 优先使用 pip（已配置镜像源）
- ✅ uv 作为备用方案
- ✅ 多个备用镜像源
- ✅ 增加超时和重试

**预期效果：**
- 构建速度更快
- 减少卡顿问题
- 提高构建成功率

**如果仍然卡住：**
1. 检查网络连接
2. 尝试完全移除 uv
3. 增加超时时间
4. 查看详细日志

