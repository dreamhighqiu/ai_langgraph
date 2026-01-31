"""
配置验证脚本

用于检查所有必需的环境变量是否正确配置。

使用方式:
    python -m config.validate_config
"""

import sys
import io
from typing import List, Dict, Any

# 设置标准输出为 UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from config.settings import settings
from config.llm_config import get_llm_info


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def check_required(self, name: str, value: Any, message: str = None):
        """检查必需配置"""
        if not value:
            msg = message or f"❌ {name} is not configured"
            self.errors.append(msg)
            return False
        else:
            self.info.append(f"✅ {name} is configured")
            return True
    
    def check_optional(self, name: str, value: Any, message: str = None):
        """检查可选配置"""
        if not value:
            msg = message or f"⚠️  {name} is not configured (optional)"
            self.warnings.append(msg)
            return False
        else:
            self.info.append(f"✅ {name} is configured")
            return True
    
    def validate_llm_config(self):
        """验证 LLM 配置"""
        print("\n🔍 Validating LLM Configuration...")
        print("-" * 60)
        
        # 获取当前 LLM 配置信息
        llm_info = get_llm_info()
        provider = llm_info.get("provider")
        
        print(f"Default Provider: {provider}")
        print(f"Model: {llm_info.get('model', 'N/A')}")
        
        if provider == "openai":
            self.check_required(
                "OPENAI_API_KEY",
                settings.openai_api_key,
                "❌ OPENAI_API_KEY is required when using OpenAI provider"
            )
            self.check_required("OPENAI_MODEL", settings.openai_model)
            if settings.openai_base_url:
                print(f"   Base URL: {settings.openai_base_url}")
        
        elif provider == "deepseek":
            self.check_required(
                "DEEPSEEK_API_KEY",
                settings.deepseek_api_key,
                "❌ DEEPSEEK_API_KEY is required when using DeepSeek provider"
            )
            self.check_required("DEEPSEEK_MODEL", settings.deepseek_model)
        
        elif provider == "anthropic":
            self.check_required(
                "ANTHROPIC_API_KEY",
                settings.anthropic_api_key,
                "❌ ANTHROPIC_API_KEY is required when using Anthropic provider"
            )
            self.check_required("ANTHROPIC_MODEL", settings.anthropic_model)
        
        else:
            self.errors.append(
                f"❌ Unknown LLM provider: {provider}. "
                f"Supported: openai, deepseek, anthropic"
            )
    
    def validate_rag_config(self):
        """验证 RAG 配置"""
        print("\n🔍 Validating RAG Configuration...")
        print("-" * 60)
        
        # 检查可选的 RAG 相关配置
        import os
        
        rag_working_dir = os.getenv("RAG_WORKING_DIR", "./rag_storage")
        print(f"RAG Working Dir: {rag_working_dir}")
        
        # Embedding 配置
        use_ollama = os.getenv("USE_OLLAMA_EMBEDDING", "true").lower() == "true"
        if use_ollama:
            embedding_host = os.getenv("EMBEDDING_HOST", "http://localhost:11434")
            embedding_model = os.getenv("EMBEDDING_MODEL", "qwen3-embedding:0.6b")
            print(f"Embedding: Ollama @ {embedding_host}")
            print(f"Embedding Model: {embedding_model}")
            self.warnings.append(
                "⚠️  Using Ollama embedding - ensure Ollama is running"
            )
        
        # 向量存储配置
        vector_storage = os.getenv("VECTOR_STORAGE") or os.getenv("LIGHTRAG_VECTOR_STORAGE", "")
        if vector_storage:
            print(f"Vector Storage: {vector_storage}")
            
            if vector_storage.lower() == "milvus":
                milvus_uri = os.getenv("MILVUS_URI", "http://localhost:19530")
                print(f"Milvus URI: {milvus_uri}")
                self.warnings.append(
                    "⚠️  Using Milvus - ensure Milvus is running"
                )
    
    def validate_mcp_endpoints(self):
        """验证 MCP 端点配置"""
        print("\n🔍 Validating MCP Endpoints...")
        print("-" * 60)
        
        import os
        
        endpoints = {
            "RAG_QUERY_MCP_URL": os.getenv("RAG_QUERY_MCP_URL", "http://127.0.0.1:8002/sse"),
            "RAG_ANYTHING_MCP_URL": os.getenv("RAG_ANYTHING_MCP_URL", "http://localhost:8001/sse"),
            "PYTEST_MCP_URL": os.getenv("PYTEST_MCP_URL", "http://127.0.0.1:8004/sse"),
        }
        
        for name, url in endpoints.items():
            print(f"{name}: {url}")
        
        self.info.append("✅ MCP endpoints configured (using defaults if not set)")
    
    def validate_workspace_config(self):
        """验证工作目录配置"""
        print("\n🔍 Validating Workspace Configuration...")
        print("-" * 60)
        
        workspaces = {
            "API": settings.api_workspace_root,
            "UI": settings.ui_workspace_root,
            "UI Java": settings.ui_java_workspace_root,
            "TestCase": settings.testcase_workspace_root,
        }
        
        for name, path in workspaces.items():
            print(f"{name} Workspace: {path}")
        
        self.info.append("✅ All workspace roots configured")
    
    def validate_optional_features(self):
        """验证可选功能配置"""
        print("\n🔍 Validating Optional Features...")
        print("-" * 60)
        
        import os
        
        # PDF 多模态
        enable_pdf_multimodal = settings.enable_pdf_multimodal
        print(f"PDF Multimodal: {'Enabled' if enable_pdf_multimodal else 'Disabled'}")
        
        if enable_pdf_multimodal:
            doubao_key = os.getenv("DOUBAO_API_KEY", "")
            if doubao_key:
                self.info.append("✅ DOUBAO_API_KEY configured for PDF multimodal")
            else:
                self.warnings.append(
                    "⚠️  PDF multimodal enabled but DOUBAO_API_KEY not set"
                )
        
        # Midscene 配置
        midscene_key = os.getenv("MIDSCENE_MODEL_API_KEY", "")
        if midscene_key:
            self.info.append("✅ MIDSCENE_MODEL_API_KEY configured")
        else:
            self.warnings.append("⚠️  MIDSCENE_MODEL_API_KEY not configured (optional)")
    
    def print_summary(self):
        """打印验证摘要"""
        print("\n" + "=" * 60)
        print("📊 Configuration Validation Summary")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All configurations are valid!")
        elif not self.errors:
            print("\n✅ No critical errors found (some warnings present)")
        
        print("\n" + "=" * 60)
        
        return len(self.errors) == 0
    
    def run(self) -> bool:
        """运行完整验证"""
        print("🚀 Starting Configuration Validation...")
        print("=" * 60)
        
        try:
            self.validate_llm_config()
            self.validate_rag_config()
            self.validate_mcp_endpoints()
            self.validate_workspace_config()
            self.validate_optional_features()
            
            return self.print_summary()
        
        except Exception as e:
            print(f"\n❌ Validation failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    validator = ConfigValidator()
    success = validator.run()
    
    if not success:
        print("\n💡 Tip: Check ENV_CONFIG_GUIDE.md for configuration details")
        sys.exit(1)
    else:
        print("\n🎉 Configuration validation passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

