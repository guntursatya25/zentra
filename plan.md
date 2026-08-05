# Implementation Plan — Zentra: AI-Powered CRM & Knowledge Engine

## Ringkasan

Membangun Zentra — platform AI yang berfungsi sebagai pusat pengetahuan dan interaksi pelanggan. Menggabungkan knowledge ingestion, RAG engine, conversational AI, CRM inbox, dan developer API dalam satu sistem multi-tenant yang dapat di-embed ke berbagai platform.

**Pivot dari:** Sistem Tanya Jawab Kebijakan & SOP Internal (internal-only, single-tenant)
**Pivot ke:** AI-Powered CRM & Knowledge Engine (customer-facing, multi-tenant, embeddable, API-first)

---

## Status Pengerjaan

| Sprint | Status | Keterangan |
|---|---|---|
| **Sprint 0** — Foundation & Infrastructure | ✅ **Selesai** | Scaffolding, database, auth, JWT, Docker |
| **Sprint 1** — Document Management (→ Zentra Ingest) | ✅ **Selesai** | Upload, CRUD, versioning, multi-owner, permission enforcement |
| **Sprint 2** — Document Parsing & Chunking | ✅ **Selesai** | DOCX + PDF parsers, chunker, embedding service, ingestion pipeline |
| **Sprint 3** — Core RAG Engine (→ Zentra Core) | ✅ **Selesai** | Vector search (pgvector), RAG orchestration, citation engine, LLM API connected |
| **Sprint 4** — Chat UI + Citation Display (→ Zentra Chat) | ✅ **Selesai** | Chat UI, citation cards, multi-turn, feedback buttons |
| **Sprint 5** — Admin Panel (→ Zentra Inbox/Dashboard) | ✅ **Selesai** | Dashboard stats, analytics, audit logs, chunk editor |
| **Sprint 6** — Production Hardening | ✅ **Selesai** | Rate limiting, structured logging, error handler, validation |
| **Sprint 7** — Multi-tenant + API + Embeddable Widget | 🔄 *In Progress* | 7.2 Advanced Analytics ✅, 7.1 & 7.3 pending |
| **Sprint 8** — CRM Inbox + Human Handoff | 📋 *Backlog* |
| **Sprint 9** — Integrations + SaaS Readiness | 📋 *Backlog* |

---

## Teknologi yang Digunakan

| Komponen | Teknologi | Alasan |
|---|---|---|
| Backend | Python (FastAPI) | Async native, NLP ecosystem matang |
| Database | PostgreSQL + pgvector | Relasional + vector search, satu DB |
| ORM | SQLAlchemy + Alembic | Mature, migration support |
| Frontend | Next.js (React) | SSR, TypeScript, Tailwind |
| Parsing | python-docx + PyMuPDF + regex | Ekstraksi struktur dari DOCX/PDF |
| Vector Search | pgvector (via SQLAlchemy) | Query embedding + metadata filter |
| Auth | JWT + API Key | User auth + developer API key |
| Model AI | Multi-model (configurable) | OpenAI, Anthropic, local model support |
| File Storage | Local / S3-compatible | Dokumen asli untuk download |
| Chat Widget | React (standalone bundle) | Embeddable via `<script>` tag |

---

## Tahapan Implementasi

### Sprint 0-6 — Foundation (✅ Selesai)

Sprint 0-6 sudah selesai dan menjadi fondasi Zentra:
- ✅ **Zentra Ingest**: File upload (PDF/DOCX), parsing, chunking, embedding pipeline
- ✅ **Zentra Core**: RAG engine, vector search, citation generation, LLM integration
- ✅ **Zentra Chat**: Chat UI dengan citation display, multi-turn, feedback
- ✅ **Admin Dashboard**: Analytics, audit logs, document management
- ✅ **Production Hardening**: Rate limiting, logging, error handling

**Refactoring yang diperlukan:**
- Rename "internal SOP Q&A" terminology → "Zentra knowledge base & chat"
- Tambah workspace_id di semua model untuk multi-tenancy
- Tambah API key authentication untuk developer API
- Extract chat widget sebagai standalone package

