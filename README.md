<div align="center">

# 🗂️ FileForge DevKit

**A local-first developer workspace toolkit and intelligence center for the terminal.**

File management • Project scaffolding • Dual-pane TUI • Git intelligence • Activity tracking. All in one CLI.

[![Python](https://img.shields.io/badge/Python-3.11%2B-5B58EB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Typer](https://img.shields.io/badge/CLI-Typer-BB63FF?style=for-the-badge)](https://typer.tiangolo.com/)
[![Rich](https://img.shields.io/badge/UI-Rich-56E1E9?style=for-the-badge)](https://github.com/Textualize/rich)
[![License: MIT](https://img.shields.io/badge/License-MIT-112C70?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-0A2353?style=for-the-badge)](https://github.com)
[![CI](https://img.shields.io/badge/Tests-33%20Passing-brightgreen?style=for-the-badge)](tests/)

</div>

---

## 🎨 Brand Identity — "Deep Space"

FileForge DevKit's visual identity is built on the **Deep Space** color palette: a focused, modern, developer-friendly range of navy, indigo, purple, and cyan.

| Swatch | Name | Hex Code | Semantic Terminal Mapping | Usage |
|---|---|---|---|---|
| 🟦 | **Deep Navy** | `#0A2353` | Backgrounds / Surfaces | Deepest backdrop |
| 🟦 | **Navy** | `#112C70` | Secondary Panels / Borders | Panels & headers |
| 🟪 | **Indigo** | `#5B58EB` | `cyan` / `bold cyan` | Primary brand, links, buttons |
| 🟣 | **Purple** | `#BB63FF` | `magenta` / `bold magenta` | Highlights, badges, active states |
| 🩵 | **Cyan** | `#56E1E9` | `green` / `bold green` | Success, focus rings, metrics |

---

## ✨ Features

### 🖥️ 1. Interactive Command Center Dashboard
- **Interactive Action Menu**: Full menu loop to navigate features with 1-click keystrokes.
- **Git & Health Integration**: Real-time git branch, clean/dirty status, uncommitted counts, and repository **Health Score (0–100%)**.
- **Context Awareness**: Displays active workspace, project type, and recent projects.

### 🧭 2. Dual-Pane TUI File Explorer
- **Full Keyboard Navigation**: Arrow keys (`↑`, `↓`, `Enter`, `Backspace`, or `h`/`j`/`k`/`l`).
- **Live In-Terminal File Preview**: Syntax-highlighted code preview (Python, JS, TS, HTML, CSS, Rust, Go, SQL) and formatted Markdown rendering.

### ⚒️ 3. DevForge Project Generator (10 Ready-to-Use Templates)
- Instant project scaffolding with Jinja2 templating:
  - `python-cli` — Typer + Rich CLI starter
  - `python-pkg` — Python package with pytest & ruff setup
  - `python-basic` — Single-file Python starter
  - `fastapi-docker` — Modern FastAPI REST API with Dockerfile & docker-compose
  - `react-vite` — React 18 + TypeScript + Vite + Tailwind CSS
  - `nextjs-ts` — Next.js App Router + TypeScript + Tailwind
  - `rust-cli` — Rust command-line tool with Clap v4
  - `go-gin` — Go REST API with Gin Framework
  - `flask-app` — Flask web app factory
  - `static-web` — Responsive HTML5/CSS3 boilerplate with Deep Space styling
- **Path-traversal safe**: Generated files are strictly validated.
- Optional automated Git init & virtual environment creation.

### 🔍 4. Advanced Storage & Maintenance Tools
- **Duplicate File Finder**: Detect duplicate files with fast SHA-256 chunked hashing.
- **Disk Usage & Cleaner**: Spot heavy build and cache directories (`node_modules`, `.venv`, `.next`, `target`, cache) with 1-click cleanup.
- **Batch Renamer**: Regex pattern replacement, numbering (`_001`, `_002`), prefixes, and dry-run previews.
- **Safe Compression**: Zip & Tar archives with Zip-Slip path-traversal protection.
- **File Organizer**: Categorize messy downloads/folders into `Images`, `Documents`, `Code`, etc.

### 🌐 5. Workspace & Activity Intelligence
- Auto-detect project types (`Python`, `Node.js`, `Next.js`, `Rust`, `Go`, `Java`, `PHP`, `Static Web`).
- SQLite-backed operation history (no file contents or secrets ever stored).
- Safe settings manager preventing accidental disabling of destructive confirmations.

### 🔌 6. Plugin & Extension System
- Manifest-based plugin architecture (`~/.fileforge/plugins/`) with lifecycle hook dispatchers.

---

## 🚀 Quick Start

### Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/your-username/fileforge-devkit.git
cd fileforge-devkit
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate

pip install -e .
```

---

## ▶️ Usage & Commands

Launch the **Interactive Command Center**:

```bash
fileforge
# or explicitly
fileforge dashboard
```

### Command Reference

| Command | Description |
|---|---|
| `fileforge` | Launch the interactive Command Center dashboard |
| `fileforge files browse [PATH]` | Open interactive dual-pane TUI File Explorer |
| `fileforge files list [PATH]` | List directory contents with metadata & sizes |
| `fileforge files tree [PATH]` | Display visual directory hierarchy |
| `fileforge files search QUERY` | Search files by name, regex, or extension |
| `fileforge files organize [PATH]` | Auto-categorize messy files (dry-run supported) |
| `fileforge files copy SRC DST` | Safely copy file/directory (with collision protection) |
| `fileforge files move SRC DST` | Safely move file/directory |
| `fileforge files delete PATH` | Safeguarded deletion with confirmation prompts |
| `fileforge create TEMPLATE NAME` | Generate a new project from a DevForge template |
| `fileforge templates list` | List all available scaffolding templates |
| `fileforge tools duplicates [PATH]` | Find duplicate files based on content hash |
| `fileforge tools disk [PATH]` | Analyze directory storage usage (`--clean` to tidy junk) |
| `fileforge tools rename [PATH]` | Batch rename files with regex patterns & numbering |
| `fileforge tools zip SOURCE` | Compress file or folder into zip/tar archive |
| `fileforge tools unzip ARCHIVE` | Extract archive safely |
| `fileforge tools health [PATH]` | Evaluate project health score & suggestions |
| `fileforge workspace list` | View registered workspaces |
| `fileforge workspace add [PATH]` | Register a new workspace |
| `fileforge projects recent` | View recently accessed projects |
| `fileforge history` | View activity audit trail in SQLite |
| `fileforge settings` | View or adjust configuration preferences |

---

## 🧪 Testing & Code Quality

Run the test suite and linter:

```bash
# Run 33 automated tests
pytest -v

# Run linting check
ruff check .

# Run formatting check
ruff format --check .
```

---

## 🔒 Security & Privacy

- **Local-First & Offline**: All metadata is stored locally in SQLite (`%APPDATA%\FileForge\fileforge.db` or `~/.local/share/fileforge/fileforge.db`).
- **No Telemetry**: No tracking, no external network requests.
- **Path-Traversal Protected**: Template engines and archive extractors strictly prevent directory traversal attacks.
- **Destructive Safeguards**: File deletion, overwrite, and batch modifications always require user confirmation.

---

## 🤝 Contributing

Contributions, feature requests, and bug reports are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on setting up your development environment.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.

<div align="center">

**FileForge DevKit** • Crafted with 🩵 using the Deep Space theme

</div>
