from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


@dataclass
class Product:
    id: Optional[int]
    title: str
    author: str
    description: str
    price: Decimal
    stock: int
    category_id: int
    collection_ids: List[int]
    attributes: dict  # JSONB: {"isbn": "...", "publisher": "...", "pages": 300, ...}
    cover_image: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_in_stock(self) -> bool:
        return self.stock > 0

    def update_stock(self, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Stock cannot be negative")
        self.stock = quantity
