# RAG Chatbot - Book Data Synchronization

## Tổng quan

Chatbot sử dụng RAG (Retrieval-Augmented Generation) để tìm kiếm và trả lời câu hỏi dựa trên dữ liệu sách. Dữ liệu sách được embed thành vector và lưu trong Qdrant vector database.

Hệ thống hỗ trợ **3 cơ chế** đồng bộ dữ liệu:

| Cơ chế | Mục đích | Khi nào dùng |
|--------|----------|-------------|
| **Webhook realtime** | Cập nhật ngay khi thêm/sửa/xóa sách | Tự động, không cần thao tác |
| **Management command** | Sync toàn bộ catalog | Lần đầu deploy, hoặc re-sync |
| **REST API sync** | Sync qua HTTP request | Admin trigger từ UI/API |

---

## 1. Webhook Realtime (Event-driven)

### Cách hoạt động

```
Book-service (thêm/sửa/xóa sách)
  ↓ POST /api/chat/webhook/book-updated/
Chatbot-service
  ↓ Embed text → Upsert/Delete vector
Qdrant vector DB
```

Khi staff tạo, cập nhật, hoặc xóa sách trong book-service, webhook tự động gọi chatbot-service để cập nhật vector store. Webhook chạy **async** (background thread) nên không ảnh hưởng tốc độ CRUD sách.

### Endpoint

```
POST /api/chat/webhook/book-updated/
Content-Type: application/json
```

### Request Body

**Tạo/Cập nhật sách:**
```json
{
  "action": "created",  // hoặc "updated"
  "book": {
    "id": 1,
    "title": "Lập Trình Python",
    "author": "Nguyễn Văn A",
    "description": "Hướng dẫn lập trình Python từ cơ bản...",
    "price": "150000",
    "stock": 50,
    "category_name": "Công nghệ thông tin",
    "publisher": "NXB Giáo Dục",
    "isbn": "978-604-xxx"
  }
}
```

**Xóa sách:**
```json
{
  "action": "deleted",
  "book_id": 1
}
```

### Response

```json
// Thành công
{"success": true, "book_id": "1", "point_ids": ["uuid..."]}

// Lỗi
{"success": false, "error": "'action' is required"}
```

### Các action hỗ trợ

| Action | Hành vi |
|--------|---------|
| `created` | Embed sách mới → thêm vector vào Qdrant |
| `updated` | Xóa vector cũ → embed lại → thêm vector mới |
| `deleted` | Xóa vector của sách khỏi Qdrant |

### Tích hợp phía Book-service

File: `services/book-service/app/webhook.py`

Webhook được gọi tự động từ `BookViewSet`:
- `perform_create()` → `notify_book_created(book_data)`
- `perform_update()` → `notify_book_updated(book_data)`
- `perform_destroy()` → `notify_book_deleted(book_id)`

**Đặc điểm:**
- Chạy trong **background thread** (daemon) — không block API response
- Timeout 5 giây — nếu chatbot-service không phản hồi, skip
- Nếu chatbot-service down → log warning, không ảnh hưởng book CRUD
- Cần biến môi trường `CHATBOT_SERVICE_URL` trong book-service

---

## 2. Management Command (Full Sync)

### Cách sử dụng

```bash
# Sync lần đầu (chỉ sync nếu vector store trống)
python manage.py sync_books

# Force re-sync toàn bộ (xóa hết vector cũ, embed lại)
python manage.py sync_books --force
```

### Khi nào dùng

- **Lần đầu deploy** hệ thống — vector store chưa có dữ liệu
- **Sau khi restore database** — dữ liệu sách thay đổi nhiều
- **Debug/fix** — vector store bị lỗi hoặc mất sync

### Cách hoạt động

1. Gọi `GET /api/books/?page_size=1000` đến book-service
2. Xóa toàn bộ vector `source_id=book_catalog` trong Qdrant
3. Build text representation cho mỗi sách (title, author, description, price, category...)
4. Batch embed tất cả text
5. Upsert toàn bộ vector vào Qdrant
6. Lưu sync record vào MongoDB

### Trong Docker

```bash
docker exec -it bookstore_btl-chatbot-service-1 python manage.py sync_books --force
```

---

## 3. REST API Sync

### Endpoint

```
POST /api/chat/sync-books/
```

### Khi nào dùng

- Admin muốn trigger sync từ giao diện quản trị
- Tích hợp vào CI/CD pipeline sau khi deploy

### Response

