# ENVIRONMENT SETUP — KIR AI Document Intelligence

> **File:** `docs/01_FOUNDATION/ENVIRONMENT_SETUP.md`  
> **Tujuan:** Panduan setup environment development lokal dari awal hingga siap digunakan  
> **Dependency:** README.md  
> **Dokumen terkait:** AI_SETUP.md, SECURITY_AND_SECRETS.md

---

## 1. Purpose

Dokumen ini memandu siapapun — developer baru atau mesin CI — untuk menyiapkan environment development yang siap menjalankan pipeline KIR AI Document Intelligence.

Setelah mengikuti panduan ini, environment Anda harus lulus verifikasi `kir doctor`.

---

## 2. Scope

- Setup Python dan virtual environment
- Instalasi dependencies
- Setup Playwright Chromium
- Verifikasi struktur direktori
- Menjalankan environment doctor
- Development commands yang tersedia
- Troubleshooting masalah umum
- Definisi "healthy environment"

## 3. Non-Scope

- Konfigurasi AI provider (lihat AI_SETUP.md)
- Pengelolaan secret (lihat SECURITY_AND_SECRETS.md)
- Setup server production

---

## 4. Persyaratan Sistem

| Komponen | Persyaratan Minimum | Rekomendasi |
|---|---|---|
| OS | Linux / macOS / Windows (WSL2) | Ubuntu 22.04+ atau macOS 13+ |
| Python | 3.11+ | 3.12 |
| RAM | 4GB | 8GB+ |
| Storage | 2GB | 5GB+ (untuk model Ollama) |
| Internet | Diperlukan untuk setup | Opsional setelah setup |

---

## 5. Python Setup

### 5.1 Verifikasi Python

```bash
python --version
# Harus menampilkan: Python 3.11.x atau lebih baru

python3 --version
# Alternatif jika `python` tidak tersedia
```

Jika Python belum terinstall atau versi terlalu lama:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev python3-pip
```

**macOS (via Homebrew):**
```bash
brew install python@3.12
```

**Windows (WSL2 — direkomendasikan):**
```bash
# Di dalam WSL2 shell (Ubuntu)
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev python3-pip
```

### 5.2 Virtual Environment

Selalu gunakan virtual environment untuk mengisolasi dependencies project.

```bash
# Masuk ke direktori project
cd /path/to/KIR

# Buat virtual environment
python3.12 -m venv .venv

# Aktifkan virtual environment
# Linux / macOS:
source .venv/bin/activate

# Windows CMD:
.venv\Scripts\activate.bat

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Verifikasi aktivasi (prompt berubah menampilkan (.venv))
which python
# Harus menampilkan: /path/to/KIR/.venv/bin/python
```

**PENTING:** Virtual environment harus **selalu aktif** saat bekerja dengan project ini. Jangan install ke Python global.

---

## 6. Instalasi Dependencies

### 6.1 Struktur pyproject.toml

Project menggunakan `pyproject.toml` sebagai konfigurasi tunggal:

```toml
# pyproject.toml (konseptual — akan dibuat saat Phase 1)
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "kir-ai"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.5",
    "pydantic-settings>=2.1",
    "python-dotenv>=1.0",
    "jinja2>=3.1",
    "playwright>=1.40",
    "pymupdf>=1.23",
    "openai>=1.10",     # kompatibel dengan 9Router
    "httpx>=0.25",
    "rich>=13.0",       # output CLI yang menarik
    "typer>=0.9",       # framework CLI
    "tenacity>=8.2",    # retry logic
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.1",
    "ruff>=0.1",
    "mypy>=1.7",
]

[project.scripts]
kir = "app.main:app"
```

### 6.2 Instalasi

```bash
# Pastikan .venv aktif terlebih dahulu

# Install package beserta dependencies
pip install -e ".[dev]"

# Verifikasi instalasi
pip list | grep -E "pydantic|playwright|jinja2|openai|typer"
```

### 6.3 Upgrade pip (jika diperlukan)

```bash
pip install --upgrade pip
```

---

## 7. Playwright Setup

Playwright digunakan untuk mengrender HTML ke PDF menggunakan browser Chromium.

### 7.1 Instalasi Chromium

```bash
# Install Playwright browsers (hanya Chromium yang diperlukan)
playwright install chromium

# Verifikasi instalasi
playwright --version
```

Chromium akan terinstall di:
- Linux: `~/.cache/ms-playwright/`
- macOS: `~/Library/Caches/ms-playwright/`
- Windows: `%USERPROFILE%\AppData\Local\ms-playwright\`

### 7.2 Dependensi Sistem untuk Playwright (Linux)

Di Linux, Playwright memerlukan beberapa library sistem:

```bash
# Install dependensi sistem (Ubuntu/Debian)
playwright install-deps chromium

# Atau secara manual:
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

### 7.3 Verifikasi Playwright

```bash
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('about:blank')
    browser.close()
    print('Playwright OK')
"
```

