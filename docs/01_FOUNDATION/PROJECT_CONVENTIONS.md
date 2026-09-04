# PROJECT CONVENTIONS — KIR AI Document Intelligence

> **File:** `docs/01_FOUNDATION/PROJECT_CONVENTIONS.md`  
> **Tujuan:** Konvensi dan standar kode yang berlaku di seluruh project  
> **Dependency:** ARCHITECTURE.md  
> **Dokumen terkait:** TESTING_STRATEGY.md

---

## 1. Purpose

Dokumen ini mendefinisikan konvensi yang harus diikuti oleh semua developer (manusia maupun AI coding agent) yang bekerja pada project KIR AI Document Intelligence.

Konvensi ini bukan preferensi estetika semata — konvensi ini ada untuk:
1. Memastikan konsistensi antar modul dan kontributor
2. Membuat kode mudah dibaca dan diaudit
3. Mencegah kategori bug yang umum
4. Memudahkan onboarding developer baru
5. Memudahkan AI coding agent memahami dan menavigasi codebase

Setiap keputusan yang bertentangan dengan konvensi ini harus didokumentasikan alasannya — tidak cukup hanya mengabaikannya.

---

## 2. Scope

- Naming conventions untuk semua artefak kode
- Python code style
- Type annotation
- Import ordering
- Exception strategy
- Logging
- Configuration pattern
- Kepemilikan folder
- Code review checklist
- Definition of done

## 3. Non-Scope

- Design pattern untuk UI (tidak ada UI di fase ini)
- Konvensi database (tidak ada database)
- Deployment conventions (aplikasi local-first)

---

## 4. Naming Conventions

### 4.1 File dan Modul Python

| Konteks | Konvensi | Contoh |
|---|---|---|
| Module file | `snake_case.py` | `blueprint_validator.py` |
| Package directory | `snake_case/` | `app/document/` |
| Test file | `test_{module_name}.py` | `test_blueprint_validator.py` |
| Configuration file | `snake_case.py` | `settings.py` |
| Fixture file | `{context}_fixtures.py` | `blueprint_fixtures.py` |

### 4.2 Python Identifiers

| Konteks | Konvensi | Contoh |
|---|---|---|
| Variable | `snake_case` | `content_unit`, `job_id` |
| Function / Method | `snake_case` | `validate_blueprint()`, `get_job_status()` |
| Class | `PascalCase` | `BlueprintValidator`, `NineRouterProvider` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_REPAIR_ATTEMPTS`, `DEFAULT_TIMEOUT` |
| Type alias | `PascalCase` | `ContentUnitList`, `JobId` |
| Enum | `PascalCase` (class) + `UPPER_SNAKE_CASE` (member) | `class ContentType: DEFINITION = "definition"` |
| Private attribute | `_snake_case` | `_client`, `_config` |
| Abstract method | `snake_case` | `generate()`, `health_check()` |

### 4.3 Domain Object Naming

Nama domain object **harus konsisten** dengan yang didefinisikan di `DOMAIN_SCHEMA.md`. Dilarang membuat alias atau nama alternatif.

| Schema Name | Python Class | TIDAK BOLEH |
|---|---|---|
| `Blueprint` | `Blueprint` | `DocBlueprint`, `DocumentBlueprint` |
| `ContentUnit` | `ContentUnit` | `Content`, `Unit`, `ContentItem` |
| `QualityReport` | `QualityReport` | `Report`, `QAResult` |
| `RenderJob` | `RenderJob` | `Job`, `RenderTask` |

### 4.4 File Output dan Artifact

| Artifact | Penamaan File |
|---|---|
| Blueprint JSON | `blueprint.json` |
| Quality report | `quality_report.json` |
| Final PDF | `{document_title_slug}.pdf` |
| HTML intermediate | `document.html` |
| Job metadata | `metadata.json` |

Slug dari judul dokumen: huruf kecil, spasi diganti `_`, karakter non-alphanumeric dihapus.

Contoh: `"Panduan Machine Learning #2"` → `panduan_machine_learning_2`

### 4.5 Environment Variables

Semua environment variables menggunakan `UPPER_SNAKE_CASE` dengan prefix yang sesuai:

| Prefix | Konteks |
|---|---|
| `NINE_ROUTER_` | Konfigurasi 9Router provider |
| `OLLAMA_` | Konfigurasi Ollama provider |
| `PLANNER_` | Konfigurasi planner agent |
| `WRITER_` | Konfigurasi writer agent |
| `DESIGN_` | Konfigurasi design director agent |
| `CRITIC_` | Konfigurasi critic agent |
| (tanpa prefix) | Konfigurasi umum: `LOG_LEVEL`, `OUTPUT_DIR`, dll |

### 4.6 Direktori dan Path

Direktori menggunakan `snake_case/` (bukan `camelCase/` atau `PascalCase/`).

```
# BENAR
app/document/
app/ai/providers/
data/processed/

