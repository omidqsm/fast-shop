from datetime import datetime

from aredis_om import JsonModel, Field


class ProductCache(JsonModel):
    id: int
    category: str = Field(index=True)
    info: dict
    price: int
    quantity: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def make_key(cls, part: str):
        return f"fast_shop:product:{part}"
