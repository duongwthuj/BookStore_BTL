from dataclasses import dataclass
from typing import Optional


@dataclass
class ListProductsQuery:
    category_id: Optional[int] = None
    collection_id: Optional[int] = None
    search: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: Optional[bool] = None
    page: int = 1
    page_size: int = 20
