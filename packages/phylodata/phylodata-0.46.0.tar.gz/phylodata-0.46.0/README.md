# 🧬 PhyloData Python Libary

## 📖 Usage

> [!TIP]
> Check out the [documentation](https://phylodata.com/docs/python_first_steps) for more information.

## For Developers

## 🔧 Tech Stack

- **Python**: Requires Python 3.10+
- **Streamlit**: Web interface for data processing
- **UV**: Modern Python package manager and installer (no venv required)
- **Just**: Command runner used for development workflows

### 📋 Prerequisites

- Python 3.10+
- [UV](https://github.com/astral-sh/uv) for dependency management
- [Just](https://github.com/casey/just) for running commands

### 🛠️ Development Commands

Run these commands with `just`:

```bash
just test    # Run pytest tests with UV
just check   # Run ruff linter with auto-fix
just format  # Format code with ruff
```

In order to run a script using the dependencies, just preface it with `uv python`:

```bash
uv python my_script.py
```