Output yang diharapkan: `Playwright OK`

---

## 8. Struktur Direktori

Buat direktori yang diperlukan jika belum ada:

```bash
# Dari root project
mkdir -p \
    app/ai/providers \
    app/agents \
    app/config \
    app/core \
    app/document \
    app/design \
    app/quality \
    app/rendering \
    assets/fonts \
    assets/icons \
    assets/images \
    assets/generated \
    data/input \
    data/processed \
    data/examples \
    data/cache \
    outputs/jobs \
    outputs/benchmarks \
    prompts/system \
    prompts/agents \
    prompts/document_types \
    prompts/output \
    templates/html \
    templates/css \
    templates/document_types \
    themes \
    tests/unit \
    tests/integration \
    tests/fixtures
```

### 8.1 Verifikasi Struktur

```bash
# Tampilkan struktur (install tree jika belum ada)
find . -type d -not -path './.venv/*' -not -path './.git/*' | sort
```

### 8.2 File `.gitignore`

Pastikan `.gitignore` mengandung (minimal):

```gitignore
# Virtual environment
.venv/
venv/

# Environment secrets
.env
.env.local
.env.*.local

# Output (tidak perlu di-commit)
outputs/jobs/
data/cache/
assets/generated/

# Python artifacts
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.mypy_cache/
.pytest_cache/
.coverage

# Playwright browsers
# (sudah di-cache oleh playwright sendiri)
```

---

## 9. Konfigurasi Environment

### 9.1 File `.env.example`

Project menyediakan `.env.example` sebagai template. Salin dan isi nilainya:

```bash
cp .env.example .env
```

Isi `.env` dengan nilai yang sesuai. Lihat [`AI_SETUP.md`](AI_SETUP.md) untuk panduan konfigurasi AI.

**TIDAK BOLEH** commit file `.env` ke Git. Lihat [`SECURITY_AND_SECRETS.md`](SECURITY_AND_SECRETS.md).

### 9.2 Contoh `.env.example`

```dotenv
# ============================================================
# KIR AI Document Intelligence — Environment Configuration
# Salin file ini ke .env dan isi nilainya
# JANGAN commit .env ke Git
# ============================================================

# --- AI Provider: 9Router (Primary) ---
AI_PROVIDER=9router
NINE_ROUTER_BASE_URL=http://127.0.0.1:20128/v1
NINE_ROUTER_API_KEY=your-api-key-here

# --- AI Provider: Ollama (Local Fallback) ---
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
OLLAMA_MODEL=qwen3:8b

# --- Model Role Assignment ---
PLANNER_MODEL=qwen3:8b
WRITER_MODEL=qwen3:8b
DESIGN_MODEL=qwen3:8b
CRITIC_MODEL=qwen3:8b

# --- Pipeline Configuration ---
MAX_REPAIR_ATTEMPTS=3
MAX_REVISION_COUNT=2
QUALITY_THRESHOLD=70.0
AI_TIMEOUT_SECONDS=120

# --- Paths ---
OUTPUT_DIR=outputs
DATA_DIR=data
CACHE_DIR=data/cache
PROMPTS_DIR=prompts
TEMPLATES_DIR=templates
THEMES_DIR=themes

# --- Logging ---
LOG_LEVEL=INFO
LOG_TO_FILE=false
LOG_FILE_PATH=logs/kir.log
```

---

## 10. Environment Doctor

`kir doctor` adalah perintah diagnostik yang memverifikasi seluruh environment.

### 10.1 Menjalankan Doctor

```bash
kir doctor
```

### 10.2 Output yang Diharapkan

```
KIR AI Document Intelligence — Environment Doctor
==================================================

[✓] Python 3.12.2 (>= 3.11 required)
[✓] Virtual environment active (.venv)
[✓] Dependencies installed (kir-ai 0.1.0)

[→] Checking directories...
[✓] data/input exists
[✓] data/cache exists
[✓] outputs/jobs exists
[✓] templates/html exists
[✓] themes exists
[✓] prompts/system exists

[→] Checking environment variables...
[✓] NINE_ROUTER_BASE_URL set
[✓] NINE_ROUTER_API_KEY set (value hidden)
[✓] OLLAMA_BASE_URL set
[✓] PLANNER_MODEL set (qwen3:8b)
[✓] WRITER_MODEL set (qwen3:8b)

[→] Checking Playwright...
[✓] Playwright 1.40.0 installed
[✓] Chromium available

[→] Checking AI providers...
[✓] 9Router: reachable (http://127.0.0.1:20128/v1)
[✓] Ollama: reachable (http://127.0.0.1:11434/v1)
[✓] Model qwen3:8b available on Ollama

==================================================
Status: HEALTHY ✓
All checks passed. Environment is ready.
```

### 10.3 Jika Ada Check yang Gagal

```
[✗] NINE_ROUTER_API_KEY not set
    → Add NINE_ROUTER_API_KEY to your .env file
    → See: docs/01_FOUNDATION/AI_SETUP.md

[✗] Chromium not found
    → Run: playwright install chromium
    → If on Linux, also run: playwright install-deps chromium
```

