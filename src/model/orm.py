from datetime import datetime, tzinfo
from typing import List, Any, Optional

from sqlalchemy import String, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Common(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class User(Common):
    __tablename__ = "user"

    password: Mapped[str]
    nid: Mapped[str] = mapped_column(String(length=10))
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[Optional[str]]
    scopes: Mapped[str] = mapped_column(String(), default='user')  # permissions

    addresses: Mapped[List["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Address(Common):
    __tablename__ = "address"

    state: Mapped[str]
    city: Mapped[str]
    latitude: Mapped[Optional[float]]
    longitude: Mapped[Optional[float]]
    description: Mapped[str]
    postal_code: Mapped[str]

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        address = f'{self.state} - {self.city} - {self.description}'
        return f"Address(id={self.id!r}, address={address})"


class Order(Common):
    __tablename__ = "order"

    status: Mapped[str]
    status_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    address_id: Mapped[int] = mapped_column(ForeignKey("address.id"))
    address: Mapped["Address"] = relationship()
    products: Mapped[List["OrderProduct"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class Product(Common):
    __tablename__ = "product"

    category: Mapped[str]
    info: Mapped[dict] = mapped_column(JSON())
    price: Mapped[int]
    stock_quantity: Mapped[int]


class OrderProduct(Common):
    __tablename__ = "order_product"

    quantity: Mapped[int]
    price: Mapped[int]

    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    order: Mapped["Order"] = relationship(back_populates="products")

    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    product: Mapped["Product"] = relationship()


