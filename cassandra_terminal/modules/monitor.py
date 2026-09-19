from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import psutil


@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str


@dataclass
class SystemSnapshot:
    cpu_percent: float
    cpu_count_logical: int
    cpu_count_physical: int
    ram_total_gb: float
    ram_used_gb: float
    ram_free_gb: float
    ram_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_free_gb: float
    disk_percent: float
    top_processes: list[ProcessInfo]


def get_system_snapshot(top_n: int = 8) -> SystemSnapshot:
    """Gather complete hardware and top process utilization."""
    # CPU
    cpu_pct = psutil.cpu_percent(interval=0.1)
    cpu_logical = psutil.cpu_count(logical=True) or 1
    cpu_physical = psutil.cpu_count(logical=False) or 1

    # Memory
    mem = psutil.virtual_memory()
    ram_total = mem.total / (1024**3)
    ram_used = mem.used / (1024**3)
    ram_free = mem.available / (1024**3)
    ram_pct = mem.percent

    # Disk (Root or CWD partition)
    try:
        root_path = Path.cwd().anchor or "/"
        disk = psutil.disk_usage(root_path)
        disk_total = disk.total / (1024**3)
        disk_used = disk.used / (1024**3)
        disk_free = disk.free / (1024**3)
        disk_pct = disk.percent
    except Exception:
        disk_total, disk_used, disk_free, disk_pct = 0.0, 0.0, 0.0, 0.0

    # Top processes
    procs: list[ProcessInfo] = []
    for p in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent", "memory_info", "status"]
    ):
        try:
            info = p.info
            mem_info = info.get("memory_info")
            mem_mb = (mem_info.rss / (1024 * 1024)) if mem_info else 0.0
            cpu_val = info.get("cpu_percent") or 0.0
            mem_val = info.get("memory_percent") or 0.0
            procs.append(
                ProcessInfo(
                    pid=info.get("pid") or 0,
                    name=info.get("name") or "unknown",
                    cpu_percent=round(cpu_val, 1),
                    memory_percent=round(mem_val, 1),
                    memory_mb=round(mem_mb, 1),
                    status=str(info.get("status") or ""),
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Sort by memory consumption descending
    procs.sort(key=lambda x: (x.memory_percent, x.cpu_percent), reverse=True)
    top_procs = procs[:top_n]

    return SystemSnapshot(
        cpu_percent=cpu_pct,
        cpu_count_logical=cpu_logical,
        cpu_count_physical=cpu_physical,
        ram_total_gb=round(ram_total, 2),
        ram_used_gb=round(ram_used, 2),
        ram_free_gb=round(ram_free, 2),
        ram_percent=ram_pct,
        disk_total_gb=round(disk_total, 2),
        disk_used_gb=round(disk_used, 2),
        disk_free_gb=round(disk_free, 2),
        disk_percent=disk_pct,
        top_processes=top_procs,
    )