Doctor tidak pernah mengekspos nilai secret dalam output — hanya mengindikasikan apakah sudah di-set atau belum.

---

## 11. Development Commands

### 11.1 CLI Commands Dasar

```bash
# Verifikasi environment
kir doctor

# Lihat model yang tersedia
kir models

# Generate dokumen
kir generate --input data/input/materi.md --mode a4-tutorial

# Generate dengan output spesifik
kir generate --input data/input/materi.md --mode presentation-16-9 --output outputs/test/

# Generate hanya blueprint (tanpa render ke PDF)
kir plan --input data/input/materi.md --mode a4-tutorial

# Render dari blueprint yang sudah ada
kir render --blueprint outputs/jobs/abc123/blueprint/blueprint.json

# Inspeksi job atau artifact
kir inspect job abc123
kir inspect job abc123 --step blueprint
kir inspect job abc123 --step quality
```

### 11.2 Development Commands

```bash
# Jalankan semua tests
pytest

# Jalankan tests dengan coverage
pytest --cov=app --cov-report=term-missing

# Jalankan hanya unit tests
pytest tests/unit/

# Jalankan hanya integration tests
pytest tests/integration/

# Linting (ruff)
ruff check app/
ruff format app/

# Type checking (mypy)
mypy app/

# Jalankan semua quality checks sekaligus
ruff check app/ && mypy app/ && pytest
```

### 11.3 Makefile (Opsional)

Untuk kemudahan, project dapat menyediakan Makefile:

```makefile
.PHONY: setup doctor test lint typecheck check

setup:
	pip install -e ".[dev]"
	playwright install chromium

doctor:
	kir doctor

test:
	pytest tests/

lint:
	ruff check app/
	ruff format --check app/

typecheck:
	mypy app/

check: lint typecheck test
```

---

## 12. Troubleshooting

### 12.1 `playwright install chromium` gagal

**Gejala:** Error saat instalasi, koneksi timeout.

**Solusi:**
```bash
# Set PLAYWRIGHT_BROWSERS_PATH jika ada masalah permission
export PLAYWRIGHT_BROWSERS_PATH=/tmp/playwright-browsers
playwright install chromium

# Atau gunakan mirror (jika di jaringan terbatas)
export PLAYWRIGHT_DOWNLOAD_HOST=https://playwright.azureedge.net
playwright install chromium
```

### 12.2 `kir doctor` melaporkan direktori tidak ada

**Gejala:** `[✗] data/input does not exist`

**Solusi:**
```bash
# Jalankan ulang script pembuatan direktori
mkdir -p data/input data/cache outputs/jobs templates/html themes prompts/system
```

### 12.3 Python version tidak sesuai

**Gejala:** `Python 3.9.x` atau lebih lama.

**Solusi (Ubuntu):**
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
# Buat ulang virtual environment dengan python3.12
deactivate
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 12.4 `pip install` gagal — dependency conflict

**Gejala:** `ERROR: pip's dependency resolver does not currently take into account all the packages...`

**Solusi:**
```bash
# Pastikan pip terbaru
pip install --upgrade pip

# Install ulang dengan --no-cache-dir
pip install --no-cache-dir -e ".[dev]"
```

### 12.5 Playwright tidak bisa membuka browser di Linux headless

**Gejala:** `Error: Browser closed unexpectedly` di server tanpa display.

**Solusi:**
```bash
# Install Xvfb untuk virtual display
sudo apt install xvfb

# Jalankan dengan virtual display
xvfb-run python -m pytest tests/

# Atau set environment variable
export PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox --disable-dev-shm-usage"
```

### 12.6 Import error setelah install

**Gejala:** `ModuleNotFoundError: No module named 'app'`

**Solusi:**
```bash
# Pastikan install dalam mode editable
pip install -e ".[dev]"

# Verifikasi
python -c "import app; print('OK')"
```

---

## 13. Definisi "Healthy Environment"

Environment dianggap **healthy** dan siap untuk development jika semua kondisi berikut terpenuhi:

| Kondisi | Cara Verifikasi |
|---|---|
| Python 3.11+ terinstall dan aktif di .venv | `python --version` |
| Semua dependencies terinstall | `pip list` + `pip check` |
| Playwright Chromium tersedia | `python -c "from playwright.sync_api import sync_playwright"` |
| File `.env` ada dan tidak kosong | `cat .env` (redacted) |
| Semua environment variable required ter-set | `kir doctor` |
| Semua direktori project ada | `kir doctor` |
| Setidaknya satu AI provider reachable | `kir doctor` |
| `pytest` dapat dijalankan tanpa import error | `pytest --collect-only` |

**Single command verification:**
```bash
kir doctor && echo "Environment is HEALTHY"
```

Jika output berakhir dengan `Environment is HEALTHY`, sistem siap digunakan.