```json
{
  "success": true,
  "synced": 150,
  "message": "Successfully synced 150 books"
}
```

---

## Kiến trúc dữ liệu

### Mỗi sách được embed thành vector với metadata:

```json
{
  "content": "Tên sách: Lập Trình Python\nTác giả: Nguyễn Văn A\nMô tả: ...\nGiá: 150000 VND\nThể loại: CNTT\nTình trạng: Còn hàng",
  "source_id": "book_catalog",
  "source_type": "book",
  "source_title": "Lập Trình Python",
  "book_id": "1",
  "author": "Nguyễn Văn A",
  "price": "150000",
  "category": "Công nghệ thông tin"
}
```

### Text representation format

Mỗi sách được chuyển thành text dạng:
```
Tên sách: {title}
Tác giả: {author}
Mô tả: {description}
Giá: {price} VND
Thể loại: {category}
Nhà xuất bản: {publisher}
ISBN: {isbn}
Tình trạng: Còn hàng / Hết hàng
```

Text này được embed bằng model `dangvantuan/vietnamese-document-embedding` (768 chiều), tối ưu cho tiếng Việt.

---

## Cấu hình môi trường

### Chatbot-service (docker-compose.yml)

```yaml
chatbot-service:
  environment:
    QDRANT_HOST: qdrant
    QDRANT_PORT: "6333"
    MONGODB_URL: mongodb://mongo:mongo@mongodb:27017/chatbot_db?authSource=admin
    BOOK_SERVICE_URL: http://book-service:8000
    EMBEDDING_MODEL: dangvantuan/vietnamese-document-embedding
    RAG_TOP_K: "5"
    RAG_SIMILARITY_THRESHOLD: "0.3"
```

### Book-service (docker-compose.yml)

```yaml
book-service:
  environment:
    CHATBOT_SERVICE_URL: http://chatbot-service:8000  # Webhook target
```

---

## Quy trình deploy

### Lần đầu

```bash
# 1. Start tất cả services
docker-compose up -d

# 2. Đợi services khởi động xong
docker-compose logs -f chatbot-service  # Chờ "Starting development server"

# 3. Sync toàn bộ sách vào vector store
docker exec -it bookstore_btl-chatbot-service-1 python manage.py sync_books

# 4. Verify
curl http://localhost:8013/api/chat/rag-stats/
```

### Các lần sau

Không cần thao tác thủ công. Webhook tự động cập nhật khi:
- Staff thêm sách mới → `POST /api/books/`
- Staff sửa sách → `PUT/PATCH /api/books/{id}/`
- Staff xóa sách → `DELETE /api/books/{id}/`

---

## Monitoring

### Kiểm tra trạng thái RAG

```bash
# Health check
curl http://localhost:8013/api/chat/health/

# RAG statistics
curl http://localhost:8013/api/chat/rag-stats/
```

### Response mẫu

```json
{
  "success": true,
  "stats": {
    "vector_store": {
      "name": "bookstore_knowledge",
      "points_count": 150,
      "status": "green"
    },
    "documents": 5,
    "embedding_model": "dangvantuan/vietnamese-document-embedding"
  }
}
```

### Troubleshooting

| Vấn đề | Nguyên nhân | Giải pháp |
|---------|-------------|-----------|
| `points_count = 0` | Chưa sync sách | Chạy `python manage.py sync_books` |
| Webhook không hoạt động | Chatbot-service down hoặc sai URL | Kiểm tra `CHATBOT_SERVICE_URL` trong book-service |
| Sách mới không tìm thấy | Webhook thất bại | Kiểm tra log chatbot-service, re-sync nếu cần |
| Embedding model chưa load | Lần đầu khởi động | Đợi model download (~1GB), hoặc build Docker image có pre-download |

---

## Cấu trúc file liên quan

```
services/
├── book-service/
│   └── app/
│       ├── views.py          # BookViewSet với webhook hooks
│       └── webhook.py         # Webhook client (async, non-blocking)
│
├── chatbot-service/
│   ├── chat/
│   │   ├── views.py          # webhook_book_updated endpoint
│   │   ├── urls.py           # /webhook/book-updated/ route
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── sync_books.py  # Management command
│   │   └── rag/
│   │       ├── document_processor.py  # upsert_single_book, delete_single_book
│   │       └── vector_store.py        # delete_by_book_id
│   └── Dockerfile            # Pre-downloads embedding model
│
└── docker-compose.yml        # CHATBOT_SERVICE_URL in book-service env
```
