from typing import Annotated

from fastapi import APIRouter, status, Depends, Security

from app_infra.routes import LogRoute
from data.product import ProductRepoABC, ProductRepo
from model.schema import ProductBase
from service.auth import AuthService

router = APIRouter(route_class=LogRoute, prefix='/product', tags=['Product'])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductBase)
async def create(
    product: ProductBase,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    _ = Security(AuthService.authorize, scopes=["admin"]),
):
    product_model = product.to_model()
    await product_repo.add(product_model)
    return product_model

@router.get("/{pk}", response_model=ProductBase)
async def get(
    pk: int,
    product_repo: ProductRepoABC = Depends(ProductRepo)
):
    return await product_repo.get_one(id=pk)


@router.put("/", response_model=ProductBase)
async def update(
    product: ProductBase,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    _ = Security(AuthService.authorize, scopes=["admin"]),
):
    product_values = product.model_dump()
    pk = product_values.get('id')
    await product_repo.update({'id': pk}, product_values)
    return await product_repo.get_one(id=pk)


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    pk: int,
    product_repo: ProductRepoABC = Depends(ProductRepo),
    _ = Security(AuthService.authorize, scopes=["admin"]),
):
    await product_repo.delete(id=pk)
