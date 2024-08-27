from datetime import datetime, tzinfo

from sqlalchemy import String, ForeignKey, JSON, DateTime, func, Column
from sqlmodel import SQLModel, Field, Relationship


class Base(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(sa_type=DateTime(timezone=True), sa_column_kwargs={'server_default': func.now()})
    updated_at: datetime = Field(sa_type=DateTime(timezone=True), sa_column_kwargs={'server_default': func.now(), 'onupdate': func.now()})


class User(Base, table=True):
    password: str
    nid: str = Field(max_length=10, min_length=10)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    phone: str = Field(max_length=20)
    email: str | None = None
    scopes: str | None = Field(default='user')  # permissions

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


