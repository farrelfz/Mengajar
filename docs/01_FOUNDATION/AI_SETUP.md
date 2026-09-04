# AI SETUP — KIR AI Document Intelligence

> **File:** `docs/01_FOUNDATION/AI_SETUP.md`  
> **Tujuan:** Konfigurasi lengkap AI provider, model assignment, retry strategy, dan offline mode  
> **Dependency:** ENVIRONMENT_SETUP.md, SECURITY_AND_SECRETS.md  
> **Dokumen terkait:** AI_AGENT_ORCHESTRATION.md, PROMPT_SPECIFICATION.md

---

## 1. Purpose

Dokumen ini mendefinisikan:
- Abstraksi provider AI dan kenapa diperlukan
- Cara mengkonfigurasi 9Router (primary) dan Ollama (fallback)
- Format `.env` dan `.env.example`
- Cara memverifikasi endpoint dan model yang tersedia
- Cara meng-assign model ke role agent
- Strategy retry, fallback, dan timeout
- Structured output: cara memastikan AI mengembalikan JSON
- Cara menjalankan sistem dalam offline mode

**TIDAK ADA API KEY NYATA dalam dokumen ini.** Semua nilai adalah placeholder.

---

## 2. Scope

- Konfigurasi dan verifikasi AI provider
- Model role assignment
- Retry dan fallback behavior
- Structured output configuration

## 3. Non-Scope

- Implementasi agent (lihat AI_AGENT_ORCHESTRATION.md)
- Prompt design (lihat PROMPT_SPECIFICATION.md)
- Pengelolaan secret (lihat SECURITY_AND_SECRETS.md)

---

## 4. Provider Abstraction

Sistem menggunakan **AIProvider interface** yang memisahkan business logic dari implementasi provider spesifik.

```
Application Layer (agents)
        │
        │ calls
        ▼
AIProvider (interface)
        │
        ├── NineRouterProvider (primary)
        │       ↓ on failure
        └── OllamaProvider (fallback)
```

**Mengapa perlu abstraksi?**

1. Agent tidak perlu tahu apakah sedang bicara ke 9Router atau Ollama.
2. Fallback dapat terjadi secara transparan tanpa mengubah agent logic.
3. Provider baru dapat ditambahkan tanpa mengubah agent.
4. Testing dapat menggunakan mock provider.

**Interface (konseptual):**

```python
from abc import ABC, abstractmethod
from app.document.schema import GenerationRequest, GenerationResponse

class AIProvider(ABC):
    """Abstract base class for all AI providers."""

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Send a generation request and return the response."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is reachable and responsive."""
        ...

    @abstractmethod
    async def list_models(self) -> list[str]:
        """List available models on this provider."""
        ...
```

---

## 5. Provider: 9Router (Primary)

**9Router** adalah AI proxy lokal yang berfungsi sebagai OpenAI-compatible endpoint.

9Router dapat mengarahkan request ke berbagai model (cloud atau lokal) melalui satu endpoint tunggal.

### 5.1 Konfigurasi

Tambahkan ke file `.env`:

```dotenv
# 9Router — Primary AI Provider
AI_PROVIDER=9router
NINE_ROUTER_BASE_URL=http://127.0.0.1:20128/v1
NINE_ROUTER_API_KEY=your-9router-api-key-here
```

- `NINE_ROUTER_BASE_URL`: URL endpoint 9Router yang berjalan di lokal. Default port: `20128`.
- `NINE_ROUTER_API_KEY`: API key untuk autentikasi ke 9Router. Lihat dokumentasi 9Router untuk cara mendapatkannya.

### 5.2 Implementasi Provider

```python
# app/ai/providers/nine_router.py (konseptual)
import openai
from app.ai.base import AIProvider
from app.document.schema import GenerationRequest, GenerationResponse

class NineRouterProvider(AIProvider):
    def __init__(self, config: NineRouterConfig):
        self.client = openai.AsyncOpenAI(
            base_url=config.base_url,
            api_key=config.api_key.get_secret_value(),  # SecretStr
            timeout=config.timeout_seconds,
        )

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        # implementasi
        ...
```

### 5.3 Verifikasi 9Router

```bash
# Cek apakah 9Router berjalan
curl -s http://127.0.0.1:20128/v1/models \
  -H "Authorization: Bearer your-api-key-here" | python3 -m json.tool

# Atau gunakan kir CLI
kir models --provider nine_router
```

