# PRD (Product Requirements Document)
# Zentra — AI-Powered CRM & Knowledge Engine

*Nama produk: **Zentra***
*Tagline: "Your AI Knowledge & CRM Hub"*

| Informasi Dokumen | |
|---|---|
| Versi | 0.2 (Draft) |
| Tanggal | 5 Agustus 2026 |
| Status | Draft — untuk direview stakeholder |
| Pemilik Produk | *(diisi)* |
| Tim Terkait | IT/Engineering, Product, Sales/Marketing, Customer Support |

---

## 1. Ringkasan Eksekutif

Zentra adalah platform AI yang berfungsi sebagai pusat (hub) untuk seluruh pengetahuan dan interaksi pelanggan dalam bisnis. Produk ini menggabungkan kemampuan knowledge ingestion, context understanding, dan conversational AI dalam satu sistem yang dapat di-embed ke berbagai platform.

Zentra mengubah dokumen menjadi sumber jawaban otomatis, menyederhanakan interaksi pelanggan, mengurangi pekerjaan manual customer support, dan meningkatkan kecepatan serta konsistensi respons.

Zentra bertindak sebagai **"otak" yang:**
- Mengumpulkan data dari berbagai sumber (file, web, API, integrasi)
- Memahami konteks secara otomatis
- Memberikan respons cerdas melalui chatbot yang dapat di-embed di website, aplikasi, atau melalui API

---

## 2. Latar Belakang & Masalah

- Informasi bisnis tersebar di banyak sumber: dokumen internal, website, email, chat — sulit ditemukan dan dikelola secara terpusat.
- Customer support menerima pertanyaan repetitif yang sebenarnya sudah terjawab di dokumentasi/FAQ.
- Respons tidak konsisten antar agen, tergantung pengetahuan masing-masing.
- Tidak ada sistem yang menggabungkan knowledge base + conversation tracking + AI automation dalam satu platform.
- Bisnis membutuhkan chatbot AI yang grounded pada dokumen resmi, bukan jawaban yang dikarang model.
- Developer membutuhkan API yang mudah diintegrasikan untuk membangun conversational AI di produk mereka.

---

## 3. Tujuan

### 3.1 Tujuan Bisnis
- Mengurangi beban customer support dengan otomatisasi FAQ dan knowledge-aware chatbot.
- Meningkatkan kecepatan dan konsistensi respons pelanggan.
- Menyediakan platform yang dapat dijual sebagai SaaS (multi-tenant) atau di-deploy on-premise untuk enterprise.
- Membuka revenue stream baru: subscription per workspace/agent/knowledge base.

### 3.2 Tujuan Produk (MVP)
1. **Knowledge Ingestion**: Import data dari berbagai sumber (file PDF/DOCX/TXT, website, API) dan jadikan basis pengetahuan AI.
2. **AI-Powered Chat**: Chatbot yang menjawab berdasarkan knowledge base, dengan sitasi sumber yang jelas.
3. **Embeddable Widget**: Chatbot dapat di-embed di website/aplikasi melalui script atau SDK.
4. **CRM Inbox**: Dashboard untuk mengelola percakapan (AI + human handoff), tagging, dan analytics.
5. **Developer API**: Endpoint untuk chat, knowledge query, embedding, dan webhook automation.
6. **Multi-tenant**: Mendukung multiple workspace/organization dengan data terisolasi.

### 3.3 Non-Tujuan (di luar lingkup saat ini)
- Bukan platform email marketing atau CRM sales pipeline (Salesforce/HubSpot competitor).
- Bukan tool untuk membangun chatbot tanpa knowledge base (pure chitchat bot).
- Bukan sistem workflow approval atau document management system (DMS).

---

## 4. Target Pengguna