# SALAH
app/Document/
app/aiProviders/
data/Processed/
```

---

## 5. Python Code Style

### 5.1 Formatter dan Linter

Project menggunakan **Ruff** sebagai formatter dan linter tunggal:

```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "UP",  # pyupgrade
    "N",   # pep8-naming
    "ANN", # flake8-annotations (type hints)
]
ignore = [
    "ANN101",  # Missing type annotation for self
    "ANN102",  # Missing type annotation for cls
]
```

**Wajib dijalankan sebelum commit:**
```bash
ruff check app/
ruff format app/
```

### 5.2 Line Length

Maksimum **100 karakter** per baris. Ini dikonfigurasi di Ruff dan konsisten di seluruh project.

### 5.3 String Quoting

Gunakan **double quotes** (`"`) secara konsisten. Ruff akan mengatur ini secara otomatis.

```python
# BENAR
message = "Hello, World!"
name = "qwen3:8b"

# SALAH (akan diformat ulang oleh Ruff)
message = 'Hello, World!'
```

### 5.4 Blank Lines

- 2 blank lines antara top-level definitions (class, function)
- 1 blank line antara method dalam class
- Tidak ada trailing blank line di akhir file (Ruff mengatur ini)

### 5.5 Docstrings

Semua public class dan function **wajib** memiliki docstring:

```python
class BlueprintValidator:
    """Validates Blueprint objects against the domain schema.

    Uses Pydantic for structural validation and additional
    business rules for semantic validation.
    """

    def validate(self, blueprint: Blueprint) -> ValidationResult:
        """Validate a blueprint and return the result.

        Args:
            blueprint: The Blueprint object to validate.

        Returns:
            ValidationResult with is_valid, errors, and warnings.

        Raises:
            SchemaValidationError: If blueprint structure is fundamentally invalid.
        """
        ...
```

Format docstring: **Google style**.

Private methods (prefix `_`) boleh tidak memiliki docstring jika namanya sudah self-explanatory.

---

## 6. Type Annotation

### 6.1 Aturan Utama

**Semua** public function dan method **wajib** memiliki type annotation — parameter dan return type:

```python
# BENAR
def calculate_density(word_count: int, max_words: int) -> float:
    return word_count / max_words

async def generate_blueprint(
    analysis: AnalysisResult,
    mode: DocumentMode,
    theme: Theme,
) -> Blueprint:
    ...

# SALAH — tidak ada type annotation
def calculate_density(word_count, max_words):
    return word_count / max_words
```

### 6.2 Import dari `typing`

Gunakan type hints modern Python 3.10+:

```python
# BENAR (Python 3.10+)
def get_unit(unit_id: str | None) -> ContentUnit | None:
    ...

list[ContentUnit]  # bukan List[ContentUnit]
dict[str, Any]     # bukan Dict[str, Any]

# SALAH (gaya lama)
from typing import Optional, List, Dict
def get_unit(unit_id: Optional[str]) -> Optional[ContentUnit]:
    ...
```

### 6.3 Pydantic Models

Domain objects menggunakan Pydantic. Jangan membuat dataclass atau TypedDict untuk domain objects — gunakan Pydantic model.

```python
# BENAR
from pydantic import BaseModel, Field, field_validator

class ContentUnit(BaseModel):
    unit_id: str = Field(description="UUID v4 identifier")
    content_type: ContentType
    raw_text: str = Field(min_length=1)
    density_score: float = Field(ge=0.0, le=1.0)

    @field_validator("unit_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        # validasi UUID format
        ...
        return v
```

### 6.4 Type Checking

Project menggunakan **mypy** dengan strict mode:

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
```

Jalankan: `mypy app/`

Tidak boleh ada `# type: ignore` tanpa penjelasan yang valid dalam komentar.

---

## 7. Import Ordering

