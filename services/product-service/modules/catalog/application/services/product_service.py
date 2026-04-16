from typing import Optional, List
from modules.catalog.domain.entities.product import Product
from modules.catalog.domain.repositories.product_repository import ProductRepository
from modules.catalog.application.commands.create_product import CreateProductCommand
from modules.catalog.application.commands.update_product import UpdateProductCommand
from modules.catalog.application.commands.update_stock import UpdateStockCommand
from modules.catalog.application.queries.get_product import GetProductQuery
from shared.exceptions import ProductNotFoundError


class ProductService:
    def __init__(self, repository: ProductRepository):
        self._repository = repository

    def get_product(self, query: GetProductQuery) -> Optional[Product]:
        product = self._repository.get_by_id(query.product_id)
        if not product:
            raise ProductNotFoundError(f"Product {query.product_id} not found")
        return product

    def list_products(self, filters: dict = None) -> List[Product]:
        return self._repository.list_all(filters)

    def create_product(self, command: CreateProductCommand) -> Product:
        product = Product(
            id=None,
            title=command.title,
            author=command.author,
            description=command.description,
            price=command.price,
            stock=command.stock,
            category_id=command.category_id,
            collection_ids=command.collection_ids,
            attributes=command.attributes,
            cover_image=command.cover_image,
        )
        return self._repository.save(product)

    def update_product(self, command: UpdateProductCommand) -> Product:
        product = self._repository.get_by_id(command.product_id)
        if not product:
            raise ProductNotFoundError(f"Product {command.product_id} not found")
        if command.title is not None:
            product.title = command.title
        if command.author is not None:
            product.author = command.author
        if command.price is not None:
            product.price = command.price
        if command.stock is not None:
            product.stock = command.stock
        if command.category_id is not None:
            product.category_id = command.category_id
        if command.description is not None:
            product.description = command.description
        if command.collection_ids is not None:
            product.collection_ids = command.collection_ids
        if command.attributes is not None:
            product.attributes = command.attributes
        if command.cover_image is not None:
            product.cover_image = command.cover_image
        return self._repository.save(product)

    def update_stock(self, command: UpdateStockCommand) -> Product:
        product = self._repository.get_by_id(command.product_id)
        if not product:
            raise ProductNotFoundError(f"Product {command.product_id} not found")
        product.update_stock(command.stock)
        return self._repository.save(product)

    def delete_product(self, product_id: int) -> None:
        product = self._repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        self._repository.delete(product_id)