---

### Sprint 7 — Multi-tenant + API + Embeddable Widget (In Progress)

**Goal:** Transform dari single-tenant internal tool → multi-tenant SaaS platform dengan developer API dan embeddable chat widget.

#### Tasks
1. **Multi-tenant architecture** ⏳
   - Tambah `workspace_id` di semua model (documents, chunks, conversations, messages)
   - Row-level isolation: setiap query filter by workspace_id
   - Workspace CRUD: create, update, delete workspace
   - Workspace member management: invite, remove, role assignment

2. **Developer API** ⏳
   - API key generation & management
   - `POST /api/v1/chat` — public chat endpoint (with API key auth)
   - `POST /api/v1/knowledge/search` — semantic search without generation
   - Rate limiting per API key (configurable quota)
   - API documentation (OpenAPI spec)

3. **Embeddable chat widget** ⏳
   - React component → build ke standalone JS bundle
   - Configurable: colors, position, logo, welcome message
   - Installation: `<script src="https://cdn.zentra.io/chat.js"></script>`
   - Communication dengan backend via API

4. **Advanced analytics** ✅
   - Weekly/monthly report generation ✅
   - Trend analysis: topik yang naik/turun popularitasnya ✅
   - User satisfaction trend (dari feedback thumbs up/down) ✅

**Deliverables:**
- Multi-tenant workspace isolation
- Developer API dengan API key authentication
- Embeddable chat widget (plug & play)
- API documentation

---

### Sprint 8 — CRM Inbox + Human Handoff (Backlog)

**Goal:** Dashboard CRM untuk mengelola percakapan, AI + human collaboration.

#### Tasks
1. **Unified inbox**
   - Dashboard: semua percakapan (AI + human) dalam satu view
   - Filter by status (AI resolved, human active, unanswered)
   - Search by keyword, user, tag, date

2. **AI + human handoff**
   - Agent bisa "take over" percakapan dari AI
   - Agent bisa "hand back" ke AI
   - Notification saat percakapan perlu human intervention

3. **Tagging & categorization**
   - Tag percakapan berdasarkan topik, prioritas, status
   - Auto-tagging berdasarkan AI classification

4. **Conversation analytics**
   - AI resolution rate (% dijawab tanpa human)
   - Response time (AI vs human)
   - Customer satisfaction (dari feedback)
   - Agent performance metrics

5. **Contact management (basic)**
   - User profile: nama, email, conversation history
   - Blocklist/spam detection

**Deliverables:**
- CRM inbox dashboard
- AI + human handoff mechanism
- Conversation analytics

---

### Sprint 9 — Integrations + SaaS Readiness (Backlog)

**Goal:** Integrasi dengan platform eksternal, billing system, enterprise features.

#### Tasks
1. **Messaging integrations**
   - Slack integration (bot di Slack workspace)
   - WhatsApp Business API integration
   - Telegram bot integration

2. **Webhook system**
   - Webhook untuk event: new message, handoff, conversation closed
   - Webhook management UI (create, test, delete)

3. **Billing & subscription**
   - Integration dengan payment gateway (Stripe)
   - Pricing plan: free tier, pro, enterprise
   - Usage tracking: conversations, API calls, storage

4. **Enterprise features**
   - SSO integration (Google, GitHub, SAML)
   - Custom domain untuk chat widget
   - On-premise deployment option (Docker Compose)

5. **Marketplace (optional)**
   - Template chatbot (customer support, FAQ, sales)
   - Third-party integrations directory

**Deliverables:**
- Messaging integrations (Slack, WhatsApp, Telegram)
- Webhook system
- Billing & subscription
- Enterprise features (SSO, custom domain)

---

## Arsitektur Multi-Tenant