Import diurutkan dalam **tiga grup**, dipisahkan oleh blank line:

```python
# Grup 1: Standard library
import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any

# Grup 2: Third-party libraries
import httpx
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings
from tenacity import retry, stop_after_attempt

# Grup 3: Project imports (relative atau absolute)
from app.config.settings import AppSettings
from app.document.schema import Blueprint, ContentUnit, DocumentMode
from app.ai.base import AIProvider
```

Ruff dengan `select = ["I"]` akan mengatur ini secara otomatis.

**Aturan tambahan:**
- Gunakan **absolute imports** untuk semua import project
- Tidak ada `from module import *` — selalu import secara eksplisit
- Import yang tidak digunakan harus dihapus (Ruff akan mendeteksi ini)

---

## 8. Exception Strategy

### 8.1 Hierarki Exception

Semua exception project diturunkan dari `KIRError`:

```python
# app/core/exceptions.py

class KIRError(Exception):
    """Base exception for all KIR application errors."""

    def __init__(
        self,
        message: str,
        job_id: str | None = None,
        step: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.job_id = job_id
        self.step = step
        self.cause = cause

    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.job_id:
            parts.append(f"job_id={self.job_id}")
        if self.step:
            parts.append(f"step={self.step}")
        return " | ".join(parts)
```

### 8.2 Aturan Exception

**1. Jangan swallow exception secara diam-diam:**

```python
# SALAH
try:
    result = risky_operation()
except Exception:
    pass  # JANGAN

# BENAR
try:
    result = risky_operation()
except SpecificError as e:
    logger.warning(f"Operation failed: {e}")
    raise PipelineError(f"Risky operation failed", step="step_name", cause=e) from e
```

**2. Gunakan exception yang spesifik:**

```python
# SALAH
raise Exception("Something went wrong")

# BENAR
raise SchemaValidationError(
    f"Blueprint validation failed: {validation_error}",
    job_id=job_id,
    step="blueprint_validation",
    cause=validation_error,
)
```

**3. Chain exception dengan `from`:**

```python
try:
    ...
except ValueError as e:
    raise NormalizationError("Failed to normalize content", cause=e) from e
```

**4. Exception untuk logika vs. exception untuk bug:**

| Situasi | Exception |
|---|---|
| Input tidak valid dari user | `ValueError` atau subclass |
| AI provider tidak tersedia | `AIProviderError` |
| Schema tidak valid | `SchemaValidationError` |
| Bug dalam kode (seharusnya tidak terjadi) | `AssertionError` atau `RuntimeError` |

### 8.3 Context Manager untuk Resource

```python
# BENAR: Resource dijamin di-release
async with browser_context() as browser:
    page = await browser.new_page()
    ...  # browser selalu di-close

# SALAH: Resource bisa tidak di-release jika terjadi exception
browser = await playwright.chromium.launch()
page = await browser.new_page()
...
await browser.close()  # Tidak dipanggil jika exception terjadi di atas
```

---

## 9. Logging

### 9.1 Setup Logger

Setiap modul membuat logger-nya sendiri:

```python
import logging

logger = logging.getLogger(__name__)
# Menghasilkan nama: "app.document.blueprint", "app.ai.providers.nine_router", dll
```

Jangan menggunakan `print()` untuk output runtime — selalu gunakan logger.

### 9.2 Level Penggunaan

| Level | Kapan Digunakan |
|---|---|
| `DEBUG` | Detail teknis: ukuran output AI, intermediate values, timing detail |
| `INFO` | Lifecycle events: job started, step completed, file saved |
| `WARNING` | Situasi tidak normal yang masih dapat ditangani: retry, fallback, quality issue |
| `ERROR` | Exception yang menyebabkan step gagal (sebelum re-raise) |
| `CRITICAL` | Kegagalan sistem yang tidak dapat dipulihkan |

### 9.3 Format Log

```python
# BENAR: Informasi yang berguna, tidak ada secret
logger.info(f"Blueprint generated: {blueprint.total_pages} pages, model={model}")
logger.warning(f"Retrying AI call (attempt {attempt}/{max_attempts}): {error_type}")
logger.error(f"Render failed for job {job_id}: {error_message}")

# SALAH: Terlalu verbose atau mengandung potensi secret
logger.debug(f"Request headers: {headers}")  # Headers mengandung Authorization!
logger.info(f"API key: {api_key}")  # JANGAN PERNAH
```

