from abc import ABC
from dataclasses import dataclass

from fastapi import Depends
from sqlalchemy import values

from data.Address import AddressRepoABC, AddressRepo
from model.orm import Address
from model.schema import AddressBase


@dataclass
class AddressServiceABC(ABC):
    address_repo: AddressRepoABC

    async def update(self, address, user_id):
        raise NotImplementedError


class AddressService(AddressServiceABC):

    def __init__(self, address_repo: AddressRepoABC = Depends(AddressRepo)):
        self.address_repo = address_repo if isinstance(address_repo, AddressRepoABC) else AddressRepo()

    async def update(self, address: AddressBase, user_id: int) -> Address:
        address_values = address.model_dump()
        filters = {'id': address_values.pop('id'), 'user_id': user_id}
        await self.address_repo.update(where=filters, values=address_values)
        updated_address = await self.address_repo.find_one(where=filters)
        return updated_address

