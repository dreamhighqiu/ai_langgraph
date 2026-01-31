"""
工作区管理器

管理基于时间戳和 URL 的工作区目录
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


class WorkspaceManager:
    """工作区管理器 - 基于时间戳 + URL 创建独立工作目录"""
    
    # 会话状态文件名
    SESSION_STATE_FILE = ".workspace_session.json"
    
    def __init__(self, base_root: Path):
        """
        初始化工作区管理器
        
        Args:
            base_root: 基础工作区根目录
        """
        self.base_root = Path(base_root)
        self.base_root.mkdir(parents=True, exist_ok=True)
        self._current_workspace: Optional[Path] = None
        self._current_url: Optional[str] = None
        
        # 尝试恢复上次会话
        self._load_session_state()
    
    def _load_session_state(self):
        """加载会话状态（用于跨请求保持工作区）"""
        state_file = self.base_root / self.SESSION_STATE_FILE
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text(encoding='utf-8'))
                workspace_path = Path(state.get('workspace', ''))
                if workspace_path.exists():
                    self._current_workspace = workspace_path
                    self._current_url = state.get('url', '')
            except Exception:
                pass  # 忽略加载错误
    
    def _save_session_state(self):
        """保存会话状态"""
        if self._current_workspace:
            state = {
                'workspace': str(self._current_workspace),
                'url': self._current_url or '',
                'updated_at': datetime.now().isoformat()
            }
            state_file = self.base_root / self.SESSION_STATE_FILE
            try:
                state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
            except Exception:
                pass  # 忽略保存错误
    
    def clear_session(self):
        """清除会话状态（用于开始全新对话）"""
        self._current_workspace = None
        self._current_url = None
        state_file = self.base_root / self.SESSION_STATE_FILE
        if state_file.exists():
            try:
                state_file.unlink()
            except Exception:
                pass
    
    @staticmethod
    def extract_page_name(url: str) -> str:
        """
        从 URL 中提取页面名称
        
        Args:
            url: 页面 URL
        
        Returns:
            页面名称（URL 最后一段路径或域名）
        
        Examples:
            >>> WorkspaceManager.extract_page_name("https://chat.deepseek.com/dashboard")
            "dashboard"
            >>> WorkspaceManager.extract_page_name("https://github.com/user/repo")
            "repo"
            >>> WorkspaceManager.extract_page_name("https://example.com/")
            "example"
        """
        if not url:
            return "unknown"
        
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            if not path:
                # 根路径 - 使用域名的第一部分
                hostname = parsed.hostname or "unknown"
                # 移除 www. 前缀和 .com/.org 等后缀
                name = hostname.split('.')[0]
                if name == 'www' and len(hostname.split('.')) > 1:
                    name = hostname.split('.')[1]
                return name if name else "home"
            
            # 获取最后一段路径
            segments = path.split('/')
            last_segment = segments[-1] if segments else "home"
            
            # 清理特殊字符，保留字母数字和连字符
            clean_name = re.sub(r'[^\w\-]', '-', last_segment)
            # 移除连续的连字符
            clean_name = re.sub(r'-+', '-', clean_name).strip('-')
            
            # 确保名称有效且长度合理
            if len(clean_name) > 50:
                clean_name = clean_name[:50]
            
            return clean_name if clean_name else "page"
            
        except Exception:
            return "unknown"
    
    @staticmethod
    def generate_workspace_name(url: str, timestamp: datetime = None) -> str:
        """
        生成工作区目录名称
        
        格式: {page_name}_{YYYYMMDD}_{HHMMSS}
        
        Args:
            url: 页面 URL
            timestamp: 时间戳（默认为当前时间）
        
        Returns:
            工作区目录名称
        
        Examples:
            >>> WorkspaceManager.generate_workspace_name("https://chat.deepseek.com/dashboard")
            "dashboard_20260131_143025"
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        page_name = WorkspaceManager.extract_page_name(url)
        time_str = timestamp.strftime('%Y%m%d_%H%M%S')
        
        return f"{page_name}_{time_str}"
    
    def create_workspace(self, url: str, timestamp: datetime = None) -> Path:
        """
        创建新的工作区目录
        
        Args:
            url: 页面 URL
            timestamp: 时间戳（默认为当前时间）
        
        Returns:
            工作区目录路径
        """
        workspace_name = self.generate_workspace_name(url, timestamp)
        workspace_path = self.base_root / workspace_name
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录结构
        subdirs = ["pageobjects", "testcases", "reports", "excel", "helpers"]
        for subdir in subdirs:
            (workspace_path / subdir).mkdir(exist_ok=True)
        
        # 创建 README
        readme_content = f"""# 工作区: {workspace_name}

## 基本信息
- **创建时间**: {timestamp or datetime.now()}
- **页面 URL**: {url}
- **页面名称**: {self.extract_page_name(url)}

## 目录结构
```
{workspace_name}/
├── pageobjects/    # Page Object 类文件
├── testcases/      # 测试用例文件
├── reports/        # 测试计划和报告
├── excel/          # 导出的 Excel 文件
├── helpers/        # Helper 类文件
└── README.md       # 本文件
```

## 生成的文件
此目录由 UI Java Agent 自动生成，包含：
1. Java PageObject 类
2. 测试用例 Excel
3. 测试计划和变更检测报告
4. Helper 工具类
"""
        (workspace_path / "README.md").write_text(readme_content, encoding='utf-8')
        
        self._current_workspace = workspace_path
        self._current_url = url
        
        # 保存会话状态
        self._save_session_state()
        
        return workspace_path
    
    def get_or_create_workspace(self, url: str) -> Path:
        """
        获取或创建工作区
        
        如果当前已有工作区且 URL 相同，返回现有工作区
        否则创建新工作区
        
        Args:
            url: 页面 URL
        
        Returns:
            工作区目录路径
        """
        # 标准化 URL 比较（移除末尾斜杠）
        normalized_url = url.rstrip('/')
        current_normalized = (self._current_url or '').rstrip('/')
        
        if self._current_workspace and self._current_workspace.exists() and current_normalized == normalized_url:
            return self._current_workspace
        
        return self.create_workspace(url)
    
    def set_current_workspace(self, workspace_path: Path, url: str = ""):
        """
        手动设置当前工作区
        
        Args:
            workspace_path: 工作区路径
            url: 关联的 URL
        """
        if workspace_path.exists():
            self._current_workspace = workspace_path
            self._current_url = url
            self._save_session_state()
    
    @property
    def current_workspace(self) -> Optional[Path]:
        """获取当前工作区路径"""
        return self._current_workspace
    
    @property
    def current_url(self) -> Optional[str]:
        """获取当前 URL"""
        return self._current_url
    
    @property
    def pageobjects_dir(self) -> Optional[Path]:
        """获取 PageObject 目录"""
        if self._current_workspace:
            path = self._current_workspace / "pageobjects"
            path.mkdir(exist_ok=True)
            return path
        return None
    
    @property
    def testcases_dir(self) -> Optional[Path]:
        """获取测试用例目录"""
        if self._current_workspace:
            path = self._current_workspace / "testcases"
            path.mkdir(exist_ok=True)
            return path
        return None
    
    @property
    def reports_dir(self) -> Optional[Path]:
        """获取报告目录"""
        if self._current_workspace:
            path = self._current_workspace / "reports"
            path.mkdir(exist_ok=True)
            return path
        return None
    
    @property
    def excel_dir(self) -> Optional[Path]:
        """获取 Excel 目录"""
        if self._current_workspace:
            path = self._current_workspace / "excel"
            path.mkdir(exist_ok=True)
            return path
        return None
    
    @property
    def helpers_dir(self) -> Optional[Path]:
        """获取 Helper 目录"""
        if self._current_workspace:
            path = self._current_workspace / "helpers"
            path.mkdir(exist_ok=True)
            return path
        return None
    
    def list_workspaces(self) -> list:
        """列出所有工作区"""
        workspaces = []
        for item in self.base_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                workspaces.append({
                    'name': item.name,
                    'path': str(item),
                    'created': datetime.fromtimestamp(item.stat().st_ctime)
                })
        
        # 按创建时间倒序排列
        workspaces.sort(key=lambda x: x['created'], reverse=True)
        return workspaces
    
    def get_latest_workspace(self, page_name: str = None) -> Optional[Path]:
        """
        获取最新的工作区
        
        Args:
            page_name: 可选，按页面名称过滤
        
        Returns:
            最新工作区路径
        """
        workspaces = self.list_workspaces()
        
        if page_name:
            workspaces = [w for w in workspaces if w['name'].startswith(page_name)]
        
        if workspaces:
            latest = Path(workspaces[0]['path'])
            # 自动设置为当前工作区
            self._current_workspace = latest
            self._save_session_state()
            return latest
        return None
    
    def use_workspace(self, workspace_name: str) -> Optional[Path]:
        """
        切换到指定工作区
        
        Args:
            workspace_name: 工作区名称或部分名称
        
        Returns:
            工作区路径，如果找到的话
        """
        for ws in self.list_workspaces():
            if workspace_name in ws['name']:
                workspace_path = Path(ws['path'])
                self._current_workspace = workspace_path
                self._save_session_state()
                return workspace_path
        return None


# 便捷函数
def create_session_workspace(base_root: str, url: str) -> Path:
    """
    创建会话工作区
    
    Args:
        base_root: 基础根目录
        url: 页面 URL
    
    Returns:
        工作区路径
    """
    manager = WorkspaceManager(Path(base_root))
    return manager.create_workspace(url)


def get_workspace_path(base_root: str, url: str, subdir: str = None) -> Path:
    """
    获取工作区子目录路径
    
    Args:
        base_root: 基础根目录
        url: 页面 URL
        subdir: 子目录名称 (pageobjects/testcases/reports/excel/helpers)
    
    Returns:
        目录路径
    """
    manager = WorkspaceManager(Path(base_root))
    workspace = manager.get_or_create_workspace(url)
    
    if subdir:
        return workspace / subdir
    return workspace
