import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jinja2

from cassandra_terminal.modules.activity import log_activity
from cassandra_terminal.modules.workspace import record_recent_project


@dataclass
class TemplateFile:
    rel_path: str
    content_template: str


@dataclass
class ProjectTemplate:
    key: str
    name: str
    description: str
    files: list[TemplateFile]


# --- Built-in Template Definitions ---

PYTHON_BASIC_FILES = [
    TemplateFile(
        "main.py",
        """def main():
    print("Welcome to {{ project_name }}!")

if __name__ == "__main__":
    main()
""",
    ),
    TemplateFile(
        "requirements.txt",
        """# Project dependencies for {{ project_name }}
""",
    ),
    TemplateFile(
        "README.md",
        """# {{ project_name }}

{{ description }}

## Author
- {{ author_name }} ({{ license }} License)

## Usage
```bash
python main.py
```
""",
    ),
    TemplateFile(
        ".gitignore",
        """__pycache__/
*.py[cod]
.venv/
.env
dist/
build/
""",
    ),
]

PYTHON_CLI_FILES = [
    TemplateFile(
        "src/{{ package_name }}/__init__.py",
        '"""{{ description }}"""\n__version__ = "0.1.0"\n',
    ),
    TemplateFile(
        "src/{{ package_name }}/cli.py",
        '''import typer
from rich.console import Console

app = typer.Typer(help="{{ description }}")
console = Console()

@app.command()
def hello(name: str = "World"):
    """Say hello."""
    console.print(f"[bold cyan]Hello[/bold cyan] [magenta]{name}[/magenta]!")

def main():
    app()

if __name__ == "__main__":
    main()
''',
    ),
    TemplateFile(
        "pyproject.toml",
        """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{{ project_name }}"
version = "0.1.0"
description = "{{ description }}"
authors = [{ name = "{{ author_name }}" }]
license = { text = "{{ license }}" }
requires-python = ">=3.11"
dependencies = [
    "typer>=0.12.0",
    "rich>=13.7.0",
]

[project.scripts]
{{ project_name }} = "{{ package_name }}.cli:main"
""",
    ),
    TemplateFile(
        "tests/test_cli.py",
        """from typer.testing import CliRunner
from {{ package_name }}.cli import app

runner = CliRunner()

def test_hello():
    result = runner.invoke(app, ["hello", "--name", "Dev"])
    assert result.exit_code == 0
    assert "Hello Dev" in result.output
""",
    ),
    TemplateFile(
        "README.md",
        """# {{ project_name }}

{{ description }}

## Installation
```bash
pip install -e .
```

## Usage
```bash
{{ project_name }} hello --name World
```
""",
    ),
    TemplateFile(".gitignore", "__pycache__/\n*.py[cod]\n.venv/\n.env\ndist/\n"),
]

PYTHON_PKG_FILES = [
    TemplateFile(
        "src/{{ package_name }}/__init__.py",
        '"""{{ description }}"""\n__version__ = "0.1.0"\n\ndef add(a: int, b: int) -> int:\n    return a + b\n',
    ),
    TemplateFile(
        "pyproject.toml",
        """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{{ project_name }}"
version = "0.1.0"
description = "{{ description }}"
authors = [{ name = "{{ author_name }}" }]
license = { text = "{{ license }}" }
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.4.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
""",
    ),
    TemplateFile(
        "tests/test_core.py",
        """from {{ package_name }} import add

def test_add():
    assert add(2, 3) == 5
""",
    ),
    TemplateFile("README.md", "# {{ project_name }}\n\n{{ description }}\n"),
    TemplateFile(".gitignore", "__pycache__/\n*.py[cod]\n.venv/\ndist/\n.pytest_cache/\n"),
]

FLASK_APP_FILES = [
    TemplateFile(
        "app.py",
        """from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
""",
    ),
    TemplateFile(
        "templates/index.html",
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project_name }}</title>
    <link rel="stylesheet" href="{% raw %}{{ url_for('static', filename='css/style.css') }}{% endraw %}">
</head>
<body>
    <main class="container">
        <h1>Welcome to {{ project_name }}</h1>
        <p>{{ description }}</p>
    </main>
</body>
</html>
""",
    ),
    TemplateFile(
        "static/css/style.css",
        """body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: #0A2353;
    color: #E2E8F0;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    margin: 0;
}
.container {
    text-align: center;
    background: #112C70;
    padding: 2.5rem;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}
