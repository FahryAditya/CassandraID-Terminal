<div align="center">

# ⚡ CassandraID-Terminal

**A local-first developer workspace toolkit, intelligence center, and power suite for the modern terminal.**

Zombie Port Killer • Universal Script Runner • Live Fuzzy Finder • Project Notes • Hardware Monitor • Dual-Pane TUI • Git Intel • 10 Scaffolding Templates.

[![Python](https://img.shields.io/badge/Python-3.11%2B-5B58EB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CLI](https://img.shields.io/badge/CLI-Typer-BB63FF?style=for-the-badge)](https://typer.tiangolo.com/)
[![UI](https://img.shields.io/badge/UI-Rich-56E1E9?style=for-the-badge)](https://github.com/Textualize/rich)
[![License: MIT](https://img.shields.io/badge/License-MIT-112C70?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-0A2353?style=for-the-badge)](https://github.com)
[![CI](https://img.shields.io/badge/Tests-43%20Passing-brightgreen?style=for-the-badge)](tests/)

</div>

---

## 🎨 Brand Identity — "Deep Space"

CassandraID-Terminal's visual identity is built on the **Deep Space** color palette: a focused, modern, developer-friendly range of navy, indigo, purple, and cyan.

| Swatch | Name | Hex Code | Semantic Terminal Mapping | Usage |
|---|---|---|---|---|
| 🟦 | **Deep Navy** | `#0A2353` | Backgrounds / Surfaces | Deepest backdrop |
| 🟦 | **Navy** | `#112C70` | Secondary Panels / Borders | Panels & headers |
| 🟪 | **Indigo** | `#5B58EB` | `cyan` / `bold cyan` | Primary brand, links, buttons |
| 🟣 | **Purple** | `#BB63FF` | `magenta` / `bold magenta` | Highlights, badges, active states |
| 🩵 | **Cyan** | `#56E1E9` | `green` / `bold green` | Success, focus rings, metrics |

---

## ✨ Power Features

### 🚀 1. Zombie Port Inspector & 1-Click Process Killer (`cassandra ports`)
- Instant scan of all active localhost listening ports (3000, 5173, 8000, 8080, etc.).
- Identifies process name, PID, and memory footprint.
- 1-click termination to immediately resolve `"Port already in use"` errors without opening Task Manager or running cryptic OS commands.

### ⚡ 2. Universal Project Script Runner (`cassandra run`)
- Auto-detects runnable commands from `package.json`, `pyproject.toml`, `Makefile`, and `Cargo.toml`.
- Presents an interactive menu or runs directly with `cassandra run <script>`. No need to remember whether a repo uses `npm run`, `cargo run`, `make`, or `python -m`.

### 🔍 3. Live Fuzzy File Finder + Instant Editor Launcher (`cassandra find`)
- Blazing-fast fuzzy file search across your workspace (with smart ignores for `node_modules`, `.git`, `.venv`, etc.).
- Launch matched files directly in your favorite editor (`code`, `cursor`, `nvim`, `vim`, `subl`).

### 📝 4. Project Scratchpad & Task Checklist (`cassandra notes`)
- Workspace-scoped task checklist (`add`, `done`, `delete`, `clean`).
- Clean visual status badges (`✔ DONE` / `⏳ TODO`) displayed directly in the Command Center dashboard.

### 📊 5. Real-Time Hardware & System Monitor (`cassandra monitor`)
- Live CPU load, RAM usage, and Disk space visual gauge bars.
- Live-updating top memory and CPU-consuming processes table.
- Supports instant snapshot or live continuous monitoring (`--live`).

### 🖥️ 6. Interactive Command Center Dashboard (`cassandra dashboard`)
- **Action Menu**: Unified keyboard loop to trigger all toolkit features.
- **Git & Health Integration**: Real-time git branch, clean/dirty status, uncommitted counts, and repository **Health Score (0–100%)**.
- **Context Awareness**: Displays active workspace, project type, recent projects, and pending tasks.

### 🧭 7. Dual-Pane TUI File Explorer (`cassandra files browse`)
- **Full Keyboard Navigation**: Arrow keys (`↑`, `↓`, `Enter`, `Backspace`, or `h`/`j`/`k`/`l`).
- **Live In-Terminal File Preview**: Syntax-highlighted code preview (Python, JS, TS, HTML, CSS, Rust, Go, SQL) and formatted Markdown rendering.

### ⚒️ 8. Project Generator (10 Scaffolding Templates)
- Instant scaffolding with Jinja2 templating:
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

### 🧹 9. Storage Intelligence & Cleaner
- **Duplicate File Finder**: Detect duplicate files with fast SHA-256 chunked hashing.
- **Disk Usage & Cleaner**: Spot heavy build and cache directories (`node_modules`, `.venv`, `.next`, `target`, cache) with 1-click cleanup.
- **Batch Renamer**: Regex pattern replacement, numbering (`_001`, `_002`), prefixes, and dry-run previews.
- **Safe Compression**: Zip & Tar archives with Zip-Slip path-traversal protection.
- **File Organizer**: Categorize messy downloads/folders into `Images`, `Documents`, `Code`, etc.

---

## 🚀 Quick Start

### Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/FahryAditya/CassandraID-Terminal.git
cd CassandraID-Terminal
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate

pip install -e .
```

---

## ▶️ Command Reference

| Command | Description |
|---|---|
| `cassandra` | Launch the interactive Command Center dashboard |
| `cassandra ports` | Inspect active localhost ports & kill zombie processes |
| `cassandra run [NAME]` | Detect & execute project scripts (`npm`, `make`, `cargo`, `py`) |
| `cassandra find [QUERY]` | Fuzzy file finder + open top match in editor |
| `cassandra notes` | View and manage workspace TODOs and notes |
| `cassandra monitor [--live]`| Real-time CPU, RAM, Disk, and Process monitor |
| `cassandra files browse [PATH]` | Open interactive dual-pane TUI File Explorer |
| `cassandra files list [PATH]` | List directory contents with metadata & sizes |
| `cassandra files tree [PATH]` | Display visual directory hierarchy |
| `cassandra files search QUERY` | Search files by name, regex, or extension |
| `cassandra files organize [PATH]` | Auto-categorize messy files (dry-run supported) |
| `cassandra create TEMPLATE NAME` | Generate a new project from a scaffold template |
| `cassandra templates list` | List all available scaffolding templates |
| `cassandra tools duplicates [PATH]` | Find duplicate files based on content hash |
| `cassandra tools disk [PATH] [--clean]`| Analyze storage usage & tidy junk folders |
| `cassandra tools rename [PATH]` | Batch rename files with regex patterns & numbering |
| `cassandra tools zip / unzip` | Safe archive compression & extraction |
| `cassandra tools health [PATH]` | Evaluate project health score & suggestions |
| `cassandra workspace list / add` | Manage registered workspace directories |
| `cassandra history` | View activity audit trail in SQLite |
| `cassandra settings` | View or adjust configuration preferences |

---

## 🧪 Testing & Code Quality

Run the automated test suite and linter:

```bash
# Run all 43 automated tests
pytest -v

# Run linting check
ruff check .

# Run formatting check
ruff format --check .
```

---

## 🔒 Security & Privacy

- **Local-First & Offline**: All metadata is stored locally in SQLite (`~/.cassandra/cassandra.db`).
- **Zero Telemetry**: No tracking, no external network requests.
- **Path-Traversal Protected**: Template engines and archive extractors strictly prevent directory traversal attacks.
- **Destructive Safeguards**: File deletion, overwrite, process termination, and batch modifications always require user confirmation.

---

## 🤝 Contributing

Contributions, feature requests, and bug reports are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on setting up your development environment.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.

<div align="center">

**CassandraID-Terminal** • Crafted with 🩵 using the Deep Space theme

</div>
