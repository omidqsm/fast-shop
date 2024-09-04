from fastapi import APIRouter, status, Depends

from app_infra.routes import LogRoute
from data.order import OrderRepoABC, OrderRepo
from model.model import OrderIn, OrderCreateOut, OrderOut
from service.auth import AuthService
from service.order import OrderServiceABC, OrderService

router = APIRouter(route_class=LogRoute, prefix='/order', tags=['Order'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderCreateOut)
async def create(
    order: OrderIn,
    user_id=Depends(AuthService.get_current_user_id),
    order_service: OrderServiceABC = Depends(OrderService),
):
    order = await order_service.create(order, user_id)
    return order


@router.get("/{pk}", response_model=OrderOut)
async def get(
    pk: int,
    user_id: int = Depends(AuthService.get_current_user_id),
    order_repo: OrderRepoABC = Depends(OrderRepo),
):
    return await order_repo.get_one(pk=pk, user_id=user_id)


@router.get("/", response_model=list[OrderOut])
async def get_all(
    page: int = 1,
    user_id: int = Depends(AuthService.get_current_user_id),
    order_repo: OrderRepoABC = Depends(OrderRepo),
):
    limit = 10
    return await order_repo.get(offset=(page-1)*limit, limit=limit, user_id=user_id)