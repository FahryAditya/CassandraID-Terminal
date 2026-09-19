<div align="center">

# 🗂️ FileForge DevKit

**A local-first developer workspace toolkit for the terminal.**

File management. Project scaffolding. Workspace intelligence. All in one CLI.

![Python](https://img.shields.io/badge/Python-3.11%2B-5B58EB?style=for-the-badge&logo=python&logoColor=white)
![Typer](https://img.shields.io/badge/CLI-Typer-BB63FF?style=for-the-badge)
![Rich](https://img.shields.io/badge/UI-Rich-56E1E9?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-112C70?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-0A2353?style=for-the-badge)

</div>

---

## 🎨 Brand Identity — "Deep Space"

FileForge DevKit's visual identity (docs, badges, and the optional future web dashboard) is built on the **Deep Space** color palette: a dark, focused, developer-friendly range of navy, indigo, purple, and cyan.

| Swatch | Name | Hex | Usage |
|---|---|---|---|
| 🟦 | Deep Navy | `#0A2353` | Backgrounds, deepest surface |
| 🟦 | Navy | `#112C70` | Secondary background, panels |
| 🟪 | Indigo | `#5B58EB` | Primary brand color, links, buttons |
| 🟣 | Purple | `#BB63FF` | Accent, highlights, active states |
| 🩵 | Cyan | `#56E1E9` | Success, highlights, focus rings |

> **Note on terminal UI:** Standard terminals only render a limited ANSI palette, so the CLI itself uses Rich's `cyan` / `green` / `yellow` / `red` / `dim` semantic colors (see [Terminal Color Mapping](#terminal-color-mapping) below) for maximum compatibility. The exact Deep Space hex values are reserved for README badges, generated HTML/docs output, and the optional web dashboard (Phase 6), where true color is guaranteed.

### Terminal Color Mapping

| Semantic Role | Deep Space Reference | Rich/ANSI Fallback |
|---|---|---|
| Primary | Indigo `#5B58EB` | `cyan` |
| Secondary | Cyan `#56E1E9` | `green` |
| Warning | — | `yellow` |
| Error | — | `red` |
| Muted | Navy `#112C70` | `dim` / `grey50` |
| Accent | Purple `#BB63FF` | `magenta` |

---

## 📖 Overview

**FileForge DevKit** combines two tools developers actually reach for every day:

- **🗃️ FileForge** — intelligent, safe file and directory management from the terminal.
- **⚒️ DevForge** — automated project scaffolding and template generation.

It runs natively in **Windows Terminal, PowerShell, and CMD**, with cross-platform compatibility for Linux and macOS. It is a real developer utility — not a tutorial script, not a novelty CLI.

---

## ✨ Features

### Module A — Command Center
- Interactive terminal dashboard with a clean, dark aesthetic
- Current directory context, recent projects, and main navigation
- Keyboard-friendly, low-noise, high-signal UI

### Module B — FileForge File Manager
- Directory explorer with sorting, tree view, and metadata (size, type, modified date)
- File search (by name, extension, partial match, recursive, case-insensitive)
- Safe file operations: create, rename, copy, move, delete
- Confirmation prompts before any destructive action — **never silently overwrites**
- File organizer with dry-run mode and collision detection

### Module C — DevForge Project Generator
- Scaffold new projects from ready-to-use templates:
  - Python Basic
  - Python CLI
  - Python Package
  - Flask Application
  - Next.js + TypeScript
  - Static HTML/CSS/JS
- Template variables (`project_name`, `author_name`, `license`, etc.)
- Structure preview before generation
- Optional (opt-in only) Git init, virtualenv creation, dependency install, VS Code launch

### Module D — Workspace Explorer
- Register and manage multiple project workspaces
- Auto-detect project type (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.) — informational only, never executed

### Module E — Recent Projects
- Track recently created or accessed projects
- Open, search, sort, and remove from history (without touching real files)

### Module F — Activity History
- SQLite-backed operation history (timestamp, operation, target, result)
- Search and filter; no file contents or secrets ever stored

### Module G — Settings
- Persistent, validated user preferences (theme, default workspace, confirmation behavior, etc.)
- Destructive-action safeguards **cannot** be casually disabled by a default setting

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| CLI Framework | [Typer](https://typer.tiangolo.com/) |
| Terminal UI | [Rich](https://github.com/Textualize/rich) |
| Filesystem | `pathlib`, `shutil` |
| Templates | [Jinja2](https://jinja.palletsprojects.com/) |
| Persistence | `sqlite3` |
| Testing | `pytest` |
| Linting/Formatting | [Ruff](https://docs.astral.sh/ruff/) |
| Packaging | `pyproject.toml` |

**Optional (Phase 6 — Web Dashboard):** Next.js App Router · TypeScript (strict) · Tailwind CSS · shadcn/ui · FastAPI · local SQLite.

---

## 📦 Requirements

- Python **3.11+**
- Windows 10/11 (primary) — CMD, PowerShell, or Windows Terminal
- Linux / macOS (secondary, cross-platform support)
- Git *(optional — detected at runtime, not required)*

---

## 🚀 Installation

### Windows (CMD)

```cmd
git clone https://github.com/your-username/fileforge-devkit.git
cd fileforge-devkit
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### Windows (PowerShell)

```powershell
git clone https://github.com/your-username/fileforge-devkit.git
cd fileforge-devkit
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

### Linux / macOS

```bash
git clone https://github.com/your-username/fileforge-devkit.git
cd fileforge-devkit
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## ▶️ Usage

Launch the interactive dashboard:

```bash
fileforge
```

or explicitly:

```bash
fileforge dashboard
```

### CLI Command Reference

| Command | Description |
|---|---|
| `fileforge dashboard` | Launch the interactive terminal dashboard |
| `fileforge files list PATH` | List files and directories |
| `fileforge files tree PATH` | Display a directory tree |
| `fileforge files search QUERY PATH` | Search files by name/extension |
| `fileforge files organize PATH` | Organize files by rule (dry-run supported) |
| `fileforge files copy SOURCE DEST` | Copy a file or directory |
| `fileforge files move SOURCE DEST` | Move a file or directory |
| `fileforge files rename SOURCE DEST` | Rename a file or directory |
| `fileforge files delete PATH` | Delete a file or directory (confirmation required) |
| `fileforge create TEMPLATE NAME` | Generate a new project from a template |
| `fileforge templates list` | List available project templates |
| `fileforge workspace list` | List registered workspaces |
| `fileforge workspace add PATH` | Register a new workspace |
| `fileforge workspace remove NAME` | Remove a workspace registration |
| `fileforge projects recent` | Show recently accessed projects |
| `fileforge history` | View activity history |
| `fileforge settings` | View or edit settings |
| `fileforge --version` | Show the installed version |
| `fileforge --help` | Show help for any command |

> ⚠️ Only commands listed above are implemented. This table is kept in sync with the actual codebase — see [Known Limitations](#-known-limitations--roadmap).

---

## 🗄️ Database & Configuration

FileForge stores local metadata in a SQLite database, kept **outside** the source package:

| OS | Location |
|---|---|
| Windows | `%APPDATA%\FileForge\fileforge.db` |
| Linux/macOS | `~/.local/share/fileforge/fileforge.db` |

Tables: `workspaces`, `recent_projects`, `activity_logs`, `settings`.

No file contents, credentials, or environment secrets are ever stored.

---

## 🔒 Safety Notes

- Destructive operations (delete, overwrite, bulk move) **always require confirmation**.
- Bulk operations support **dry-run mode** with a full preview before execution.
- Template generation is **path-traversal safe** — generated files can never escape the destination directory.
- External tools (Git, virtualenv, VS Code) are **opt-in only**, never invoked implicitly.
- No shell-string interpolation for subprocess calls.
- No automatic network requests. No telemetry.

Full details: [`docs/security.md`](docs/security.md)

---

## 🧪 Testing

```bash
pytest
ruff check .
ruff format --check .
```

Tests use isolated temp directories and a throwaway test database — they never touch your real projects or home directory.

---

## 🧭 Roadmap

- [x] Phase 1 — Foundation (CLI entry point, dashboard, config)
- [x] Phase 2 — File Manager
- [ ] Phase 3 — Project Generator (templates in progress)
- [ ] Phase 4 — Workspace & History
- [ ] Phase 5 — Quality & Release
- [ ] Phase 6 — Optional Web Dashboard (Next.js + FastAPI)

---

## ⚠️ Known Limitations

- Web dashboard is **not implemented** — CLI is the only supported interface today.
- Symlinked directories are not followed recursively by design (safety, not a bug).
- Large directory trees (100k+ files) may need pagination improvements.

*(Update this section as features land — do not claim completed work that hasn't shipped.)*

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run `pytest` and `ruff check .` before opening a PR
4. Keep documentation in sync with implementation

---

## 📄 License

MIT — see [`LICENSE`](LICENSE) for details.

---

<div align="center">

**FileForge DevKit** · Built with 🩵 using the Deep Space palette

</div>