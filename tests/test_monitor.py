from __future__ import annotations

from cassandra_terminal.modules.monitor import SystemSnapshot, get_system_snapshot


def test_get_system_snapshot() -> None:
    snapshot = get_system_snapshot(top_n=5)
    assert isinstance(snapshot, SystemSnapshot)
    assert 0.0 <= snapshot.cpu_percent <= 100.0
    assert snapshot.cpu_count_logical >= 1
    assert snapshot.ram_total_gb > 0
    assert snapshot.disk_total_gb >= 0
    assert isinstance(snapshot.top_processes, list)
