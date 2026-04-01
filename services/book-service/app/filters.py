import django_filters
from .models import Book


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    publisher = django_filters.CharFilter(lookup_expr='icontains')
    published_after = django_filters.DateFilter(field_name='published_date', lookup_expr='gte')
    published_before = django_filters.DateFilter(field_name='published_date', lookup_expr='lte')

    class Meta:
        model = Book
        fields = [
            'category_id',
            'title',
            'author',
            'isbn',
            'publisher',
            'min_price',
            'max_price',
            'in_stock',
            'published_after',
            'published_before',
        ]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)
