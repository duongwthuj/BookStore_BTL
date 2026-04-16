from dataclasses import dataclass


@dataclass
class UpdateStockCommand:
    product_id: int
    stock: int
