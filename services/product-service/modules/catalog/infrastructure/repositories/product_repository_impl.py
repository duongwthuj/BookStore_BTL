from typing import Optional, List
from modules.catalog.domain.entities.product import Product
from modules.catalog.domain.repositories.product_repository import ProductRepository
from modules.catalog.infrastructure.models.product_model import ProductModel
from modules.catalog.infrastructure.querysets.product_queryset import ProductQuerySet


class DjangoProductRepository(ProductRepository):
    def _to_entity(self, model: ProductModel) -> Product:
        return Product(
            id=model.id,
            title=model.title,
            author=model.author,
            description=model.description,
            price=model.price,
            stock=model.stock,
            category_id=model.category_id,
            collection_ids=model.collection_ids,
            attributes=model.attributes,
            cover_image=model.cover_image,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _get_queryset(self) -> ProductQuerySet:
        return ProductQuerySet(ProductModel)

    def get_by_id(self, product_id: int) -> Optional[Product]:
        try:
            model = self._get_queryset().get(pk=product_id)
            return self._to_entity(model)
        except ProductModel.DoesNotExist:
            return None

    def list_all(self, filters: dict = None) -> List[Product]:
        qs = self._get_queryset()
        if filters:
            if filters.get('category_id'):
                qs = qs.by_category(filters['category_id'])
            if filters.get('collection_id'):
                qs = qs.by_collection(filters['collection_id'])
            if filters.get('search'):
                qs = qs.search(filters['search'])
            if filters.get('in_stock'):
                qs = qs.in_stock()
            if filters.get('min_price') or filters.get('max_price'):
                qs = qs.price_range(filters.get('min_price'), filters.get('max_price'))
        return [self._to_entity(m) for m in qs]

    def save(self, product: Product) -> Product:
        if product.id:
            model = ProductModel.objects.get(pk=product.id)
            model.title = product.title
            model.author = product.author
            model.description = product.description
            model.price = product.price
            model.stock = product.stock
            model.category_id = product.category_id
            model.collection_ids = product.collection_ids
            model.attributes = product.attributes
            model.cover_image = product.cover_image
            model.save()
        else:
            model = ProductModel.objects.create(
                title=product.title,
                author=product.author,
                description=product.description,
                price=product.price,
                stock=product.stock,
                category_id=product.category_id,
                collection_ids=product.collection_ids,
                attributes=product.attributes,
                cover_image=product.cover_image,
            )
        return self._to_entity(model)

    def delete(self, product_id: int) -> None:
        ProductModel.objects.filter(pk=product_id).delete()

    def update_stock(self, product_id: int, stock: int) -> Optional[Product]:
        updated = ProductModel.objects.filter(pk=product_id).update(stock=stock)
        if not updated:
            return None
        return self.get_by_id(product_id)
