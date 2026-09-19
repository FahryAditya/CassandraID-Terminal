import json
from pathlib import Path

from cassandra_terminal.modules.plugins import dispatch_hook, list_plugins


def test_plugin_discovery_and_hook(tmp_path: Path, monkeypatch):
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    monkeypatch.setattr("cassandra_terminal.modules.plugins.get_plugins_dir", lambda: plugins_dir)

    # Create dummy plugin
    p1 = plugins_dir / "my_plugin"
    p1.mkdir()
    (p1 / "plugin.json").write_text(
        json.dumps(
            {"name": "TestPlugin", "version": "0.1.0", "description": "Test", "author": "Tester"}
        ),
        encoding="utf-8",
    )
    (p1 / "main.py").write_text(
        "def on_test(value):\n    return f'processed_{value}'\n",
        encoding="utf-8",
    )

    plugins = list_plugins()
    assert len(plugins) == 1
    assert plugins[0].name == "TestPlugin"

    results = dispatch_hook("on_test", value="abc")
    assert results == ["processed_abc"]
