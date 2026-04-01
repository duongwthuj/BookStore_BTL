#!/bin/bash

# Seed data script for BookStore
# Run this after all services are up

API_URL="http://localhost:8000/api"

echo "=== Seeding BookStore Data ==="

# Create categories
echo "Creating categories..."
curl -s -X POST "$API_URL/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Văn học", "description": "Sách văn học trong và ngoài nước"}' > /dev/null

curl -s -X POST "$API_URL/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Kinh tế", "description": "Sách kinh tế, kinh doanh"}' > /dev/null

curl -s -X POST "$API_URL/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Kỹ năng sống", "description": "Sách kỹ năng sống, phát triển bản thân"}' > /dev/null

curl -s -X POST "$API_URL/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Thiếu nhi", "description": "Sách dành cho thiếu nhi"}' > /dev/null

curl -s -X POST "$API_URL/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Công nghệ", "description": "Sách công nghệ thông tin, lập trình"}' > /dev/null

echo "Categories created."

# Create collections
echo "Creating collections..."
curl -s -X POST "$API_URL/collections/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Sách bán chạy", "description": "Những cuốn sách bán chạy nhất"}' > /dev/null

curl -s -X POST "$API_URL/collections/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Sách mới", "description": "Sách mới ra mắt"}' > /dev/null

curl -s -X POST "$API_URL/collections/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Sách giảm giá", "description": "Sách đang khuyến mãi"}' > /dev/null

echo "Collections created."

# Create shipping methods
echo "Creating shipping methods..."
curl -s -X POST "$API_URL/shipping/methods/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Giao hàng nhanh", "fee": 30000, "estimated_days": 2, "free_ship_threshold": 500000}' > /dev/null

curl -s -X POST "$API_URL/shipping/methods/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Giao hàng tiết kiệm", "fee": 15000, "estimated_days": 5, "free_ship_threshold": 300000}' > /dev/null

echo "Shipping methods created."

# Create sample books
echo "Creating sample books..."
curl -s -X POST "$API_URL/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Đắc Nhân Tâm",
    "author": "Dale Carnegie",
    "description": "Đắc nhân tâm là cuốn sách nổi tiếng nhất, bán chạy nhất và có tầm ảnh hưởng nhất của mọi thời đại.",
    "price": 86000,
    "stock": 100,
    "category_id": 3,
    "collection_ids": [1],
    "isbn": "9786043651249"
  }' > /dev/null

curl -s -X POST "$API_URL/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nhà Giả Kim",
    "author": "Paulo Coelho",
    "description": "Tiểu thuyết Nhà giả kim của Paulo Coelho như một câu chuyện cổ tích giản dị, nhân ái.",
    "price": 79000,
    "stock": 80,
    "category_id": 1,
    "collection_ids": [1, 2],
    "isbn": "9786043651256"
  }' > /dev/null

curl -s -X POST "$API_URL/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sapiens: Lược Sử Loài Người",
    "author": "Yuval Noah Harari",
    "description": "Sapiens khám phá lịch sử loài người từ thời kỳ đồ đá đến thế kỷ 21.",
    "price": 299000,
    "stock": 50,
    "category_id": 2,
    "collection_ids": [2],
    "isbn": "9786043651263"
  }' > /dev/null

curl -s -X POST "$API_URL/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "description": "A Handbook of Agile Software Craftsmanship.",
    "price": 450000,
    "stock": 30,
    "category_id": 5,
    "collection_ids": [1],
    "isbn": "9780132350884"
  }' > /dev/null

curl -s -X POST "$API_URL/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Doraemon - Tập 1",
    "author": "Fujiko F. Fujio",
    "description": "Truyện tranh Doraemon tập 1.",
    "price": 25000,
    "stock": 200,
    "category_id": 4,
    "collection_ids": [],
    "isbn": "9786043651270"
  }' > /dev/null

echo "Sample books created."

# Create coupons
echo "Creating coupons..."
curl -s -X POST "$API_URL/coupons/" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "WELCOME10",
    "discount_type": "percent",
    "discount_value": 10,
    "min_order": 100000,
    "max_uses": 1000,
    "is_active": true
  }' > /dev/null

curl -s -X POST "$API_URL/coupons/" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "FREESHIP",
    "discount_type": "fixed",
    "discount_value": 30000,
    "min_order": 200000,
    "max_uses": 500,
    "is_active": true
  }' > /dev/null

echo "Coupons created."

echo "=== Seeding Complete ==="
