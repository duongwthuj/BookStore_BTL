#!/bin/bash

# Run tests for all services

echo "=== Running Tests for All Services ==="

SERVICES=(
    "auth-service"
    "customer-service"
    "staff-service"
    "manager-service"
    "catalog-service"
    "book-service"
    "cart-service"
    "order-service"
    "pay-service"
    "ship-service"
    "comment-rate-service"
    "recommender-service"
)

FAILED_SERVICES=()

for service in "${SERVICES[@]}"; do
    echo ""
    echo "Testing $service..."
    cd "services/$service"

    if docker-compose exec "$service" python manage.py test; then
        echo "$service: PASSED"
    else
        echo "$service: FAILED"
        FAILED_SERVICES+=("$service")
    fi

    cd ../..
done

echo ""
echo "=== Test Summary ==="
if [ ${#FAILED_SERVICES[@]} -eq 0 ]; then
    echo "All services passed!"
else
    echo "Failed services:"
    for service in "${FAILED_SERVICES[@]}"; do
        echo "  - $service"
    done
    exit 1
fi
