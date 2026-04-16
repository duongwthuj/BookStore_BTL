from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List


@dataclass
class CreateProductCommand:
    title: str
    author: str
    price: Decimal
    stock: int
    category_id: int
    description: str = ""
    collection_ids: List[int] = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
    cover_image: Optional[str] = None
