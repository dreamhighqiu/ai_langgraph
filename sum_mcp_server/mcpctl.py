from __future__ import annotations

import argparse
import json
import os
import platform
import re
import signal
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import shutil
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"


@dataclass(frozen=True)
class Service:
    id: str
    name: str
    type: str
    transport: str
    entrypoint: str
    default_port: int | None
    port_env: str | None
    args: list[str]
    pid_file: str
    log_file: str
    env: dict[str, str]
    health_url: str | None = None
    auto_start: bool = True
    depends_on: list[str] = field(default_factory=list)

    @property
    def entrypoint_path(self) -> Path:
        return REPO_ROOT / self.entrypoint

    @property
    def pid_path(self) -> Path:
        return REPO_ROOT / self.pid_file

    @property
    def log_path(self) -> Path:
        return REPO_ROOT / self.log_file


def _load_manifest() -> list[Service]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    services: list[Service] = []
    for item in data.get("services", []):
        services.append(
            Service(
                id=item["id"],
                name=item.get("name", item["id"]),
                type=item["type"],
                transport=item.get("transport", ""),
                entrypoint=item["entrypoint"],
                default_port=item.get("default_port"),
                port_env=item.get("port_env"),
                args=list(item.get("args", [])),
                pid_file=item["pid_file"],
                log_file=item["log_file"],
                env=dict(item.get("env", {})),
                health_url=item.get("health_url"),
                auto_start=bool(item.get("auto_start", True)),
                depends_on=list(item.get("depends_on", [])),
            )
        )
    return services


def _load_dotenv_files() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return

    # Prefer sum_mcp_server/.env, fallback to repo root .env
    sum_env = REPO_ROOT / "sum_mcp_server" / ".env"
    root_env = REPO_ROOT / ".env"
    if sum_env.exists():
        load_dotenv(sum_env, override=False)
    if root_env.exists():
        load_dotenv(root_env, override=False)


