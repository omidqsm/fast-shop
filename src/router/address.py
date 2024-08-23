from fastapi import APIRouter, status, Depends

from app_infra.routes import LogRoute
from data.Address import AddressRepoABC, AddressRepo
from model.orm import Address
from model.schema import AddressBase
from service.address import AddressServiceABC, AddressService
from service.auth import AuthService

router = APIRouter(route_class=LogRoute, prefix='/address', tags=['Address'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AddressBase)
async def create(
    address: AddressBase,
    address_repo: AddressRepoABC = Depends(AddressRepo),
    user_id = Depends(AuthService.get_current_user_id)
):
    address_model: Address = address.to_model()
    address_model.user_id = user_id
    await address_repo.add(address_model)
    return address_model


@router.get("/{pk}", response_model=AddressBase)
async def get(
    pk: int,
    address_repo: AddressRepoABC = Depends(AddressRepo)
):
    return await address_repo.get_one(pk)

@router.put("/", response_model=AddressBase)
async def put(
    address: AddressBase,
    user_id: int = Depends(AuthService.get_current_user_id),
    address_service: AddressServiceABC = Depends(AddressService)
):
    return await address_service.update(address, user_id)