Output yang diharapkan:
```json
{
  "object": "list",
  "data": [
    {"id": "qwen3:8b", "object": "model"},
    {"id": "claude-3-5-sonnet", "object": "model"}
  ]
}
```

---

## 6. Provider: Ollama (Local Fallback)

**Ollama** adalah runtime untuk menjalankan model LLM lokal. Digunakan sebagai fallback jika 9Router tidak tersedia.

### 6.1 Instalasi Ollama

```bash
# Linux / macOS
curl -fsSL https://ollama.com/install.sh | sh

# Verifikasi
ollama --version
```

### 6.2 Download Model

```bash
# Download model yang akan digunakan (contoh: qwen3:8b)
ollama pull qwen3:8b

# Verifikasi model tersedia
ollama list
```

### 6.3 Konfigurasi

Tambahkan ke `.env`:

```dotenv
# Ollama — Local Fallback Provider
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
OLLAMA_MODEL=qwen3:8b
```

- `OLLAMA_ENABLED`: Set `false` untuk menonaktifkan fallback ke Ollama.
- `OLLAMA_BASE_URL`: Ollama juga menyediakan endpoint kompatibel OpenAI di port `11434/v1`.
- `OLLAMA_MODEL`: Model default untuk Ollama. Dapat di-override oleh role-specific model config.

### 6.4 Verifikasi Ollama

```bash
# Cek Ollama berjalan
curl http://127.0.0.1:11434/v1/models

# Test generation
curl http://127.0.0.1:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:8b",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'

# Atau gunakan kir CLI
kir models --provider ollama
```

---

## 7. File `.env` Lengkap

### 7.1 `.env.example` (Template)

File ini HARUS di-commit ke Git sebagai referensi. Tidak boleh mengandung nilai nyata.

```dotenv
# ============================================================
# KIR AI Document Intelligence — Environment Configuration
# ============================================================
# INSTRUKSI:
# 1. Salin file ini: cp .env.example .env
# 2. Isi nilai yang sesuai di .env
# 3. JANGAN commit .env ke Git
# ============================================================

# ============================================================
# AI PROVIDER — PRIMARY: 9Router
# ============================================================
# Pilih provider utama: "9router" atau "ollama"
AI_PROVIDER=9router

# URL endpoint 9Router (OpenAI-compatible)
NINE_ROUTER_BASE_URL=http://127.0.0.1:20128/v1

# API key untuk 9Router
# Dapatkan dari dokumentasi/dashboard 9Router
NINE_ROUTER_API_KEY=replace-with-your-9router-api-key

# ============================================================
# AI PROVIDER — FALLBACK: Ollama
# ============================================================
# Aktifkan/nonaktifkan Ollama sebagai fallback
OLLAMA_ENABLED=true

# URL endpoint Ollama (OpenAI-compatible)
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1

# Model default untuk Ollama
OLLAMA_MODEL=qwen3:8b

# ============================================================
# MODEL ROLE ASSIGNMENT
# ============================================================
# Setiap role memiliki model tersendiri.
# Gunakan format: provider/model-name atau hanya model-name
# Jika tidak diset, akan menggunakan OLLAMA_MODEL sebagai default.

# Model untuk Document Planner agent
PLANNER_MODEL=qwen3:8b

# Model untuk Content Writer agent
WRITER_MODEL=qwen3:8b

# Model untuk Design Director agent
DESIGN_MODEL=qwen3:8b

# Model untuk Quality Critic agent
CRITIC_MODEL=qwen3:8b

# ============================================================
# PIPELINE CONFIGURATION
# ============================================================
# Maksimum percobaan repair saat Blueprint validation gagal
MAX_REPAIR_ATTEMPTS=3

# Maksimum siklus revisi kualitas
MAX_REVISION_COUNT=2

# Threshold skor kualitas (0-100). Di bawah ini = gagal.
QUALITY_THRESHOLD=70.0

# Timeout untuk setiap AI call (detik)
AI_TIMEOUT_SECONDS=120

# ============================================================
# PATHS
# ============================================================
OUTPUT_DIR=outputs
DATA_DIR=data
CACHE_DIR=data/cache
PROMPTS_DIR=prompts
TEMPLATES_DIR=templates
THEMES_DIR=themes

# ============================================================
# LOGGING
# ============================================================
# Level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Aktifkan log ke file (selain stdout)
LOG_TO_FILE=false
LOG_FILE_PATH=logs/kir.log
```