h1 { color: #56E1E9; }
""",
    ),
    TemplateFile("requirements.txt", "Flask>=3.0.0\n"),
    TemplateFile("README.md", "# {{ project_name }}\n\nRun:\n```bash\npython app.py\n```\n"),
    TemplateFile(".gitignore", "__pycache__/\n.venv/\n.env\n"),
]

NEXTJS_TS_FILES = [
    TemplateFile(
        "package.json",
        """{
  "name": "{{ project_name }}",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "lucide-react": "^0.378.0"
  },
  "devDependencies": {
    "@types/node": "^20.12.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "typescript": "^5.4.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
""",
    ),
    TemplateFile(
        "tsconfig.json",
        """{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
""",
    ),
    TemplateFile(
        "app/layout.tsx",
        """import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '{{ project_name }}',
  description: '{{ description }}',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#0A2353] text-slate-100 min-h-screen">{children}</body>
    </html>
  );
}
""",
    ),
    TemplateFile(
        "app/page.tsx",
        """export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-[#56E1E9] mb-4">{{ project_name }}</h1>
      <p className="text-slate-300">{{ description }}</p>
    </main>
  );
}
""",
    ),
    TemplateFile(
        "app/globals.css",
        "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n",
    ),
    TemplateFile(
        "tailwind.config.ts",
        """import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        deepNavy: "#0A2353",
        navy: "#112C70",
        indigo: "#5B58EB",
        purple: "#BB63FF",
        cyan: "#56E1E9",
      },
    },
  },
  plugins: [],
};
export default config;
""",
    ),
    TemplateFile("README.md", "# {{ project_name }}\n\nRun:\n```bash\nnpm run dev\n```\n"),
    TemplateFile(".gitignore", "node_modules/\n.next/\n.env*.local\n"),
]

STATIC_WEB_FILES = [
    TemplateFile(
        "index.html",
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project_name }}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header class="header">
        <div class="logo">⚡ {{ project_name }}</div>
    </header>
    <main class="hero">
        <h1>Welcome to {{ project_name }}</h1>
        <p>{{ description }}</p>
        <button id="ctaBtn" class="btn">Explore Now</button>
    </main>
    <script src="js/app.js"></script>
</body>
</html>
""",
    ),
    TemplateFile(
        "css/style.css",
        """* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0A2353;
    color: #F8FAFC;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}
.header { padding: 1.5rem 2rem; border-bottom: 1px solid rgba(86, 225, 233, 0.2); }
.logo { font-size: 1.25rem; font-weight: bold; color: #56E1E9; }
.hero { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 2rem; }
.hero h1 { font-size: 2.75rem; margin-bottom: 1rem; color: #BB63FF; }
.hero p { font-size: 1.2rem; color: #94A3B8; max-width: 600px; margin-bottom: 2rem; }
.btn {
    background: #5B58EB;
    color: #fff;
    border: none;
    padding: 0.8rem 1.8rem;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.2s, background 0.2s;
}
.btn:hover { background: #BB63FF; transform: translateY(-2px); }
""",
    ),
    TemplateFile(
        "js/app.js",
        """document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("ctaBtn");
    btn.addEventListener("click", () => {
        alert("Welcome to {{ project_name }}!");
    });
});
""",
    ),
    TemplateFile("README.md", "# {{ project_name }}\n\n{{ description }}\n"),
    TemplateFile(".gitignore", ".DS_Store\nThumbs.db\n"),
]

