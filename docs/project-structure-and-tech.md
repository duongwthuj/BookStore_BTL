# Tài liệu cấu trúc project và công nghệ sử dụng

## 1. Mục tiêu tài liệu

Tài liệu này giúp bạn đọc nhanh và đúng codebase hiện tại của project `BookStore_BTL`.

Tài liệu tập trung vào 4 câu hỏi:
1. Repo này được tổ chức như thế nào?
2. Mỗi service chịu trách nhiệm gì?
3. Project đang dùng những công nghệ nào?
4. Những cú pháp và pattern quan trọng trong code nên hiểu theo cách nào?

> Nguồn sự thật ưu tiên trong tài liệu này là code hiện tại và `docker-compose.yml`, không phải mọi mô tả cũ trong README.

---

## 2. Tổng quan kiến trúc hệ thống

Project này là một **hệ thống bán sách theo kiến trúc microservices**.

Luồng tổng quát:

```text
Frontend (React)
    -> API Gateway (Django)
        -> Auth / Customer / Staff / Manager
        -> Catalog / Book
        -> Cart / Order / Pay / Ship
        -> Comment-Rate / Recommender
        -> Chatbot Service
```

### Thành phần chính
- **Frontend**: giao diện người dùng viết bằng React.
- **API Gateway**: cổng vào chung cho frontend, chịu trách nhiệm route request đến đúng service backend.
- **Các microservice Django REST**: mỗi domain nghiệp vụ có service riêng.
- **Phần lớn domain service dùng PostgreSQL riêng**: tách dữ liệu theo domain; riêng `chatbot-service` dùng MongoDB và Qdrant, còn `api-gateway` là stateless.
- **Chatbot/RAG**: dùng để hỏi đáp, tìm sách, lưu session/document metadata và truy xuất tri thức từ vector store.
- **Recommender**: nhận interaction signal và sinh gợi ý sách tương tự, phổ biến, cá nhân hóa.

> Trong tài liệu này, các ví dụ endpoint mặc định được hiểu là endpoint đi qua **API Gateway** (`/api/...`), trừ khi có ghi chú rõ là endpoint nội bộ của từng service.

### Source tham chiếu
- `README.md`
- `docker-compose.yml`

---

## 3. Cấu trúc thư mục repo

```text
BookStore_BTL/
├── frontend/                 # Ứng dụng React
├── services/                 # Toàn bộ backend microservices
│   ├── api-gateway/
│   ├── auth-service/
│   ├── customer-service/
│   ├── staff-service/
│   ├── manager-service/
│   ├── catalog-service/
│   ├── book-service/
│   ├── cart-service/
│   ├── order-service/
│   ├── pay-service/
│   ├── ship-service/
│   ├── comment-rate-service/
│   ├── recommender-service/
│   └── chatbot-service/
├── docs/                     # Tài liệu chuyên sâu
├── scripts/                  # Script hỗ trợ test/seed/init
├── docker-compose.yml        # Sơ đồ runtime toàn hệ thống
└── .env / .env.example       # Biến môi trường
```

### Ý nghĩa từng khu vực

#### `frontend/`
Chứa toàn bộ client app React.

Những file quan trọng:
- `frontend/package.json`: khai báo dependency frontend.
- `frontend/src/App.js`: định nghĩa route và layout chính.
- `frontend/src/services/api.js`: Axios instance dùng chung cho toàn app.
- `frontend/src/contexts/AuthContext.js`: quản lý trạng thái đăng nhập.

#### `services/`
Chứa toàn bộ backend microservices. Mỗi service gần như là một Django project độc lập.

Mỗi service thường có các thành phần:
- `manage.py`: entrypoint của Django.
- `<project_name>/settings.py`: cấu hình Django.
- `app/models.py`: model dữ liệu.
- `app/serializers.py`: chuyển đổi model <-> JSON.
- `app/views.py`: xử lý logic API.
- `app/urls.py`: định nghĩa endpoint.
- `requirements.txt`: dependency Python của service đó.
- `Dockerfile`: cách build service trong Docker.

#### `docs/`
Chứa tài liệu bổ sung.

Hiện tại đã có:
- `docs/rag-chatbot-sync.md`: tài liệu về cơ chế đồng bộ dữ liệu sách sang chatbot/RAG.

