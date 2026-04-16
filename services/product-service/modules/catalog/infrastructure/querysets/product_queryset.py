from django.db.models import QuerySet, Q


class ProductQuerySet(QuerySet):
    def in_stock(self):
        return self.filter(stock__gt=0)

    def by_category(self, category_id: int):
        return self.filter(category_id=category_id)

    def by_collection(self, collection_id: int):
        return self.filter(collection_ids__contains=[collection_id])

    def search(self, query: str):
        return self.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query)
        )

    def price_range(self, min_price=None, max_price=None):
        qs = self
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        return qs
