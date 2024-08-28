from datetime import datetime
from typing import Self, ClassVar

import phonenumbers
from pydantic import BaseModel, model_validator, field_validator, EmailStr, SecretStr, ConfigDict

from model.orm import User, Product, Base, Address, Order


class BaseOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    _model: ClassVar = Base

    def to_model(self, **kwargs) -> _model:
        dump = self.model_dump(exclude={'id'})
        return self._model(**dump, **kwargs)


class Token(BaseModel):
    access_token: str


class PhoneLogin(BaseModel):
    phone: str
    password: str


class ProductBase(BaseSchema):
    category: str
    info: dict
    price: int
    stock_quantity: int

    _model = Product


class ProductOut(ProductBase, BaseOut):
    pass


class AddressBase(BaseSchema):
    state: str
    city: str
    latitude: float
    longitude: float
    description: str
    postal_code: str

    _model = Address


class AddressOut(AddressBase, BaseOut):
    pass


class OrderBase(BaseSchema):
    address_id: int

    _model = Order


class OrderIn(OrderBase):
    pass


class OrderOut(OrderBase, BaseOut):
    pass