```
┌─────────────────────────────────────────────────────────┐
│                    Zentra Platform                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Workspace A  │  │ Workspace B  │  │ Workspace C  │  │
│  │ (Company A)  │  │ (Company B)  │  │ (Company C)  │  │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  │
│  │ - Documents  │  │ - Documents  │  │ - Documents  │  │
│  │ - Chunks     │  │ - Chunks     │  │ - Chunks     │  │
│  │ - Conversations│ │ - Conversations│ │ - Conversations│
│  │ - Users      │  │ - Users      │  │ - Users      │  │
│  │ - API Keys   │  │ - API Keys   │  │ - API Keys   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  Isolation: workspace_id filter di setiap query          │
│  Migration: tenant-aware (RLS atau schema-per-tenant)    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Database strategy:**
- Option 1: Row-level security (RLS) — satu schema, filter by workspace_id
- Option 2: Schema-per-tenant — setiap workspace punya schema terpisah
- Recommendation: RLS untuk MVP, migrate ke schema-per-tenant jika perlu strict isolation

---

## Struktur Folder (Updated)

```
zentra/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + middleware
│   │   ├── config.py            # Settings via env vars
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── workspace.py     # Workspace, WorkspaceMember
│   │   │   ├── user.py          # User, Role
│   │   │   ├── document.py      # Document, DocumentChunk (with workspace_id)
│   │   │   ├── conversation.py  # Conversation, Message (with workspace_id)
│   │   │   ├── api_key.py       # APIKey model
│   │   │   └── audit.py         # AuditLog
│   │   ├── routers/             # API endpoints
│   │   │   ├── auth.py          # login, register
│   │   │   ├── workspaces.py    # workspace CRUD + members
│   │   │   ├── documents.py     # document management
│   │   │   ├── chat.py          # chat + conversations
│   │   │   ├── inbox.py         # CRM inbox (Sprint 8)
│   │   │   ├── api_keys.py      # API key management
│   │   │   ├── public_api.py    # developer API (v1)
│   │   │   └── admin.py         # analytics + audit
│   │   ├── services/
│   │   │   ├── ingestion.py     # parse → chunk → embed
│   │   │   ├── rag.py           # RAG orchestration
│   │   │   ├── vector_search.py # semantic search
│   │   │   └── ...
│   │   └── utils/
│   │       ├── pdf_parser.py
│   │       ├── docx_parser.py
│   │       └── chunker.py
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   │   ├── (auth)/          # login, register
│   │   │   ├── (dashboard)/     # workspace dashboard
│   │   │   │   ├── documents/
│   │   │   │   ├── chat/
│   │   │   │   ├── inbox/       # CRM inbox (Sprint 8)
│   │   │   │   ├── settings/
│   │   │   │   └── api-keys/
│   │   │   └── admin/           # super admin
│   │   └── ...
│   └── ...
├── chat-widget/                 # Standalone chat widget (React)
│   ├── src/
│   │   ├── components/
│   │   ├── App.tsx
│   │   └── index.tsx            # entry point
│   ├── package.json
│   └── vite.config.ts           # build ke standalone JS
├── docker-compose.yml
└── ...
```

---

## Database Schema (Multi-Tenant Update)

```sql
-- Workspaces (NEW)
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,  -- for URL: zentra.io/ws/{slug}
    plan VARCHAR(50) DEFAULT 'free',    -- 'free', 'pro', 'enterprise'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workspace members (NEW)
CREATE TABLE workspace_members (
    id SERIAL PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,  -- 'owner', 'admin', 'agent', 'viewer'
    UNIQUE(workspace_id, user_id)
);

-- API keys (NEW)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,  -- hashed API key
    permissions JSONB,               -- ['chat', 'search', 'embeddings']
    rate_limit INT DEFAULT 1000,     -- requests per hour
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP
);

-- Documents (UPDATED: add workspace_id)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,  -- NEW
    title VARCHAR(500) NOT NULL,
    -- ... other fields
);

-- Document chunks (UPDATED: add workspace_id)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,  -- NEW
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    -- ... other fields
);

-- Conversations (UPDATED: add workspace_id)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,  -- NEW
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    -- ... other fields
);

