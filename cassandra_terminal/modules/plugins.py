import importlib.util
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cassandra_terminal.config import get_app_dir
from cassandra_terminal.modules.activity import log_activity


@dataclass
class PluginInfo:
    name: str
    version: str
    description: str
    author: str
    path: Path
    enabled: bool = True


def get_plugins_dir() -> Path:
    """Return the plugins directory."""
    p_dir = get_app_dir() / "plugins"
    p_dir.mkdir(parents=True, exist_ok=True)
    return p_dir


def list_plugins() -> list[PluginInfo]:
    """Scan and list all installed plugins in the plugins directory."""
    plugins_dir = get_plugins_dir()
    plugins: list[PluginInfo] = []

    for item in plugins_dir.iterdir():
        if item.is_dir():
            manifest_file = item / "plugin.json"
            if manifest_file.exists():
                try:
                    data = json.loads(manifest_file.read_text(encoding="utf-8"))
                    plugins.append(
                        PluginInfo(
                            name=data.get("name", item.name),
                            version=data.get("version", "1.0.0"),
                            description=data.get("description", "No description"),
                            author=data.get("author", "Unknown"),
                            path=item,
                            enabled=data.get("enabled", True),
                        )
                    )
                except Exception:
                    continue
    return plugins


def dispatch_hook(hook_name: str, **kwargs: Any) -> list[Any]:
    """Execute a hook on all active plugins and collect results."""
    results: list[Any] = []
    plugins = list_plugins()

    for p in plugins:
        if not p.enabled:
            continue
        entry_file = p.path / "main.py"
        if entry_file.exists():
            try:
                spec = importlib.util.spec_from_file_location(f"plugin_{p.name}", entry_file)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    hook_fn: Callable[..., Any] | None = getattr(mod, hook_name, None)
                    if callable(hook_fn):
                        res = hook_fn(**kwargs)
                        results.append(res)
            except Exception as e:
                log_activity("PLUGIN_ERROR", p.name, "FAILED", f"Error in hook {hook_name}: {e}")

    return results
