# RAG Chatbot - Tài liệu chi tiết từ A-Z

## Mục lục

1. [RAG là gì?](#1-rag-là-gì)
2. [Kiến trúc tổng quan](#2-kiến-trúc-tổng-quan)
3. [Công nghệ sử dụng](#3-công-nghệ-sử-dụng)
4. [Cấu trúc thư mục](#4-cấu-trúc-thư-mục)
5. [Phase 1: Ingestion - Nạp dữ liệu sách vào Vector DB](#5-phase-1-ingestion---nạp-dữ-liệu-sách-vào-vector-db)
6. [Phase 2: Query - Xử lý câu hỏi người dùng](#6-phase-2-query---xử-lý-câu-hỏi-người-dùng)
7. [Chi tiết từng module](#7-chi-tiết-từng-module)
8. [Conversation History](#8-conversation-history---lịch-sử-hội-thoại)
9. [API Endpoints](#9-api-endpoints)
10. [Cấu hình & Biến môi trường](#10-cấu-hình--biến-môi-trường)
11. [Docker & Infrastructure](#11-docker--infrastructure)
12. [Error Handling & Fallback](#12-error-handling--fallback)
13. [Ví dụ end-to-end](#13-ví-dụ-end-to-end)

---

## 1. RAG là gì?

**RAG (Retrieval-Augmented Generation)** là kỹ thuật kết hợp 2 bước:

1. **Retrieval (Truy xuất)**: Tìm kiếm thông tin liên quan từ cơ sở dữ liệu dựa trên câu hỏi
2. **Generation (Sinh câu trả lời)**: Đưa thông tin tìm được vào LLM (Gemini) để sinh câu trả lời

**Tại sao cần RAG?**

- LLM (Gemini) không biết gì về dữ liệu sách trong hệ thống BookStore
- Nếu hỏi "Có sách Python nào?", Gemini chỉ trả lời chung chung
- RAG giúp Gemini trả lời dựa trên **dữ liệu thực** trong database

**So sánh:**

| Không có RAG | Có RAG |
|---|---|
| "Có nhiều sách Python hay, bạn thử tìm trên Google" | "Có, chúng tôi có 'Lập Trình Python' của Nguyễn Văn A, giá 150.000 VND, còn hàng" |

---

## 2. Kiến trúc tổng quan

```
┌──────────────────────────────────────────────────────────────────────┐
│                         INGESTION PHASE                              │
│                  (Nạp dữ liệu sách vào Vector DB)                   │
│                                                                      │
│  Book Service                  Chatbot Service           Qdrant      │
│  ┌────────────┐               ┌──────────────────┐    ┌──────────┐  │
│  │ CRUD sách  │──Webhook───>  │ document_processor│──> │ Vectors  │  │
│  │ create     │  (async)      │ ├ build_book_text │    │ (768D)   │  │
│  │ update     │               │ ├ embed_text      │    │ +metadata│  │
│  │ delete     │               │ └ upsert/delete   │    └──────────┘  │
│  └────────────┘               └──────────────────┘                   │
│                                       │                              │
│                                       ▼                              │
│                               ┌──────────────────┐                   │
│                               │ MongoDB           │                  │
│                               │ (sync records)    │                  │
│                               └──────────────────┘                   │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                          QUERY PHASE                                 │
│                (Người dùng hỏi → Chatbot trả lời)                   │
│                                                                      │
│  User        views.py         rag_service.py          gemini_client  │
│  ┌────┐     ┌──────────┐     ┌──────────────────┐    ┌──────────┐  │
│  │ Hỏi│──>  │ POST     │──>  │ 1. History        │──> │ Gemini   │  │
│  │    │     │ /chat/   │     │ 2. Smart query    │    │ API      │  │
│  │    │     │          │     │ 3. Stats summary  │    │          │  │
│  │    │     │          │     │ 4. Embed + search │    │ Response │  │
│  │    │ <── │          │ <── │ 5. KB enrichment  │ <──│          │  │
│  └────┘     └──────────┘     │ 6. Build prompt   │    └──────────┘  │
│                              └──────────────────┘                    │
│                                      │                               │
│                              ┌───────┴───────┐                       │
│                              ▼               ▼                       │
│                        ┌──────────┐   ┌──────────┐                   │
│                        │ Qdrant   │   │ MongoDB  │                   │
│                        │ (search) │   │ (history)│                   │
│                        └──────────┘   └──────────┘                   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Công nghệ sử dụng

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Backend | Django REST Framework | API server cho chatbot |
| LLM | Google Gemini (`gemini-2.0-flash-lite`) | Sinh câu trả lời từ context |
| Embedding model | `dangvantuan/vietnamese-document-embedding` | Chuyển text thành vector 768 chiều, tối ưu cho tiếng Việt |
| Vector DB | Qdrant | Lưu và tìm kiếm vector (semantic search) |
| Document DB | MongoDB | Lưu conversation history, session, document metadata |
| Text Chunking | langchain-text-splitters | Chia văn bản dài thành đoạn nhỏ |
| ML Backend | PyTorch + sentence-transformers | Chạy mô hình embedding |
| HTTP Client | httpx, requests | Gọi API giữa các service |

---

## 4. Cấu trúc thư mục

```
services/chatbot-service/
├── Dockerfile                          # Build image, pre-download embedding model
├── requirements.txt                    # Python dependencies
│
├── chatbot_service/                    # Django project config
│   ├── settings.py                     # Cấu hình: Gemini, MongoDB, Qdrant, RAG params
│   ├── urls.py                         # Root URL → /api/chat/
│   └── wsgi.py                         # WSGI entry point (gunicorn)
│
└── chat/                               # App chính
    ├── views.py                        # 11 API endpoints (chat, sessions, docs, webhooks)
    ├── urls.py                         # URL routing cho app
    ├── services.py                     # HTTP client gọi book-service, order-service
    ├── gemini_client.py                # Client gọi Gemini API
    │
    ├── rag/                            # === RAG Pipeline ===
    │   ├── rag_service.py              # Orchestrator - điều phối toàn bộ pipeline
    │   ├── embedding_service.py        # Sinh embedding từ text (SentenceTransformer)
    │   ├── vector_store.py             # CRUD trên Qdrant (upsert, search, delete)
    │   ├── mongo_store.py              # CRUD trên MongoDB (sessions, messages, docs)
    │   ├── chunking.py                 # Chia text thành chunks nhỏ
    │   ├── document_processor.py       # Nạp sách/tài liệu vào knowledge base
    │   ├── context_builder.py          # Ghép context từ nhiều nguồn → prompt
    │   └── book_query.py               # Smart query routing (đắt nhất, rẻ nhất...)
    │
    └── management/commands/
        └── sync_books.py               # CLI: python manage.py sync_books
```

**Vai trò từng file trong RAG pipeline:**

```
                    rag_service.py (Orchestrator)
                    ┌─────────────────────────────┐
                    │ Điều phối 7 bước của pipeline │
                    └──────────┬──────────────────┘
                               │ gọi
        ┌──────────┬───────────┼───────────┬──────────────┐
        ▼          ▼           ▼           ▼              ▼
  book_query   embedding   vector_store  mongo_store  context_builder
  (smart query)(embed text)(Qdrant CRUD) (MongoDB)   (ghép prompt)
       │
       ▼
  document_processor ←── chunking.py
  (nạp sách vào DB)      (chia text)
```

---

## 5. Phase 1: Ingestion - Nạp dữ liệu sách vào Vector DB

### 5.1. Tổng quan

Trước khi chatbot có thể trả lời về sách, dữ liệu sách cần được:
1. Lấy từ Book Service
2. Chuyển thành text mô tả
3. Chuyển text thành vector (embedding)
4. Lưu vector + metadata vào Qdrant

### 5.2. Ba cách trigger ingestion

#### Cách 1: Webhook realtime (Tự động khi CRUD sách)

Khi staff tạo/sửa/xóa sách trên Book Service, webhook tự động gửi đến Chatbot Service.

**File**: `services/book-service/app/webhook.py`

```python
# Khi tạo sách mới trong BookViewSet (views.py)
def perform_create(self, serializer):
    book = serializer.save()
    notify_book_created(BookSerializer(book).data)  # ← gửi webhook

# Webhook chạy trên thread riêng, không block Book Service
def _send_webhook(action, book_data=None, book_id=None):
    thread = threading.Thread(target=_do_send, daemon=True)
    thread.start()  # Non-blocking, timeout 5s
```

**Flow:**
```
Book Service                         Chatbot Service
┌──────────────────┐                ┌──────────────────────────────┐
│ POST /api/books/ │                │ POST /chat/webhook/book-     │
│ (tạo sách mới)   │───Webhook───> │      updated/                │
│                  │  {             │                              │
│                  │   "action":    │ → upsert_single_book(book)   │
│                  │   "created",   │   1. build_book_text()       │
│                  │   "book": {    │   2. embed_text() → [0.12,..]│
│                  │     "title":.. │   3. upsert to Qdrant        │
│                  │   }            │                              │
│                  │  }             │ ← {"success": true}          │
└──────────────────┘                └──────────────────────────────┘
```

#### Cách 2: Full sync qua CLI

Dùng khi deploy lần đầu hoặc cần sync lại toàn bộ.

```bash
# Trong Docker
docker exec chatbot-service python manage.py sync_books --force
```

#### Cách 3: REST API

```bash
POST /api/chat/sync-books/
# Response: {"success": true, "synced": 150, "message": "Successfully synced 150 books"}
```

### 5.3. Chi tiết pipeline ingestion

**File**: `chat/rag/document_processor.py`

```
Bước 1: Fetch sách                    Bước 2: Build text
┌────────────────────┐                ┌────────────────────────────┐
│ GET /api/books/    │                │ _build_book_text(book):    │
│ ?page_size=200     │ ──────────>    │                            │
│                    │                │ "Tên sách: Lập Trình Python│
│ Lặp qua từng page │                │  Tác giả: Nguyễn Văn A     │
│ (pagination)       │                │  Mô tả: Hướng dẫn lập...  │
│                    │                │  Giá: 150000 VND           │
│ books = [150 sách] │                │  Thể loại: CNTT            │
└────────────────────┘                │  NXB: NXB Giáo Dục        │
                                      │  ISBN: 978-604-xxx         │
                                      │  Tình trạng: Còn hàng"    │
                                      └────────────────────────────┘
                                                   │
                                                   ▼
Bước 3: Embedding                     Bước 4: Lưu vào Qdrant
┌────────────────────┐                ┌────────────────────────────┐
│ SentenceTransformer│                │ Qdrant upsert:             │
│ .encode(text)      │ ──────────>    │                            │
│                    │                │ Point {                    │
│ Input:  "Tên sách: │                │   id: "uuid-xxx"           │
│  Lập Trình Python  │                │   vector: [0.12, -0.45,    │
│  Tác giả:..."      │                │            0.78, ...] 768D │
│                    │                │   payload: {               │
│ Output: [0.12,     │                │     content: "Tên sách:.." │
│  -0.45, 0.78, ...] │                │     source_type: "book"    │
│  (768 số thực)     │                │     book_id: "1"           │
│                    │                │     author: "Nguyễn Văn A" │
│ Normalized (L2)    │                │     price: "150000"        │
└────────────────────┘                │   }                        │
                                      │ }                          │
                                      └────────────────────────────┘
```

### 5.4. Embedding là gì?

**Embedding** = chuyển text thành vector (mảng số thực) sao cho:
- Text có ý nghĩa **tương tự** → vector **gần nhau**
- Text có ý nghĩa **khác nhau** → vector **xa nhau**

```
"Sách lập trình Python"  → [0.12, -0.45, 0.78, ...]  ─┐
"Học Python cơ bản"       → [0.11, -0.43, 0.80, ...]  ─┤ GẦN NHAU (cosine ~ 0.95)
                                                        │
"Tiểu thuyết tình cảm"   → [-0.67, 0.23, -0.11, ...] ─┘ XA (cosine ~ 0.15)
```

**Model**: `dangvantuan/vietnamese-document-embedding`
- Được train trên dữ liệu tiếng Việt
- Output: vector 768 chiều
- Normalized (chuẩn hóa L2) để dùng cosine similarity

### 5.5. Qdrant lưu gì?

Mỗi sách = 1 point trong Qdrant collection `bookstore_knowledge`:

```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "vector": [0.12, -0.45, 0.78, ...],
  "payload": {
    "content": "Tên sách: Lập Trình Python\nTác giả: Nguyễn Văn A\n...",
    "source_id": "book_catalog",
    "source_type": "book",
    "source_title": "Lập Trình Python",
    "book_id": "1",
    "author": "Nguyễn Văn A",
    "price": "150000",
    "category": "Công nghệ thông tin"
  }
}
```

- **vector**: dùng để tìm kiếm similarity
- **payload**: metadata trả về kèm kết quả (không dùng để search)

---

## 6. Phase 2: Query - Xử lý câu hỏi người dùng

### 6.1. Tổng quan 7 bước

Khi user gửi tin nhắn, `rag_service.py` chạy 7 bước tuần tự:

**File**: `chat/rag/rag_service.py` → method `query()`

```
User: "Có sách Python nào?"
         │
         ▼
┌─ Bước 1: Conversation History ──────────────────────┐
│ mongo_store.get_recent_context(session_id, limit=6)  │
│ → Lấy 6 tin nhắn gần nhất để chatbot nhớ ngữ cảnh  │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌─ Bước 2: Smart Query Detection ─────────────────────┐
│ detect_query_intent("Có sách Python nào?")           │
│ → None (không match pattern đắt nhất/rẻ nhất/...)   │
│                                                      │
│ Nếu user hỏi "Sách nào đắt nhất?" → intent =       │
│ "most_expensive" → fetch top 5 sách đắt nhất từ API │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌─ Bước 3: Stats Summary ─────────────────────────────┐
│ build_stats_summary() → gọi Book Service API        │
│ → "[Thông tin tổng quan cửa hàng]                   │
│    Tổng số sách: 150 cuốn                           │
│    Còn hàng: 140 cuốn                               │
│    Sách đắt nhất: "Advanced Python" - 450000 VND    │
│    Sách rẻ nhất: "Python Cơ Bản" - 89000 VND"      │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌─ Bước 4: Semantic Search (Vector Search) ────────────┐
│ 4a. embedding_service.embed_text("Có sách Python     │
│     nào?") → [0.15, -0.32, 0.67, ...]               │
│                                                      │
│ 4b. vector_store.search(                             │
│       query_embedding=[0.15, -0.32, ...],            │
│       top_k=5,                                       │
│       score_threshold=0.3                            │
│     )                                                │
│     → Qdrant so sánh cosine similarity với 150 sách  │
│     → Trả về top 5 sách giống nhất                   │
│                                                      │
│ 4c. _deduplicate() → loại bỏ trùng lặp              │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌─ Bước 5: Build Context ─────────────────────────────┐
│ context_builder.build_context(search_results)        │
│ → "[Lập Trình Python]                               │
│    Tên sách: Lập Trình Python                       │
│    Tác giả: Nguyễn Văn A                            │
│    Giá: 150000 VND ..."                              │
│                                                      │
│ + sources: [{title, score, book_id, author, price}]  │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌─ Bước 6: KB-lite Enrichment ────────────────────────┐
│ enrich_with_related_books(search_results)            │
│ → Lấy sách top 1 → tìm thêm sách cùng tác giả     │
│   và cùng thể loại từ Book Service API              │
│ → "[Sách cùng tác giả Nguyễn Văn A]                │
│    1. Lập Trình Java - 160000 VND                   │
│    [Sách cùng thể loại]                             │
│    1. Data Science Cơ Bản - 200000 VND"             │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌─ Bước 7: Build Final Prompt ────────────────────────┐
│ context_builder.build_chat_prompt(...)               │
│ → Ghép tất cả lại thành 1 prompt duy nhất gửi      │
│   cho Gemini (xem chi tiết bên dưới)                │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌─ Gemini Generate Response ──────────────────────────┐
│ gemini_client.generate_response(message, prompt)     │
│ → POST https://generativelanguage.googleapis.com/... │
│ → Gemini đọc prompt + context → sinh câu trả lời    │
│ → "Có, chúng tôi có sách Lập Trình Python của       │
│    Nguyễn Văn A, giá 150.000 VND, hiện còn hàng..." │
└──────────────────────────────────────────────────────┘
```

### 6.2. Smart Query Routing

**File**: `chat/rag/book_query.py`

Một số câu hỏi không thể trả lời bằng vector search (vd: "Sách nào đắt nhất?"). Module này detect intent và fetch data trực tiếp từ Book Service API.

```
User message              → Intent            → API call                    → Kết quả
─────────────────────────────────────────────────────────────────────────────────────────
"Sách nào đắt nhất?"      → most_expensive    → GET /books/?ordering=-price  → Top 5 đắt nhất
"Sách nào rẻ nhất?"       → cheapest          → GET /books/?ordering=price   → Top 5 rẻ nhất
"Sách mới nhất?"          → newest            → GET /books/?ordering=-created_at → Top 5 mới
"Có bao nhiêu cuốn sách?" → count             → GET /books/?page_size=1      → Tổng + Còn/Hết
"Sách còn hàng?"          → in_stock          → GET /books/?in_stock=true    → Số lượng còn
"Sách hết hàng?"          → out_of_stock      → Tính: total - in_stock       → Số lượng hết
"Có sách Python nào?"     → None              → (dùng vector search)
```

**Regex patterns** (detect intent):
```python
_PATTERNS = {
    "most_expensive": r"(đắt nhất|giá cao nhất|mắc nhất|expensive)",
    "cheapest":       r"(rẻ nhất|giá thấp nhất|giá rẻ|cheapest)",
    "newest":         r"(mới nhất|mới ra|ra mắt gần đây|newest|latest)",
    "count":          r"(bao nhiêu cuốn|bao nhiêu sách|tổng.*sách|how many books)",
    "in_stock":       r"(còn hàng|còn bán|available|in.?stock)",
    "out_of_stock":   r"(hết hàng|out.?of.?stock)",
}
```

### 6.3. Semantic Search hoạt động thế nào?

```
                    "Có sách Python nào?"
                           │
                           ▼
                ┌─ Embedding Service ──┐
                │ encode("Có sách     │
                │ Python nào?")       │
                │ → query_vector      │
                │   [0.15, -0.32, ...]│
                └─────────┬───────────┘
                          │
                          ▼
         ┌─ Qdrant Collection ─────────────────────────────┐
         │                                                  │
         │  Point 1: "Lập Trình Python..."                 │
         │  vector: [0.14, -0.30, 0.65, ...]               │
         │  cosine(query, point1) = 0.92 ✅ (rất giống!)    │
         │                                                  │
         │  Point 2: "Data Science với Python..."           │
         │  vector: [0.12, -0.28, 0.60, ...]               │
         │  cosine(query, point2) = 0.85 ✅                  │
         │                                                  │
         │  Point 3: "Tiểu thuyết Mắt Biếc..."            │
         │  vector: [-0.67, 0.23, -0.11, ...]              │
         │  cosine(query, point3) = 0.12 ❌ (dưới threshold)│
         │                                                  │
         │  → Trả về: [Point 1, Point 2] (top_k=5,         │
         │            score_threshold=0.3)                  │
         └──────────────────────────────────────────────────┘
```

**Cosine similarity**:
- Đo góc giữa 2 vector
- Giá trị từ 0 đến 1 (đã normalize)
- `> 0.3` = đủ liên quan (threshold mặc định)
- `> 0.8` = rất liên quan

### 6.4. Final Prompt gửi cho Gemini

**File**: `chat/rag/context_builder.py` → `build_chat_prompt()`

Prompt cuối cùng ghép từ 6 lớp context:

```
┌──────────────────────────────────────────────────────────────────────┐
│ [System Prompt]                                                      │
│ "Bạn là trợ lý AI thông minh của BookStore..."                      │
│                                                                      │
│ Thông tin bổ sung:                                                   │
│                                                                      │
│ ① [Thông tin tổng quan cửa hàng]          ← stats_summary           │
│ Tổng số sách: 150 cuốn                                              │
│ Còn hàng: 140 cuốn                                                  │
│ Sách đắt nhất: "Advanced Python" - 450000 VND                       │
│ Sách rẻ nhất: "Python Cơ Bản" - 89000 VND                          │
│                                                                      │
│ ② [Dữ liệu chính xác từ hệ thống]        ← structured_context      │
│ (Chỉ có khi smart query match, vd: top 5 đắt nhất)                 │
│                                                                      │
│ ③ Thông tin tham khảo từ cơ sở dữ liệu:   ← context_text (RAG)     │
│ ---                                                                  │
│ [Lập Trình Python]                                                   │
│ Tên sách: Lập Trình Python                                          │
│ Tác giả: Nguyễn Văn A                                               │
│ Giá: 150000 VND                                                     │
│ Tình trạng: Còn hàng                                                │
│ ---                                                                  │
│                                                                      │
│ ④ [Sách liên quan gợi ý]                  ← related_context (KB-lite)│
│ [Sách cùng tác giả Nguyễn Văn A]                                    │
│ 1. "Lập Trình Java" - 160000 VND                                    │
│                                                                      │
│ ⑤ Lịch sử hội thoại gần đây:              ← conversation_history    │
│ Khách hàng: "Có sách Python nào?"                                   │
│ Trợ lý: "Có, chúng tôi có..."                                       │
│                                                                      │
│ ⑥ Khách hàng: {user_message}              ← câu hỏi hiện tại       │
│                                                                      │
│ Người dùng: Có sách Python nào?                                     │
│ Trợ lý:                                                             │
└──────────────────────────────────────────────────────────────────────┘
```

Gemini đọc toàn bộ prompt này và sinh câu trả lời dựa trên context được cung cấp.

---

## 7. Chi tiết từng module

### 7.1. `embedding_service.py` - Sinh vector từ text

**File**: `chat/rag/embedding_service.py`

| Thuộc tính | Giá trị |
|---|---|
| Model | `dangvantuan/vietnamese-document-embedding` |
| Dimension | 768 |
| Normalize | L2 (tự động) |
| Lazy loading | Có (load lần đầu dùng, thread-safe) |
| Batch size | 32 |

```python
class EmbeddingService:
    def embed_text(self, text: str) -> List[float]:
        # Một câu → 1 vector [768 số]
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size=32) -> List[List[float]]:
        # Nhiều câu → nhiều vector (batch 32 câu/lần)
```

**Singleton**: `embedding_service = EmbeddingService()` — load model 1 lần, dùng chung.

### 7.2. `vector_store.py` - Qdrant operations

**File**: `chat/rag/vector_store.py`

| Thuộc tính | Giá trị |
|---|---|
| Collection | `bookstore_knowledge` |
| Distance metric | COSINE |
| Vector size | 768 |
| Batch upsert | 100 points/batch |

**Các operations chính:**

```python
# Lưu documents vào Qdrant
vector_store.upsert_documents(texts, embeddings, metadatas) → point_ids

# Tìm kiếm semantic
vector_store.search(query_embedding, top_k=5, score_threshold=0.3) → results

# Xóa theo book_id (khi sách bị xóa/update)
vector_store.delete_by_book_id(book_id)

# Xóa theo source (khi full sync)
vector_store.delete_by_source("book_catalog")

# Thống kê collection
vector_store.get_collection_info() → {name, points_count, status}
```

### 7.3. `document_processor.py` - Nạp dữ liệu

**File**: `chat/rag/document_processor.py`

3 chức năng chính:

```python
# 1. Full sync: lấy toàn bộ sách từ Book Service → index vào Qdrant
sync_books_from_service() → {"success": true, "synced": 150}

# 2. Single book: webhook gọi khi 1 sách được tạo/sửa
upsert_single_book(book) → {"success": true, "book_id": "1"}

# 3. Delete: webhook gọi khi sách bị xóa
delete_single_book(book_id) → {"success": true}
```

**`_build_book_text()`** — chuyển book object thành text:
```
Input:  {"title": "Lập Trình Python", "author": "Nguyễn Văn A", "price": "150000", ...}
Output: "Tên sách: Lập Trình Python\nTác giả: Nguyễn Văn A\nGiá: 150000 VND\n..."
```

### 7.4. `chunking.py` - Chia text

**File**: `chat/rag/chunking.py`

| Config | Giá trị | Ý nghĩa |
|---|---|---|
| chunk_size | 512 chars | Tối đa 512 ký tự/chunk |
| chunk_overlap | 50 chars | 50 ký tự overlap giữa 2 chunk |
| min_chunk_size | 100 chars | Bỏ chunk < 100 ký tự |

Dùng `RecursiveCharacterTextSplitter` (langchain) với thứ tự chia:
1. `\n\n` (đoạn văn)
2. `\n` (dòng mới)
3. `. ` (câu)
4. `, ` (mệnh đề)
5. ` ` (từ)

**Lưu ý**: Với sách, mỗi cuốn thường chỉ tạo 1-2 chunk vì text mô tả ngắn (< 512 chars).

### 7.5. `mongo_store.py` - MongoDB operations

**File**: `chat/rag/mongo_store.py`

**3 collections:**

```
MongoDB: chatbot_db
├── chat_sessions     ← Phiên trò chuyện
│   {user_id, title, message_count, created_at, updated_at}
│   Index: (user_id, -updated_at)
│
├── chat_messages     ← Tin nhắn trong phiên
│   {session_id, role, content, sources, metadata, created_at}
│   Index: (session_id, created_at)
│
└── documents         ← Metadata tài liệu đã nạp
    {title, content, source_type, chunk_count, vector_ids, created_at}
    Index: (source_type)
```

### 7.6. `context_builder.py` - Ghép prompt

**File**: `chat/rag/context_builder.py`

2 method:

```python
# 1. Ghép search results thành text context (max 4000 chars)
build_context(search_results) → {context_text, sources, avg_score}

# 2. Ghép tất cả các lớp context thành final prompt
build_chat_prompt(user_message, context_text, structured_context,
                  related_context, stats_summary, conversation_history) → str
```

### 7.7. `gemini_client.py` - Gọi Gemini API

**File**: `chat/gemini_client.py`

```python
class GeminiClient:
    model = "gemini-2.0-flash-lite"
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def generate_response(self, user_message, context):
        prompt = f"{system_prompt}\n\nThông tin bổ sung:\n{context}\n\n"
        prompt += f"Người dùng: {user_message}\nTrợ lý:"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,      # Cân bằng sáng tạo/chính xác
                "maxOutputTokens": 1024,  # Giới hạn độ dài response
            }
        }
        # POST to Gemini API
```

**System Prompt** (trong `settings.py`):

```
Bạn là trợ lý AI thông minh của BookStore, được trang bị khả năng tìm kiếm
thông tin từ cơ sở dữ liệu sách và tài liệu.

Nhiệm vụ của bạn:
- Tư vấn và gợi ý sách phù hợp dựa trên nhu cầu khách hàng
- Trả lời câu hỏi về thông tin sách (tác giả, giá, mô tả, thể loại...)
- Hướng dẫn đặt hàng, thanh toán (MoMo, COD), vận chuyển
- Giải đáp chính sách đổi trả, bảo hành
- Tra cứu trạng thái đơn hàng

Quy tắc:
- Trả lời dựa trên thông tin được cung cấp trong ngữ cảnh (context)
- Trả lời ngắn gọn, thân thiện, chuyên nghiệp bằng tiếng Việt
- Khi giới thiệu sách, luôn kèm tên sách, tác giả và giá (nếu có)
- Nếu không có thông tin, nói rõ và hướng dẫn liên hệ nhân viên
```

---

## 8. Conversation History - Lịch sử hội thoại

### 8.1. Flow

```
Tin nhắn 1: "Có sách Python nào?"
→ Tạo session mới (MongoDB)
→ Lưu user message + bot response
→ Trả về session_id cho frontend

Tin nhắn 2: "Giá bao nhiêu?" (gửi kèm session_id)
→ Lấy 6 tin nhắn gần nhất từ session
→ Đưa vào context để Gemini hiểu "giá" = giá sách Python ở tin nhắn 1
→ Lưu tiếp vào session
```

### 8.2. Tại sao giới hạn 6 tin nhắn?

- Gemini có giới hạn context window
- 6 tin nhắn (3 cặp user-bot) đủ để duy trì ngữ cảnh
- Tránh prompt quá dài → tốn token + chậm

### 8.3. Session management

```
Frontend lưu session_id trong localStorage
  │
  ├─ Tin nhắn đầu tiên: không gửi session_id
  │   → Backend tạo session mới, trả về session_id
  │
  ├─ Tin nhắn tiếp theo: gửi kèm session_id
  │   → Backend lấy history, thêm vào context
  │
  └─ User mở tab mới / cuộc trò chuyện mới
      → Không gửi session_id → tạo session mới
```

---

## 9. API Endpoints

### Chat

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/chat/` | Chat chính (RAG pipeline) |
| GET | `/api/chat/search-book/?q=Python` | Tìm sách + AI tóm tắt |
| GET | `/api/chat/order-status/{id}/` | Tra cứu đơn hàng |

**POST /api/chat/** — Request/Response:

```json
// Request
{
  "message": "Có sách Python nào?",
  "session_id": "507f1f77bcf86cd799439011"  // optional
}

// Response
{
  "success": true,
  "response": "Có, chúng tôi có sách Lập Trình Python...",
  "model": "gemini-2.0-flash-lite",
  "sources": [
    {
      "title": "Lập Trình Python",
      "score": 0.875,
      "source_type": "book",
      "book_id": "1",
      "author": "Nguyễn Văn A",
      "price": "150000"
    }
  ],
  "session_id": "507f1f77bcf86cd799439011"
}
```

### Session Management

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/chat/sessions/` | Danh sách sessions |
| POST | `/api/chat/sessions/` | Tạo session mới |
| GET | `/api/chat/sessions/{id}/` | Chi tiết session + messages |
| DELETE | `/api/chat/sessions/{id}/` | Xóa session |
| GET | `/api/chat/history/{id}/` | Lịch sử tin nhắn |

### Knowledge Base

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/chat/documents/` | Danh sách tài liệu |
| POST | `/api/chat/documents/` | Upload tài liệu (file hoặc text) |
| DELETE | `/api/chat/documents/{id}/` | Xóa tài liệu |

### Admin & Monitoring

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/chat/sync-books/` | Full sync sách từ Book Service |
| POST | `/api/chat/webhook/book-updated/` | Webhook nhận event từ Book Service |
| GET | `/api/chat/rag-stats/` | Thống kê RAG system |
| GET | `/api/chat/health/` | Health check (Gemini + Qdrant + MongoDB) |

---

## 10. Cấu hình & Biến môi trường

**File**: `chatbot_service/settings.py`

### Gemini

| Biến | Mặc định | Mô tả |
|---|---|---|
| `GEMINI_API_KEY` | (bắt buộc) | API key từ Google AI Studio |
| `GEMINI_MODEL` | `gemini-2.0-flash-lite` | Model Gemini sử dụng |

### MongoDB

| Biến | Mặc định | Mô tả |
|---|---|---|
| `MONGODB_URL` | `mongodb://mongo:mongo@mongodb:27017/chatbot_db?authSource=admin` | Connection string |
| `MONGODB_DB_NAME` | `chatbot_db` | Tên database |

### Qdrant

| Biến | Mặc định | Mô tả |
|---|---|---|
| `QDRANT_HOST` | `qdrant` | Hostname (Docker service name) |
| `QDRANT_PORT` | `6333` | Port |
| `QDRANT_COLLECTION` | `bookstore_knowledge` | Tên collection |

### Embedding

| Biến | Mặc định | Mô tả |
|---|---|---|
| `EMBEDDING_MODEL` | `dangvantuan/vietnamese-document-embedding` | HuggingFace model |
| `EMBEDDING_DIMENSION` | `768` | Số chiều vector |

### RAG

| Biến | Mặc định | Mô tả |
|---|---|---|
| `RAG_TOP_K` | `5` | Số kết quả search trả về |
| `RAG_SIMILARITY_THRESHOLD` | `0.3` | Ngưỡng cosine similarity tối thiểu |

### Chunking

| Biến | Mặc định | Mô tả |
|---|---|---|
| `CHUNK_SIZE` | `512` | Tối đa ký tự/chunk |
| `CHUNK_OVERLAP` | `50` | Ký tự overlap giữa 2 chunk |
| `MIN_CHUNK_SIZE` | `100` | Bỏ chunk < 100 ký tự |

### External Services

| Biến | Mặc định | Mô tả |
|---|---|---|
| `BOOK_SERVICE_URL` | `http://book-service:8001` | URL Book Service |
| `ORDER_SERVICE_URL` | `http://order-service:8004` | URL Order Service |

---

## 11. Docker & Infrastructure

### docker-compose.yml (RAG stack)

```yaml
chatbot-service:
  build: ./services/chatbot-service
  ports:
    - "8013:8000"
  environment:
    GEMINI_API_KEY: ${GEMINI_API_KEY}
    BOOK_SERVICE_URL: http://book-service:8000
    MONGODB_URL: mongodb://mongo:mongo@mongodb:27017/chatbot_db?authSource=admin
    QDRANT_HOST: qdrant
    QDRANT_PORT: "6333"
    EMBEDDING_MODEL: dangvantuan/vietnamese-document-embedding
    RAG_TOP_K: "5"
    RAG_SIMILARITY_THRESHOLD: "0.3"
  depends_on:
    - qdrant
    - mongodb

qdrant:
  image: qdrant/qdrant:latest
  ports:
    - "6333:6333"                    # REST API
  volumes:
    - qdrant_data:/qdrant/storage   # Persist vectors

mongodb:
  image: mongo:7
  ports:
    - "27017:27017"
  environment:
    MONGO_INITDB_ROOT_USERNAME: mongo
    MONGO_INITDB_ROOT_PASSWORD: mongo
    MONGO_INITDB_DATABASE: chatbot_db
  volumes:
    - mongodb_data:/data/db         # Persist data
```

### Dockerfile (chatbot-service)

```dockerfile
FROM python:3.11-slim

# Pre-download embedding model (~500MB) tại build time
# Để container start nhanh hơn (không cần download lúc runtime)
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('dangvantuan/vietnamese-document-embedding', trust_remote_code=True)"

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", \
     "--workers", "2", "chatbot_service.wsgi:application"]
```

---

## 12. Error Handling & Fallback

### Graceful Degradation

Hệ thống được thiết kế để **không bao giờ trả lỗi cho user** — luôn có fallback:

```
Trường hợp 1: RAG pipeline lỗi hoàn toàn
┌──────────────────────────────────────────────┐
│ rag_service.query() → Exception!             │
│                                              │
│ Fallback: gọi Gemini trực tiếp (không RAG)   │
│ → Trả lời chung chung nhưng vẫn trả lời     │
└──────────────────────────────────────────────┘

Trường hợp 2: Qdrant chết
┌──────────────────────────────────────────────┐
│ vector_store.search() → Exception!           │
│                                              │
│ search_results = [] (empty)                  │
│ → Vẫn có stats_summary + smart query         │
│ → Gemini trả lời dựa trên dữ liệu còn lại  │
└──────────────────────────────────────────────┘

Trường hợp 3: MongoDB chết
┌──────────────────────────────────────────────┐
│ get_recent_context() → Exception!            │
│                                              │
│ conversation_history = [] (empty)            │
│ → Mất ngữ cảnh hội thoại nhưng vẫn trả lời │
└──────────────────────────────────────────────┘

Trường hợp 4: Webhook thất bại
┌──────────────────────────────────────────────┐
│ Book Service → Chatbot Service (timeout)     │
│                                              │
│ logger.debug("Chatbot unreachable, skipping")│
│ → Book CRUD vẫn thành công, chỉ miss sync   │
│ → Sửa lại bằng POST /sync-books/ sau        │
└──────────────────────────────────────────────┘

Trường hợp 5: Gemini API lỗi
┌──────────────────────────────────────────────┐
│ gemini_client → 403/timeout/connection error │
│                                              │
│ Return: {"success": false, "error": "..."}   │
│ → HTTP 503 Service Unavailable               │
└──────────────────────────────────────────────┘
```

### Health Check

```
GET /api/chat/health/

{
  "status": "healthy",          // hoặc "degraded"
  "gemini": "configured",       // hoặc "not_configured"
  "rag": {
    "qdrant": "connected",      // hoặc "disconnected"
    "mongodb": "connected",     // hoặc "disconnected"
    "embedding": "loaded"       // hoặc "not_loaded"
  }
}
```

---

## 13. Ví dụ end-to-end

### Scenario: Khách hỏi "Có sách nào về Python không?"

**Bước 1**: Frontend gửi request

```
POST /api/chat/
Header: X-User-Id: 42
Body: {"message": "Có sách nào về Python không?"}
```

**Bước 2**: `views.py` → `chat()` nhận request

```python
message = "Có sách nào về Python không?"
session_id = None  # Chưa có → tạo session mới
session_id = mongo_store.create_session(user_id="42", title="Có sách nào về Pyth")
# → session_id = "507f1f77bcf86cd799439011"
```

**Bước 3**: `rag_service.query()` chạy 7 bước

```
① History: [] (session mới, chưa có lịch sử)

② Smart query: detect_query_intent("Có sách nào về Python không?") → None
   (không match pattern đắt/rẻ/mới/bao nhiêu)

③ Stats: "[Thông tin tổng quan] Tổng: 150 cuốn, Còn hàng: 140..."

④ Semantic search:
   embed_text("Có sách nào về Python không?") → [0.15, -0.32, ...]
   vector_store.search(top_k=5, threshold=0.3)
   → Results:
     1. "Lập Trình Python" (score: 0.92)
     2. "Data Science với Python" (score: 0.85)
     3. "Python cho Người Mới" (score: 0.81)

⑤ Build context:
   "[Lập Trình Python]\nTên sách: Lập Trình Python\nTác giả: Nguyễn Văn A..."

⑥ KB-lite enrichment:
   Top book = "Lập Trình Python" by Nguyễn Văn A
   → Tìm sách cùng tác giả: "Lập Trình Java" by Nguyễn Văn A
   → Tìm sách cùng thể loại CNTT: "Machine Learning Cơ Bản"

⑦ Final prompt: ghép tất cả → gửi Gemini
```

**Bước 4**: Gemini trả lời

```
"Có ạ! Cửa hàng chúng tôi có một số sách về Python:

1. **Lập Trình Python** - Nguyễn Văn A - 150.000 VND (còn hàng)
   Hướng dẫn lập trình Python từ cơ bản đến nâng cao.

2. **Data Science với Python** - Trần Văn B - 200.000 VND (còn hàng)

3. **Python cho Người Mới** - Lê Văn C - 120.000 VND (còn hàng)

Bạn quan tâm cuốn nào, mình tư vấn thêm nhé?"
```

**Bước 5**: Lưu interaction + trả response

```python
rag_service.save_interaction(
    session_id="507f1f77bcf86cd799439011",
    user_message="Có sách nào về Python không?",
    bot_response="Có ạ! Cửa hàng chúng tôi có...",
    sources=[{"title": "Lập Trình Python", "score": 0.92, ...}]
)
```

**Bước 6**: Response về Frontend

```json
{
  "success": true,
  "response": "Có ạ! Cửa hàng chúng tôi có một số sách về Python...",
  "model": "gemini-2.0-flash-lite",
  "sources": [
    {"title": "Lập Trình Python", "score": 0.92, "book_id": "1", "price": "150000"},
    {"title": "Data Science với Python", "score": 0.85, "book_id": "5", "price": "200000"},
    {"title": "Python cho Người Mới", "score": 0.81, "book_id": "12", "price": "120000"}
  ],
  "session_id": "507f1f77bcf86cd799439011"
}
```

**Bước 7**: Khách hỏi tiếp "Cuốn đầu tiên giá bao nhiêu?"

```
→ Gửi kèm session_id
→ Lấy history: [user: "Có sách Python nào?", bot: "Có ạ! ..."]
→ Gemini hiểu "cuốn đầu tiên" = Lập Trình Python
→ Trả lời: "Cuốn Lập Trình Python có giá 150.000 VND ạ."
```