### 7.2 Urutan Prioritas Konfigurasi

```
1. Environment Variables (dari shell/OS)
     ↓ override
2. .env file (dari direktori project)
     ↓ override
3. Default values (didefinisikan di AppSettings)
```

Pydantic Settings secara otomatis mengikuti urutan ini.

---

## 8. Model Discovery

### 8.1 List Model yang Tersedia

```bash
# Semua provider
kir models

# Provider spesifik
kir models --provider nine_router
kir models --provider ollama
```

### 8.2 Memilih Model yang Tepat

| Role | Kebutuhan Utama | Rekomendasi Minimum |
|---|---|---|
| PLANNER_MODEL | Kemampuan reasoning, structured output | 7B params |
| WRITER_MODEL | Kemampuan menulis konten berkualitas | 7B params |
| DESIGN_MODEL | Pemahaman layout dan struktur JSON | 7B params |
| CRITIC_MODEL | Kemampuan evaluasi kritis | 7B params |

Model yang lebih besar = kualitas lebih baik tetapi lebih lambat dan membutuhkan lebih banyak resource.

---

## 9. Retry Strategy

Setiap AI call menggunakan retry strategy yang terdefinisi:

```
REQUEST
   │
   ▼
Attempt 1
   │
   ├── [success] ──────────────────→ Return response
   │
   └── [failure: transient error]
         │
         ▼ wait exponential backoff (1s, 2s, 4s)
      Attempt 2
         │
         ├── [success] ──────────→ Return response
         │
         └── [failure]
               │
               ▼ wait backoff
            Attempt 3 (MAX_RETRIES=3)
               │
               ├── [success] ──→ Return response
               │
               └── [failure]
                     │
                     ▼
               TRIGGER FALLBACK PROVIDER
```

### 9.1 Error Classification

Tidak semua error di-retry. Error diklasifikasikan:

| Error Type | Di-retry? | Keterangan |
|---|---|---|
| `APIConnectionError` | ✅ Ya | Network issue, sementara |
| `APITimeoutError` | ✅ Ya | Timeout, coba lagi |
| `APIRateLimitError` | ✅ Ya | Rate limit, wait + retry |
| `APIAuthenticationError` | ❌ Tidak | API key salah → immediate fail |
| `JSONDecodeError` (output AI) | ✅ Ya | Gunakan repair prompt |
| `SchemaValidationError` | ✅ Ya | Gunakan repair prompt |
| `MaxTokensExceededError` | ❌ Tidak | Prompt terlalu panjang → fail |

### 9.2 Exponential Backoff

```python
# Konfigurasi tenacity (konseptual)
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
async def call_with_retry(self, request: GenerationRequest) -> GenerationResponse:
    ...
```

---

## 10. Fallback Behavior

### 10.1 Fallback Chain

```
9Router (primary)
      │ failure setelah MAX_RETRIES
      ▼
Ollama (fallback) — jika OLLAMA_ENABLED=true
      │ failure setelah MAX_RETRIES
      ▼
AIProviderError (fatal) — job gagal dengan FAILED_AI
```

### 10.2 Conditions untuk Fallback

Fallback ke Ollama terjadi jika:
- `9Router` tidak reachable (connection refused, timeout)
- `9Router` mengembalikan error 5xx setelah max retries
- `9Router` mengembalikan error rate limit dan backoff habis

Fallback **TIDAK** terjadi jika:
- API key salah (`401 Unauthorized`) — ini adalah configuration error
- Request tidak valid (`400 Bad Request`) — ini adalah prompt error

### 10.3 Fallback Logging

Saat fallback terjadi, sistem mencatat:

```
[WARNING] [ai.fallback] 9Router failed after 3 attempts (APIConnectionError: Connection refused)
[WARNING] [ai.fallback] Switching to Ollama fallback provider
[INFO]    [ai.ollama]   Using model: qwen3:8b
```

API key **tidak pernah** muncul dalam log. Lihat [`SECURITY_AND_SECRETS.md`](SECURITY_AND_SECRETS.md).

---

## 11. Timeout Configuration

