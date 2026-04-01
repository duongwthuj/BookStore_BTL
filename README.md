# BookStore Microservice

A complete e-commerce bookstore application built with microservice architecture.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│                        http://localhost:3000                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (Django)                       │
│                    http://localhost:8000                        │
│              [Routing + JWT Authentication]                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Identity      │   │ Catalog       │   │ Ordering      │
│ ─────────────│   │ ─────────────│   │ ─────────────│
│ • auth        │   │ • catalog     │   │ • cart        │
│ • customer    │   │ • book        │   │ • order       │
│ • staff       │   │               │   │               │
│ • manager     │   │               │   │               │
└───────────────┘   └───────────────┘   └───────────────┘

        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Payment       │   │ Shipping      │   │ Review        │
│ ─────────────│   │ ─────────────│   │ ─────────────│
│ • pay (MoMo)  │   │ • ship        │   │ • comment-rate│
│ • COD         │   │               │   │               │
└───────────────┘   └───────────────┘   └───────────────┘

        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────┐                         ┌───────────────┐
│ AI Services   │                         │ Support       │
│ ─────────────│                         │ ─────────────│
│ • recommender │                         │ • chatbot     │
│   (Hybrid)    │                         │   (Ollama)    │
└───────────────┘                         └───────────────┘
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| API Gateway | 8000 | Routing + JWT Authentication |
| Auth Service | 8001 | User authentication with JWT |
| Customer Service | 8002 | Customer management |
| Staff Service | 8003 | Staff management |
| Manager Service | 8004 | Manager + Dashboard |
| Catalog Service | 8005 | Categories & Collections |
| Book Service | 8006 | Book management |
| Cart Service | 8007 | Shopping cart |
| Order Service | 8008 | Order management |
| Pay Service | 8009 | MoMo + COD payments |
| Ship Service | 8010 | Shipping management |
| Comment-Rate Service | 8011 | Reviews & Ratings |
| Recommender Service | 8012 | Book recommendations |
| Chatbot Service | 8013 | FAQ chatbot (Ollama) |
| Frontend | 3000 | React application |

## Tech Stack

- **Backend:** Django REST Framework
- **Frontend:** React 18 + Tailwind CSS
- **Database:** PostgreSQL (one per service)
- **Authentication:** JWT
- **Payment:** MoMo Sandbox
- **AI/Chatbot:** Ollama (llama3.2:1b)
- **Containerization:** Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Run the application

```bash
# Clone the repository
git clone <repository-url>
cd bookstore-microservice

# Start all services
docker-compose up --build

# Wait for all services to be healthy (this may take a few minutes)
```

### Access the application

- **Frontend:** http://localhost:3000
- **API Gateway:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/docs/

### Pull Ollama model (for chatbot)

```bash
# After services are running, pull the llama model
docker-compose exec ollama ollama pull llama3.2:1b
```

## Development

### Run individual services

```bash
# Run a specific service
cd services/auth-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

### Environment Variables

Each service uses the following environment variables:

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL connection string |
| JWT_SECRET | Secret key for JWT tokens |
| DEBUG | Enable debug mode |

Payment service additional variables:
| Variable | Description |
|----------|-------------|
| MOMO_PARTNER_CODE | MoMo partner code |
| MOMO_ACCESS_KEY | MoMo access key |
| MOMO_SECRET_KEY | MoMo secret key |
| MOMO_REDIRECT_URL | Redirect URL after payment |
| MOMO_IPN_URL | IPN callback URL |

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh token
- `GET /api/auth/me/` - Current user info

### Books
- `GET /api/books/` - List books
- `GET /api/books/{id}/` - Book detail
- `GET /api/books/search/?q=` - Search books
- `POST /api/books/` - Create book (Staff)
- `PUT /api/books/{id}/` - Update book (Staff)

### Cart
- `GET /api/carts/{customer_id}/` - View cart
- `POST /api/carts/{customer_id}/items/` - Add to cart
- `PUT /api/carts/{customer_id}/items/{id}/` - Update quantity
- `DELETE /api/carts/{customer_id}/items/{id}/` - Remove item

### Orders
- `POST /api/orders/` - Create order
- `GET /api/orders/` - List orders
- `GET /api/orders/{id}/` - Order detail
- `GET /api/orders/customer/{id}/` - Customer orders

### Payments
- `POST /api/payments/momo/create/` - Create MoMo payment
- `POST /api/payments/cod/create/` - Create COD payment
- `GET /api/payments/{order_id}/` - Payment status

### Reviews
- `GET /api/reviews/book/{book_id}/` - Book reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/book/{book_id}/stats/` - Rating stats

### Recommendations
- `GET /api/recommend/book/{book_id}/` - Similar books
- `GET /api/recommend/user/{customer_id}/` - Personalized
- `GET /api/recommend/popular/` - Popular books

### Chatbot
- `POST /api/chat/` - Send message

## Demo Flow

1. **Customer Registration**
   - Register at /register
   - Cart is automatically created

2. **Browse & Add to Cart**
   - Browse books at /books
   - View book details
   - Add books to cart

3. **Checkout**
   - Go to /cart
   - Proceed to checkout
   - Enter shipping info
   - Select payment method (MoMo or COD)

4. **Payment**
   - MoMo: Redirect to MoMo sandbox
   - COD: Order confirmed immediately

5. **Track Order**
   - View orders at /orders
   - Track shipment status

6. **Review**
   - Write review after receiving order

7. **Chat Support**
   - Use chatbot widget for FAQ

## Testing

```bash
# Run tests for a service
cd services/auth-service
python manage.py test

# Run all tests
./scripts/run-tests.sh
```

## License

MIT License
# BookStore_BTL
