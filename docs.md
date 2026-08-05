# Zentra — Dokumentasi

Sistem Tanya Jawab Kebijakan & SOP Berbasis AI Internal.

---

## Daftar Isi

1. [Persyaratan Sistem](#1-persyaratan-sistem)
2. [Cara Menjalankan (Docker)](#2-cara-menjalankan-docker)
3. [Cara Menjalankan (Manual)](#3-cara-menjalankan-manual)
4. [Seed Data & Akun Default](#4-seed-data--akun-default)
5. [Struktur Proyek](#5-struktur-proyek)
6. [API Endpoints](#6-api-endpoints)
7. [Role & Permission](#7-role--permission)
8. [Audit Logging](#8-audit-logging)
9. [FAQ & Troubleshooting](#9-faq--troubleshooting)

---

## 1. Persyaratan Sistem

- **Docker Desktop** (Windows) **atau** Docker Engine + docker-compose (Linux)
- Python 3.12+, PostgreSQL 16+ dengan pgvector, Node.js 20+ (untuk manual)

Cek versi Docker Compose:

```bash
docker-compose --version
# atau
docker compose version
```

---

## 2. Cara Menjalankan (Docker)

### 2.1 Build & Jalankan Semua Service

```bash
# Masuk ke direktori project
cd D:\Code\project\Zentra

# Build images (lakukan sekali, atau setelah ada perubahan kode)
docker-compose build

# Jalankan semua container di background
docker-compose up -d
```

Perintah `docker-compose up -d` otomatis menjalankan 3 container:

| Service | Port | Deskripsi |
|---|---|---|
| `db` | 5432 | PostgreSQL 16 + pgvector |
| `backend` | 8000 | FastAPI backend (Python) |
| `frontend` | 3000 | Next.js frontend (React)  |

> **Catatan untuk Windows / MINGW64:** Gunakan `docker-compose` (dengan hyphen). Jika versi Docker Compose v2, `docker compose` (space) juga bisa.

### 2.2 Cek Status Container

```bash
docker-compose ps
# Semua service harus status "Up"
```

### 2.3 Cek Log Real-time

```bash
# Semua log
docker-compose logs -f

# Log service tertentu
docker-compose logs -f backend
docker-compose logs -f db
docker-compose logs -f frontend
```

Tunggu beberapa detik sampai `db` siap (healthcheck), lalu `backend` akan connect.

### 2.4 Akses Aplikasi

| Halaman | URL |
|---|---|
| Frontend (Chat) | http://localhost:3000 |
| Admin Panel | http://localhost:3000/admin |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/health |

### 2.5 Menghentikan Service

```bash
# Stop container (data tetap ada)
docker-compose down

# Stop + hapus volume database (data hilang)
docker-compose down -v
```

### 2.6 Reset Total (Mulai Dari Awal)

Gunakan jika ada perubahan migration, seed, atau database corrupt:

```bash
# Hentikan + hapus volume database + rebuild ulang
docker-compose down -v
docker-compose build --no-cache backend  # force rebuild backend
docker-compose up -d
```

> **Perhatian:** `down -v` akan menghapus semua data di database. Seed akan dijalankan ulang otomatis.

---

## 3. Cara Menjalankan (Manual)

### 3.1 Database

Pastikan PostgreSQL 16 + pgvector sudah terinstall dan running:

```bash
# Akses psql
psql -U postgres
```

```sql
CREATE DATABASE sasis;
CREATE USER sasis WITH PASSWORD 'sasis';
GRANT ALL PRIVILEGES ON DATABASE sasis TO sasis;
\c sasis
CREATE EXTENSION vector;
\q
```

Jalankan seed:

```bash
psql -U sasis -d sasis -f backend/seed.sql
```

### 3.2 Backend

```bash
cd backend

# Buat virtual env
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Jalankan migration (buat tabel)
alembic upgrade head

# Jalankan server
uvicorn app.main:app --reload --port 8000
```

### 3.3 Frontend

```bash
cd frontend

npm install
npm run dev
# → http://localhost:3000
```

### 3.4 Environment Variables

Buat file `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://sasis:sasis@localhost:5432/sasis
JWT_SECRET_KEY=change-me-in-production

# LLM API Configuration
LLM_API_URL=http://localhost:20128/v1
LLM_API_KEY=your-api-key-here
LLM_MODEL=mimo/mimo-v2.5-pro
EMBEDDING_DIMENSION=1536

# File upload
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=50

DEBUG=false
```

Buat file `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3.5 Menguji API

```bash
# Health check
curl http://localhost:8000/api/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 4. Seed Data & Akun Default

Seed dijalankan **otomatis** saat pertama kali container `db` start (via `backend/seed.sql` yang di-mount ke `/docker-entrypoint-initdb.d/`).

### Roles

| Role | Deskripsi |
|---|---|
| `employee` | Karyawan — hanya tanya jawab |
| `data_manager` | Pengelola Master Data — kelola dokumen di kategori tertentu |
| `super_admin` | Admin platform — full akses |

### Akun Default

| Username | Password | Role | Departemen | Catatan |
|---|---|---|---|---|
| `admin` | `admin123` | super_admin | IT | Full akses |
| `manager_sdm` | `manager123` | data_manager | SDM | Ter-assign ke kategori **SDM** |
| `employee1` | `employee123` | employee | Finance | Hanya tanya jawab |

> **Data Manager**: `manager_sdm` sudah terhubung ke kategori **SDM** via tabel `category_managers`. Jadi dia bisa upload/edit/hapus dokumen di kategori SDM, tapi tidak bisa menyentuh kategori lain.

### Kategori Default

| Kategori | Deskripsi |
|---|---|
| SDM | Kebijakan dan SOP Sumber Daya Manusia |
| Keuangan | Kebijakan dan SOP Keuangan & Akuntansi |
| IT Security | Kebijakan keamanan informasi dan IT |
| Operasional | SOP Operasional harian |
| Legal & Compliance | Dokumen hukum dan kepatuhan |

---

## 5. Struktur Proyek

```
sasis/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Entry point FastAPI
│   │   ├── config.py               # Settings dari env vars
│   │   ├── database.py             # Async SQLAlchemy engine
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── user.py             # User, Role, CategoryManager
│   │   │   ├── document.py         # DocumentCategory, Document, DocumentChunk
│   │   │   ├── conversation.py     # Conversation, Message
│   │   │   └── audit.py            # AuditLog
│   │   ├── schemas/                # Pydantic request/response
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   └── chat.py
│   │   ├── routers/                # API endpoints
│   │   │   ├── auth.py             # login, me
│   │   │   ├── users.py            # admin user management
│   │   │   ├── categories.py       # CRUD + manager assignment
│   │   │   ├── documents.py        # CRUD + versions + chunks + reparse
│   │   │   ├── chat.py             # RAG chat + conversations + feedback
│   │   │   ├── admin.py            # analytics + audit logs
│   │   │   └── health.py           # health + DB check
│   │   ├── services/               # Business logic
│   │   │   ├── auth.py             # JWT, password hash
│   │   │   ├── document.py         # Upload, access check
│   │   │   ├── ingestion.py        # parse → chunk → embed pipeline
│   │   │   ├── embedding.py        # embedding (stub → real API)
│   │   │   ├── vector_search.py    # pgvector cosine search + ILIKE fallback
│   │   │   ├── rag.py              # prompt orchestration + citation extraction
│   │   │   ├── audit.py            # audit log service
│   │   │   └── rate_limit.py       # in-memory rate limiter
│   │   ├── middleware/
│   │   │   ├── auth.py             # get_current_user, require_role
│   │   │   ├── logging.py          # RequestLoggingMiddleware
│   │   │   └── error_handler.py    # global exception handler
│   │   └── utils/
│   │       ├── pdf_parser.py       # PyMuPDF + regex Bab/Pasal/Ayat
│   │       ├── docx_parser.py      # python-docx + heading detection
│   │       ├── chunker.py          # overlapping chunk strategy
│   │       └── validation.py       # input sanitization
│   ├── alembic/                    # Database migrations
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── seed.sql                    # Seed data (auto-run di Docker)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # redirect → /chat atau /login
│   │   │   ├── layout.tsx          # Root layout
│   │   │   ├── globals.css         # Tailwind base
│   │   │   ├── login/page.tsx      # Halaman login
│   │   │   ├── chat/page.tsx       # Chat + citations + feedback + sources sidebar
│   │   │   └── admin/
│   │   │       ├── layout.tsx      # Admin sidebar
│   │   │       ├── page.tsx        # Dashboard (live stats)
│   │   │       ├── documents/page.tsx         # Table + upload modal
│   │   │       ├── documents/[id]/page.tsx    # Chunk editor
│   │   │       ├── categories/page.tsx
│   │   │       ├── users/page.tsx
│   │   │       └── analytics/page.tsx         # FAQ + unanswered + per-day + audit
│   │   ├── lib/
│   │   │   ├── api.ts              # API client
│   │   │   └── auth.tsx            # Auth context/provider
│   │   └── types/index.ts          # TypeScript interfaces
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── docs.md                         # ← File ini
└── plan.md                         # Implementation plan
```

---

## 6. API Endpoints

### Auth

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| POST | `/api/auth/login` | No | Login, return JWT + user ✅ |
| GET | `/api/auth/me` | Yes | Current user info ✅ |

### Categories

| Method | Endpoint | Role | Deskripsi |
|---|---|---|---|
| GET | `/api/categories` | Any | List kategori ✅ |
| POST | `/api/categories` | super_admin | Buat kategori baru ✅ |
| PUT | `/api/categories/{id}` | super_admin | Update kategori ✅ |
| DELETE | `/api/categories/{id}` | super_admin | Hapus kategori ✅ |
| POST | `/api/categories/{id}/managers?user_id=` | super_admin | Assign manager ✅ |
| DELETE | `/api/categories/{id}/managers/{user_id}` | super_admin | Remove manager ✅ |

### Documents

| Method | Endpoint | Role | Deskripsi |
|---|---|---|---|
| GET | `/api/documents` | Any | List (filtered by role) ✅ |
| GET | `/api/documents/{id}` | Any | Detail dokumen ✅ |
| POST | `/api/documents` | data_manager/super_admin | Upload PDF/DOCX ✅ |
| PUT | `/api/documents/{id}` | owner/super_admin | Update metadata/status ✅ |
| DELETE | `/api/documents/{id}` | owner/super_admin | Hapus dokumen ✅ |
| GET | `/api/documents/{id}/file` | Any | Download file asli ✅ |
| GET | `/api/documents/{id}/versions` | Any | Riwayat versi ✅ |
| POST | `/api/documents/{id}/versions` | owner/super_admin | Upload versi baru ✅ |

### Document Chunks (Parsing)

| Method | Endpoint | Role | Deskripsi |
|---|---|---|---|
| GET | `/api/documents/{id}/chunks` | Any | List chunk (auto-process jika kosong) ✅ |
| PUT | `/api/documents/chunks/{chunk_id}` | owner/super_admin | Edit metadata Bab/Pasal/Ayat ✅ |
| POST | `/api/documents/{id}/reparse?use_ai=false` | owner/super_admin | Re-parse dari awal (opsional AI-assisted) ✅ |

### Chat (RAG)

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| POST | `/api/chat` | Yes | Kirim pesan → vector search → RAG → jawaban + citations ✅ |
| GET | `/api/conversations` | Yes | List percakapan user ✅ |
| GET | `/api/conversations/{id}` | Yes | Detail percakapan + pesan ✅ |
| DELETE | `/api/conversations/{id}` | Yes | Hapus percakapan ✅ |
| POST | `/api/messages/{id}/feedback` | Yes | Feedback (up/down) ✅ |

### Admin

| Method | Endpoint | Role | Deskripsi |
|---|---|---|---|
| GET | `/api/admin/users` | super_admin | List semua user ✅ |
| POST | `/api/admin/users` | super_admin | Buat user baru ✅ |
| PUT | `/api/admin/users/{id}` | super_admin | Update user ✅ |
| GET | `/api/admin/analytics/overview` | admin/data_manager | 6 metrik dashboard ✅ |
| GET | `/api/admin/analytics/faq` | admin/data_manager | Top FAQ ✅ |
| GET | `/api/admin/analytics/unanswered` | admin/data_manager | Gap analysis ✅ |
| GET | `/api/admin/analytics/per-day` | admin/data_manager | Pertanyaan per hari ✅ |
| GET | `/api/admin/analytics/weekly-report` | admin/data_manager | Laporan mingguan ✅ |
| GET | `/api/admin/analytics/trends` | admin/data_manager | Trend analysis (rising/falling) ✅ |
| GET | `/api/admin/analytics/satisfaction` | admin/data_manager | User satisfaction trend ✅ |
| GET | `/api/admin/audit-logs` | super_admin | Log audit (filterable) ✅ |

### Health

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| GET | `/api/health` | No | Status + DB connectivity ✅ |

---

## 7. Role & Permission

| Fitur | employee | data_manager | super_admin |
|---|---|---|---|
| Chat / Tanya jawab | ✅ | ✅ | ✅ |
| Upload dokumen | ❌ | ✅ (kategorinya sendiri) | ✅ (semua kategori) |
| Edit dokumen | ❌ | ✅ (kategorinya sendiri) | ✅ (semua kategori) |
| Hapus dokumen | ❌ | ✅ (kategorinya sendiri) | ✅ (semua kategori) |
| Edit chunk metadata | ❌ | ✅ (kategorinya sendiri) | ✅ (semua kategori) |
| Re-parse dokumen | ❌ | ✅ (kategorinya sendiri) | ✅ (semua kategori) |
| Kelola kategori | ❌ | ❌ | ✅ |
| Kelola user | ❌ | ❌ | ✅ |
| Assign manager | ❌ | ❌ | ✅ |
| Lihat analytics | ❌ | ✅ | ✅ |
| Audit logs | ❌ | ❌ | ✅ |

---

## 8. Audit Logging

### 8.1 Apakah itu?

Setiap write operation di sistem tercatat di tabel `audit_logs` untuk keperluan compliance dan investigasi.

### 8.2 Yang Tercatat

| Aksi | Dicatat |
|---|---|
| Login user | ✅ username, timestamp, IP |
| Upload dokumen | ✅ user, title, version |
| Update dokumen | ✅ user, status baru |
| Delete dokumen | ✅ user, title |
| Buat/edit/hapus kategori | ✅ user, nama kategori |
| Assign/remove manager | ✅ user, category_id, manager_user_id |
| Update user (role/department) | ✅ user, detail perubahan |
| Kirim chat | ✅ question (100 char pertama), jumlah citations |
| Feedback jawaban | ✅ message_id, feedback (up/down) |
| Hapus percakapan | ✅ user, conversation_id |

### 8.3 Cara Lihat Audit Log

**Via Admin Panel:**
1. Login sebagai `admin` / `admin123`
2. Buka **Analytics** tab → pilih tab **Audit Logs**

**Via API:**
```bash
# Login dulu dapat token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Ambil audit logs
curl http://localhost:8000/api/admin/audit-logs \
  -H "Authorization: Bearer $TOKEN"

# Dengan filter
curl "http://localhost:8000/api/admin/audit-logs?action=upload&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 8.4 Filter yang Tersedia

| Parameter | Contoh | Deskripsi |
|---|---|---|
| `limit` | `50` | Jumlah log per halaman (max 200) |
| `offset` | `0` | Pagination |
| `action` | `upload` | Filter by tipe aksi |
| `user_id` | `uuid...` | Filter by user ID |
| `entity_type` | `document` | Filter by tipe entitas |
| `date_from` | `2026-06-01` | Filter tanggal mulai |
| `date_to` | `2026-06-30` | Filter tanggal akhir |

---

## 9. FAQ & Troubleshooting

### 9.0 Ganti Model LLM

Edit `backend/.env`:

```env
LLM_MODEL=mimo/mimo-v2.5-pro
# atau: deepseekv4, sonnet, 2
```

Restart tanpa rebuild:

```bash
docker-compose restart backend
```

### 9.1 Docker: `docker-compose up -d` tidak ditemukan

```bash
# Coba versi v2 (spasi, bukan hyphen)
docker compose up -d

# Atau cek apakah sudah terinstall
docker-compose --version
docker compose version
```

Jika belum ada, install Docker Desktop dari https://www.docker.com/products/docker-desktop/

### 9.2 Docker: `db` container tidak bisa start

```bash
# Cek apakah port 5432 dipakai service PostgreSQL lokal
netstat -ano | findstr :5432

# Jika iya, stop service PostgreSQL lokal:
# Windows: Services → PostgreSQL → Stop
# Atau ganti port di docker-compose.yml (5432:5432 → 5433:5432)
```

### 9.3 Backend tidak bisa connect ke database

Tunggu beberapa saat — `db` perlu waktu startup + healthcheck. Cek:

```bash
docker-compose logs db      # Apakah PostgreSQL sudah siap?
docker-compose logs backend # Apakah ada connection error?
```

### 9.4 Reset database (volume dihapus)

```bash
docker-compose down -v
docker-compose up -d
```

Ini menghapus semua data dan seed dijalankan ulang.

### 9.5 Login gagal / user not found

Seed hanya berjalan saat **pertama kali** volume database dibuat. Jika sudah pernah running sebelumnya:

```bash
# Reset volume + rebuild
docker-compose down -v
docker-compose build
docker-compose up -d
```

### 9.6 `manager_sdm` tidak bisa upload dokumen

Pastikan manager sudah ter-assign ke kategori:

```bash
# Login sebagai admin
curl -X POST http://localhost:8000/api/auth/login ... (dapat token)

# Cek category managers
curl http://localhost:8000/api/categories/1/managers \
  -H "Authorization: Bearer $TOKEN"
```

### 9.7 RAG selalu jawab "Tidak ditemukan referensi"

Ini normal jika belum ada dokumen aktif. Upload & parse dokumen dulu:

1. Login sebagai `admin` atau `manager_sdm`
2. Buka Admin → Documents → Upload file PDF/DOCX
3. Set status dokumen ke **active**
4. Coba chat lagi

### 9.8 Swagger / API docs tidak muncul

Buka http://localhost:8000/docs — FastAPI auto-generate dari kode.

---

## Catatan Pengembangan

- **MVP complete** (Sprint 0-6) — semua fitur dasar sudah terimplementasi
- **Sprint saat ini:** Sprint 7 in progress (7.2 Advanced Analytics ✅, 7.1 & 7.3 pending)
- **LLM API** sudah terhubung ke `mimo/mimo-v2.5-pro` — konfigurasi di `backend/.env`
- **AI-Assisted Parsing** tersedia — centang "AI Parsing" saat reparse dokumen
- **Advanced Analytics** — weekly reports, trend analysis, satisfaction tracking
- **Audit logging** aktif di semua write operations
- **Rate limiter:** 100 request per 60 detik per IP
- **38 audit issues** sudah difix (7 critical, 14 backend, 7 frontend, 8 minor)
- Semua endpoint otomatis terdokumentasi di Swagger: http://localhost:8000/docs
- **Ganti model LLM:** edit `LLM_MODEL` di `backend/.env`, lalu `docker-compose restart backend`