-- Messages (no workspace_id needed, join via conversation)
CREATE TABLE messages (
    -- ... existing schema
);

-- Index untuk performance
CREATE INDEX idx_documents_workspace ON documents(workspace_id);
CREATE INDEX idx_chunks_workspace ON document_chunks(workspace_id);
CREATE INDEX idx_conversations_workspace ON conversations(workspace_id);
```

---

## API Endpoints (Updated)

### Public API (Developer API — v1)

**Authentication:** API Key (header: `Authorization: Bearer zk_live_...`)

- `POST /api/v1/chat` — Send message, get AI response + citations
- `POST /api/v1/knowledge/search` — Semantic search (no generation)
- `POST /api/v1/embeddings` — Generate embedding for text
- `GET /api/v1/conversations` — List conversations (for CRM integration)
- `GET /api/v1/conversations/{id}` — Get conversation details

### Internal API (Dashboard)

**Authentication:** JWT (user session)

**Workspace**
- `POST /api/workspaces` — Create workspace
- `GET /api/workspaces` — List user workspaces
- `GET /api/workspaces/{id}` — Workspace details
- `PUT /api/workspaces/{id}` — Update workspace
- `DELETE /api/workspaces/{id}` — Delete workspace

**Workspace Members**
- `POST /api/workspaces/{id}/members` — Invite member
- `GET /api/workspaces/{id}/members` — List members
- `PUT /api/workspaces/{id}/members/{user_id}` — Update member role
- `DELETE /api/workspaces/{id}/members/{user_id}` — Remove member

**API Keys**
- `POST /api/workspaces/{id}/api-keys` — Generate API key
- `GET /api/workspaces/{id}/api-keys` — List API keys
- `DELETE /api/workspaces/{id}/api-keys/{key_id}` — Revoke API key

**Documents, Chat, Analytics** — same as existing, but scoped to workspace

---

## Chat Widget Specification

**Installation:**
```html
<script src="https://cdn.zentra.io/chat.js"></script>
<script>
  Zentra.init({
    workspaceId: 'ws_abc123',
    theme: {
      primaryColor: '#0066FF',
      position: 'bottom-right'
    },
    welcomeMessage: 'Hi! How can I help you today?'
  });
</script>
```

**Features:**
- Floating chat bubble
- Expandable chat window
- Multi-turn conversation
- Citation display
- Feedback (thumbs up/down)
- "Talk to human" button → create ticket / send email
- Mobile responsive

**Build:**
- React + TypeScript + Vite
- Output: single JS bundle (~200KB gzipped)
- Hosted on CDN: `cdn.zentra.io/chat.js`

---

## Current Status

**MVP (Sprint 0-6) complete. Sprint 7 in progress (1/4 done).**

### Completed:
- ✅ Full RAG pipeline: document upload → parse → chunk → embed → vector search → LLM answer with citations
- ✅ LLM API connected (mimo/mimo-v2.5-pro) with SSE response handling
- ✅ 38 audit issues fixed
- ✅ Markdown rendering in chat UI
- ✅ AI-assisted parsing option
- ✅ Advanced analytics: weekly reports, trends, satisfaction

### Sprint 7 Progress:
- ✅ 7.2 Advanced analytics
- ⏳ 7.1 Multi-tenant architecture — not started
- ⏳ 7.3 Developer API — not started
- ⏳ 7.4 Embeddable chat widget — not started

### Remaining:
- 📋 Sprint 8: CRM Inbox + Human Handoff
- 📋 Sprint 9: Integrations + SaaS Readiness

---

## Catatan

- **Priority:** Sprint 7 (multi-tenant + API + widget) adalah prioritas untuk transform ke SaaS platform.
- **Estimasi:** Sprint 7 ~4-6 minggu, Sprint 8 ~3-4 minggu, Sprint 9 ~4-6 minggu.
- **Dependencies:** Multi-tenant migration perlu careful planning (data migration strategy).
- **Validation:** Beta tester needed untuk Sprint 7 deliverables (API + widget).
