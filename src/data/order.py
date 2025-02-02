from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from data._base import RepoABC, Repo
from helpers.exceptions import entity_not_found_exception
from model.model import Order, Address, OrderProduct


class OrderRepoABC(RepoABC, ABC):
    @abstractmethod
    async def get_one(self, pk, user_id):
        raise NotImplementedError

    @abstractmethod
    async def get(self, limit, offset, user_id):
        raise NotImplementedError


class OrderRepo(Repo, OrderRepoABC):
    model = Order

    async def get_one(self, pk, user_id) -> Order:
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

    async def get(self, limit, offset, user_id) -> list[Order]:

        stmt = (
            select(Order).where(Address.user_id == user_id).offset(offset).limit(limit).
            options(joinedload(Order.products).joinedload(OrderProduct.product))
        )
        async with self.session as session:
            orders = (await session.scalars(stmt)).unique().all()
        return orders


