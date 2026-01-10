from __future__ import annotations

import argparse
import json
import os
import platform
import signal
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
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
    args: list[str]
    pid_file: str
    log_file: str
    env: dict[str, str]
    health_url: str | None = None
    auto_start: bool = True

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
                args=list(item.get("args", [])),
                pid_file=item["pid_file"],
                log_file=item["log_file"],
                env=dict(item.get("env", {})),
                health_url=item.get("health_url"),
                auto_start=bool(item.get("auto_start", True)),
            )
        )
    return services


def _get_python_exe() -> Path:
    candidates = [
        REPO_ROOT / ".venv" / "Scripts" / "python.exe",
        REPO_ROOT / ".venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path(sys.executable)


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


def _build_command(service: Service, port: int | None) -> tuple[list[str], dict[str, str]]:
    env = os.environ.copy()
    env.update(service.env)
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

    args: list[str] = []
    for part in service.args:
        if part == "{port}":
            if port is None:
                raise SystemExit(f"{service.id} requires a port but none was provided")
            args.append(str(port))
        else:
            args.append(part)

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


def _start_one(service: Service, port: int | None, *, kill_port: bool, wait_s: float) -> None:
    if port is None:
        port = service.default_port

    if port is not None:
        if _is_port_open(int(port)):
            if not kill_port:
                raise SystemExit(
                    f"Port {port} is already in use. Use --kill-port to terminate the process occupying it."
                )
            pids = _pids_listening_on_port(int(port))
            if not pids:
                raise SystemExit(f"Port {port} is in use but could not resolve PID(s).")
            for pid in sorted(pids):
                _kill_pid_tree(pid)
            time.sleep(0.4)

    # If pid file exists and process alive, do not start twice
    existing_pid = _read_pid(service.pid_path)
    if existing_pid and _pid_exists(existing_pid):
        print(f"[SKIP] {service.id} already running (PID {existing_pid})")
        return

    service.log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = service.log_path.open("a", encoding="utf-8", errors="ignore")

    cmd, env = _build_command(service, port)
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
    print(f"[OK] started {service.id} (PID {proc.pid}) :: {_format_cmd(cmd)}")

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
                return
            time.sleep(0.3)
        print(f"[WARN] {service.id} not responding yet: {url}")


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
        return
    _remove_pid(service.pid_path)
    if ok:
        print(f"[OK] stopped {service.id} (PID {pid})")
    else:
        print(f"[WARN] failed to stop {service.id} (PID {pid})")


def _status_one(service: Service) -> dict[str, Any]:
    pid = _read_pid(service.pid_path)
    running = False
    if pid:
        running = _pid_exists(pid)

    port = service.default_port
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
    services = _load_manifest()
    _validate_unique_ports(services)

    parser = argparse.ArgumentParser(prog="mcpctl", description="Unified MCP manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List all MCP services")

    start_p = sub.add_parser("start", help="Start MCP service(s)")
    start_p.add_argument("id", nargs="?", help="Service id")
    start_p.add_argument("--all", action="store_true", help="Start all services")
    start_p.add_argument("--port", type=int, help="Override port (single service only)")
    start_p.add_argument("--kill-port", action="store_true", help="Kill process occupying the port")
    start_p.add_argument("--wait", type=float, default=8.0, help="Wait seconds for /sse health (default: 8)")

    stop_p = sub.add_parser("stop", help="Stop MCP service(s)")
    stop_p.add_argument("id", nargs="?", help="Service id")
    stop_p.add_argument("--all", action="store_true", help="Stop all services")

    sub.add_parser("status", help="Show MCP status")

    args = parser.parse_args(argv)

    if args.cmd == "list":
        for svc in services:
            port = f":{svc.default_port}" if svc.default_port else ""
            suffix = "" if svc.auto_start else " (manual)"
            print(f"- {svc.id}{port} [{svc.type}/{svc.transport}] {svc.name}{suffix}")
        return 0

    if args.cmd == "start":
        if not args.all and not args.id:
            raise SystemExit("Provide <id> or use --all")
        selected = [svc for svc in services if svc.auto_start] if args.all else _select_services(services, [args.id])
        if args.port is not None and args.all:
            raise SystemExit("--port can only be used when starting a single service")

        for svc in selected:
            port = int(args.port) if args.port is not None else svc.default_port
            _start_one(svc, port, kill_port=bool(args.kill_port), wait_s=float(args.wait))
        return 0

    if args.cmd == "stop":
        if not args.all and not args.id:
            raise SystemExit("Provide <id> or use --all")
        selected = services if args.all else _select_services(services, [args.id])
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

    raise SystemExit("Unhandled command")


if __name__ == "__main__":
    raise SystemExit(main())