| Scenario | Timeout | Keterangan |
|---|---|---|
| Normal AI call | `AI_TIMEOUT_SECONDS` (default: 120s) | Untuk output normal |
| Blueprint generation | `AI_TIMEOUT_SECONDS * 2` (default: 240s) | Output panjang |
| Health check | 5s | Hanya cek konektivitas |
| Model list | 10s | Cek daftar model |

Timeout per model dapat dioverride di konfigurasi jika model tertentu memerlukan lebih banyak waktu.

---

## 12. Structured Output

Sistem menggunakan **structured output** untuk memastikan AI mengembalikan JSON yang valid.

### 12.1 Mengapa Structured Output Penting?

AI tidak selalu mengembalikan JSON yang bersih. Tanpa structured output:
- AI bisa menambahkan markdown di sekitar JSON (`\`\`\`json ... \`\`\``)
- AI bisa menambahkan penjelasan setelah JSON
- JSON bisa memiliki field yang tidak sesuai schema
- JSON bisa parsial (output dipotong)

### 12.2 Pendekatan Structured Output

**Level 1: JSON Mode (basic)**

Jika provider mendukung `response_format: {"type": "json_object"}`:

```python
response = await client.chat.completions.create(
    model=model,
    messages=messages,
    response_format={"type": "json_object"},
)
```

**Level 2: Schema-constrained output (preferred)**

Jika provider mendukung JSON Schema:

```python
response = await client.chat.completions.create(
    model=model,
    messages=messages,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "Blueprint",
            "schema": Blueprint.model_json_schema(),
        }
    },
)
```

**Level 3: Prompt-enforced + parser (fallback)**

Jika provider tidak mendukung structured output natively:

```
System prompt: "You MUST respond with valid JSON only. No markdown. No explanation."
→ Parse response
→ If JSONDecodeError: use repair prompt
→ If SchemaValidationError: use repair prompt
→ Retry (max MAX_REPAIR_ATTEMPTS)
```

### 12.3 Repair Prompt

Saat output AI tidak valid JSON atau tidak sesuai schema:

```
SYSTEM: You are a JSON repair specialist.

USER:
The following AI output failed JSON validation.

ORIGINAL OUTPUT:
{invalid_output}

VALIDATION ERROR:
{error_message}

REQUIRED SCHEMA:
{schema_json}

Please return ONLY valid JSON that conforms to the schema.
No explanation. No markdown. Only the JSON object.
```

---

## 13. Offline Mode

Sistem dapat berjalan dalam offline mode menggunakan **hanya Ollama** jika tidak ada koneksi internet.

### 13.1 Mengaktifkan Offline Mode

```dotenv
# .env — Offline mode
AI_PROVIDER=ollama
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
OLLAMA_MODEL=qwen3:8b

# Nonaktifkan 9Router
NINE_ROUTER_BASE_URL=
NINE_ROUTER_API_KEY=
```

### 13.2 Persyaratan Offline Mode

1. Ollama terinstall dan berjalan: `ollama serve`
2. Model sudah di-download sebelumnya: `ollama pull qwen3:8b`
3. `OLLAMA_ENABLED=true` dalam `.env`

### 13.3 Verifikasi Offline Mode

```bash
# Pastikan Ollama berjalan
ollama list

# Jalankan doctor
kir doctor

# Output yang diharapkan (offline mode):
# [✓] Ollama: reachable (http://127.0.0.1:11434/v1)
# [✓] Model qwen3:8b available on Ollama
# [!] 9Router: not configured (offline mode active)
```

---

## 14. Acceptance Criteria

Konfigurasi AI dianggap benar jika:

- [ ] `kir doctor` menampilkan setidaknya satu provider sebagai reachable
- [ ] `kir models` menampilkan daftar model yang tersedia
- [ ] `NINE_ROUTER_API_KEY` tidak pernah muncul dalam log (hanya `[HIDDEN]`)
- [ ] Fallback ke Ollama terjadi secara otomatis saat 9Router tidak tersedia
- [ ] `MAX_REPAIR_ATTEMPTS` membatasi loop repair — tidak pernah infinite
- [ ] Saat semua provider gagal, sistem menghasilkan `AIProviderError` dengan job status `FAILED_AI`
- [ ] Model yang di-assign ke setiap role dapat di-override via `.env` tanpa mengubah kode
- [ ] Offline mode berfungsi menggunakan hanya Ollama