def _toposort_services(services: list[Service], *, only_auto_start: bool) -> list[Service]:
    selected = [svc for svc in services if (svc.auto_start or not only_auto_start)]
    by_id = {svc.id: svc for svc in selected}

    # Build graph (deps -> svc)
    indegree: dict[str, int] = {svc.id: 0 for svc in selected}
    outgoing: dict[str, set[str]] = {svc.id: set() for svc in selected}

    for svc in selected:
        deps = svc.depends_on or []
        for dep in deps:
            if dep not in by_id:
                # If dependency exists in manifest but is filtered out, treat as error
                # because startup order would be invalid.
                raise SystemExit(f"Service '{svc.id}' depends on missing service '{dep}'")
            outgoing[dep].add(svc.id)
            indegree[svc.id] += 1

    queue = [svc_id for svc_id, deg in indegree.items() if deg == 0]
    queue.sort()
    ordered_ids: list[str] = []

    while queue:
        current = queue.pop(0)
        ordered_ids.append(current)
        for nxt in sorted(outgoing[current]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
                queue.sort()

    if len(ordered_ids) != len(selected):
        remaining = [svc_id for svc_id, deg in indegree.items() if deg > 0]
        raise SystemExit(f"Dependency cycle detected among: {', '.join(sorted(remaining))}")

    return [by_id[svc_id] for svc_id in ordered_ids]


def _expand_with_deps(services: list[Service], root_ids: list[str]) -> list[Service]:
    by_id = {svc.id: svc for svc in services}
    visited: set[str] = set()

    def dfs(svc_id: str) -> None:
        if svc_id in visited:
            return
        svc = by_id.get(svc_id)
        if not svc:
            raise SystemExit(f"Unknown service id: {svc_id}")
        visited.add(svc_id)
        for dep in svc.depends_on or []:
            dfs(dep)

    for rid in root_ids:
        dfs(rid)

    return [by_id[sid] for sid in visited]


def _get_python_exe_for(repo_root: Path) -> Path:
    candidates = [
        repo_root / ".venv" / "Scripts" / "python.exe",
        repo_root / ".venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path(sys.executable)


def _get_python_exe() -> Path:
    return _get_python_exe_for(REPO_ROOT)


def _is_port_open(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((host, port)) == 0


def _http_ok(url: str, timeout_s: float = 1.0) -> bool:
    # NOTE: SSE endpoints keep the connection open; use a raw socket and only read headers.
    try:
        if not url.startswith("http://"):
            return False
        rest = url[len("http://") :]
        if "/" in rest:
            hostport, path = rest.split("/", 1)
            path = "/" + path
        else:
            hostport, path = rest, "/"

        if ":" in hostport:
            host, port_str = hostport.rsplit(":", 1)
            port = int(port_str)
        else:
            host, port = hostport, 80

        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Accept: text/event-stream\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode("utf-8")

        with socket.create_connection((host, port), timeout=timeout_s) as sock:
            sock.settimeout(timeout_s)
            sock.sendall(req)
            data = b""
            while b"\r\n\r\n" not in data and len(data) < 4096:
                chunk = sock.recv(512)
                if not chunk:
                    break
                data += chunk

        first_line = data.split(b"\r\n", 1)[0].decode("utf-8", errors="ignore")
        # e.g. "HTTP/1.1 200 OK"
        parts = first_line.split()
        if len(parts) < 2 or not parts[1].isdigit():
            return False
        status = int(parts[1])
        return 200 <= status < 500
    except Exception:
        return False


def _try_import_psutil():
    try:
        import psutil  # type: ignore

        return psutil
    except Exception:
        return None


def _pid_exists(pid: int) -> bool:
    psutil = _try_import_psutil()
    if psutil is not None:
        try:
            return bool(psutil.pid_exists(pid))
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _pids_listening_on_port(port: int) -> set[int]:
    psutil = _try_import_psutil()
    if psutil is not None:
        pids: set[int] = set()
        try:
            for conn in psutil.net_connections(kind="inet"):
                if not conn.laddr:
                    continue
                if conn.laddr.port != port:
                    continue
                if conn.status and conn.status.upper() != "LISTEN":
                    continue
                if conn.pid:
                    pids.add(int(conn.pid))
        except Exception:
            pass
        if pids:
            return pids

    # Fallback: netstat -ano
    try:
        if platform.system().lower().startswith("win"):
            out = subprocess.check_output(["netstat", "-ano"], text=True, encoding="utf-8", errors="ignore")
        else:
            out = subprocess.check_output(["netstat", "-anp"], text=True, encoding="utf-8", errors="ignore")
        pids: set[int] = set()
        for line in out.splitlines():
            if f":{port} " not in line and f":{port}\t" not in line:
                continue
            if "LISTEN" not in line.upper():
                continue
            parts = line.split()
            pid_part = parts[-1]
            if platform.system().lower().startswith("win"):
                if pid_part.isdigit():
                    pids.add(int(pid_part))
        return pids
    except Exception:
        return set()


def _kill_pid_tree(pid: int, timeout_s: float = 5.0) -> bool:
    psutil = _try_import_psutil()
    if psutil is not None:
        try:
            proc = psutil.Process(pid)
        except Exception:
            return False
        children = []
        try:
            children = proc.children(recursive=True)
        except Exception:
            children = []

        for child in children:
            try:
                child.terminate()
            except Exception:
                pass
        try:
            proc.terminate()
        except Exception:
            pass

        gone, alive = psutil.wait_procs([*children, proc], timeout=timeout_s)
        if alive:
            for p in alive:
                try:
                    p.kill()
                except Exception:
                    pass
            psutil.wait_procs(alive, timeout=timeout_s)
        return True

    # Fallback: best-effort
    try:
        if platform.system().lower().startswith("win"):
            subprocess.check_call(["taskkill", "/PID", str(pid), "/T", "/F"])
            return True
        os.kill(pid, signal.SIGTERM)
        return True
    except Exception:
        return False


def _validate_unique_ports(services: Iterable[Service]) -> None:
    ports: dict[int, list[str]] = {}
    for svc in services:
        if svc.default_port is None:
            continue
        ports.setdefault(int(svc.default_port), []).append(svc.id)
    duplicates = {port: ids for port, ids in ports.items() if len(ids) > 1}
    if duplicates:
        lines = ["Duplicate ports in manifest:"]
        for port, ids in sorted(duplicates.items()):
            lines.append(f"  {port}: {', '.join(ids)}")
        raise SystemExit("\n".join(lines))


def _format_cmd(cmd: list[str]) -> str:
    return " ".join([json.dumps(c, ensure_ascii=False) if " " in c else c for c in cmd])


def _meta_path(service: Service) -> Path:
    # Keep pid file as-is for compatibility; store richer metadata alongside it.
    return service.pid_path.with_suffix(".json")


def _read_meta(service: Service) -> dict[str, Any] | None:
    path = _meta_path(service)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_meta(service: Service, payload: dict[str, Any]) -> None:
    path = _meta_path(service)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _remove_meta(service: Service) -> None:
    try:
        _meta_path(service).unlink(missing_ok=True)  # py3.8+: missing_ok
    except TypeError:
        p = _meta_path(service)
        if p.exists():
            p.unlink()


def _desired_port(service: Service) -> int | None:
    if service.default_port is None:
        return None
    # Highest priority: MCPCTL_PORT_<ID>
    env_key = f"MCPCTL_PORT_{service.id.upper()}"
    raw = os.environ.get(env_key)
    if raw:
        return int(raw)
    # Next: manifest-provided port env name
    if service.port_env:
        raw = os.environ.get(service.port_env)
        if raw:
            return int(raw)
    return int(service.default_port)


def _find_free_port(start_port: int, *, avoid: set[int] | None = None) -> int:
    avoid = avoid or set()
    port = int(start_port)
    while 1 <= port <= 65535:
        if port not in avoid and not _is_port_open(port):
            return port
        port += 1
    raise SystemExit("Unable to find a free TCP port")


_TEMPLATE_RE = re.compile(r"\{([^{}]+)\}")


def _expand_templates(
    value: str,
    *,
    service: Service,
    this_port: int | None,
    ports: dict[str, int],
    env: dict[str, str],
) -> str:
    def repl(match: re.Match[str]) -> str:
        token = match.group(1).strip()
        if token in ("port", "this.port"):
            if this_port is None:
                raise SystemExit(f"{service.id} requires a port but none was provided")
            return str(int(this_port))
        if token.endswith(".port"):
            dep_id = token[: -len(".port")]
            if dep_id not in ports:
                raise SystemExit(f"Template requires unknown port: {token} (missing '{dep_id}')")
            return str(int(ports[dep_id]))
        if token.startswith("env:"):
            var = token[len("env:") :].strip()
            return str(env.get(var, ""))
        return match.group(0)

    if "{" not in value:
        return value
    return _TEMPLATE_RE.sub(repl, value)


def _build_command(
    service: Service,
    port: int | None,
    *,
    ports: dict[str, int] | None = None,
) -> tuple[list[str], dict[str, str]]:
    ports = ports or {}
    env = os.environ.copy()
    # Expand env templates after merging; allow referencing other ports.
    for k, v in service.env.items():
        # Do not override user-provided environment values.
        if env.get(k):
            continue
        env[k] = _expand_templates(v, service=service, this_port=port, ports=ports, env=env)
    if service.type == "python":
        env.setdefault("PYTHONUTF8", "1")
        env.setdefault("PYTHONIOENCODING", "utf-8")

    # Ensure vendored deps are discoverable for standalone deployment.
    vendor_root = REPO_ROOT / "sum_mcp_server" / "vendor"
    candidate_paths: list[Path] = []
    if vendor_root.exists():
        candidate_paths.append(vendor_root)
    anything_chat_rag_root = REPO_ROOT / "anything-chat-rag"
    if anything_chat_rag_root.exists():
        candidate_paths.append(anything_chat_rag_root)

    if candidate_paths:
        existing = env.get("PYTHONPATH", "").strip()
        prefix = os.pathsep.join(str(p) for p in candidate_paths)
        env["PYTHONPATH"] = prefix if not existing else prefix + os.pathsep + existing

    args: list[str] = [
        _expand_templates(part, service=service, this_port=port, ports=ports, env=env) for part in service.args
    ]

    if service.type == "python":
        python_exe = _get_python_exe()
        cmd = [str(python_exe), str(service.entrypoint_path), *args]
        return cmd, env

    if service.type == "node":
        cmd = ["node", str(service.entrypoint_path), *args]
        return cmd, env

    raise SystemExit(f"Unsupported service type: {service.type}")


def _read_pid(pid_path: Path) -> int | None:
    try:
        raw = pid_path.read_text(encoding="utf-8").strip()
        return int(raw) if raw else None
    except Exception:
        return None


def _write_pid(pid_path: Path, pid: int) -> None:
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    pid_path.write_text(str(pid), encoding="utf-8")


def _remove_pid(pid_path: Path) -> None:
    try:
        pid_path.unlink(missing_ok=True)  # py3.8+: missing_ok
    except TypeError:
        if pid_path.exists():
            pid_path.unlink()

def _tail_text_file(path: Path, *, max_lines: int = 80, max_bytes: int = 64_000) -> str:
    if not path.exists():
        return ""
    try:
        data = path.read_bytes()
        if len(data) > max_bytes:
            data = data[-max_bytes:]
        text = data.decode("utf-8", errors="ignore")
        lines = text.splitlines()
        return "\n".join(lines[-max_lines:])
    except Exception:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""


def _start_one(
    service: Service,
    port: int | None,
    *,
    ports: dict[str, int] | None = None,
    kill_port: bool,
    auto_port: bool,
    wait_s: float,
) -> int | None:
    ports = ports or {}
    if port is None:
        port = _desired_port(service)

    if port is not None:
        if _is_port_open(int(port)):
            if kill_port:
                pids = _pids_listening_on_port(int(port))
                if not pids:
                    raise SystemExit(f"Port {port} is in use but could not resolve PID(s).")
                for pid in sorted(pids):
                    _kill_pid_tree(pid)
                time.sleep(0.4)
            elif auto_port:
                avoid = set(ports.values())
                new_port = _find_free_port(int(port), avoid=avoid)
                print(f"[INFO] {service.id} port {port} is busy, switching to {new_port}")
                port = new_port
            else:
                raise SystemExit(
                    f"Port {port} is already in use. Use --kill-port to terminate the process occupying it, "
                    "or use --auto-port to pick a free port."
                )

    # If pid file exists and process alive, do not start twice
    existing_pid = _read_pid(service.pid_path)
    if existing_pid and _pid_exists(existing_pid):
        print(f"[SKIP] {service.id} already running (PID {existing_pid})")
        return port

    service.log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = service.log_path.open("a", encoding="utf-8", errors="ignore")

    # Ensure this service's port is available to template expansion for dependents.
    if port is not None:
        ports = dict(ports)
        ports[service.id] = int(port)

    cmd, env = _build_command(service, port, ports=ports)
    creationflags = 0
    if platform.system().lower().startswith("win"):
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

    proc = subprocess.Popen(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    try:
        log_handle.close()
    except Exception:
        pass
    effective_pid = int(proc.pid)
    _write_pid(service.pid_path, effective_pid)
    _write_meta(
        service,
        {
            "id": service.id,
            "pid": effective_pid,
            "port": int(port) if port is not None else None,
            "started_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "cmd": cmd,
        },
    )
    print(f"[OK] started {service.id} (PID {proc.pid}) :: {_format_cmd(cmd)}")

    # Quick fail-fast: if process exits immediately, surface logs.
    time.sleep(0.2)
    if not _pid_exists(effective_pid):
        tail = _tail_text_file(service.log_path, max_lines=120)
        if tail:
            print(f"[ERROR] {service.id} exited immediately. Log tail:\n{tail}")
        raise SystemExit(f"Failed to start {service.id} (process exited immediately)")

    if wait_s > 0 and port is not None:
        if service.health_url:
            url = service.health_url.format(port=port)
        elif service.transport == "sse":
            url = f"http://127.0.0.1:{port}/sse"
        else:
            url = f"http://127.0.0.1:{port}/"
        deadline = time.time() + wait_s
        while time.time() < deadline:
            if _http_ok(url, timeout_s=0.8):
                # Some FastMCP/uvicorn setups fork; prefer tracking the real listener PID.
                listener_pids = _pids_listening_on_port(int(port))
                if len(listener_pids) == 1:
                    effective_pid = next(iter(listener_pids))
                    _write_pid(service.pid_path, effective_pid)
                    _write_meta(
                        service,
                        {
                            "id": service.id,
                            "pid": int(effective_pid),
                            "port": int(port),
                            "started_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                            "cmd": cmd,
                        },
                    )
                return
            if not _pid_exists(effective_pid):
                tail = _tail_text_file(service.log_path, max_lines=120)
                if tail:
                    print(f"[ERROR] {service.id} exited. Log tail:\n{tail}")
                raise SystemExit(f"Failed to start {service.id} (process exited)")
            time.sleep(0.3)
        print(f"[WARN] {service.id} not responding yet: {url}")
    return port


def _stop_one(service: Service) -> None:
    pid = _read_pid(service.pid_path)
    ok = False
    if pid and _pid_exists(pid):
        ok = _kill_pid_tree(pid)
    elif service.default_port is not None:
        listener_pids = _pids_listening_on_port(int(service.default_port))
        if listener_pids:
            for listener_pid in sorted(listener_pids):
                _kill_pid_tree(listener_pid)
            ok = True
    else:
        print(f"[SKIP] {service.id} not running (no live pid)")
        _remove_pid(service.pid_path)
        _remove_meta(service)
        return
    _remove_pid(service.pid_path)
    _remove_meta(service)
    if ok:
        print(f"[OK] stopped {service.id} (PID {pid})")
    else:
        print(f"[WARN] failed to stop {service.id} (PID {pid})")


def _status_one(service: Service) -> dict[str, Any]:
    pid = _read_pid(service.pid_path)
    meta = _read_meta(service) or {}
    running = False
    if pid:
        running = _pid_exists(pid)

    port = meta.get("port")
    if port is None:
        port = _desired_port(service)
    http_ok = None
    if port is not None:
        if service.health_url:
            http_ok = _http_ok(service.health_url.format(port=port), timeout_s=0.6)
        elif service.transport == "sse":
            http_ok = _http_ok(f"http://127.0.0.1:{port}/sse", timeout_s=0.6)
        else:
            http_ok = _http_ok(f"http://127.0.0.1:{port}/", timeout_s=0.6)
        if not running and http_ok:
            # Prefer service availability over pid tracking.
            running = True
            listener_pids = _pids_listening_on_port(int(port))
            if len(listener_pids) == 1:
                pid = next(iter(listener_pids))

    return {
        "id": service.id,
        "running": running,
        "pid": pid,
        "port": port,
        "http_ok": http_ok,
        "log": str(service.log_path),
    }

def _rm_tree(path: Path) -> None:
    if not path.exists():
        return
    shutil.rmtree(path, ignore_errors=False)


def _sync_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        raise SystemExit(f"Missing source: {src}")
    if dst.exists():
        _rm_tree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)


def _vendorize(*, repo_root: Path, vendor_dir: Path) -> None:
    vendor_dir.mkdir(parents=True, exist_ok=True)

    print("[1/5] Sync lightrag -> vendor/lightrag")
    _sync_tree(repo_root / "anything-chat-rag" / "lightrag", vendor_dir / "lightrag")

    print("[2/5] Sync lightrag_webui -> vendor/lightrag_webui")
    _sync_tree(repo_root / "anything-chat-rag" / "lightrag_webui", vendor_dir / "lightrag_webui")

    print("[3/5] Sync raganything -> vendor/raganything")
    _sync_tree(repo_root / "anything-chat-rag" / "raganything", vendor_dir / "raganything")

    print("[4/5] Sync mcp_server_rag_anything -> vendor/mcp_server_rag_anything")
    _sync_tree(
        repo_root / "mcp-server" / "src" / "mcp_server_rag_anything",
        vendor_dir / "mcp_server_rag_anything",
    )

    print("[5/5] Sync automation-quality-mcp -> vendor/automation-quality-mcp")
    aq_src = repo_root / "testing-agents-service" / "src" / "api_agent" / "mcp_servers" / "automation-quality-mcp"
    aq_dst = vendor_dir / "automation-quality-mcp"
    if aq_dst.exists():
        _rm_tree(aq_dst)
    aq_dst.mkdir(parents=True, exist_ok=True)

    _sync_tree(aq_src / "src", aq_dst / "src")
    for filename in [
        "mcpServer.js",
        "run-server.js",
        "cli.js",
        "browserControl.js",
        "package.json",
        "package-lock.json",
        "README.md",
    ]:
        src_file = aq_src / filename
        if not src_file.exists():
            raise SystemExit(f"Missing source file: {src_file}")
        shutil.copy2(src_file, aq_dst / filename)

    print(f"[OK] vendor sync complete: {vendor_dir}")


def _bundle(*, repo_root: Path, out_dir: Path) -> None:
    target = repo_root / out_dir
    if target.exists():
        _rm_tree(target)
    target.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] Copy sum_mcp_server -> {out_dir.as_posix()}")
    shutil.copytree(repo_root / "sum_mcp_server", target / "sum_mcp_server")

    print("[2/3] Vendorize deps into bundle")
    _vendorize(repo_root=repo_root, vendor_dir=target / "sum_mcp_server" / "vendor")

    print("[3/3] Done")
    print(f"Bundle ready: {target}")
    print("Run:")
    print(f"  cd {target}")
    print("  python sum_mcp_server/mcpctl.py start --all")


def _run_checked(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print(f"[RUN] {_format_cmd(cmd)}")
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None, env=env)


def _setup_backend(*, repo_root: Path) -> None:
    python_exe = _get_python_exe_for(repo_root)
    req = repo_root / "sum_mcp_server" / "requirements.txt"
    if not req.exists():
        raise SystemExit(f"Missing requirements file: {req}")
    _run_checked([str(python_exe), "-m", "pip", "install", "-r", str(req)])


def _setup_frontend(*, repo_root: Path) -> None:
    npm = shutil.which("npm")
    if not npm:
        raise SystemExit("Cannot find 'npm' on PATH. Install Node.js (includes npm).")

    candidates = [
        repo_root / "sum_mcp_server" / "vendor" / "lightrag_webui",
        repo_root / "anything-chat-rag" / "lightrag_webui",
    ]
    webui_dir = next((p for p in candidates if (p / "package.json").exists()), None)
    if webui_dir is None:
        raise SystemExit("Cannot find lightrag_webui. Run `mcpctl vendorize` first or keep anything-chat-rag present.")

    # Install deps + build into ../lightrag/api/webui (as configured by Vite).
    _run_checked([npm, "ci"], cwd=webui_dir)
    _run_checked([npm, "run", "build-no-bun"], cwd=webui_dir)


def _select_services(all_services: list[Service], ids: list[str]) -> list[Service]:
    by_id = {svc.id: svc for svc in all_services}
    selected: list[Service] = []
    for service_id in ids:
        svc = by_id.get(service_id)
        if not svc:
            raise SystemExit(f"Unknown service id: {service_id}")
        selected.append(svc)
    return selected


def main(argv: list[str] | None = None) -> int:
    _load_dotenv_files()
    services = _load_manifest()
    _validate_unique_ports(services)

    parser = argparse.ArgumentParser(prog="mcpctl", description="Unified MCP manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List all MCP services")

    start_p = sub.add_parser("start", help="Start MCP service(s)")
    start_p.add_argument("id", nargs="?", help="Service id")
    start_p.add_argument("--all", action="store_true", help="Start all services")
    start_p.add_argument("--with-deps", action="store_true", help="Start dependencies first (single service only)")
    start_p.add_argument("--port", type=int, help="Override port (single service only)")
    start_p.add_argument("--kill-port", action="store_true", help="Kill process occupying the port")
    start_p.add_argument("--auto-port", action="store_true", help="Pick a free port if the desired port is busy")
    start_p.add_argument("--wait", type=float, default=8.0, help="Wait seconds for /sse health (default: 8)")

    stop_p = sub.add_parser("stop", help="Stop MCP service(s)")
    stop_p.add_argument("id", nargs="?", help="Service id")
    stop_p.add_argument("--all", action="store_true", help="Stop all services")

    sub.add_parser("status", help="Show MCP status")

    restart_p = sub.add_parser("restart", help="Restart MCP service(s)")
    restart_p.add_argument("id", nargs="?", help="Service id")
    restart_p.add_argument("--all", action="store_true", help="Restart all services")
    restart_p.add_argument("--kill-port", action="store_true", help="Kill process occupying the port")
    restart_p.add_argument("--auto-port", action="store_true", help="Pick a free port if the desired port is busy")
    restart_p.add_argument("--wait", type=float, default=8.0, help="Wait seconds for /sse health (default: 8)")

    sub.add_parser("doctor", help="Check config/vendor/ports and print suggestions")

    vendorize_p = sub.add_parser("vendorize", help="Sync vendored deps from monorepo into sum_mcp_server/vendor")
    vendorize_p.add_argument("--repo-root", type=str, default=str(REPO_ROOT), help="Monorepo root path")

    bundle_p = sub.add_parser("bundle", help="Build a standalone deployment bundle (includes vendorized deps)")
    bundle_p.add_argument("--repo-root", type=str, default=str(REPO_ROOT), help="Monorepo root path")
    bundle_p.add_argument("--out-dir", type=str, default="dist/sum_mcp_bundle", help="Output directory (relative to repo root)")

    setup_p = sub.add_parser("setup", help="One-shot setup for deployment (backend pip + frontend build)")
    setup_p.add_argument("--repo-root", type=str, default=str(REPO_ROOT), help="Monorepo root path")
    setup_p.add_argument("--backend", action="store_true", help="Setup backend only (pip install)")
    setup_p.add_argument("--frontend", action="store_true", help="Setup frontend only (npm ci + build)")

    args = parser.parse_args(argv)

    if args.cmd == "list":
        for svc in services:
            effective = _desired_port(svc)
            port = ""
            if effective is not None:
                if svc.default_port is not None and int(effective) != int(svc.default_port):
                    port = f":{effective} (default {svc.default_port})"
                else:
                    port = f":{effective}"
            suffix = "" if svc.auto_start else " (manual)"
            print(f"- {svc.id}{port} [{svc.type}/{svc.transport}] {svc.name}{suffix}")
        return 0

    if args.cmd == "start":
        if not args.all and not args.id:
            raise SystemExit("Provide <id> or use --all")
        if args.all:
            selected = _toposort_services(services, only_auto_start=True)
        else:
            if args.with_deps:
                expanded = _expand_with_deps(services, [args.id])
                # Keep only expanded set but start by dependency order
                expanded_ids = {s.id for s in expanded}
                ordered = _toposort_services(services, only_auto_start=False)
                selected = [s for s in ordered if s.id in expanded_ids]
            else:
                selected = _select_services(services, [args.id])
        if args.port is not None and args.all:
            raise SystemExit("--port can only be used when starting a single service")

        # Pre-resolve ports for template expansion like {lightrag_api.port}.
        ports: dict[str, int] = {}
        for svc in selected:
            desired = int(args.port) if args.port is not None else _desired_port(svc)
            if desired is not None:
                if desired in ports.values():
                    if bool(args.auto_port):
                        desired = _find_free_port(desired, avoid=set(ports.values()))
                    else:
                        clashing = [sid for sid, p in ports.items() if p == desired]
                        raise SystemExit(
                            f"Duplicate desired port {desired} for {svc.id} (already used by {', '.join(clashing)}). "
                            "Fix env overrides or use --auto-port."
                        )
                ports[svc.id] = int(desired)
        for svc in selected:
            desired = int(args.port) if args.port is not None else ports.get(svc.id)
            started_port = _start_one(
                svc,
                desired,
                ports=ports,
                kill_port=bool(args.kill_port),
                auto_port=bool(args.auto_port),
                wait_s=float(args.wait),
            )
            if started_port is not None:
                ports[svc.id] = int(started_port)
        return 0

    if args.cmd == "stop":
        if not args.all and not args.id:
            raise SystemExit("Provide <id> or use --all")
        if args.all:
            selected = list(reversed(_toposort_services(services, only_auto_start=False)))
        else:
            selected = _select_services(services, [args.id])
        for svc in selected:
            _stop_one(svc)
        return 0

    if args.cmd == "status":
        rows = [_status_one(svc) for svc in services]
        for row in rows:
            if row["running"]:
                if row["port"] is None:
                    print(f"[OK] {row['id']} running (PID {row['pid']})")
                else:
                    suffix = "http_ok" if row["http_ok"] else "no_http"
                    print(f"[OK] {row['id']} running (PID {row['pid']}) :{row['port']} ({suffix})")
            else:
                print(f"[X]  {row['id']} stopped")
        return 0

    if args.cmd == "restart":
        if not args.all and not args.id:
            raise SystemExit("Provide <id> or use --all")
        if args.all:
            stop_list = list(reversed(_toposort_services(services, only_auto_start=False)))
            start_list = _toposort_services(services, only_auto_start=True)
        else:
            stop_list = _select_services(services, [args.id])
            start_list = _select_services(services, [args.id])

        for svc in stop_list:
            _stop_one(svc)

        ports: dict[str, int] = {}
        for svc in start_list:
            desired = _desired_port(svc)
            if desired is not None:
                if desired in ports.values():
                    if bool(args.auto_port):
                        desired = _find_free_port(desired, avoid=set(ports.values()))
                    else:
                        clashing = [sid for sid, p in ports.items() if p == desired]
                        raise SystemExit(
                            f"Duplicate desired port {desired} for {svc.id} (already used by {', '.join(clashing)}). "
                            "Fix env overrides or use --auto-port."
                        )
                ports[svc.id] = int(desired)
        for svc in start_list:
            desired = ports.get(svc.id)
            started_port = _start_one(
                svc,
                desired,
                ports=ports,
                kill_port=bool(args.kill_port),
                auto_port=bool(args.auto_port),
                wait_s=float(args.wait),
            )
            if started_port is not None:
                ports[svc.id] = int(started_port)
        return 0

    if args.cmd == "doctor":
        # Effective ports (including env overrides)
        effective_ports: dict[int, list[str]] = {}
        for svc in services:
            p = _desired_port(svc)
            if p is None:
                continue
            effective_ports.setdefault(int(p), []).append(svc.id)
        dup = {p: ids for p, ids in effective_ports.items() if len(ids) > 1}
        if dup:
            print("[X] Duplicate effective ports (env overrides caused conflict):")
            for p, ids in sorted(dup.items()):
                print(f"  {p}: {', '.join(sorted(ids))}")
        else:
            print("[OK] No duplicate effective ports")

        for svc in services:
            p = _desired_port(svc)
            if p is None:
                continue
            busy = _is_port_open(int(p))
            tag = "BUSY" if busy else "FREE"
            print(f"- port {p:>5} {tag} :: {svc.id}")

        vendor = REPO_ROOT / "sum_mcp_server" / "vendor"
        needed = [
            ("lightrag", vendor / "lightrag"),
            ("lightrag_webui", vendor / "lightrag_webui"),
            ("raganything", vendor / "raganything"),
            ("mcp_server_rag_anything", vendor / "mcp_server_rag_anything"),
            ("automation-quality-mcp", vendor / "automation-quality-mcp"),
        ]
        for name, path in needed:
            print(f"- vendor {name}: {'OK' if path.exists() else 'MISSING'} ({path})")
        return 0

    if args.cmd == "vendorize":
        repo_root = Path(args.repo_root).resolve()
        _vendorize(repo_root=repo_root, vendor_dir=REPO_ROOT / "sum_mcp_server" / "vendor")
        return 0

    if args.cmd == "bundle":
        repo_root = Path(args.repo_root).resolve()
        out_dir = Path(args.out_dir)
        _bundle(repo_root=repo_root, out_dir=out_dir)
        return 0

    if args.cmd == "setup":
        repo_root = Path(args.repo_root).resolve()
        do_backend = bool(args.backend)
        do_frontend = bool(args.frontend)
        if not do_backend and not do_frontend:
            do_backend = True
            do_frontend = True

        if do_backend:
            _setup_backend(repo_root=repo_root)
        if do_frontend:
            _setup_frontend(repo_root=repo_root)
        return 0

    raise SystemExit("Unhandled command")


if __name__ == "__main__":
    raise SystemExit(main())
