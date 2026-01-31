import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


def ui_playwright_codegen(
    url: str,
    output_path: Optional[str] = None,
    language: str = "python",
) -> Dict[str, Any]:
    """Run Playwright codegen to record test steps."""
    target = language.lower()
    if target == "typescript":
        target = "ts"
    if target not in {"python", "java", "javascript", "ts"}:
        raise ValueError("Unsupported language for codegen.")

    cmd = ["playwright", "codegen", "--target", target]
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cmd += ["-o", output_path]
    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    return {
        "command": " ".join(cmd),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_path": output_path,
    }
