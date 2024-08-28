from abc import ABC

from data._base import RepoABC, Repo
from model.model import Address


class AddressRepoABC(RepoABC, ABC):
    pass


class AddressRepo(Repo, AddressRepoABC):
    model = Address
