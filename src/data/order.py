from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from data._base import RepoABC, Repo
from helpers.exceptions import entity_not_found_exception
from model.model import Order, Address, OrderProduct


class OrderRepoABC(RepoABC, ABC):
    @abstractmethod
    async def get_one_for_user(self, pk, user_id):
        pass

    @abstractmethod
    async def submit_order(self, order, stock_products):
        pass

class OrderRepo(Repo, OrderRepoABC):
    model = Order

    async def get_one_for_user(self, pk, user_id):
        stmt = (
            select(Order).
            where(Order.id == pk, Address.user_id == user_id).
            options(joinedload(Order.products).joinedload(OrderProduct.product))
        )
        async with self.session as session:
            order = await session.scalar(stmt)
        if not order:
            raise entity_not_found_exception
        return order

    async def submit_order(self, order, stock_products):
        async with self.session.begin():
            for p in order.products:
                stock_product = stock_products[p.product_id]
                self.session.add(stock_product)
                p.price = stock_products[p.product_id].price
                stock_product.quantity -= p.quantity

            self.session.add(order)