| Persona | Kebutuhan Utama |
|---|---|
| **Startup & SaaS Companies** | Embed AI chatbot di produk mereka untuk customer support automation |
| **Customer Support Teams** | Reduce repetitive questions, AI-assisted responses, unified inbox |
| **E-commerce Businesses** | FAQ automation, product documentation AI, order status inquiry |
| **Digital Agencies** | White-label chatbot untuk klien mereka |
| **Internal Company Knowledge Systems** | Employee self-service, SOP/kebijakan Q&A (use case yang sudah ada) |

---

## 5. Lingkup

### 5.1 Dalam Lingkup — MVP
- **Zentra Core**: RAG engine, embedding, semantic search, context understanding.
- **Zentra Ingest**: Upload file (PDF/DOCX/TXT), web scraping, API ingestion, chunking + indexing.
- **Zentra Chat**: Embeddable chat widget (website), multi-turn conversation, citation display.
- **Zentra Inbox**: Unified conversation view, AI + human handoff, tagging, basic analytics.
- **Zentra API**: REST API untuk chat, knowledge query, embedding, webhook.
- **Multi-tenant architecture**: Workspace isolation, role-based access (Owner, Admin, Agent, Viewer).

### 5.2 Luar Lingkup — Backlog Fase Berikutnya
- Integrasi dengan platform messaging (WhatsApp, Telegram, Slack, Messenger).
- Voice chatbot (voice-to-text + text-to-speech).
- Multi-language auto-detection & response.
- Advanced CRM features: contact management, ticketing, SLA tracking.
- Marketplace untuk template chatbot & integrasi third-party.
- Mobile app (iOS/Android) untuk inbox management.

---

## 6. User Stories Utama

| ID | Sebagai | Saya ingin | Sehingga |
|---|---|---|---|
| US-01 | Product Owner | Mengimpor dokumentasi produk ke Zentra | Chatbot bisa menjawab pertanyaan customer secara otomatis |
| US-02 | Customer Support Agent | Melihat percakapan AI + mengambil alih jika perlu | Customer mendapat jawaban cepat, tapi tetap bisa bicara dengan manusia |
| US-03 | Developer | Mengintegrasikan Zentra chat widget di website saya | Customer bisa chat langsung di produk saya tanpa build chat system dari nol |
| US-04 | Business Owner | Melihat analytics: berapa pertanyaan yang dijawab AI vs human | Saya tahu ROI dari AI automation dan area yang perlu diperbaiki |
| US-05 | Admin | Mengelola knowledge base (tambah/edit/hapus dokumen) | Informasi yang dijawab AI selalu up-to-date |
| US-06 | End-user (customer) | Bertanya tentang produk/layanan dan mendapat jawaban instan | Tidak perlu menunggu agen atau cari-cari di FAQ |
| US-07 | Agency | Membuat workspace terpisah untuk tiap klien | Data dan knowledge base terisolasi per klien |

---

## 7. Kebutuhan Fungsional (Functional Requirements)

### 7.1 Zentra Ingest (Knowledge Ingestion)
| ID | Fitur | Deskripsi | Prioritas |
|---|---|---|---|
| FR-1.1 | File upload | Admin dapat upload PDF, DOCX, TXT sebagai knowledge base | Must |
| FR-1.2 | Web scraping | Import konten dari URL website (crawl + extract text) | Should |
| FR-1.3 | API ingestion | Endpoint untuk push data dari sistem eksternal (CRM, CMS, dll) | Should |
| FR-1.4 | Auto-chunking | Pecah dokumen jadi chunk kecil untuk embedding | Must |
| FR-1.5 | Metadata extraction | Ekstrak struktur dokumen (judul, bab, section) untuk sitasi | Must |
| FR-1.6 | Re-indexing | Jika dokumen diupdate, otomatis re-chunk + re-embed | Must |