#### `scripts/`
Script hỗ trợ vận hành:
- seed dữ liệu
- chạy test
- khởi tạo môi trường AI cũ/phụ trợ

#### `docker-compose.yml`
Đây là file cực kỳ quan trọng để hiểu hệ thống chạy thực tế ra sao:
- service nào tồn tại
- service nào gọi service nào
- port mapping
- database nào thuộc về service nào
- hạ tầng như MongoDB, Qdrant

---

## 4. Bản đồ service và trách nhiệm

Dựa trên `docker-compose.yml`, hệ thống hiện có các service sau:

| Service | Host Port | Vai trò chính |
|---|---:|---|
| api-gateway | 8000 | Cổng vào chung, route request, truyền thông tin auth |
| auth-service | 8001 | Đăng ký, đăng nhập, refresh JWT, lấy thông tin user |
| customer-service | 8002 | Quản lý khách hàng |
| staff-service | 8003 | Quản lý nhân viên |
| manager-service | 8004 | Chức năng quản trị/manager |
| catalog-service | 8005 | Danh mục, collection |
| book-service | 8006 | Quản lý sách, tìm kiếm sách, tồn kho |
| cart-service | 8007 | Giỏ hàng |
| order-service | 8008 | Đơn hàng |
| pay-service | 8009 | Thanh toán MoMo, COD |
| ship-service | 8010 | Vận chuyển |
| comment-rate-service | 8011 | Đánh giá, nhận xét |
| recommender-service | 8012 | Gợi ý sách |
| chatbot-service | 8013 | Chatbot + RAG |
| frontend | 3000 | Giao diện web |
| qdrant | 6333 | Vector database cho RAG |
| mongodb | 27017 | Lưu dữ liệu chatbot/sync |

### Nhóm theo domain

#### Nhóm định danh và quyền
- `auth-service`
- `customer-service`
- `staff-service`
- `manager-service`

#### Nhóm catalog và sách
- `catalog-service`
- `book-service`

#### Nhóm thương mại
- `cart-service`
- `order-service`
- `pay-service`
- `ship-service`

#### Nhóm tương tác và AI
- `comment-rate-service`
- `recommender-service`
- `chatbot-service`

### Luồng gọi service

Luồng phổ biến nhất là:

```text
Trình duyệt
  -> frontend
  -> /api/... tại api-gateway
  -> downstream service tương ứng
```

Ví dụ:
- frontend gọi `http://localhost:8000/api/books/`
- API Gateway forward request sang `book-service`
- `book-service` trả dữ liệu JSON
- API Gateway trả ngược lại cho frontend

---

## 5. Vì sao repo chia theo microservice?

Ở repo này, mỗi domain nghiệp vụ được tách thành service riêng để:
- dễ triển khai độc lập
- dễ tách trách nhiệm
- tránh dồn mọi logic vào một backend lớn
- dễ scale hoặc thay đổi từng phần

Ví dụ:
- logic thanh toán nằm ở `pay-service`
- logic gợi ý nằm ở `recommender-service`
- logic chatbot nằm ở `chatbot-service`
- logic sách nằm ở `book-service`

Điểm quan trọng là **phần lớn domain service có database riêng**. Điều này thể hiện rất rõ trong `docker-compose.yml`:
- `auth-db`
- `customer-db`
- `book-db`
- `order-db`
- `recommender-db`
- ...

Tuy nhiên có ngoại lệ quan trọng:
- `chatbot-service` dùng **MongoDB + Qdrant** thay vì PostgreSQL
- `api-gateway` không sở hữu database riêng

Vì vậy, có thể xem đây là pattern **database-per-service** theo nghĩa rộng, nhưng công nghệ lưu trữ được chọn theo nhu cầu từng service.

---

## 6. Frontend được tổ chức như thế nào?

### 6.1. Stack frontend

Dựa trên `frontend/package.json`, frontend dùng:
- **React 18**
- **react-router-dom** để routing
- **axios** để gọi API
- **react-scripts** để build/run theo kiểu Create React App
- **Tailwind CSS** để styling
- **PostCSS + Autoprefixer** để xử lý CSS

### 6.2. Cấu trúc thư mục frontend