### 9.4 Konfigurasi Logger Aplikasi

```python
# app/config/logging_config.py

import logging
from app.config.settings import AppSettings

def setup_logging(settings: AppSettings) -> None:
    """Configure application-wide logging."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Kurangi verbosity dari library eksternal
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
```

---

## 10. Configuration Pattern

### 10.1 Aturan Konfigurasi

1. **Semua konfigurasi dari environment** — tidak ada hardcoded values dalam business logic.
2. **Konfigurasi dibaca sekali** di startup via `AppSettings`.
3. **Konfigurasi di-inject** ke setiap komponen yang membutuhkannya — tidak pernah dibaca langsung dari `os.environ` di dalam modul.

### 10.2 AppSettings Structure

```python
# app/config/settings.py (konseptual)

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class NineRouterConfig(BaseSettings):
    base_url: str = "http://127.0.0.1:20128/v1"
    api_key: SecretStr
    timeout_seconds: int = 120
    max_retries: int = 3

    model_config = SettingsConfigDict(env_prefix="NINE_ROUTER_")

class OllamaConfig(BaseSettings):
    enabled: bool = True
    base_url: str = "http://127.0.0.1:11434/v1"
    model: str = "qwen3:8b"
    timeout_seconds: int = 120

    model_config = SettingsConfigDict(env_prefix="OLLAMA_")

class ModelConfig(BaseSettings):
    planner_model: str = Field(default="qwen3:8b", validation_alias="PLANNER_MODEL")
    writer_model: str = Field(default="qwen3:8b", validation_alias="WRITER_MODEL")
    design_model: str = Field(default="qwen3:8b", validation_alias="DESIGN_MODEL")
    critic_model: str = Field(default="qwen3:8b", validation_alias="CRITIC_MODEL")
    provider_preference: list[str] = Field(default=["nine_router", "ollama"], validation_alias="PROVIDER_PREFERENCE")

    model_config = SettingsConfigDict(populate_by_name=True, extra="ignore")

class AppSettings(BaseSettings):
    ai_provider: str = Field(default="9router", validation_alias="AI_PROVIDER")
    nine_router: NineRouterConfig = NineRouterConfig()
    ollama: OllamaConfig = OllamaConfig()
    models: ModelConfig = ModelConfig()

    # Pipeline
    max_repair_attempts: int = Field(default=3, validation_alias="MAX_REPAIR_ATTEMPTS")
    max_revision_count: int = Field(default=2, validation_alias="MAX_REVISION_COUNT")
    quality_threshold: float = Field(default=70.0, validation_alias="QUALITY_THRESHOLD")
    ai_timeout_seconds: int = Field(default=120, validation_alias="AI_TIMEOUT_SECONDS")

    # Paths
    output_dir: str = Field(default="outputs", validation_alias="OUTPUT_DIR")
    data_dir: str = Field(default="data", validation_alias="DATA_DIR")
    cache_dir: str = Field(default="data/cache", validation_alias="CACHE_DIR")
    prompts_dir: str = Field(default="prompts", validation_alias="PROMPTS_DIR")
    templates_dir: str = Field(default="templates", validation_alias="TEMPLATES_DIR")
    themes_dir: str = Field(default="themes", validation_alias="THEMES_DIR")

    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_to_file: bool = Field(default=False, validation_alias="LOG_TO_FILE")
    log_file_path: str = Field(default="logs/kir.log", validation_alias="LOG_FILE_PATH")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
```

### 10.3 Penggunaan Konfigurasi

```python
# BENAR: Inject lewat konstruktor
class DocumentPipeline:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._ai_provider = create_provider(settings)

# SALAH: Baca langsung dari environment
class DocumentPipeline:
    def generate(self) -> None:
        api_key = os.environ["NINE_ROUTER_API_KEY"]  # JANGAN
```

---

## 11. Folder Ownership

Setiap folder memiliki tanggung jawab yang jelas. Jangan menaruh kode di folder yang salah:

