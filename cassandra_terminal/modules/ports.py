from __future__ import annotations

from dataclasses import dataclass

import psutil

from cassandra_terminal.modules.activity import log_activity


@dataclass
class PortProcess:
    port: int
    protocol: str
    ip: str
    pid: int | None
    process_name: str
    status: str
    memory_mb: float = 0.0
    exe_path: str = ""


def get_active_listening_ports() -> list[PortProcess]:
    """Scan all active listening TCP/UDP ports and their associated processes."""
    results: list[PortProcess] = []
    seen_keys: set[tuple[int, str]] = set()

    try:
        connections = psutil.net_connections(kind="inet")
    except Exception:
        # If permissions on net_connections is limited, fallback
        connections = []

    for conn in connections:
        if conn.status == "LISTEN" or conn.type == 2:  # 2 is SOCK_DGRAM (UDP)
            port = conn.laddr.port
            ip = conn.laddr.ip
            proto = "TCP" if conn.type == 1 else "UDP"
            pid = conn.pid

            key = (port, proto)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            proc_name = "Unknown"
            mem_mb = 0.0
            exe = ""
            if pid:
                try:
                    p = psutil.Process(pid)
                    proc_name = p.name()
                    try:
                        mem_mb = round(p.memory_info().rss / (1024 * 1024), 1)
                    except Exception:
                        pass
                    try:
                        exe = p.exe()
                    except Exception:
                        pass
                except Exception:
                    proc_name = "System / Terminated"

            results.append(
                PortProcess(
                    port=port,
                    protocol=proto,
                    ip=ip,
                    pid=pid,
                    process_name=proc_name,
                    status=conn.status if conn.status else "LISTENING",
                    memory_mb=mem_mb,
                    exe_path=exe,
                )
            )

    results.sort(key=lambda x: x.port)
    return results


def kill_port_process(port_or_pid: int) -> tuple[bool, str]:
    """Terminate the process listening on a specific port or by PID."""
    # Check if input is a known active port
    ports = get_active_listening_ports()
    target_pid: int | None = None
    target_name = "Unknown"
    is_port_match = False

    for p in ports:
        if p.port == port_or_pid:
            target_pid = p.pid
            target_name = p.process_name
            is_port_match = True
            break

    if not target_pid:
        # Try treating as direct PID
        target_pid = port_or_pid

    try:
        proc = psutil.Process(target_pid)
        target_name = proc.name()
        proc.terminate()
        proc.wait(timeout=3)
        log_activity(
            operation="KILL_PORT",
            target=str(port_or_pid),
            result="SUCCESS",
            details=f"Killed process '{target_name}' (PID: {target_pid})",
        )
        return True, f"Successfully terminated '{target_name}' (PID: {target_pid})"
    except psutil.TimeoutExpired:
        try:
            proc.kill()
            return True, f"Force-killed '{target_name}' (PID: {target_pid})"
        except Exception as e:
            return False, f"Failed to force-kill process: {e}"
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
        if not is_port_match:
            return False, f"No process found with port or PID: {port_or_pid} ({e})"
        return False, f"Cannot terminate PID {target_pid}: {e}"