Các khu vực quan trọng trong `frontend/src/`:
- `pages/`: các màn hình cấp route
- `components/`: UI component tái sử dụng
- `contexts/`: state dùng chung toàn app
- `services/`: lớp gọi API

### 6.3. File nên đọc đầu tiên: `frontend/src/App.js`

File này cho bạn cái nhìn nhanh nhất về frontend đang có gì.

Vai trò của file:
- import các page/component chính
- thiết lập `Router`
- bọc app bằng `AuthProvider` và `CartProvider`
- chia route customer và route admin/manager

### 6.4. Cú pháp React tiêu biểu trong `App.js`

Ví dụ:

```jsx
<AuthProvider>
  <CartProvider>
    <Router>
      <AppRoutes />
    </Router>
  </CartProvider>
</AuthProvider>
```

#### Giải thích cú pháp
- `<AuthProvider>...</AuthProvider>`: component provider bọc cây component con để chia sẻ state qua Context API.
- `<CartProvider>`: provider cho giỏ hàng.
- `<Router>`: bật cơ chế client-side routing.
- `<AppRoutes />`: component tự định nghĩa, dùng để render route tương ứng.

Đây là pattern **provider composition**: bọc nhiều provider ở root để mọi page bên dưới đều truy cập được state chung.

### 6.5. React Router trong project này

Ví dụ trong `frontend/src/App.js`:

```jsx
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/books" element={<Books />} />
  <Route path="/books/:id" element={<BookDetail />} />
</Routes>
```

#### Giải thích cú pháp
- `<Routes>`: chứa danh sách route.
- `<Route ... />`: định nghĩa một route.
- `path="/books/:id"`: route động, `:id` là tham số URL.
- `element={<BookDetail />}`: component sẽ render khi URL khớp route đó.

### 6.6. JSX là gì?

JSX là cú pháp trông giống HTML nhưng thực chất là JavaScript mở rộng để mô tả UI.

Ví dụ:

```jsx
<div className="min-h-screen flex flex-col bg-gray-50">
  <Navbar />
  <main className="flex-grow">{children}</main>
  <Footer />
</div>
```

Giải thích:
- `className` thay cho `class` vì đây là JSX.
- `<Navbar />`, `<Footer />`: component tùy biến.
- `{children}`: chèn biến JavaScript vào trong JSX.
- class Tailwind như `min-h-screen`, `flex`, `bg-gray-50` là utility classes.

### 6.7. Context API trong `frontend/src/contexts/AuthContext.js`

File `AuthContext.js` là ví dụ rất rõ về cách app quản lý trạng thái xác thực.

Ví dụ cú pháp:

```jsx
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

#### Giải thích
- `createContext(null)`: tạo context dùng chung.
- `useContext(AuthContext)`: lấy dữ liệu từ context.
- custom hook `useAuth()`: giúp component khác gọi ngắn hơn và an toàn hơn.
- `throw new Error(...)`: đảm bảo hook chỉ được dùng khi đang nằm trong provider.

Ví dụ state trong provider:

```jsx
const [user, setUser] = useState(null);
const [loading, setLoading] = useState(true);
```

- `useState(null)`: tạo state `user`, mặc định chưa đăng nhập.
- `setUser(...)`: hàm cập nhật state.
- `useEffect(...)`: chạy side effect như đọc token từ `localStorage` khi app mount.

### 6.8. Lớp gọi API dùng Axios trong `frontend/src/services/api.js`

File `api.js` tạo một Axios instance dùng chung:

```js
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

#### Giải thích
- `axios.create(...)`: tạo client riêng thay vì gọi `axios.get/post` trực tiếp khắp nơi.
- `baseURL`: tiền tố chung cho mọi API call.
- `headers`: header mặc định.

### 6.9. Axios interceptor là gì?

Project này dùng interceptor cho 2 việc:
1. tự gắn access token vào request
2. tự refresh token khi gặp lỗi 401

Ví dụ request interceptor:

```js
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

Giải thích:
- `interceptors.request.use(...)`: bắt mọi request trước khi gửi.
- `config`: cấu hình request hiện tại.
- `Authorization = Bearer ...`: chuẩn JWT Bearer token.

Ví dụ response interceptor:

```js
if (error.response?.status === 401 && !originalRequest._retry) {
  originalRequest._retry = true;
  ...
}
```

Giải thích:
- `error.response?.status`: optional chaining, tránh crash nếu `response` không tồn tại.
- `=== 401`: backend báo token hết hạn hoặc không hợp lệ.
- `_retry`: cờ để tránh vòng lặp refresh vô hạn.

### 6.10. Tailwind CSS trong project này

Frontend dùng Tailwind nên style thường xuất hiện ngay trong JSX:

```jsx
<div className="min-h-screen flex flex-col bg-gray-50">
```

Ý nghĩa:
- `min-h-screen`: chiều cao tối thiểu bằng chiều cao màn hình.
- `flex`: bật flexbox.
- `flex-col`: flex theo cột.
- `bg-gray-50`: nền xám nhạt.

Ưu điểm của cách này:
- không cần viết quá nhiều CSS riêng
- nhìn UI structure ngay trong component
- nhất quán cho app nhỏ đến vừa

---

## 7. Backend được tổ chức như thế nào?

### 7.1. Stack backend

Phần lớn backend service dùng:
- **Django 4.2**
- **Django REST Framework**
- **gunicorn**
- **psycopg2-binary** để kết nối PostgreSQL
- `dj-database-url` ở một số service
- `django-filter` ở service cần filter API

### 7.2. Vì sao mỗi service lại có `manage.py` riêng?

Vì mỗi service là một Django project độc lập.

Ví dụ:
- `services/book-service/manage.py`
- `services/auth-service/manage.py`
- `services/api-gateway/manage.py`

Điều này có nghĩa là mỗi service có thể:
- migrate riêng
- chạy riêng
- test riêng
- build Docker riêng

### 7.3. Cấu trúc Django REST điển hình

Lấy `book-service` làm ví dụ:
- `services/book-service/app/models.py`
- `services/book-service/app/serializers.py`
- `services/book-service/app/views.py`
- `services/book-service/app/urls.py`
- `services/book-service/app/filters.py`

#### Vai trò từng file
- `models.py`: định nghĩa bảng dữ liệu.
- `serializers.py`: chuyển model thành JSON và validate input từ API.
- `views.py`: xử lý request/response.
- `urls.py`: ánh xạ URL -> view.
- `filters.py`: định nghĩa logic lọc dữ liệu cho endpoint list.

---

## 8. Cú pháp Django REST quan trọng trong project

### 8.1. `ModelViewSet` trong `services/book-service/app/views.py`

Ví dụ:

```python
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    filterset_class = BookFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
```

#### Giải thích cú pháp
- `class BookViewSet(...)`: khai báo class-based view.
- `viewsets.ModelViewSet`: DRF cung cấp sẵn CRUD chuẩn.
- `queryset = Book.objects.all()`: tập dữ liệu mặc định cho view.
- `filterset_class = BookFilter`: dùng class filter riêng.
- `filter_backends = [...]`: bật filter/search/order.

Vì dùng `ModelViewSet`, service có sẵn các action chuẩn như:
- `list`
- `create`
- `retrieve`
- `update`
- `partial_update`
- `destroy`

### 8.2. Tách serializer theo action

Ví dụ:

```python
def get_serializer_class(self):
    if self.action == 'list':
        return BookListSerializer
    return BookSerializer
```

Ý nghĩa:
- khi `list`, dùng serializer gọn hơn
- khi xem chi tiết hoặc tạo/sửa, dùng serializer đầy đủ hơn

Đây là pattern hay trong DRF để:
- giảm payload cho list API
- vẫn giữ dữ liệu chi tiết cho detail API

### 8.3. Custom action với `@action`

Ví dụ:

```python
@action(detail=True, methods=['put'], url_path='stock')
def update_stock(self, request, pk=None):
```

Giải thích:
- `@action(...)`: thêm endpoint tùy biến vào ViewSet.
- `detail=True`: action này áp dụng cho một object cụ thể.
- `methods=['put']`: chỉ cho phép HTTP PUT.
- `url_path='stock'`: tạo route kiểu `/books/{id}/stock/`.

### 8.4. `APIView` cho endpoint tùy biến

Ví dụ:

```python
class BookSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
```

Giải thích:
- `APIView`: dùng khi endpoint không phù hợp với CRUD chuẩn.
- `request.query_params.get('q', '')`: lấy query string `?q=...`.
- `.strip()`: bỏ khoảng trắng đầu/cuối.

`APIView` phù hợp với các endpoint như:
- search
- thống kê
- workflow đặc thù
- endpoint tổng hợp nhiều nguồn

### 8.5. `Response(...)` trong DRF

Ví dụ:

```python
return Response(serializer.data)
```

Hoặc:

```python
return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

