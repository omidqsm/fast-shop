from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import Depends

from data.Address import AddressRepo, AddressRepoABC
from data.order import OrderRepoABC, OrderRepo
from model.enums import OrderStatus
from model.orm import Order
from model.schema import OrderBase, OrderIn


@dataclass
class OrderServiceABC(ABC):
    address_repo: AddressRepoABC
    order_repo: OrderRepoABC

    @abstractmethod
    async def create(self, order, user_id):
        raise NotImplementedError


@dataclass
class OrderService(OrderServiceABC):
    address_repo: AddressRepo = Depends(AddressRepo)
    order_repo: OrderRepo = Depends(OrderRepo)

    # def __init__(
    #         self,
    #         address_repo: AddressRepoABC = Depends(AddressRepo),
    #         order_repo: OrderRepoABC = Depends(OrderRepo)
    # ):
    #     self.address_repo = address_repo if isinstance(address_repo, AddressRepoABC) else AddressRepo()
    #     self.order_repo = order_repo if isinstance(order_repo, OrderRepoABC) else OrderRepo()

    async def create(self, order_in: OrderIn, user_id: int) -> Order:
        order = order_in.to_model(status=OrderStatus.created.value)
        address_lookup = {'id': order.address_id, 'user_id': user_id}
        await self.address_repo.exists(where=address_lookup, not_found_error=True)
        await self.order_repo.add(order)
        return order
