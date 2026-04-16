from dataclasses import dataclass


@dataclass(frozen=True)
class SKU:
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("SKU cannot be empty")