FASTAPI_DOCKER_FILES = [
    TemplateFile(
        "src/main.py",
        """from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="{{ project_name }}", description="{{ description }}")

class HealthResponse(BaseModel):
    status: str
    app: str

@app.get("/", response_model=HealthResponse)
def root():
    return {"status": "online", "app": "{{ project_name }}"}
""",
    ),
    TemplateFile(
        "Dockerfile",
        """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    ),
    TemplateFile(
        "docker-compose.yml",
        """version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
""",
    ),
    TemplateFile("requirements.txt", "fastapi>=0.110.0\nuvicorn>=0.28.0\npydantic>=2.6.0\n"),
    TemplateFile(
        "README.md", "# {{ project_name }}\n\nRun:\n```bash\nuvicorn src.main:app --reload\n```\n"
    ),
    TemplateFile(".gitignore", "__pycache__/\n.venv/\n.env\n"),
]

REACT_VITE_FILES = [
    TemplateFile(
        "package.json",
        """{
  "name": "{{ project_name }}",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "lucide-react": "^0.378.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
""",
    ),
    TemplateFile(
        "src/App.tsx",
        """import React from 'react';

export default function App() {
  return (
    <div className="min-h-screen bg-[#0A2353] text-white flex flex-col items-center justify-center p-6">
      <h1 className="text-4xl font-bold text-[#56E1E9] mb-4">Welcome to {{ project_name }}</h1>
      <p className="text-slate-300">{{ description }}</p>
    </div>
  );
}
""",
    ),
    TemplateFile(
        "src/main.tsx",
        """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",
    ),
    TemplateFile("src/index.css", "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n"),
    TemplateFile(
        "index.html",
        '<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="UTF-8" />\n  <title>{{ project_name }}</title>\n</head>\n<body>\n  <div id="root"></div>\n  <script type="module" src="/src/main.tsx"></script>\n</body>\n</html>\n',
    ),
    TemplateFile(
        "vite.config.ts",
        "import { defineConfig } from 'vite'\nimport react from '@vitejs/plugin-react'\n\nexport default defineConfig({\n  plugins: [react()],\n})\n",
    ),
    TemplateFile(
        "README.md", "# {{ project_name }}\n\nRun:\n```bash\nnpm install\nnpm run dev\n```\n"
    ),
    TemplateFile(".gitignore", "node_modules/\ndist/\n"),
]

RUST_CLI_FILES = [
    TemplateFile(
        "Cargo.toml",
        """[package]
name = "{{ project_name }}"
version = "0.1.0"
edition = "2021"
authors = ["{{ author_name }}"]
description = "{{ description }}"

[dependencies]
clap = { version = "4.4", features = ["derive"] }
""",
    ),
    TemplateFile(
        "src/main.rs",
        """use clap::Parser;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(short, long, default_value = "World")]
    name: String,
}

fn main() {
    let args = Args::parse();
    println!("Hello, {}! Welcome to {{ project_name }}", args.name);
}
""",
    ),
    TemplateFile(
        "README.md", "# {{ project_name }}\n\nRun:\n```bash\ncargo run -- --name Dev\n```\n"
    ),
    TemplateFile(".gitignore", "target/\nCargo.lock\n"),
]

GO_GIN_FILES = [
    TemplateFile(
        "go.mod",
        """module {{ project_name }}

go 1.21

require github.com/gin-gonic/gin v1.9.1
""",
    ),
    TemplateFile(
        "main.go",
        """package main

import (
	"net/http"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Welcome to {{ project_name }}",
			"status":  "online",
		})
	})
	r.Run(":8080")
}
""",
    ),
    TemplateFile("README.md", "# {{ project_name }}\n\nRun:\n```bash\ngo run main.go\n```\n"),
    TemplateFile(".gitignore", "bin/\n*.exe\n"),
]

TEMPLATES: dict[str, ProjectTemplate] = {
    "python-basic": ProjectTemplate(
        key="python-basic",
        name="Python Basic",
        description="Single-file Python starter with requirements and README",
        files=PYTHON_BASIC_FILES,
    ),
    "python-cli": ProjectTemplate(
        key="python-cli",
        name="Python CLI (Typer + Rich)",
        description="Ready-to-use terminal CLI app with Typer and Rich",
        files=PYTHON_CLI_FILES,
    ),
    "python-pkg": ProjectTemplate(
        key="python-pkg",
        name="Python Package",
        description="Standard Python package structure with pytest & ruff config",
        files=PYTHON_PKG_FILES,
    ),
    "fastapi-docker": ProjectTemplate(
        key="fastapi-docker",
        name="FastAPI + Docker",
        description="Modern FastAPI REST API with Docker and docker-compose",
        files=FASTAPI_DOCKER_FILES,
    ),
    "flask-app": ProjectTemplate(
        key="flask-app",
        name="Flask Application",
        description="Lightweight web application structure with Flask",
        files=FLASK_APP_FILES,
    ),
    "react-vite": ProjectTemplate(
        key="react-vite",
        name="React + Vite + Tailwind",
        description="React 18 frontend with TypeScript, Vite, and Tailwind CSS",
        files=REACT_VITE_FILES,
    ),
    "nextjs-ts": ProjectTemplate(
        key="nextjs-ts",
        name="Next.js + TypeScript",
        description="Modern Next.js App Router starter with TypeScript and Tailwind",
        files=NEXTJS_TS_FILES,
    ),
    "rust-cli": ProjectTemplate(
        key="rust-cli",
        name="Rust CLI (Clap)",
        description="Rust terminal command line starter with Clap v4",
        files=RUST_CLI_FILES,
    ),
    "go-gin": ProjectTemplate(
        key="go-gin",
        name="Go Gin Web API",
        description="High-performance Go web service starter using Gin framework",
        files=GO_GIN_FILES,
    ),
    "static-web": ProjectTemplate(
        key="static-web",
        name="Static HTML/CSS/JS",
        description="Clean, responsive HTML5/CSS3 boilerplate with Deep Space styling",
        files=STATIC_WEB_FILES,
    ),
}


def get_available_templates() -> list[ProjectTemplate]:
    """Return all available project generator templates."""
    return list(TEMPLATES.values())


def preview_template_structure(
    template_key: str,
    project_name: str,
    variables: dict[str, Any] | None = None,
) -> list[str]:
    """Generate list of relative file paths that will be created."""
    if template_key not in TEMPLATES:
        raise ValueError(f"Unknown template: '{template_key}'. Available: {list(TEMPLATES.keys())}")

    tpl = TEMPLATES[template_key]
    context = {
        "project_name": project_name,
        "package_name": project_name.replace("-", "_").lower(),
        **(variables or {}),
    }

    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    file_paths: list[str] = []
    for tf in tpl.files:
        rendered_path = env.from_string(tf.rel_path).render(context)
        file_paths.append(rendered_path)
    return file_paths


def generate_project(
    template_key: str,
    project_name: str,
    target_dir: Path,
    author_name: str = "Developer",
    license_type: str = "MIT",
    description: str | None = None,
    git_init: bool = False,
    create_venv: bool = False,
    open_editor: bool = False,
    db_path: Path | None = None,
) -> Path:
    """Scaffold a new project from a template with security checks."""
    if template_key not in TEMPLATES:
        raise ValueError(f"Unknown template: '{template_key}'. Available: {list(TEMPLATES.keys())}")

    dest_dir = (target_dir / project_name).resolve()
    if dest_dir.exists() and any(dest_dir.iterdir()):
        raise FileExistsError(f"Target directory '{dest_dir}' already exists and is not empty.")

    dest_dir.mkdir(parents=True, exist_ok=True)

    package_name = project_name.replace("-", "_").lower()
    desc = description or f"A new project generated with FileForge DevKit ({template_key})."

    context = {
        "project_name": project_name,
        "package_name": package_name,
        "author_name": author_name,
        "license": license_type,
        "description": desc,
    }

    tpl = TEMPLATES[template_key]
    jinja_env = jinja2.Environment(undefined=jinja2.StrictUndefined)

    # Render and write files with Path-Traversal protection
    for tf in tpl.files:
        rel_path_rendered = jinja_env.from_string(tf.rel_path).render(context)
        file_dest = (dest_dir / rel_path_rendered).resolve()

        # Path traversal guard: must be strictly inside dest_dir
        try:
            file_dest.relative_to(dest_dir)
        except ValueError:
            raise PermissionError(
                f"Security error: template attempted path traversal to {file_dest}"
            )

        file_dest.parent.mkdir(parents=True, exist_ok=True)
        content_rendered = jinja_env.from_string(tf.content_template).render(context)
        file_dest.write_text(content_rendered, encoding="utf-8")

    # Opt-in external tasks (Safe & isolated)
    if git_init:
        try:
            subprocess.run(["git", "init"], cwd=str(dest_dir), check=False, capture_output=True)
        except Exception:
            pass

    if create_venv:
        try:
            subprocess.run(
                ["python", "-m", "venv", ".venv"],
                cwd=str(dest_dir),
                check=False,
                capture_output=True,
            )
        except Exception:
            pass

    if open_editor:
        try:
            subprocess.run(["code", "."], cwd=str(dest_dir), check=False, shell=True)
        except Exception:
            pass

    # Record to Recent Projects and Activity Logs
    record_recent_project(dest_dir, name=project_name, db_path=db_path)
    log_activity(
        operation="PROJECT_CREATE",
        target=str(dest_dir),
        result="SUCCESS",
        details=f"Generated '{template_key}' project '{project_name}'",
        db_path=db_path,
    )

    return dest_dir
