from fastapi import APIRouter, status, Depends

from app_infra.routes import LogRoute
from data.order import OrderRepoABC, OrderRepo
from model.model import OrderBase, Order
from service.auth import AuthService
from service.order import OrderServiceABC, OrderService

router = APIRouter(route_class=LogRoute, prefix='/order', tags=['Order'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Order)
async def create(
    order: OrderBase,
    user_id = Depends(AuthService.get_current_user_id),
    order_service: OrderServiceABC = Depends(OrderService),
):
    return await order_service.create(order, user_id)


@router.get("/{pk}", response_model=Order)
async def get(
        pk: int,
        user_id: int = Depends(AuthService.get_current_user_id),
        order_repo: OrderRepoABC = Depends(OrderRepo),
):
    return await order_repo.get_one_for_user(pk=pk, user_id=user_id)