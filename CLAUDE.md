# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zentra is an AI-powered RAG (Retrieval-Augmented Generation) system for document Q&A. Users upload documents (PDF/DOCX), which are parsed, chunked, and embedded into a vector database. The system answers questions using semantic search + LLM with citations.

## Common Commands

### Docker (Recommended)
```bash
# Start all services (db, backend, frontend)
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### Backend (FastAPI)
```bash
cd backend

# Run migrations
alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Run dev server
uvicorn app.main:app --reload --port 8000

# Run tests (not yet implemented)
# pytest
```

### Frontend (Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

## Architecture

### Backend Structure
- **Entry point**: `backend/app/main.py` - FastAPI app with middleware stack
- **Config**: `backend/app/config.py` - Pydantic settings from env vars
- **Database**: `backend/app/database.py` - Async SQLAlchemy with pgvector
- **Models**: `backend/app/models/` - SQLAlchemy ORM models
- **Routers**: `backend/app/routers/` - API endpoints (auth, documents, chat, admin, etc.)
- **Services**: `backend/app/services/` - Business logic (RAG, embedding, vector search, ingestion)
- **Utils**: `backend/app/utils/` - Parsers (PDF/DOCX), chunker, validation

### Frontend Structure
- **App Router**: `frontend/src/app/` - Next.js 14 pages
  - `/chat` - Main chat interface with citations
  - `/admin` - Admin panel (documents, analytics, users, categories)
  - `/login` - Authentication
- **Components**: `frontend/src/components/` - Reusable UI components
- **Lib**: `frontend/src/lib/` - API client, auth context

### Data Flow
1. **Document Ingestion**: Upload → Parse (PDF/DOCX) → Chunk → Embed → Store in pgvector
2. **Query Flow**: User question → Embed query → Vector search → Retrieve chunks → LLM with context → Answer + citations
3. **Auth Flow**: JWT-based with 3 roles (employee, data_manager, super_admin)

### Key Services
- `services/rag.py` - RAG orchestration, prompt construction, citation extraction
- `services/vector_search.py` - pgvector cosine similarity + ILIKE fallback
- `services/embedding.py` - LLM API integration for embeddings
- `services/ingestion.py` - Document parsing and chunking pipeline
- `utils/pdf_parser.py`, `utils/docx_parser.py` - Structure extraction (Bab/Pasal/Ayat)

## Environment Variables

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql+asyncpg://zentra:zentra@db:5432/zentra
JWT_SECRET_KEY=change-me-in-production
LLM_API_URL=http://localhost:20128/v1
LLM_API_KEY=your-api-key
LLM_MODEL=mimo/mimo-v2.5-pro
EMBEDDING_DIMENSION=1536
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=50
```

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database

- **PostgreSQL 16** with **pgvector** extension
- **Async SQLAlchemy** with Alembic migrations
- Key tables: `users`, `documents`, `document_chunks` (with embedding vector), `conversations`, `messages`, `audit_logs`
- Vector dimension: 1536 (configurable via `EMBEDDING_DIMENSION`)

## Default Accounts (from seed.sql)
- `admin` / `admin123` - super_admin (full access)
- `manager_sdm` / `manager123` - data_manager (SDM category only)
- `employee1` / `employee123` - employee (chat only)

## API Documentation
- Swagger UI: http://localhost:8000/docs
- All endpoints documented in `docs.md`

## Important Notes

- **Rate limiting**: 100 requests per 60 seconds per IP (configurable in `services/rate_limit.py`)
- **Audit logging**: All write operations logged to `audit_logs` table
- **Multi-tenancy**: Currently single-tenant; Sprint 7 will add workspace isolation
- **LLM integration**: Uses internal LLM API (mimo/mimo-v2.5-pro) for embeddings and generation
- **File storage**: Documents stored in `uploads/` directory (configurable)
- **CORS**: Configured for localhost:3000 by default (adjust `CORS_ORIGINS` in production)
