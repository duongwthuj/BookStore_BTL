from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from .models import Book
from .serializers import BookSerializer, BookListSerializer, StockUpdateSerializer
from .filters import BookFilter


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books.

    list: GET /books/ - List all books with pagination and filtering
    create: POST /books/ - Create a new book (Staff only)
    retrieve: GET /books/{id}/ - Get book details
    update: PUT /books/{id}/ - Update a book (Staff only)
    partial_update: PATCH /books/{id}/ - Partially update a book (Staff only)
    destroy: DELETE /books/{id}/ - Delete a book (Staff only)
    """
    queryset = Book.objects.all()
    filterset_class = BookFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'author', 'description', 'isbn', 'publisher']
    ordering_fields = ['title', 'author', 'price', 'created_at', 'published_date', 'stock']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer

    @action(detail=True, methods=['put'], url_path='stock')
    def update_stock(self, request, pk=None):
        """
        PUT /books/{id}/stock/ - Update book stock
        Used for order processing
        """
        book = self.get_object()
        serializer = StockUpdateSerializer(data=request.data)
        if serializer.is_valid():
            book.stock = serializer.validated_data['stock']
            book.save(update_fields=['stock', 'updated_at'])
            return Response(BookSerializer(book).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookSearchView(APIView):
    """
    GET /books/search/?q= - Search books by title or author
    """
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

        # Apply pagination
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(books, request)

        if page is not None:
            serializer = BookListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)


class BooksByCategoryView(APIView):
    """
    GET /books/category/{category_id}/ - Get books by category
    """
    def get(self, request, category_id):
        books = Book.objects.filter(category_id=category_id)

        # Apply pagination
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(books, request)

        if page is not None:
            serializer = BookListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)


class BooksByCollectionView(APIView):
    """
    GET /books/collection/{collection_id}/ - Get books by collection
    """
    def get(self, request, collection_id):
        # Filter books where collection_id is in the collection_ids JSON array
        books = Book.objects.filter(collection_ids__contains=[collection_id])

        # Apply pagination
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(books, request)

        if page is not None:
            serializer = BookListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)
