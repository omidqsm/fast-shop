from abc import ABC

from data._base import RepoABC, Repo, CacheRepo, CacheRepoABC
from model.cache import ProductCache
from model.model import Product


class ProductRepoABC(RepoABC, ABC):
    pass


class ProductRepo(Repo, ProductRepoABC):
    model = Product


class ProductCacheRepoABC(CacheRepoABC, ABC):
    pass


class ProductCacheRepo(CacheRepo, ProductCacheRepoABC):
    model = ProductCache
