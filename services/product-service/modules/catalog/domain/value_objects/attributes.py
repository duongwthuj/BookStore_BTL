from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProductAttributes:
    """Wraps JSONB attributes dict. For books: isbn, publisher, pages, published_date, etc."""
    data: dict

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
