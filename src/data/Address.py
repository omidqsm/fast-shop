from abc import ABC, abstractmethod

from sqlalchemy import update

from data import RepoABC, Repo
from model.orm import Address


class AddressRepoABC(RepoABC, ABC):
    pass


class AddressRepo(Repo, AddressRepoABC):
    model = Address
