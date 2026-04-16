from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List


@dataclass
class UpdateProductCommand:
    product_id: int
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    collection_ids: Optional[List[int]] = None
    attributes: Optional[dict] = None
    cover_image: Optional[str] = None
