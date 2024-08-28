from abc import ABC

from data._base import RepoABC, Repo
from model.model import Product


class ProductRepoABC(RepoABC, ABC):
    pass


class ProductRepo(Repo, ProductRepoABC):
    model = Product