### 7.2 Zentra Core (RAG Engine)
| ID | Fitur | Deskripsi | Prioritas |
|---|---|---|---|
| FR-2.1 | Semantic search | Cari chunk relevan berdasarkan similarity (cosine distance) | Must |
| FR-2.2 | RAG orchestration | Gabungkan query + retrieved context → prompt ke LLM | Must |
| FR-2.3 | Citation generation | Setiap jawaban menyertai sumber (nama dokumen, section, excerpt) | Must |
| FR-2.4 | "Not found" handling | Jika tidak ada konteks relevan, jawab "tidak ditemukan" (anti-hallucination) | Must |
| FR-2.5 | Multi-model support | Konfigurasi LLM backend (OpenAI, Anthropic, local model, dll) | Should |
| FR-2.6 | Confidence score | Tampilkan skor keyakinan jawaban (high/medium/low) | Could |

### 7.3 Zentra Chat (Embeddable Chatbot)
| ID | Fitur | Deskripsi | Prioritas |
|---|---|---|---|
| FR-3.1 | Chat widget | JavaScript snippet untuk embed chat di website (`<script src="zentra.js">`) | Must |
| FR-3.2 | Customizable UI | Atur warna, posisi, logo, welcome message | Should |
| FR-3.3 | Multi-turn conversation | Follow-up question dengan context dari percakapan sebelumnya | Must |
| FR-3.4 | Citation display | Tampilkan sumber di bawah setiap jawaban AI | Must |
| FR-3.5 | Feedback mechanism | Thumbs up/down untuk setiap jawaban | Should |
| FR-3.6 | Offline form | Jika AI tidak bisa jawab, tawarkan form untuk hubungi human | Should |

### 7.4 Zentra Inbox (CRM Dashboard)
| ID | Fitur | Deskripsi | Prioritas |
|---|---|---|---|
| FR-4.1 | Unified conversation view | Lihat semua percakapan (AI + human) dalam satu dashboard | Must |
| FR-4.2 | AI + human handoff | Agent bisa mengambil alih percakapan dari AI, atau sebaliknya | Must |
| FR-4.3 | Tagging & categorization | Tag percakapan berdasarkan topik, status, prioritas | Should |
| FR-4.4 | Analytics dashboard | Metrik: total conversations, AI resolution rate, response time, CSAT | Must |
| FR-4.5 | Conversation search | Cari percakapan berdasarkan keyword, user, tag, date | Should |
| FR-4.6 | Export conversations | Export ke CSV/JSON untuk analisis lebih lanjut | Could |

### 7.5 Zentra API (Developer API)
| ID | Fitur | Deskripsi | Prioritas |
|---|---|---|---|
| FR-5.1 | Chat endpoint | `POST /api/chat` — kirim pesan, terima jawaban AI + citations | Must |
| FR-5.2 | Knowledge query | `POST /api/knowledge/search` — semantic search tanpa generate jawaban | Should |
| FR-5.3 | Embedding endpoint | `POST /api/embeddings` — generate embedding untuk teks | Could |
| FR-5.4 | Webhook | Notifikasi ke URL eksternal saat event tertentu (new message, handoff, dll) | Should |
| FR-5.5 | API key management | Generate/revoke API key per workspace | Must |
| FR-5.6 | Rate limiting | Batasi request per API key (configurable) | Must |

### 7.6 Multi-tenancy & Access Control
| ID | Fitur | Deskripsi | Prioritas |
|---|---|---|---|
| FR-6.1 | Workspace isolation | Data per workspace terisolasi (knowledge base, conversations, users) | Must |
| FR-6.2 | Role-based access | 4 role: Owner, Admin, Agent, Viewer — permission berbeda | Must |
| FR-6.3 | Invite members | Admin bisa invite user ke workspace via email | Should |
| FR-6.4 | SSO integration | Login via Google, GitHub, atau SAML untuk enterprise | Could |

---

## 8. Kebutuhan Non-Fungsional (Non-Functional Requirements)

