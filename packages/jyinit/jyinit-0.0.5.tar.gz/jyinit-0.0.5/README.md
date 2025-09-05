# jyinit

🚀 **Extended Python Project Scaffolder** – create production-ready Python projects (apps, services, libraries, ML projects, etc.) with one command.  
Includes templates, licenses, CI/CD workflows, Git setup, and interactive prompts.

---

## ✨ Features

- 📦 **Multiple templates**: scaffold Flask, FastAPI, Django, Streamlit, ML, libraries, etc.
- ⚡ **Interactive mode** (`--interactive`): prompts you for missing options.
- 🔧 **Per-template GitHub Actions workflows** (via `--ci`).
- 📝 **Licenses included** (MIT, Apache-2.0, GPL-3.0, …).
- 🐙 **Git integration**:  
  - `--git` → initializes git repo(s) without remote.  
  - `--gitrep [url]` → initializes repo(s) and optionally sets a remote + pushes initial commit.
- 🧪 **Tests scaffold**: creates a `tests/` folder with `__init__.py`.
- 🐍 **Virtual environments** (`--venv`) per subproject.
- 🔍 **Dry-run mode** (`--dry-run`) – preview everything before creating files.

---

## 📥 Installation

```bash
pip install jyinit
````

Or clone locally for development:

```bash
git clone https://github.com/nj2216/jyinit.git
cd jyinit
pip install -e .
```

---

## 🚀 Usage

### Show help

```bash
jyinit --help
```

### Interactive mode

Prompts for template, license, Python version, etc.

```bash
jyinit create myproj --interactive
```

### Non-interactive example

Create a Flask app with CI, initialize git, and push to GitHub:

```bash
jyinit create myrepo --types flask --ci --gitrep https://github.com/you/myrepo.git
```

### Multiple templates (monorepo style)

```bash
jyinit create combo --types streamlit mlops --venv --gitrep
```

### List available templates and licenses

```bash
jyinit list-templates
```

---

## ⚙️ CLI Options

| Option           | Description                                                        |
| ---------------- | ------------------------------------------------------------------ |
| `--type`         | Legacy: single template scaffold                                   |
| `--types`        | One or more templates (`library`, `flask`, `fastapi`, `django`, …) |
| `--dir`          | Base directory for project                                         |
| `--license`      | Choose license (default: MIT)                                      |
| `--author`       | Author name (defaults to system user)                              |
| `--py`           | Minimum Python version (default: 3.8)                              |
| `--git`          | Initialize git (no remote)                                         |
| `--gitrep [url]` | Init git + set optional remote & push                              |
| `--venv`         | Create `.venv` per subproject                                      |
| `--no-tests`     | Skip creating `tests/` folder                                      |
| `--ci`           | Add tailored GitHub Actions workflow                               |
| `--interactive`  | Prompt for missing values                                          |
| `--dry-run`      | Preview without writing files                                      |

---

## 📂 Example Generated Project Structure

For a **Flask** project:

```
myrepo/
├── README.md
├── LICENSE
├── requirements.txt
├── myrepo/
│   └── __init__.py
├── tests/
│   └── __init__.py
└── .github/
    └── workflows/
        └── python-package.yml
```

For a **monorepo** with `streamlit` + `mlops`, you’ll get:

```
combo/
├── README.md
├── streamlit/
│   ├── ...
│   └── tests/
├── mlops/
│   ├── ...
│   └── tests/
```

---

## 🛠 Development

Clone the repo and install dev dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests (if you scaffolded pytest):

```bash
pytest
```

---

## 📜 License

jyinit is licensed under the **MIT License**.
See [LICENSE](https://github.com/nj2216/jyinit/blob/main/LICENSE) for details.

---

## 🙌 Acknowledgments

Inspired by Python project cookiecutters, but with **interactive scaffolding, monorepo support, and built-in CI**.

---

## 🤝 Contributing

Contributions are welcome! 🎉  
Please see our [CONTRIBUTING.md](https://github.com/nj2216/jyinit/blob/main/CONTRIBUTING.md) for guidelines on how to report issues, propose changes, and submit pull requests.

---

## 🧑‍💻 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://github.com/nj2216/jyinit/blob/main/CODE_OF_CONDUCT.md).  
By participating, you are expected to uphold this code. Please report any unacceptable behavior to the maintainers.

---
