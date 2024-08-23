from fastapi import APIRouter, status, Depends

from app_infra.routes import LogRoute
from data.product import ProductRepoABC, ProductRepo
from model.schema import ProductBase

router = APIRouter(route_class=LogRoute, prefix='/product', tags=['Product'])

# todo: in product creation we should make sure product belongs to the user

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductBase)
async def create(
    product: ProductBase,
    product_repo: ProductRepoABC = Depends(ProductRepo)
):
    product_model = product.to_model()
    await product_repo.add(product_model)
    return product_model


@router.get("/{pk}", response_model=ProductBase)
async def get(
    pk: int,
    product_repo: ProductRepoABC = Depends(ProductRepo)
):
    return await product_repo.get_one(pk)