| Aspek | Kebutuhan |
|---|---|
| **Keamanan & Privasi Data** | Enkripsi data at rest (AES-256) dan in transit (TLS 1.3). Workspace isolation ketat. Compliance: GDPR-ready (data export, deletion). |
| **Performa** | Response time < 3 detik untuk chat. Embedding generation < 10 detik per dokumen 10 halaman. |
| **Skalabilitas** | Multi-tenant architecture: support 1000+ workspace, 1M+ conversations/bulan. Horizontal scaling untuk API server. |
| **Ketersediaan** | Target uptime 99.9% (SLA). Auto-failover untuk database. |
| **Maintainability** | Modular design: Ingest, Core, Chat, Inbox, API bisa di-develop/deploy terpisah. |
| **Extensibility** | Plugin system untuk integrasi third-party (Slack, WhatsApp, dll). |

---

## 9. Arsitektur Sistem (Gambaran Tingkat Tinggi)

```
 [End-User / Customer]
        │
        ▼
 [Zentra Chat Widget] ──────► [Zentra API Gateway] ──────► [Auth / API Key]
 (embeddable JS snippet)           │
                                    │
                                    ▼
                             [Zentra Core Engine]
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
     [Vector Database]      [LLM API Router]      [Document Store]
     (pgvector / Qdrant)    (OpenAI/Anthropic/    (S3 / MinIO)
              │                local model)
              │                     │
              ▼                     ▼
     [Zentra Ingest]         [Zentra Inbox]
     (file/web/API)          (CRM dashboard)
              │                     │
              └─────────────────────┘
                         │
                         ▼
                [Admin / Agent UI]
                (workspace management)
```

**Alur jawaban (RAG — Retrieval Augmented Generation):**
1. User mengirim pertanyaan via chat widget / API.
2. API Gateway validasi API key / session, forward ke Zentra Core.
3. Core generate embedding untuk query, cari chunk relevan di Vector DB (cosine similarity).
4. Top-K chunk (dengan metadata sumber) dikirim sebagai context ke LLM.
5. LLM generate jawaban + sitasi (nama dokumen, section, excerpt).
6. Response dikirim ke frontend, tampilkan jawaban + citation cards.
7. Conversations tercatat di Inbox untuk analytics & human handoff.

---

## 10. Strategi Parsing & Chunking Dokumen

Komponen kritis karena kualitas sitasi bergantung pada parsing.

**Pendekatan:**
- **File upload**: Deteksi pola heading (BAB, Pasal, Section, Chapter) + fallback ke paragraf.
- **Web scraping**: Extract main content (boilerplate removal), chunk by section/heading.
- **API ingestion**: Caller bertanggung jawab atas struktur data; sistem chunk berdasarkan delimiter atau size.

**Metadata per chunk:**
```json
{
  "workspace_id": "ws_abc123",
  "document_id": "doc_xyz789",
  "document_name": "Product Documentation",
  "section": "Getting Started",
  "subsection": "Installation",
  "teks": "To install Zentra, run npm install zentra-sdk...",
  "source_url": "https://docs.example.com/install",
  "halaman": 3,
  "versi_dokumen": "v2.1"
}
```

**Manual correction**: Admin bisa edit metadata chunk jika parsing tidak sempurna.

---

## 11. Contoh Tampilan (Ilustrasi UX)

### Chat Widget (End-User View)
```
[User]: How do I install Zentra?

[AI]: To install Zentra, run the following command:

      npm install zentra-sdk

      After installation, initialize the SDK with your API key:

      const zentra = new Zentra({ apiKey: 'your-api-key' });

      📄 Sources:
         Product Documentation → Getting Started → Installation
         "To install Zentra, run npm install zentra-sdk..."
         [View full document]

[👍] [👎] [💬 Talk to human]
```

