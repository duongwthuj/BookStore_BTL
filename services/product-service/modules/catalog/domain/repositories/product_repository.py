from abc import ABC, abstractmethod
from typing import Optional, List
from modules.catalog.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        pass

    @abstractmethod
    def list_all(self, filters: dict = None) -> List[Product]:
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        pass

    @abstractmethod
    def delete(self, product_id: int) -> None:
        pass

    @abstractmethod
    def update_stock(self, product_id: int, stock: int) -> Optional[Product]:
        pass