| Folder | Pemilik / Tanggung Jawab | TIDAK BOLEH mengandung |
|---|---|---|
| `app/ai/` | AI provider abstraction dan implementasi | Business logic dokumen |
| `app/agents/` | Agent orchestration logic | AI provider implementation |
| `app/config/` | Konfigurasi dan settings | Business logic |
| `app/core/` | Pipeline orchestration | UI, rendering detail |
| `app/document/` | Domain schema dan validation | AI calls, rendering |
| `app/design/` | Theme, page types, design decisions | AI calls langsung |
| `app/quality/` | Quality inspection dan scoring | Rendering logic |
| `app/rendering/` | HTML generation dan PDF export | Business logic |
| `prompts/` | Prompt templates (Jinja2) | Python code |
| `templates/` | HTML/CSS templates | Python code, business logic |
| `themes/` | Theme definition files (JSON/YAML) | Code |
| `tests/` | Test files | Production code |
| `data/input/` | Raw input files dari user | Generated outputs |
| `outputs/` | Generated artifacts | Input files |

---

## 12. Code Review Checklist

Gunakan checklist ini saat melakukan code review atau self-review sebelum commit:

### Correctness
- [ ] Logic sudah benar sesuai spesifikasi yang relevan?
- [ ] Edge case sudah ditangani (empty list, None value, zero)?
- [ ] Error handling sudah ada dan sesuai dengan exception hierarchy?

### Schema & Types
- [ ] Semua function memiliki type annotation?
- [ ] Domain objects menggunakan Pydantic (bukan plain dict atau dataclass)?
- [ ] `SecretStr` digunakan untuk semua API key?
- [ ] Tidak ada `Any` type yang tidak perlu?

### Security
- [ ] Tidak ada hardcoded secret?
- [ ] Log tidak mengandung nilai secret?
- [ ] API key menggunakan `get_secret_value()` hanya di tempat yang tepat?

### Architecture
- [ ] Domain layer tidak mengimport dari `app.ai` atau `app.rendering`?
- [ ] Konfigurasi dibaca dari `AppSettings`, bukan dari `os.environ` langsung?
- [ ] File berada di folder yang tepat sesuai kepemilikan?

### Code Quality
- [ ] Ruff check lulus tanpa warning?
- [ ] mypy check lulus?
- [ ] Semua public class dan function memiliki docstring?
- [ ] Tidak ada `# type: ignore` tanpa penjelasan?
- [ ] Tidak ada code yang di-comment-out tanpa alasan?

### Testing
- [ ] Ada unit test untuk logic baru?
- [ ] Test menggunakan mock untuk external dependencies (AI provider, filesystem)?
- [ ] `pytest` lulus?

---

## 13. Definition of Done

Sebuah task dianggap **selesai** jika semua kondisi berikut terpenuhi:

### Kode
- [ ] Implementasi sesuai dengan spesifikasi yang relevan (dokumen `docs/`)
- [ ] Tidak ada TODO yang belum diselesaikan (kecuali yang sengaja ditandai untuk fase berikutnya)
- [ ] Ruff check lulus: `ruff check app/`
- [ ] Ruff format lulus: `ruff format --check app/`
- [ ] mypy lulus: `mypy app/`

### Testing
- [ ] Unit test ada untuk setiap modul baru yang memiliki logic
- [ ] Semua test lulus: `pytest`
- [ ] Coverage tidak turun dari threshold (target: 80%)

### Dokumentasi
- [ ] Docstring ada untuk semua public API baru
- [ ] Jika ada perubahan pada domain schema: `DOMAIN_SCHEMA.md` diperbarui
- [ ] Jika ada perubahan pada arsitektur: `ARCHITECTURE.md` diperbarui
- [ ] Jika ada perubahan pada environment: `ENVIRONMENT_SETUP.md` atau `AI_SETUP.md` diperbarui

### Fungsionalitas
- [ ] `kir doctor` masih lulus
- [ ] Tidak ada regression pada fungsionalitas yang sudah ada
- [ ] Jika melibatkan AI call: artifact tersimpan dengan benar di `outputs/jobs/{job_id}/`

---

## 14. Acceptance Criteria

Konvensi dianggap diterapkan dengan benar jika:

- [ ] `ruff check app/` tidak menampilkan error apapun
- [ ] `mypy app/ --strict` tidak menampilkan error apapun  
- [ ] `grep -r "os.environ" app/ --include="*.py"` hanya menampilkan hasil dari `app/config/` (jika ada)
- [ ] `grep -r "print(" app/ --include="*.py"` tidak menampilkan hasil (semua output menggunakan logger)
- [ ] Tidak ada file Python di direktori yang salah (misalnya business logic di `app/rendering/`)
- [ ] Semua class domain mengextend `BaseModel` dari Pydantic