### Inbox Dashboard (Agent View)
```
┌─────────────────────────────────────────────────────┐
│  Zentra Inbox — All Conversations                   │
├─────────────────────────────────────────────────────┤
│  🔍 Search conversations...                         │
│                                                     │
│  [All] [AI Resolved] [Human Active] [Unanswered]    │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │ #1234 — John Doe                              │  │
│  │ "How to reset password?"                      │  │
│  │ Status: ✅ AI Resolved | Tag: Account         │  │
│  │ Last message: 2 min ago                       │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │ #1235 — Jane Smith                            │  │
│  │ "Can I get a refund?"                         │  │
│  │ Status: 🔄 Human Active | Agent: Sarah        │  │
│  │ Last message: 5 min ago                       │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 12. Metrik Keberhasilan (KPI)

| Metrik | Target Indikatif |
|---|---|
| AI resolution rate (% pertanyaan dijawab tanpa human) | > 70% |
| Response time (p95) | < 3 detik |
| Customer satisfaction (CSAT) | > 85% |
| Time to first response (AI) | < 5 detik |
| Knowledge base coverage (% pertanyaan yang punya konteks relevan) | > 90% |
| Monthly active workspaces (untuk SaaS) | 100+ dalam 6 bulan |
| API uptime | > 99.9% |

---

## 13. Asumsi & Ketergantungan

- LLM API (OpenAI/Anthropic/local) tersedia dan stabil; jika tidak, fallback ke model open-source (Llama, Mistral).
- Infrastruktur cloud (AWS/GCP/Azure) untuk deployment; on-premise option untuk enterprise.
- Tim memiliki kapasitas untuk develop multi-tenant architecture dari awal (tidak bisa retrofit mudah).
- Early adopter / beta tester tersedia untuk feedback MVP.

---

## 14. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| LLM hallucination (jawab di luar konteks) | User mendapat informasi salah | Wajibkan sitasi; jika confidence rendah, jawab "tidak ditemukan" |
| Multi-tenant data leakage | Workspace A lihat data Workspace B | Strict tenant isolation di DB level (row-level security / separate schema) |
| Embedding API latency tinggi | UX lambat | Cache embedding untuk dokumen statis; async processing |
| Chat widget performance issue di website client | Website client lambat | Lazy load widget; minify JS; CDN hosting |
| Low AI resolution rate | User frustrasi, abandon chat | Continuous improvement: retrain on unanswered questions, improve chunking |
| API abuse (rate limit exceeded, malicious queries) | Cost bengkak, service degradation | Rate limiting per API key; anomaly detection; quota system |

---

## 15. Roadmap / Fase Pengembangan (Indikatif)

| Fase | Fokus |
|---|---|
| **Fase 1 — MVP (Bulan 1-3)** | Zentra Core (RAG), Ingest (file upload), Chat (embeddable widget), basic Inbox, API |
| **Fase 2 — SaaS Ready (Bulan 4-6)** | Multi-tenant, workspace management, billing/subscription, advanced analytics |
| **Fase 3 — Integrations (Bulan 7-9)** | Webhook, Slack/WhatsApp integration, API marketplace, SSO |
| **Fase 4 — Enterprise (Bulan 10-12)** | On-premise deployment, advanced security (SOC2, HIPAA), custom LLM fine-tuning |

---

## 16. Pertanyaan Terbuka (untuk dikonfirmasi bersama tim)

1. Model LLM yang akan dipakai: OpenAI GPT-4, Anthropic Claude, atau local model (Llama 3)? Multi-model support dari awal atau single model dulu?
2. Pricing model untuk SaaS: per workspace, per agent, per conversation, atau usage-based (token)?
3. On-premise deployment: apakah perlu dari Fase 1, atau cukup cloud-only untuk MVP?
4. Early adopter: ada 1-2 perusahaan yang mau jadi beta tester?
5. Branding: apakah Zentra akan di-white-label untuk agency, atau tetap pakai brand Zentra?
6. Compliance: apakah perlu GDPR/ISO 27001 certification dari Fase 1?

---

*Dokumen ini adalah draft v0.2 — pivot dari "internal SOP Q&A" ke "AI-Powered CRM & Knowledge Engine". Terbuka untuk revisi bersama stakeholder.*
