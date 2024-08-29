from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status

from data.Address import AddressRepo, AddressRepoABC
from data.order import OrderRepoABC, OrderRepo
from data.product import ProductRepo, ProductRepoABC
from model.model import Order, OrderIn


@dataclass
class OrderServiceABC(ABC):
    address_repo: AddressRepoABC
    order_repo: OrderRepoABC

    @abstractmethod
    async def create(self, order, user_id):
        raise NotImplementedError


class OrderService(OrderServiceABC):

    def __init__(
            self,
            address_repo: AddressRepoABC = Depends(AddressRepo),
            order_repo: OrderRepoABC = Depends(OrderRepo),
            product_repo: ProductRepoABC = Depends(ProductRepo),
    ):
        self.address_repo = address_repo if isinstance(address_repo, AddressRepoABC) else AddressRepo()
        self.order_repo = order_repo if isinstance(order_repo, OrderRepoABC) else OrderRepo()
        self.product_repo = product_repo if isinstance(product_repo, ProductRepoABC) else ProductRepo()

    async def create(self, order_in: OrderIn, user_id: int) -> Order:
        order = Order.model_validate(order_in)

        if not await self.address_repo.exists(id=order.address_id, user_id=user_id):
            raise HTTPException(detail="invalid ", status_code=status.HTTP_400_BAD_REQUEST)

        order_product_ids = [o.product_id for o in order.products]
        stock_products = {s.id: s for s in await self.product_repo.get_by_ids(order_product_ids)}

        # check stock quantity
        for p in order.products:
            stock_product = stock_products[p.product_id]
            if p.quantity > stock_product.quantity:
                raise HTTPException(detail="quantity for than stock", status_code=status.HTTP_400_BAD_REQUEST)

        await self.order_repo.submit_order(order, stock_products)
        return order
