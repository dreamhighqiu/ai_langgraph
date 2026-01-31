"""
API Agent异常模块

定义API自动化测试系统中使用的自定义异常类。
"""



from typing import Optional, Dict, Any, List


class APIAgentError(Exception):
    """API Agent基础异常类"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code or "API_AGENT_ERROR"
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"[{self.code}] {self.message} - {self.details}"
        return f"[{self.code}] {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": True,
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


# ============================================================================
# 配置相关异常
# ============================================================================

class ConfigurationError(APIAgentError):
    """配置错误"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=message,
            code="CONFIG_ERROR",
            details={"config_key": config_key} if config_key else {}
        )


class MissingConfigError(ConfigurationError):
    """缺少必要配置"""
# fmt: off  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVU5SVJRPT06MzA1NWU0M2U=
    
    def __init__(self, config_key: str):
        super().__init__(
            message=f"缺少必要配置: {config_key}",
            config_key=config_key
        )
        self.code = "MISSING_CONFIG"


# ============================================================================
# MCP服务器相关异常
# ============================================================================

class MCPServerError(APIAgentError):
    """MCP服务器错误"""
    
    def __init__(
        self,
        message: str,
        server_name: Optional[str] = None,
        server_url: Optional[str] = None
    ):
        super().__init__(
            message=message,
            code="MCP_SERVER_ERROR",
            details={
                "server_name": server_name,
                "server_url": server_url
            }
        )


class MCPConnectionError(MCPServerError):
    """MCP服务器连接错误"""
    
    def __init__(self, server_name: str, server_url: str, reason: str = ""):
        super().__init__(
            message=f"无法连接到MCP服务器 '{server_name}': {reason}",
            server_name=server_name,
            server_url=server_url
        )
        self.code = "MCP_CONNECTION_ERROR"


class MCPToolError(MCPServerError):
    """MCP工具执行错误"""
    
    def __init__(
        self,
        tool_name: str,
        message: str,
        server_name: Optional[str] = None
    ):
        super().__init__(
            message=f"工具 '{tool_name}' 执行失败: {message}",
            server_name=server_name
        )
        self.code = "MCP_TOOL_ERROR"
        self.details["tool_name"] = tool_name


# ============================================================================
# 测试生成相关异常
# ============================================================================

class TestGenerationError(APIAgentError):
    """测试生成错误"""
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVU5SVJRPT06MzA1NWU0M2U=
    
    def __init__(
        self,
        message: str,
        phase: Optional[str] = None,
        file_path: Optional[str] = None
    ):
        super().__init__(
            message=message,
            code="TEST_GENERATION_ERROR",
            details={
                "phase": phase,
                "file_path": file_path
            }
        )


class InvalidTestSuiteError(TestGenerationError):
    """无效的测试套件"""
    
    def __init__(self, message: str, validation_errors: Optional[List[str]] = None):
        super().__init__(
            message=message,
            phase="validation"
        )
        self.code = "INVALID_TEST_SUITE"
        self.details["validation_errors"] = validation_errors or []


class TemplateError(TestGenerationError):
    """模板处理错误"""
    
    def __init__(self, template_name: str, message: str):
        super().__init__(
            message=f"模板 '{template_name}' 处理失败: {message}",
            phase="template_rendering"
        )
        self.code = "TEMPLATE_ERROR"
        self.details["template_name"] = template_name


# ============================================================================
# 测试执行相关异常
# ============================================================================
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVU5SVJRPT06MzA1NWU0M2U=

class TestExecutionError(APIAgentError):
    """测试执行错误"""
    
    def __init__(
        self,
        message: str,
        test_path: Optional[str] = None,
        exit_code: Optional[int] = None
    ):
        super().__init__(
            message=message,
            code="TEST_EXECUTION_ERROR",
            details={
                "test_path": test_path,
                "exit_code": exit_code
            }
        )


class TestTimeoutError(TestExecutionError):
    """测试超时错误"""
    
    def __init__(self, test_path: str, timeout: int):
        super().__init__(
            message=f"测试执行超时 ({timeout}秒): {test_path}",
            test_path=test_path
        )
        self.code = "TEST_TIMEOUT"
        self.details["timeout"] = timeout


class TestParseError(TestExecutionError):
    """测试结果解析错误"""
    
    def __init__(self, file_path: str, message: str):
        super().__init__(
            message=f"无法解析测试结果文件 '{file_path}': {message}",
            test_path=file_path
        )
        self.code = "TEST_PARSE_ERROR"


# ============================================================================
# API分析相关异常
# ============================================================================
# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVU5SVJRPT06MzA1NWU0M2U=

class APIAnalysisError(APIAgentError):
    """API分析错误"""
    
    def __init__(
        self,
        message: str,
        api_url: Optional[str] = None,
        spec_format: Optional[str] = None
    ):
        super().__init__(
            message=message,
            code="API_ANALYSIS_ERROR",
            details={
                "api_url": api_url,
                "spec_format": spec_format
            }
        )


class InvalidAPISpecError(APIAnalysisError):
    """无效的API规范"""
    
    def __init__(self, message: str, spec_format: str = "unknown"):
        super().__init__(
            message=message,
            spec_format=spec_format
        )
        self.code = "INVALID_API_SPEC"


class APIFetchError(APIAnalysisError):
    """API文档获取错误"""
    
    def __init__(self, api_url: str, status_code: Optional[int] = None):
        super().__init__(
            message=f"无法获取API文档: {api_url}",
            api_url=api_url
        )
        self.code = "API_FETCH_ERROR"
        self.details["status_code"] = status_code


# ============================================================================
# Agent编排相关异常
# ============================================================================

class OrchestrationError(APIAgentError):
    """编排错误"""
    
    def __init__(
        self,
        message: str,
        phase: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        super().__init__(
            message=message,
            code="ORCHESTRATION_ERROR",
            details={
                "phase": phase,
                "session_id": session_id
            }
        )


class PhaseExecutionError(OrchestrationError):
    """阶段执行错误"""
    
    def __init__(self, phase: str, message: str, session_id: Optional[str] = None):
        super().__init__(
            message=f"阶段 '{phase}' 执行失败: {message}",
            phase=phase,
            session_id=session_id
        )
        self.code = "PHASE_EXECUTION_ERROR"


class SubAgentError(OrchestrationError):
    """子Agent错误"""
    
    def __init__(
        self,
        agent_name: str,
        message: str,
        session_id: Optional[str] = None
    ):
        super().__init__(
            message=f"子Agent '{agent_name}' 错误: {message}",
            session_id=session_id
        )
        self.code = "SUBAGENT_ERROR"
        self.details["agent_name"] = agent_name