Giải thích:
- `Response` là object response của DRF.
- `serializer.data`: dữ liệu đã serialize thành JSON-friendly structure.
- `status.HTTP_400_BAD_REQUEST`: hằng số dễ đọc hơn việc hardcode `400`.

### 8.6. Filter/search/order backend

Ví dụ:

```python
filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
search_fields = ['title', 'author', 'description']
ordering_fields = ['title', 'price', 'created_at']
```

Ý nghĩa:
- `DjangoFilterBackend`: filter theo field có cấu hình.
- `SearchFilter`: search text đơn giản.
- `OrderingFilter`: sort dữ liệu.
- `search_fields`: các field được phép search.
- `ordering_fields`: các field được phép order.

Đây là cách project chuẩn hóa API list thay vì viết tay từng điều kiện lọc.

---

## 9. API Gateway hoạt động như thế nào?

File nên đọc: `services/api-gateway/app/proxy.py`

Gateway ở project này không phải nơi chứa toàn bộ business logic. Nó chủ yếu làm nhiệm vụ:
- nhận request từ frontend
- xác định service đích
- forward request sang service đó
- chuyển response ngược lại
- thêm header thông tin người dùng nếu đã xác thực

### 9.1. Proxy pattern

Ví dụ:

```python
service_url, prefix = get_service_for_path(request.path)
target_url = f"{service_url}{target_path}"
```

Giải thích:
- `get_service_for_path(...)`: quyết định path hiện tại thuộc service nào.
- `target_url`: URL thật của downstream service.

Sau đó gateway dùng `httpx` để gọi sang service đích:

```python
async with httpx.AsyncClient(timeout=self.timeout) as client:
    response = await client.request(
        method=request.method,
        url=target_url,
        headers=headers,
        content=body,
    )
```

Giải thích:
- `httpx.AsyncClient(...)`: HTTP client async.
- `await client.request(...)`: gửi request bất đồng bộ.
- `method=request.method`: giữ nguyên method gốc như GET/POST/PUT.
- `headers=headers`: forward header cần thiết.
- `content=body`: forward body gốc.

### 9.2. Header forwarding

Gateway giữ lại một số header quan trọng và bổ sung thông tin auth:
- `Authorization`
- `X-User-Id`
- `X-User-Role`
- `X-User-Email`
- `x-forwarded-for`

Ý nghĩa:
- downstream service không cần lặp lại toàn bộ logic xác thực như ở cổng vào
- gateway có thể truyền thông tin user đã xác thực cho service bên dưới
- business service có thể tập trung vào nghiệp vụ thay vì đứng trực tiếp trước frontend

### 9.3. Phân biệt URL public và URL nội bộ

Có 2 kiểu URL cần phân biệt:

1. **URL public**: frontend gọi qua gateway, ví dụ `http://localhost:8000/api/books/`
2. **URL nội bộ**: service gọi nhau trong Docker network, ví dụ `http://book-service:8000`

Điều này quan trọng vì cùng một chức năng có thể được nhìn từ 2 lớp khác nhau:
- người dùng/frontend thấy endpoint dạng `/api/...` qua gateway
- service nội bộ thấy endpoint trên hostname container như `book-service`, `order-service`, `chatbot-service`

### 9.4. Xử lý lỗi gateway

Trong `proxy.py` có xử lý riêng cho:
- timeout -> `504`
- không kết nối được service -> `503`
- lỗi khác -> `500`

Đây là một pattern đúng vì gateway là chỗ dễ phát sinh lỗi liên service nhất.


---

## 10. Pattern giao tiếp giữa các service

Project này không chỉ có request-response trực tiếp. Nó còn có kiểu đồng bộ gần real-time bằng webhook.

### 10.1. Webhook trong `services/book-service/app/webhook.py`

File này dùng để báo cho `chatbot-service` biết khi dữ liệu sách thay đổi.

Ví dụ:

```python
thread = threading.Thread(target=_do_send, daemon=True)
thread.start()
```

Giải thích:
- `threading.Thread(...)`: tạo luồng nền.
- `target=_do_send`: hàm sẽ được chạy trong thread.
- `daemon=True`: thread nền, không chặn process chính thoát.
- `thread.start()`: bắt đầu chạy.

### 10.2. Vì sao dùng background thread?

Vì khi staff tạo/sửa/xóa sách, API CRUD sách không nên bị block bởi chatbot.

Nghĩa là:
- nếu chatbot đang chậm hoặc down
- book-service vẫn trả response CRUD bình thường
- phần sync sang chatbot chỉ là best-effort, không phá flow chính

### 10.3. Webhook payload

`book-service` gửi action:
- `created`
- `updated`
- `deleted`

Điều này khớp với tài liệu trong `docs/rag-chatbot-sync.md`.

---

## 11. Chatbot/RAG đang dùng công nghệ gì?

### 11.1. Source of truth hiện tại

Để hiểu chatbot hiện tại, nên dựa vào:
- `services/chatbot-service/requirements.txt`
- `services/chatbot-service/chat/gemini_client.py`
- `docker-compose.yml`
- `docs/rag-chatbot-sync.md`

### 11.2. Stack hiện tại của chatbot

Từ code và compose hiện tại, chatbot đang dùng:
- **Gemini API** để sinh câu trả lời
- **sentence-transformers** để tạo embedding
- **torch** làm backend ML
- **Qdrant** để lưu vector
- **MongoDB** để lưu dữ liệu chat, session, sync record và document metadata
- **markitdown** và `langchain-text-splitters` cho xử lý dữ liệu RAG

### 11.3. Chatbot-service thực sự sở hữu những gì?

Dựa trên `services/chatbot-service/chat/urls.py`, service này không chỉ có endpoint chat đơn giản mà còn sở hữu các nhóm chức năng sau:
- chat và hỗ trợ tìm sách / tra đơn hàng
- quản lý session và lịch sử chat
- quản lý tài liệu knowledge base
- sync dữ liệu sách vào RAG store
- nhận webhook từ `book-service`
- thống kê RAG và health check

Nói ngắn gọn:
- `book-service` **không** sở hữu RAG index
- `book-service` chỉ phát tín hiệu thay đổi dữ liệu sách qua webhook
- `chatbot-service` mới là nơi sở hữu logic ingest, embedding, vector store và truy vấn RAG

### 11.4. Cú pháp trong `gemini_client.py`

Ví dụ:

```python
self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
```

Đây là **f-string** của Python:
- chuỗi có thể chèn biến trực tiếp bằng `{...}`
- `self.model` sẽ được nội suy vào URL

Ví dụ gọi API:

```python
response = requests.post(
    f"{self.api_url}?key={self.api_key}",
    json=payload,
    timeout=30
)
```

Giải thích:
- `requests.post(...)`: gửi HTTP POST.
- `json=payload`: tự serialize dict Python thành JSON.
- `timeout=30`: tránh treo request quá lâu.

### 11.5. Lưu ý quan trọng về tài liệu cũ

`README.md` hiện còn nhắc **Ollama** cho chatbot.

Tuy nhiên, implementation hiện tại cho thấy runtime đang nghiêng rõ về:
- Gemini
- Qdrant
- MongoDB
- Vietnamese embedding model

Vì vậy, khi đọc project này, hãy coi:
- `docker-compose.yml`
- `requirements.txt`
- `gemini_client.py`

là nguồn chính xác hơn cho stack chatbot hiện tại.

---

## 12. Recommender service dùng để làm gì?

Tài liệu chi tiết đã có ở:
- `services/recommender-service/RECOMMENDER_SYSTEM_DOCUMENTATION.md`

Ở mức tổng quan, service này chịu trách nhiệm:
- gợi ý sách tương tự
- gợi ý cá nhân hóa theo user
- gợi ý sách phổ biến
- gợi ý sách xu hướng
- nhận và lưu interaction signal qua endpoint `/interactions/`

Trong kiến trúc tổng thể:
- `comment-rate-service`, `cart-service`, `order-service` gửi tín hiệu tương tác sang `recommender-service`
- `recommender-service` mới là nơi sở hữu logic recommendation và tính toán similarity
- `book-service` chỉ cung cấp dữ liệu sách để recommender tham chiếu khi cần

