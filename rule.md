# AI 智能体编写代码规范规则

## 1. 总体原则

- **专业工程师标准**：遵循企业级代码规范
- **可扩展性**：代码必须易于扩展和维护
- **复用性强**：提高代码复用率，减少重复代码
- **中文注释**：所有代码注释使用中文
- **无版权声明**：不添加任何版权或授权声明
- **README文件保存docs目录下**：生成的操作手册不要啰嗦，保存到 docs 目录，不要每次执行任务都生成大量手册
- **调试或者测试文件保存到debug目录下**：测试文件生成到 debug 目录下

## 2. Python 编码规范

### 2.1 文件结构

```
文件头注释（模块说明）
  ↓
导入语句（标准库 → 第三方库 → 本地库）
  ↓
常量定义
  ↓
类定义
  ↓
函数定义
  ↓
主程序入口
```

### 2.2 命名规范

- **模块名**：小写，用下划线分隔（`test_case_generator.py`）
- **类名**：PascalCase（`TestCaseGenerator`）
- **函数名**：snake_case（`generate_test_cases`）
- **常量名**：UPPER_SNAKE_CASE（`MAX_RETRY_COUNT`）
- **私有变量**：前缀下划线（`_internal_state`）

### 2.3 代码风格

- **缩进**：4 个空格
- **行长**：最多 100 个字符
- **空行**：类之间 2 行，方法之间 1 行
- **导入**：每行一个，按字母顺序排列
- **字符串**：优先使用双引号

### 2.4 注释规范

```python
# 单行注释：说明代码意图
"""
多行注释/文档字符串：
- 模块级别：说明模块功能
- 类级别：说明类的用途和主要方法
- 函数级别：说明参数、返回值、异常
"""

def function_name(param1: str, param2: int) -> dict:
    """
    函数简要说明
  
    详细说明（如需要）
  
    参数:
        param1: 参数1说明
        param2: 参数2说明
  
    返回:
        返回值说明
  
    异常:
        ValueError: 异常情况说明
    """
    pass
```

### 2.5 类设计规范

```python
class MyClass:
    """类说明"""
  
    # 类变量
    CLASS_CONSTANT = "value"
  
    def __init__(self, param: str):
        """初始化方法"""
        # 实例变量
        self._private_var = param
        self.public_var = None
  
    def public_method(self) -> str:
        """公开方法"""
        return self._private_var
  
    def _private_method(self) -> None:
        """私有方法"""
        pass
```

### 2.6 函数设计规范

- **单一职责**：一个函数只做一件事
- **参数个数**：不超过 5 个，多于 5 个用对象传递
- **返回值**：明确指定返回类型
- **异常处理**：明确捕获和处理异常
- **长度**：单个函数不超过 50 行

### 2.7 类型提示

```python
from typing import List, Dict, Optional, Union

def process_data(
    items: List[str],
    config: Dict[str, any],
    callback: Optional[callable] = None
) -> Union[str, None]:
    """使用类型提示提高代码可读性"""
    pass
```

### 2.8 错误处理

```python
try:
    # 业务逻辑
    result = risky_operation()
except SpecificException as e:
    # 处理特定异常
    logger.error(f"特定错误: {e}")
    raise
except Exception as e:
    # 处理通用异常
    logger.error(f"未知错误: {e}")
    raise
finally:
    # 清理资源
    cleanup()
```

### 2.9 日志规范

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

## 3. 前端编码规范

### 3.1 TypeScript/React 规范

- **文件命名**：PascalCase for components（`TestCaseGenerator.tsx`）
- **变量命名**：camelCase（`testCaseData`）
- **常量命名**：UPPER_SNAKE_CASE（`MAX_ITEMS`）
- **类型定义**：使用 interface 而非 type（除非必要）

### 3.2 组件结构

