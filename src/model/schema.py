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


class UserBase(BaseSchema):
    nid: str
    first_name: str
    last_name: str
    phone: str
    email: EmailStr | None = None


class UserIn(UserBase):
    re_password: SecretStr
    password: SecretStr

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        pw1 = self.password.get_secret_value()
        pw2 = self.re_password.get_secret_value()
        if pw1 != pw2:
            raise ValueError('passwords do not match')
        return self
    @field_validator('nid')
    @classmethod
    def check_nid_length(cls, v: str):
        if len(v) != 10:
            raise ValueError('nid must be 10 characters long')
        return v

    @field_validator('phone')
    @classmethod
    def check_phone_number(cls, v: str):
        p = phonenumbers.parse(v, region='IR')
        phonenumbers.is_valid_number(p)  # raises exception in case of invalid number
        return v

    def to_model(self) -> User:
        dump = self.model_dump(exclude={'password', 're_password', 'id'})
        return User(**dump)


class UserOut(UserBase, BaseOut):
    pass


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
