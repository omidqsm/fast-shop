from datetime import datetime
from typing import Self

import phonenumbers
from pydantic import EmailStr, SecretStr, model_validator, field_validator, ConfigDict
from sqlalchemy import JSON, DateTime, func, Column, String
from sqlmodel import SQLModel, Field, Relationship


class Base(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True), sa_column_kwargs={'server_default': func.now()})
    updated_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True), sa_column_kwargs={'server_default': func.now(), 'onupdate': func.now()})


class UserBase(SQLModel):
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


class UserOut(UserBase, Base):
    pass


class User(UserBase, Base, table=True):
    password: SecretStr = Field(sa_type=String())
    scopes: str = Field(default='user')  # permissions

    addresses: list["Address"] | None = Relationship(
        back_populates="user",
        sa_relationship_kwargs={'cascade': "all, delete-orphan"}
    )


class Address(Base, table=True):

    state: str
    city: str
    description: str
    postal_code: str
    latitude: float | None = None
    longitude: float | None = None

    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="addresses")


class Order(Base, table=True):
    status: str
    status_date: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))

    address_id: int = Field(default=None, foreign_key="address.id")
    address: Address = Relationship()

    # products: Mapped[List["OrderProduct"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class Product(Base, table=True):
    category: str
    info: dict = Field(sa_type=JSON())
    price: int
    stock_quantity: int


# class OrderProduct(Common):
#     __tablename__ = "order_product"
#
#     quantity: Mapped[int]
#     price: Mapped[int]
#
#     order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
#     order: Mapped["Order"] = relationship(back_populates="products")
#
#     product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
#     product: Mapped["Product"] = relationship()