```typescript
// 导入
import React, { useState, useEffect } from 'react';
import { ComponentType } from './types';

// 类型定义
interface Props {
  title: string;
  onSubmit: (data: any) => void;
}

interface State {
  loading: boolean;
  error: string | null;
}

// 组件
export function MyComponent({ title, onSubmit }: Props) {
  const [state, setState] = useState<State>({
    loading: false,
    error: null,
  });

  useEffect(() => {
    // 副作用逻辑
  }, []);

  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

### 3.3 样式规范

- **CSS 类名**：kebab-case（`test-case-container`）
- **Tailwind**：优先使用 Tailwind 工具类
- **自定义样式**：使用 CSS Modules 或 styled-components

### 3.4 代码组织

```
src/
├── components/          # 可复用组件
│   ├── Button.tsx
│   └── Form.tsx
├── pages/              # 页面组件
│   └── Dashboard.tsx
├── hooks/              # 自定义 hooks
│   └── useApi.ts
├── types/              # 类型定义
│   └── index.ts
├── utils/              # 工具函数
│   └── helpers.ts
└── styles/             # 全局样式
    └── globals.css
```

## 4. 企业级编码规范

### 4.1 代码审查清单

- [ ] 代码符合命名规范
- [ ] 有完整的注释和文档
- [ ] 没有硬编码的值
- [ ] 有适当的错误处理
- [ ] 有单元测试
- [ ] 代码可读性强
- [ ] 没有重复代码
- [ ] 性能满足要求

### 4.2 版本控制

- **提交信息**：`[类型] 简要说明`
  - `[feat]` 新功能
  - `[fix]` 修复
  - `[refactor]` 重构
  - `[docs]` 文档
  - `[test]` 测试

### 4.3 文档要求

- **README**：项目概述、安装、使用
- **API 文档**：接口说明、参数、返回值
- **操作手册**：简洁、清晰、可执行
- **存储位置**：`docs/` 目录

### 4.4 测试规范

- **单元测试**：覆盖率 > 80%
- **集成测试**：关键流程
- **测试文件位置**：`debug/` 目录
- **命名规范**：`test_*.py` 或 `*.test.ts`

### 4.5 性能要求

- **API 响应时间**：< 2s
- **前端加载时间**：< 3s
- **数据库查询**：< 1s
- **内存占用**：合理范围内

## 5. 文件生成规范

### 5.1 代码文件

- 位置：项目根目录或对应模块目录
- 格式：`.py`（Python）、`.tsx`（React）、`.ts`（TypeScript）
- 包含：模块说明、导入、实现、测试

### 5.2 测试文件

- 位置：`debug/` 目录
- 命名：`test_*.py` 或 `*.test.ts`
- 内容：单元测试、集成测试、性能测试

### 5.3 文档文件

- 位置：`docs/` 目录
- 格式：`.md`（Markdown）
- 内容：简洁、清晰、可执行
- 原则：**不啰嗦**，避免冗余信息

### 5.4 文档生成原则

- **不重复生成**：避免每次都生成大量文档
- **按需生成**：只生成必要的文档
- **增量更新**：更新现有文档而非重新生成
- **简洁明了**：避免冗长的说明

## 6. 代码复用性设计

### 6.1 模块化设计

```python
# 好的设计：高内聚、低耦合
class DataProcessor:
    """数据处理器基类"""
    def process(self, data: any) -> any:
        raise NotImplementedError

class JsonProcessor(DataProcessor):
    """JSON 处理器"""
    def process(self, data: str) -> dict:
        return json.loads(data)

class CsvProcessor(DataProcessor):
    """CSV 处理器"""
    def process(self, data: str) -> list:
        return list(csv.reader(data.split('\n')))
```

### 6.2 工厂模式

```python
class ProcessorFactory:
    """处理器工厂"""
    _processors = {
        'json': JsonProcessor,
        'csv': CsvProcessor,
    }
  
    @classmethod
    def create(cls, type_name: str) -> DataProcessor:
        """创建处理器"""
        processor_class = cls._processors.get(type_name)
        if not processor_class:
            raise ValueError(f"未知类型: {type_name}")
        return processor_class()
```

### 6.3 配置管理

```python
# config.py
class Config:
    """配置管理"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    API_TIMEOUT = 30
  
    @classmethod
    def from_env(cls):
        """从环境变量加载配置"""
        cls.DEBUG = os.getenv('DEBUG', 'False') == 'True'
        cls.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        return cls
```
