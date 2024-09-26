from aredis_om import NotFoundError
from fastapi import APIRouter, status, Depends, Security

from app_infra.dependencies import get_redis
from app_infra.routes import LogRoute
from data.product import ProductRepoABC, ProductRepo, ProductCacheRepo, ProductCacheRepoABC
from model.cache import ProductCache
from model.model import ProductBase, ProductOut, Product
from service.auth import AuthService

router = APIRouter(route_class=LogRoute, prefix='/product', tags=['Product'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductOut)
async def create(
    product_in: ProductBase,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    product_cache_repo: ProductCacheRepoABC = Depends(ProductCacheRepo),
    _=Security(AuthService.authorize, scopes=["admin"]),
):
    product = Product.model_validate(product_in)
    await product_repo.in_tran(product)
    await product_cache_repo.save(product)
    return product


@router.get("/{pk}", response_model=ProductOut)
async def get(
    pk: int,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    product_cache_repo: ProductCacheRepoABC = Depends(ProductCacheRepo),
):
    try:
        product = await product_cache_repo.get(pk)
    except NotFoundError:
        product = await product_repo.get_one(id=pk)
        await product_cache_repo.save(product)
    return product


@router.put("/{pk}", response_model=ProductOut)
async def update(
    pk: int,
    product: ProductBase,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    product_cache_repo: ProductCacheRepoABC = Depends(ProductCacheRepo),
    _=Security(AuthService.authorize, scopes=["admin"]),
):
    product_values = product.model_dump()
    update_stmt = product_repo.update({'id': pk}, product_values)
    await product_repo.in_tran(update_stmt)
    product = await product_repo.get_one(id=pk)
    await product_cache_repo.save(product)
    return product


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    pk: int,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    product_cache_repo: ProductCacheRepoABC = Depends(ProductCacheRepo),
    _=Security(AuthService.authorize, scopes=["admin"]),
):
    await product_cache_repo.delete(pk)
    delete_stmt = product_repo.delete(id=pk)
    await product_repo.in_tran(delete_stmt)


@router.get("/", response_model=list[ProductOut])
async def get_all(
    page: int = 1,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    product_cache_repo: ProductCacheRepoABC = Depends(ProductCacheRepo),
):
    limit = 10
    offset = (page-1)*limit
    products = await product_cache_repo.all(offset=offset, limit=limit)
    if not products:
        products = await product_repo.get(offset=offset, limit=limit)
        await product_cache_repo.save(products)
    return products
