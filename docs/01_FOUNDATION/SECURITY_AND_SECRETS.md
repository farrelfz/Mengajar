# SECURITY AND SECRETS — KIR AI Document Intelligence

> **File:** `docs/01_FOUNDATION/SECURITY_AND_SECRETS.md`  
> **Tujuan:** Panduan lengkap pengelolaan secret, keamanan konfigurasi, dan incident response  
> **Dependency:** README.md  
> **Dokumen terkait:** AI_SETUP.md, ENVIRONMENT_SETUP.md

---

## 1. Purpose

Dokumen ini mendefinisikan cara yang benar dan aman untuk mengelola API key, credential, dan informasi sensitif lainnya dalam project KIR AI Document Intelligence.

Sistem ini bersifat **local-first** — artinya sebagian besar operasi terjadi di mesin lokal. Namun, sistem berinteraksi dengan layanan eksternal via API key yang harus dijaga kerahasiaannya.

---

## 2. Scope

- Secret lifecycle: dari setup hingga rotasi
- Penggunaan file `.env` yang benar
- Perlindungan Git (apa yang tidak boleh di-commit)
- Log redaction — mencegah secret muncul di log
- Keamanan endpoint lokal (9Router, Ollama)
- Prosedur rotasi API key
- Incident response saat secret bocor

## 3. Non-Scope

- Keamanan server production (ini adalah aplikasi local-first)
- Enkripsi database (tidak ada database dalam sistem ini)
- OAuth / SSO (tidak relevan untuk setup ini)

---

## 4. Klasifikasi Informasi Sensitif

| Kategori | Contoh | Level Sensitifitas |
|---|---|---|
| API Key | `NINE_ROUTER_API_KEY` | 🔴 TINGGI |
| URL Endpoint Internal | `NINE_ROUTER_BASE_URL`, `OLLAMA_BASE_URL` | 🟡 SEDANG |
| Konfigurasi model | `PLANNER_MODEL`, `WRITER_MODEL` | 🟢 RENDAH |
| Nilai threshold | `QUALITY_THRESHOLD` | 🟢 RENDAH |
| Path direktori | `OUTPUT_DIR` | 🟢 RENDAH |

---

## 5. Secret Lifecycle

```
GENERASI
Secret dibuat (dari dashboard 9Router atau konfigurasi Ollama)
      │
      ▼
DISTRIBUSI
Secret dimasukkan ke .env (TIDAK pernah ke source code)
      │
      ▼
PENGGUNAAN
Sistem membaca secret via Pydantic Settings (SecretStr)
Secret tidak pernah di-log atau di-print
      │
      ▼
ROTASI (berkala atau jika ada indikasi kebocoran)
Secret baru dimasukkan ke .env
Secret lama di-invalidate di dashboard provider
      │
      ▼
REVOKASI (jika terjadi insiden)
Secret di-invalidate segera
Lihat: Incident Response
```

---

## 6. File `.env` — Aturan Penggunaan

### 6.1 Apa itu `.env`

File `.env` adalah file teks plain yang menyimpan environment variables untuk development lokal. File ini **hanya ada di mesin lokal** dan tidak pernah di-commit ke Git.

### 6.2 Aturan Wajib

1. **`.env` TIDAK PERNAH di-commit ke Git.** Ini adalah aturan keras, tidak ada pengecualian.

2. **`.env.example` SELALU di-commit ke Git.** File ini berisi template tanpa nilai nyata.

3. **Secret tidak boleh ada dalam kode sumber apapun** — termasuk test files, fixtures, atau configuration files yang di-commit.

4. **Secret tidak boleh ada dalam komentar kode.**

5. **Secret tidak boleh di-print ke stdout/stderr** dalam kondisi apapun.

### 6.3 Cara Membuat `.env`

```bash
# Salin template
cp .env.example .env

# Edit dengan editor teks
nano .env
# atau
code .env

# Isi nilai yang diperlukan (ganti placeholder dengan nilai nyata)
```

### 6.4 Contoh `.env` yang SALAH

```dotenv
# SALAH: API key nyata di .env.example (yang di-commit)
NINE_ROUTER_API_KEY=nr-abc123-real-key-here-JANGAN-COMMIT-INI

# SALAH: URL production dengan kredensial
DATABASE_URL=postgresql://user:password@host/db
```

### 6.5 Contoh `.env.example` yang BENAR

```dotenv
# BENAR: Hanya placeholder
NINE_ROUTER_API_KEY=replace-with-your-9router-api-key

# BENAR: URL lokal tanpa kredensial
NINE_ROUTER_BASE_URL=http://127.0.0.1:20128/v1
```

---

## 7. Proteksi Git

### 7.1 `.gitignore` Wajib

File berikut HARUS ada dalam `.gitignore`:

```gitignore
# === SECRETS — TIDAK PERNAH DI-COMMIT ===
.env
.env.local
.env.*.local
.env.development
.env.production
*.key
*.pem
*.p12
*.pfx
secrets/
credentials/

# Jika ada tool secrets management
.secrets
.vault
```

### 7.2 Verifikasi `.gitignore` Bekerja

```bash
# Pastikan .env tidak ter-track
git status | grep ".env"
# Tidak boleh ada output

# Pastikan .env tidak ter-stage
git diff --cached --name-only | grep ".env"
# Tidak boleh ada output

# Test: tambah .env ke gitignore check
git check-ignore -v .env
# Harus menampilkan: .gitignore:X:.env
```

### 7.3 Pre-commit Hook (Opsional tapi Sangat Direkomendasikan)

Tambahkan hook untuk mencegah commit yang mengandung secret:

```bash
# Install pre-commit
pip install pre-commit

# Buat .pre-commit-config.yaml
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
      - id: detect-private-key
```

```bash
# Install hooks
pre-commit install

# Scan repository saat ini
pre-commit run --all-files
```

### 7.4 Jika Secret Sudah Terlanjur di-commit

Jika API key atau secret sudah masuk ke Git history:

**Langkah pertama (segera):**
1. **Revoke secret tersebut sekarang** — sebelum melakukan apapun yang lain. Asumsikan secret sudah bocor.

**Langkah kedua (cleanup Git history):**

```bash
# Hapus file dari seluruh history (gunakan git-filter-repo)
pip install git-filter-repo

# Hapus file yang mengandung secret dari history
git filter-repo --path .env --invert-paths

# Force push (koordinasi dengan tim terlebih dahulu)
git push origin --force --all
git push origin --force --tags
```

**Langkah ketiga:**
- Generate secret baru
- Update `.env` dengan secret baru
- Pastikan `.gitignore` sudah benar
- Lakukan audit: periksa apakah ada tempat lain secret tersebut muncul

---

## 8. Log Redaction

Sistem harus memastikan secret tidak pernah muncul dalam log.

### 8.1 Pydantic SecretStr

Semua API key menggunakan `SecretStr` dari Pydantic — ini mencegah nilai muncul saat objek di-print atau di-repr:

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings

class NineRouterConfig(BaseSettings):
    api_key: SecretStr  # Nilai TIDAK muncul di repr()

# Saat digunakan:
config = NineRouterConfig()
print(config.api_key)  # Output: **********
str(config.api_key)    # Output: **********
config.api_key.get_secret_value()  # Ini nilai nyata — hanya gunakan saat dibutuhkan
```

### 8.2 Aturan Logging

```python
# BENAR: Log tanpa secret
logger.info(f"Connecting to 9Router at {config.base_url}")
logger.info(f"API key configured: {'yes' if config.api_key else 'no'}")

# SALAH: Log dengan secret
logger.info(f"API key: {config.api_key.get_secret_value()}")  # JANGAN!
logger.debug(f"Request headers: {headers}")  # Headers mungkin mengandung Authorization!
```

### 8.3 Request/Response Logging

Saat melakukan AI call, **JANGAN log**:
- Header `Authorization`
- Full request body (mungkin mengandung context sensitif)
- API key dalam URL query parameter

Yang **BOLEH di-log**:
- URL endpoint (tanpa credentials)
- Model yang digunakan
- Token count
- Latency
- Status (success/failure)

```python
# Template log yang aman
logger.info(
    f"[AI call] provider={provider_id} model={model} "
    f"prompt_tokens={usage.prompt_tokens} "
    f"completion_tokens={usage.completion_tokens} "
    f"latency={latency_ms}ms"
)
```

### 8.4 Error Log Redaction

Pastikan error message tidak mengandung API key:

```python
# BENAR: Error tanpa secret
try:
    response = await client.generate(request)
except APIAuthenticationError as e:
    logger.error(f"Authentication failed for provider {provider_id}: {e.status_code}")
    # Tidak perlu log e.message karena mungkin mengandung key fragment

# SALAH
try:
    ...
except Exception as e:
    logger.error(f"Error: {e}")  # e.args mungkin mengandung headers atau key!
```

---

## 9. Keamanan Endpoint Lokal

### 9.1 9Router

9Router berjalan di lokal (`127.0.0.1`). Ini berarti:
- Hanya accessible dari mesin yang sama (lokal)
- Tidak accessible dari jaringan luar secara default

**Jangan** expose 9Router ke jaringan publik:
```bash
# JANGAN bind ke 0.0.0.0
# BENAR: bind ke 127.0.0.1 saja
```

### 9.2 Ollama

Ollama secara default mendengarkan di `127.0.0.1:11434`. Pastikan tidak di-bind ke `0.0.0.0`.

Cek konfigurasi Ollama:
```bash
# Cek di mana Ollama mendengarkan
ss -tlnp | grep 11434

