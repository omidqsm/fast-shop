from fastapi import APIRouter, status, Depends, Security

from app_infra.routes import LogRoute
from data.product import ProductRepoABC, ProductRepo
from model.model import ProductBase, ProductOut, Product
from service.auth import AuthService

router = APIRouter(route_class=LogRoute, prefix='/product', tags=['Product'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductOut)
async def create(
    product_in: ProductBase,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    _=Security(AuthService.authorize, scopes=["admin"]),
):
    product = Product.model_validate(product_in)
    await product_repo.add(product)
    return product


@router.get("/{pk}", response_model=ProductOut)
async def get(
    pk: int,
    product_repo: ProductRepoABC = Depends(ProductRepo)
):
    return await product_repo.get_one(id=pk)


@router.put("/{pk}", response_model=ProductOut)
async def update(
    pk: int,
    product: ProductBase,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    _=Security(AuthService.authorize, scopes=["admin"]),
):
    product_values = product.model_dump()
    await product_repo.update({'id': pk}, product_values)
    return await product_repo.get_one(id=pk)


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    pk: int,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    _=Security(AuthService.authorize, scopes=["admin"]),
):
    await product_repo.delete(id=pk)


@router.get("/", response_model=list[ProductOut])
async def get(
    page: int = 1,
    product_repo: ProductRepoABC = Depends(ProductRepo)
):
    limit = 10
    return await product_repo.get(offset=(page-1)*limit, limit=limit)
