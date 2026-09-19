# Contributing to CassandraID-Terminal

Thank you for your interest in contributing to **CassandraID-Terminal**! We welcome contributions of all kinds: bug fixes, new project templates, performance improvements, and documentation enhancements.

---

## 🛠️ Development Setup

1. **Fork and Clone** the repository:
   ```bash
   git clone https://github.com/your-username/fileforge-devkit.git
   cd fileforge-devkit
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1

   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies in editable mode**:
   ```bash
   pip install -e .[dev]
   ```

---

## 🧪 Testing & Code Standards

Before opening a pull request, ensure all tests pass and your code complies with our formatting standards:

1. **Run test suite**:
   ```bash
   pytest -v
   ```

2. **Run linter**:
   ```bash
   ruff check .
   ```

3. **Format code**:
   ```bash
   ruff format .
   ```

---

## 🌿 Git Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/my-cool-feature
   ```
2. Commit your changes with clear, descriptive commit messages.
3. Push to your fork and submit a Pull Request.

---

## 💡 Adding New Project Templates

If you'd like to add a new project scaffolding template:
1. Define the template files in `fileforge/modules/generator.py`.
2. Register the template key in `TEMPLATES` dict.
3. Add a corresponding test in `tests/test_generator.py`.
4. Update the template list in `README.md`.

Thank you for making FileForge DevKit better! 🩵