# Harus menampilkan:
# 127.0.0.1:11434  (AMAN)
# Bukan:
# 0.0.0.0:11434    (TIDAK AMAN — accessible dari luar)
```

### 9.3 Keamanan Jaringan

Untuk keamanan tambahan, pastikan firewall memblokir port 9Router dan Ollama dari jaringan eksternal:

```bash
# Ubuntu/Debian dengan UFW
sudo ufw deny 20128  # 9Router
sudo ufw deny 11434  # Ollama
```

---

## 10. API Key Rotation

### 10.1 Kapan Merotasi

- **Rutin:** Setiap 90 hari (atau sesuai kebijakan organisasi)
- **Segera:** Jika ada indikasi kebocoran
- **Setelah offboarding:** Jika developer yang memiliki akses meninggalkan tim

### 10.2 Prosedur Rotasi

```
1. Generate key baru di dashboard provider (9Router)

2. Update .env dengan key baru:
   NINE_ROUTER_API_KEY=new-key-here

3. Verifikasi koneksi dengan key baru:
   kir doctor

4. Revoke key lama di dashboard provider

5. Konfirmasi:
   kir models  # Harus berjalan dengan key baru
```

### 10.3 Zero-Downtime Rotation

Untuk rotasi tanpa downtime (jika ada proses yang berjalan):

```
1. Generate key baru
2. Tambahkan key baru sementara menjalankan dengan key lama
3. Update .env dengan key baru
4. Restart/reload konfigurasi (untuk proses yang berjalan lama)
5. Verifikasi key baru berfungsi
6. Revoke key lama
```

---

## 11. Incident Response

### 11.1 Tanda-tanda Secret Bocor

- API key muncul dalam Git log (`git log --all -S "api-key-value"`)
- API key muncul dalam GitHub/GitLab remote repository
- Penggunaan API yang tidak dikenal (biaya tidak terduga)
- Alert dari provider (jika ada sistem monitoring)

### 11.2 Prosedur Respons Insiden

**LANGKAH 1 — Revoke Segera (dalam menit pertama)**

```bash
# Di dashboard provider (9Router):
# Navigasi ke API Keys → Revoke [compromised key]

# Di Ollama: tidak ada API key, skip
```

**LANGKAH 2 — Penilaian Dampak**

- Apakah key sudah bocor ke publik (internet)?
- Sudah berapa lama?
- Apakah ada penggunaan tidak sah yang terdeteksi?

**LANGKAH 3 — Cleanup**

```bash
# Jika key ada di Git history:
git log --all --full-history --source -- .env
git filter-repo --path .env --invert-paths
git push --force --all
```

**LANGKAH 4 — Generate dan Setup Key Baru**

```bash
# Generate key baru dari dashboard
# Update .env
# Verifikasi
kir doctor
```

**LANGKAH 5 — Post-Incident Review**

Catat:
- Bagaimana key bisa bocor?
- Apa yang harus diubah untuk mencegah terulang?
- Apakah ada kerusakan akibat kebocoran?

---

## 12. Checklist Keamanan

Lakukan checklist ini sebelum setiap commit pertama ke repository baru dan secara berkala:

### Setup Awal
- [ ] `.env` ada dalam `.gitignore`
- [ ] `.env.example` menggunakan placeholder, tidak ada nilai nyata
- [ ] `git status` tidak menampilkan `.env`
- [ ] Pre-commit hook ter-install (jika digunakan)

### Kode
- [ ] Tidak ada hardcoded API key atau secret dalam kode
- [ ] API key menggunakan `SecretStr` (bukan `str`)
- [ ] Log tidak mencatat header `Authorization`
- [ ] Log tidak mencatat nilai API key
- [ ] `config.api_key.get_secret_value()` hanya dipanggil di tempat yang benar-benar dibutuhkan (saat membuat HTTP request)

### Runtime
- [ ] 9Router hanya mendengarkan di `127.0.0.1`
- [ ] Ollama hanya mendengarkan di `127.0.0.1`
- [ ] `kir doctor` tidak menampilkan nilai API key (hanya status "configured" atau "not configured")

### Periodik
- [ ] API key dirotasi sesuai jadwal
- [ ] Akses di-review setelah perubahan tim

---

## 13. Acceptance Criteria

Keamanan dianggap memadai jika:

- [ ] `git grep -r "NINE_ROUTER_API_KEY=" -- "*.py"` mengembalikan 0 hasil
- [ ] `cat .gitignore | grep ".env"` menampilkan `.env`
- [ ] `python -c "from app.config.settings import AppSettings; s = AppSettings(); print(s.nine_router.api_key)"` menampilkan `**********` bukan nilai nyata
- [ ] Log dari `kir doctor` tidak mengandung nilai API key (hanya `configured: yes`)
- [ ] Pre-commit hook atau `detect-secrets` mendeteksi jika secret coba di-commit
