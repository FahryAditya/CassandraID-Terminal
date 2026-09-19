from __future__ import annotations

from unittest.mock import MagicMock, patch

from cassandra_terminal.modules.ports import (
    PortProcess,
    get_active_listening_ports,
    kill_port_process,
)


def test_get_active_listening_ports() -> None:
    ports = get_active_listening_ports()
    assert isinstance(ports, list)
    for p in ports:
        assert isinstance(p, PortProcess)
        assert isinstance(p.port, int)


@patch("cassandra_terminal.modules.ports.get_active_listening_ports")
@patch("cassandra_terminal.modules.ports.psutil.Process")
def test_kill_port_process_not_found(mock_proc_cls: MagicMock, mock_get_ports: MagicMock) -> None:
    mock_get_ports.return_value = []
    mock_proc_cls.side_effect = Exception("NoSuchProcess")

    success, msg = kill_port_process(99999)
    assert success is False
    assert "99999" in msg


@patch("cassandra_terminal.modules.ports.get_active_listening_ports")
@patch("cassandra_terminal.modules.ports.psutil.Process")
def test_kill_port_process_success(mock_proc_cls: MagicMock, mock_get_ports: MagicMock) -> None:
    mock_get_ports.return_value = [
        PortProcess(
            port=8080,
            protocol="TCP",
            ip="127.0.0.1",
            pid=1234,
            process_name="node.exe",
            status="LISTEN",
        )
    ]

    mock_target = MagicMock()
    mock_target.name.return_value = "node.exe"
    mock_proc_cls.return_value = mock_target

    success, msg = kill_port_process(8080)
    assert success is True
    assert "1234" in msg
    assert "node.exe" in msg
    mock_target.terminate.assert_called_once()