Đây là một service AI/logic riêng, không trộn trực tiếp vào `book-service` hay các service giao dịch.

Ví dụ trong `services/recommender-service/app/urls.py` có các endpoint:
- `recommend/book/<int:book_id>/`
- `recommend/user/<int:customer_id>/`
- `recommend/popular/`
- `recommend/trending/`
- `interactions/`
- `similarity/compute/`

Cách tổ chức này cho thấy recommender là một bounded context riêng: nơi khác chỉ phát sự kiện/tương tác, còn việc xếp hạng và gợi ý được gom về một service chuyên trách.

---

## 13. Công nghệ sử dụng trong toàn project

| Nhóm | Công nghệ | Dùng để làm gì |
|---|---|---|
| Frontend | React 18 | Xây dựng SPA |
| Frontend | React Router | Điều hướng client-side |
| Frontend | Axios | Gọi API và xử lý interceptor |
| Frontend | Tailwind CSS | Utility-first styling |
| Frontend | PostCSS, Autoprefixer | Xử lý CSS |
| Backend | Django | Framework backend chính |
| Backend | Django REST Framework | Xây API REST |
| Backend | django-filter | Filter dữ liệu cho API list |
| Backend | httpx | Proxy/gọi HTTP giữa services |
| Backend | requests | Gọi HTTP ở các service đồng bộ/webhook |
| Data | PostgreSQL | Database chính cho phần nghiệp vụ |
| Data | MongoDB | Lưu dữ liệu chatbot và sync |
| AI/RAG | Qdrant | Vector database |
| AI/RAG | sentence-transformers | Tạo embedding |
| AI/RAG | torch | Chạy model embedding |
| AI/RAG | Gemini API | Sinh phản hồi chatbot |
| AI/RAG | markitdown | Chuyển đổi nội dung tài liệu phục vụ RAG |
| AI/RAG | langchain-text-splitters | Chia chunk văn bản |
| Infra | Docker | Container hóa |
| Infra | Docker Compose | Chạy toàn bộ hệ thống nhiều service |
| Auth | JWT | Xác thực giữa frontend và backend |
| Payment | MoMo Sandbox | Thanh toán điện tử |

---

## 14. Thứ tự nên đọc code nếu bạn mới vào project

### Nếu bạn muốn hiểu toàn hệ thống
1. `README.md`
2. `docker-compose.yml`
3. `frontend/src/App.js`
4. `services/api-gateway/app/proxy.py`
5. `services/book-service/app/views.py`
6. `docs/rag-chatbot-sync.md`
7. `services/recommender-service/RECOMMENDER_SYSTEM_DOCUMENTATION.md`

### Nếu bạn muốn hiểu frontend trước
1. `frontend/package.json`
2. `frontend/src/App.js`
3. `frontend/src/contexts/AuthContext.js`
4. `frontend/src/services/api.js`
5. `frontend/src/pages/`
6. `frontend/src/components/`

### Nếu bạn muốn hiểu backend trước
1. `docker-compose.yml`
2. `services/api-gateway/app/proxy.py`
3. một service đại diện như `services/book-service/app/views.py`
4. `services/book-service/app/urls.py`
5. `services/book-service/app/serializers.py`
6. `services/book-service/app/models.py`

---

## 15. Kết luận ngắn

Project này không phải monolith mà là một hệ thống microservices khá rõ ràng:
- frontend React ở riêng một khối
- backend chia theo domain
- gateway đứng giữa để điều phối request
- AI được tách thành chatbot service và recommender service
- dữ liệu được tách theo từng service

Nếu cần hiểu nhanh repo này, hãy nhớ 3 ý chính:
1. **`docker-compose.yml` là bản đồ runtime thật của hệ thống**.
2. **`frontend/src/App.js` là điểm vào tốt nhất để hiểu frontend**.
3. **mỗi thư mục trong `services/` gần như là một backend độc lập theo chuẩn Django REST**.

---

## 16. Tài liệu liên quan

- `docs/rag-chatbot-sync.md`
- `services/recommender-service/RECOMMENDER_SYSTEM_DOCUMENTATION.md`
