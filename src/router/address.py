from fastapi import APIRouter, status, Depends

from app_infra.routes import LogRoute
from data.Address import AddressRepoABC, AddressRepo
from model.model import Address, AddressBase, AddressOut
from service.auth import AuthService

router = APIRouter(route_class=LogRoute, prefix='/address', tags=['Address'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AddressOut)
async def create(
    address_in: AddressBase,
    address_repo: AddressRepoABC = Depends(AddressRepo),
    user_id = Depends(AuthService.get_current_user_id)
):
    address = Address.model_validate(address_in, update={'user_id': user_id})
    await address_repo.in_tran(address)
    return address


@router.get("/{pk}", response_model=AddressOut)
async def get(
    pk: int,
    user_id: int = Depends(AuthService.get_current_user_id),
    address_repo: AddressRepoABC = Depends(AddressRepo)
):
    return await address_repo.get_one(id=pk, user_id=user_id)


@router.put("/{pk}", response_model=AddressOut)
async def update(
    pk: int,
    address: AddressBase,
    user_id: int = Depends(AuthService.get_current_user_id),
    address_repo: AddressRepoABC = Depends(AddressRepo),
):
    where = {'id': pk, 'user_id': user_id}
    update_stmt = address_repo.update(where=where, values=address.model_dump())
    await address_repo.in_tran(update_stmt)
    return await address_repo.get_one(**where)


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    pk: int,
    user_id: int = Depends(AuthService.get_current_user_id),
    address_repo: AddressRepoABC = Depends(AddressRepo)
):
    delete_stmt = address_repo.delete(id=pk, user_id=user_id)
    await address_repo.in_tran(delete_stmt)