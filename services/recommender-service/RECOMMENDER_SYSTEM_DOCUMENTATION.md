# Book Recommender System - Documentation

## Table of Contents
1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Các thuật toán Recommendation](#3-các-thuật-toán-recommendation)
4. [Data Models](#4-data-models)
5. [API Endpoints](#5-api-endpoints)
6. [Tích hợp với các Services khác](#6-tích-hợp-với-các-services-khác)
7. [Ví dụ thực tế](#7-ví-dụ-thực-tế)

---

## 1. Tổng quan hệ thống

### 1.1. Mục đích
Book Recommender System được xây dựng để:
- **Cá nhân hóa trải nghiệm người dùng**: Gợi ý sách phù hợp với sở thích từng người
- **Tăng doanh số**: Cross-selling và up-selling thông qua gợi ý thông minh
- **Giải quyết information overload**: Giúp user tìm sách trong hàng nghìn đầu sách

### 1.2. Các loại Recommendation

| Loại | Use Case | Hiển thị ở đâu |
|------|----------|----------------|
| **Similar Books** | Sách tương tự với sách đang xem | Trang chi tiết sách |
| **Personalized** | Gợi ý riêng cho từng user | Trang chủ, "Dành cho bạn" |
| **Popular** | Sách được mua/xem nhiều nhất | Trang chủ, "Bán chạy" |
| **Trending** | Sách đang hot trong 7 ngày | Trang chủ, "Xu hướng" |

### 1.3. Hybrid Approach
Hệ thống sử dụng **Hybrid Recommender** - kết hợp nhiều phương pháp:

```
                    ┌─────────────────┐
                    │  User Request   │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │Collaborative│   │Content-Based│   │ Popularity  │
   │  Filtering  │   │  Filtering  │   │    Based    │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
                   ┌─────────────────┐
                   │  Hybrid Engine  │
                   │ (Merge + Rank)  │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Recommendations │
                   └─────────────────┘
```

**Tại sao dùng Hybrid?**
- Collaborative Filtering: Mạnh khi có nhiều data, yếu với new items (cold start)
- Content-Based: Giải quyết cold start, nhưng thiếu serendipity
- Popularity: Fallback khi không có đủ data về user
- **Hybrid = Kết hợp ưu điểm, khắc phục nhược điểm của từng phương pháp**

---

## 2. Kiến trúc hệ thống

### 2.1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MICROSERVICES ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   Frontend  │     │ API Gateway │     │    User     │                   │
│  │   (React)   │────▶│   (Django)  │────▶│  Actions    │                   │
│  └─────────────┘     └──────┬──────┘     └─────────────┘                   │
│                             │                                               │
│         ┌───────────────────┼───────────────────┐                          │
│         ▼                   ▼                   ▼                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │order-service│     │cart-service │     │comment-rate │                   │
│  │             │     │             │     │  -service   │                   │
│  │ (purchase)  │     │  (cart)     │     │   (rate)    │                   │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                   │
│         │                   │                   │                          │
│         │     POST /interactions/               │                          │
│         └───────────────────┼───────────────────┘                          │
│                             ▼                                               │
│                ┌────────────────────────┐                                   │
│                │   RECOMMENDER SERVICE  │                                   │
│                │                        │                                   │
│                │  ┌──────────────────┐  │                                   │
│                │  │ UserInteraction  │  │     ┌─────────────┐              │
│                │  │      Table       │◀─┼─────│book-service │              │
│                │  └────────┬─────────┘  │     │(book details)│              │
│                │           │            │     └─────────────┘              │
│                │           ▼            │                                   │
│                │  ┌──────────────────┐  │                                   │
│                │  │ RecommenderEngine│  │                                   │
│                │  │                  │  │                                   │
│                │  │ - Collaborative  │  │                                   │
│                │  │ - Content-Based  │  │                                   │
│                │  │ - Popularity     │  │                                   │
│                │  └────────┬─────────┘  │                                   │
│                │           │            │                                   │
│                │           ▼            │                                   │
│                │  ┌──────────────────┐  │                                   │
│                │  │  BookSimilarity  │  │                                   │
│                │  │     Table        │  │                                   │
│                │  └──────────────────┘  │                                   │
│                └────────────────────────┘                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2. Data Flow

```
1. USER ACTION
   User xem sách / thêm giỏ hàng / mua / đánh giá
                    │
                    ▼
2. SERVICE GỬI INTERACTION
   order-service ──────▶ POST /interactions/ { customer_id, book_id, type: "purchase" }
   cart-service  ──────▶ POST /interactions/ { customer_id, book_id, type: "cart" }
   review-service ─────▶ POST /interactions/ { customer_id, book_id, type: "rate", rating: 5 }
                    │
                    ▼
3. LƯU VÀO DATABASE
   UserInteraction table
   ┌────┬─────────────┬─────────┬──────────────────┬────────┐
   │ id │ customer_id │ book_id │ interaction_type │ rating │
   ├────┼─────────────┼─────────┼──────────────────┼────────┤
   │ 1  │     30      │   45    │      view        │  null  │
   │ 2  │     30      │   45    │      cart        │  null  │
   │ 3  │     30      │   45    │    purchase      │  null  │
   │ 4  │     30      │   45    │      rate        │   5    │
   └────┴─────────────┴─────────┴──────────────────┴────────┘
                    │
                    ▼
4. COMPUTE SIMILARITIES (Batch job - chạy định kỳ)
   Tính Jaccard similarity giữa các books
                    │
                    ▼
5. SERVE RECOMMENDATIONS
   GET /recommend/user/30/ ──▶ [Book 48, Book 42, Book 35, ...]
```

---

## 3. Các thuật toán Recommendation

### 3.1. Collaborative Filtering (Jaccard Similarity)

#### Concept
> "Users who bought X also bought Y"

Dựa trên hành vi của users tương tự để gợi ý. Nếu User A và User B đều mua Book 1, 2, 3, và User A còn mua Book 4, thì gợi ý Book 4 cho User B.

#### Jaccard Similarity Formula

```
                    |Users(Book_A) ∩ Users(Book_B)|
Jaccard(A, B) = ─────────────────────────────────────
                    |Users(Book_A) ∪ Users(Book_B)|
```

**Ví dụ:**
```
Book 1 được mua bởi: {User 1, User 2, User 3, User 4, User 5}
Book 2 được mua bởi: {User 2, User 3, User 5, User 6, User 7}

Intersection (∩): {User 2, User 3, User 5} = 3 users
Union (∪): {User 1, User 2, User 3, User 4, User 5, User 6, User 7} = 7 users

Jaccard(Book1, Book2) = 3/7 = 0.4286
```

#### Implementation

```python
def compute_similarities(self, book_ids=None):
    # Build user-book matrix
    user_books = defaultdict(set)
    for interaction in interactions:
        if interaction.weight >= 2:  # Chỉ tính purchase/cart/rate
            user_books[interaction.customer_id].add(interaction.book_id)

    # Compute co-occurrence
    co_occurrence = defaultdict(lambda: defaultdict(int))
    book_counts = defaultdict(int)

    for user_id, books in user_books.items():
        for book1 in books:
            book_counts[book1] += 1
            for book2 in books:
                if book1 != book2:
                    co_occurrence[book1][book2] += 1

    # Calculate Jaccard similarity
    for book_id in target_books:
        for similar_book_id, co_count in co_occurrence[book_id].items():
            union = book_counts[book_id] + book_counts[similar_book_id] - co_count
            score = co_count / union if union > 0 else 0

            if score > 0.05:  # Minimum threshold
                BookSimilarity.objects.update_or_create(
                    book_id=book_id,
                    similar_book_id=similar_book_id,
                    defaults={'score': score}
                )
```

#### Ưu điểm & Nhược điểm

| Ưu điểm | Nhược điểm |
|---------|------------|
| Không cần biết nội dung sách | Cold Start Problem (new items) |
| Tìm được patterns bất ngờ | Cần nhiều data |
| Serendipity cao | Popularity bias |

---

### 3.2. Content-Based Filtering

#### Concept
> "If you liked X, you'll like similar items"

Gợi ý sách có đặc điểm tương tự với sách user đã thích (cùng tác giả, cùng thể loại, etc.)

#### Implementation

```python
def _get_content_based_recommendations(self, book_id, limit):
    recommendations = []

    # Lấy thông tin sách gốc
    book = self.book_client.get_book(book_id)

    # 1. Sách cùng CATEGORY
    if book.get('category_id'):
        category_books = self.book_client.get_books_by_category(
            book['category_id'], limit
        )
        for b in category_books:
            if b['id'] != book_id:
                recommendations.append({
                    'book_id': b['id'],
                    'score': 0.7,  # Score cho same category
                    'reason': 'same_category'
                })

    # 2. Sách cùng AUTHOR
    if book.get('author_id'):
        author_books = self.book_client.get_books_by_author(
            book['author_id'], limit
        )
        for b in author_books:
            if b['id'] != book_id:
                recommendations.append({
                    'book_id': b['id'],
                    'score': 0.8,  # Score cao hơn cho same author
                    'reason': 'same_author'
                })

    return recommendations
```

#### Ưu điểm & Nhược điểm

| Ưu điểm | Nhược điểm |
|---------|------------|
| Giải quyết Cold Start | Over-specialization |
| Không cần data từ users khác | Thiếu serendipity |
| Dễ giải thích | Cần metadata tốt |

---

### 3.3. Popularity-Based Filtering

#### Concept
> "What's hot right now?"

Gợi ý sách được nhiều người quan tâm nhất trong khoảng thời gian gần đây.

#### Weighted Popularity Score

```python
INTERACTION_WEIGHTS = {
    'purchase': 5.0,  # Mua hàng quan trọng nhất
    'cart': 3.0,      # Thêm giỏ hàng
    'rate': 2.0,      # Đánh giá
    'view': 1.0,      # Xem sách
}

def get_popular_books(self, limit=10):
    thirty_days_ago = timezone.now() - timedelta(days=30)

    popular_books = UserInteraction.objects.filter(
        created_at__gte=thirty_days_ago
    ).values('book_id').annotate(
        score=Sum(
            Case(
                When(interaction_type='purchase', then=5),
                When(interaction_type='cart', then=3),
                When(interaction_type='rate', then=2),
                When(interaction_type='view', then=1),
                default=0
            )
        )
    ).order_by('-score')[:limit]

    return popular_books
```

**Ví dụ tính điểm:**
```
Book #41 trong 30 ngày:
- 10 purchases × 5.0 = 50
- 15 carts × 3.0 = 45
- 8 rates × 2.0 = 16
- 50 views × 1.0 = 50
─────────────────────────
Total Score = 161 → Normalized: 16.1
```

---

### 3.4. Trending Algorithm

#### Concept
> "What's gaining momentum?"

Khác với Popular (tổng số), Trending tập trung vào **tốc độ tăng trưởng**.

```python
def get_trending_books(self, limit=10):
    seven_days_ago = timezone.now() - timedelta(days=7)
    one_day_ago = timezone.now() - timedelta(days=1)

    trending_books = UserInteraction.objects.filter(
        created_at__gte=seven_days_ago
    ).values('book_id').annotate(
        # Interactions trong 24h gần nhất (weight 3x)
        recent_count=Count(
            Case(When(created_at__gte=one_day_ago, then=1))
        ),
        # Interactions trong 7 ngày
        week_count=Count('id'),
        # Score = recent × 3 + week
        score=F('recent_count') * 3 + F('week_count')
    ).order_by('-score')[:limit]

    return trending_books
```

**Ví dụ:**
```
Book A: 100 interactions/tuần, 5 trong 24h  → Score = 5×3 + 100 = 115
Book B: 30 interactions/tuần, 20 trong 24h → Score = 20×3 + 30 = 90

Book A popular hơn, nhưng Book B đang trending nhanh hơn!
```

---

### 3.5. Hybrid Engine

#### Flow

```python
def get_personalized_recommendations(self, customer_id, limit=10):
    recommendations = []
    seen_book_ids = set()

    # Lấy sách user đã tương tác (để loại trừ)
    interacted_books = set(UserInteraction.objects.filter(
        customer_id=customer_id
    ).values_list('book_id', flat=True))

    # STEP 1: Collaborative Filtering (ưu tiên cao nhất)
    collab_recs = self._get_collaborative_recommendations(customer_id, limit * 2)
    for rec in collab_recs:
        if rec['book_id'] not in interacted_books:
            recommendations.append(rec)
            if len(recommendations) >= limit:
                return recommendations

    # STEP 2: Content-Based (bổ sung)
    if len(recommendations) < limit:
        content_recs = self._get_user_content_recommendations(customer_id, limit)
        for rec in content_recs:
            if rec['book_id'] not in interacted_books and rec['book_id'] not in seen_book_ids:
                recommendations.append(rec)
                if len(recommendations) >= limit:
                    return recommendations

    # STEP 3: Popularity Fallback (cho new users hoặc không đủ data)
    if len(recommendations) < limit:
        popular_recs = self.get_popular_books(limit)
        for rec in popular_recs:
            if rec['book_id'] not in interacted_books and rec['book_id'] not in seen_book_ids:
                rec['reason'] = 'popular_fallback'
                recommendations.append(rec)
                if len(recommendations) >= limit:
                    return recommendations

    return recommendations
```

#### Priority & Fallback Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    RECOMMENDATION FLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User có đủ interaction data?                                │
│         │                                                    │
│         ├─── YES ──▶ Collaborative Filtering (primary)      │
│         │                    │                               │
│         │                    ▼                               │
│         │           Đủ recommendations?                      │
│         │                    │                               │
│         │           NO ──────┼───▶ Content-Based (secondary) │
│         │                    │                               │
│         │                    ▼                               │
│         │           Đủ recommendations?                      │
│         │                    │                               │
│         │           NO ──────┼───▶ Popularity (fallback)     │
│         │                    │                               │
│         └─── NO ────────────────▶ Popularity (cold start)   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Data Models

### 4.1. UserInteraction

```python
class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('view', 'View'),        # Xem sách
        ('cart', 'Add to Cart'), # Thêm giỏ hàng
        ('purchase', 'Purchase'), # Mua
        ('rate', 'Rate'),        # Đánh giá
    ]

    customer_id = models.IntegerField()      # ID của customer
    book_id = models.IntegerField()          # ID của sách
    interaction_type = models.CharField(     # Loại tương tác
        max_length=20,
        choices=INTERACTION_TYPES
    )
    rating = models.IntegerField(            # Rating (1-5), chỉ cho type='rate'
        null=True, blank=True
    )
    created_at = models.DateTimeField(       # Thời điểm tương tác
        auto_now_add=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['book_id']),
        ]
```

### 4.2. BookSimilarity

```python
class BookSimilarity(models.Model):
    book_id = models.IntegerField()          # Book gốc
    similar_book_id = models.IntegerField()  # Book tương tự
    score = models.FloatField()              # Similarity score (0-1)

    class Meta:
        unique_together = ['book_id', 'similar_book_id']
        indexes = [
            models.Index(fields=['book_id', '-score']),  # Tối ưu query
        ]
```

### 4.3. Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                    UserInteraction                           │
├─────────────────────────────────────────────────────────────┤
│ id              │ SERIAL PRIMARY KEY                        │
│ customer_id     │ INTEGER NOT NULL (INDEX)                  │
│ book_id         │ INTEGER NOT NULL (INDEX)                  │
│ interaction_type│ VARCHAR(20) NOT NULL                      │
│ rating          │ INTEGER NULL                              │
│ created_at      │ TIMESTAMP DEFAULT NOW()                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    BookSimilarity                            │
├─────────────────────────────────────────────────────────────┤
│ id              │ SERIAL PRIMARY KEY                        │
│ book_id         │ INTEGER NOT NULL                          │
│ similar_book_id │ INTEGER NOT NULL                          │
│ score           │ FLOAT NOT NULL                            │
│                 │ UNIQUE(book_id, similar_book_id)          │
│                 │ INDEX(book_id, score DESC)                │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. API Endpoints

### 5.1. Recommendation APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recommend/book/{book_id}/` | Sách tương tự |
| GET | `/recommend/user/{customer_id}/` | Gợi ý cá nhân hóa |
| GET | `/recommend/popular/` | Sách phổ biến |
| GET | `/recommend/trending/` | Sách trending |

### 5.2. Data Collection APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/interactions/` | Ghi nhận tương tác |
| POST | `/similarity/compute/` | Trigger tính similarity |

### 5.3. Request/Response Examples

#### GET /recommend/user/30/?limit=5

**Response:**
```json
{
    "customer_id": 30,
    "recommendations": [
        {
            "book_id": 48,
            "score": 0.1667,
            "reason": "collaborative",
            "book_details": {
                "id": 48,
                "title": "Clean Code",
                "author": "Robert C. Martin",
                "price": "450000"
            }
        },
        {
            "book_id": 42,
            "score": 0.125,
            "reason": "collaborative"
        }
    ]
}
```

#### POST /interactions/

**Request:**
```json
{
    "customer_id": 30,
    "book_id": 45,
    "interaction_type": "purchase"
}
```

**Response:**
```json
{
    "id": 1001,
    "customer_id": 30,
    "book_id": 45,
    "interaction_type": "purchase",
    "rating": null,
    "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 6. Tích hợp với các Services khác

### 6.1. Integration Architecture

```python
# order-service/app/services.py
class RecommenderServiceClient:
    def record_purchase(self, customer_id, book_ids):
        """Ghi nhận purchase khi đơn hàng được tạo"""
        for book_id in book_ids:
            requests.post(
                f"{self.base_url}/interactions/",
                json={
                    'customer_id': customer_id,
                    'book_id': book_id,
                    'interaction_type': 'purchase'
                }
            )

# Gọi khi tạo order
def create_order(request):
    order = Order.objects.create(...)
    recommender_service.record_purchase(
        order.customer_id,
        [item.book_id for item in order.items.all()]
    )
```

### 6.2. Service Integration Map

```
┌─────────────────┐          ┌─────────────────────┐
│  order-service  │─────────▶│                     │
│   (purchase)    │          │                     │
└─────────────────┘          │                     │
                             │                     │
┌─────────────────┐          │    RECOMMENDER      │
│  cart-service   │─────────▶│      SERVICE        │
│    (cart)       │          │                     │
└─────────────────┘          │  POST /interactions │
                             │                     │
┌─────────────────┐          │                     │
│ comment-rate-   │─────────▶│                     │
│    service      │          │                     │
│    (rate)       │          └─────────────────────┘
└─────────────────┘
```

---

## 7. Ví dụ thực tế

### 7.1. Scenario: New User (Cold Start)

```
User #100 mới đăng ký, chưa có interaction nào

Request: GET /recommend/user/100/?limit=5

Flow:
1. Collaborative: Không có data → Skip
2. Content-Based: Không biết sở thích → Skip
3. Popularity Fallback: Trả về sách bán chạy

Response:
[
    { "book_id": 41, "score": 8.4, "reason": "popular_fallback" },
    { "book_id": 40, "score": 6.4, "reason": "popular_fallback" },
    { "book_id": 33, "score": 6.1, "reason": "popular_fallback" }
]
```

### 7.2. Scenario: Active User

```
User #30 có history:
- Viewed: Book 45, 34, 49
- Purchased: Book 41, 50

Request: GET /recommend/user/30/?limit=5

Flow:
1. Tìm users khác cũng mua Book 41, 50
2. Xem họ còn mua gì khác
3. Gợi ý những sách đó (trừ sách user đã có)

Response:
[
    { "book_id": 48, "score": 0.17, "reason": "collaborative" },
    { "book_id": 42, "score": 0.12, "reason": "collaborative" },
    { "book_id": 35, "score": 0.12, "reason": "collaborative" }
]

Giải thích: Nhiều users mua Book 41, 50 cũng mua Book 48!
```

### 7.3. Scenario: Book Detail Page

```
User đang xem Book #14 (Python Programming)

Request: GET /recommend/book/14/?limit=5

Flow:
1. Tìm trong BookSimilarity table
2. Lấy top 5 books similar với Book 14

Response:
[
    { "book_id": 7, "score": 0.25, "reason": "collaborative" },   // Java Programming
    { "book_id": 13, "score": 0.25, "reason": "collaborative" },  // JavaScript
    { "book_id": 16, "score": 0.19, "reason": "collaborative" },  // C++
    { "book_id": 11, "score": 0.14, "reason": "same_category" },  // Data Structures
    { "book_id": 3, "score": 0.14, "reason": "same_author" }      // Same author
]
```

---

## 8. Performance Considerations

### 8.1. Batch Processing
- Similarity computation chạy **offline** (batch job mỗi đêm)
- Không tính realtime để tránh ảnh hưởng performance

### 8.2. Caching Strategy
```python
# Có thể thêm Redis cache
@cache(timeout=3600)  # Cache 1 giờ
def get_popular_books(limit=10):
    ...
```

### 8.3. Database Indexing
```sql
-- Đã có indexes tối ưu
CREATE INDEX idx_interaction_customer ON user_interaction(customer_id);
CREATE INDEX idx_interaction_book ON user_interaction(book_id);
CREATE INDEX idx_similarity_book_score ON book_similarity(book_id, score DESC);
```

---

## 9. Future Improvements

| Feature | Description | Priority |
|---------|-------------|----------|
| Matrix Factorization | SVD/ALS cho better predictions | Medium |
| Real-time updates | Cập nhật similarity realtime | Low |
| A/B Testing | So sánh các algorithms | Medium |
| Deep Learning | Neural Collaborative Filtering | Low |
| Contextual Recommendations | Theo thời gian, location | Low |

---

## 10. Summary

Book Recommender System sử dụng **Hybrid approach** kết hợp:

1. **Collaborative Filtering** (Jaccard Similarity)
   - Dựa trên co-purchase patterns
   - "Users who bought X also bought Y"

2. **Content-Based Filtering**
   - Dựa trên metadata (category, author)
   - Giải quyết cold start

3. **Popularity-Based**
   - Weighted by interaction types
   - Fallback cho new users

4. **Trending Algorithm**
   - Velocity-based (recent growth)
   - Capture momentum

**Kết quả:** Hệ thống có khả năng:
- Gợi ý cá nhân hóa cho từng user
- Xử lý cold start problem
- Scale với lượng data lớn
- Dễ dàng mở rộng và cải thiện
