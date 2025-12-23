"""Test Executor Sub-Agent for K6 Performance Testing.

This module provides the test executor sub-agent that specializes
in running K6 tests and monitoring their execution.
"""



from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
import subprocess
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionConfig:
    """Configuration for test execution."""
    script_path: str
    output_path: Optional[str] = None
    vus: Optional[int] = None
    duration: Optional[str] = None
    env_vars: Optional[Dict[str, str]] = None
    tags: Optional[Dict[str, str]] = None
    cloud: bool = False
    project_id: Optional[str] = None
# pragma: no cover  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVhGeWVBPT06ZTE5ZjFhZmE=


@dataclass
class ExecutionResult:
    """Result of test execution."""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    output_file: Optional[str] = None
    duration_seconds: float = 0.0
    
    @property
    def output(self) -> str:
        return self.stdout + self.stderr

# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVhGeWVBPT06ZTE5ZjFhZmE=

class TestExecutorAgent:
    """Sub-agent specialized in K6 test execution.
    
    This agent handles:
    - Local test execution
    - Cloud test execution
    - Real-time monitoring
    - Output management
    
    Example:
        >>> executor = TestExecutorAgent()
        >>> result = executor.run_test(
        ...     script_path="./scripts/load_test.js",
        ...     output_path="./results/load_test.json",
        ... )
    """
    
    def __init__(
        self,
        k6_binary: str = "k6",
        default_timeout: int = 3600,
    ):
        """Initialize the test executor agent.
        
        Args:
            k6_binary: Path to K6 binary.
            default_timeout: Default execution timeout in seconds.
        """
        self.k6_binary = k6_binary
        self.default_timeout = default_timeout
    
    def run_test(
        self,
        script_path: str,
        output_path: Optional[str] = None,
        vus: Optional[int] = None,
        duration: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        """Run a K6 test locally.
        
        Args:
            script_path: Path to the K6 script.
            output_path: Optional path for JSON output.
            vus: Optional VU count override.
            duration: Optional duration override.
            env_vars: Optional environment variables.
            tags: Optional tags for the test run.
            timeout: Optional execution timeout.
            
        Returns:
            ExecutionResult with test output and status.
        """
        import time
        start_time = time.time()
        
        # Build command
        cmd = [self.k6_binary, "run"]
        
        if output_path:
            cmd.extend(["--out", f"json={output_path}"])
        
        if vus:
            cmd.extend(["--vus", str(vus)])
        
        if duration:
            cmd.extend(["--duration", duration])
        
        if tags:
            for key, value in tags.items():
                cmd.extend(["--tag", f"{key}={value}"])
        
        cmd.append(script_path)
        
        # Prepare environment
        import os
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=timeout or self.default_timeout,
            )
# fmt: off  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVhGeWVBPT06ZTE5ZjFhZmE=
            
            duration_seconds = time.time() - start_time
            
            return ExecutionResult(
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                output_file=output_path,
                duration_seconds=duration_seconds,
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="Test execution timed out",
            )
        except FileNotFoundError:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"K6 binary not found: {self.k6_binary}",
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
            )
    
    def run_cloud(
        self,
        script_path: str,
        project_id: Optional[str] = None,
    ) -> ExecutionResult:
        """Run a K6 test on K6 Cloud.
        
        Args:
            script_path: Path to the K6 script.
            project_id: Optional K6 Cloud project ID.
            
        Returns:
            ExecutionResult with cloud upload status.
        """
        cmd = [self.k6_binary, "cloud"]
        
        if project_id:
            cmd.extend(["--project-id", project_id])
        
        cmd.append(script_path)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            return ExecutionResult(
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
            )

# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVhGeWVBPT06ZTE5ZjFhZmE=
