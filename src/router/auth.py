from fastapi import APIRouter, Depends, status

from app_infra.routes import LogRoute
from config import settings
from model.orm import User, UserIn, UserOut
from model.schema import Token, PhoneLogin
from service.auth import AuthServiceABC, AuthService

# todo: we should avoid logging for signup and login apis, since the carry sensitive data

# todo: we should avoid pass credentials in query string though its being encrypted with SSL. because it may get
#       logged in web server logs like nginx or even fastapi itself (second case happens because of our recklessness)


router = APIRouter(route_class=LogRoute, prefix=settings.auth_route_prefix, tags=['Auth'])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def signup(
    user_in: UserIn,
    auth_service: AuthServiceABC = Depends(AuthService)
):
    return await auth_service.signup(user_in)


@router.post("/login", response_model=Token)
async def login(
    login_data: PhoneLogin,
    auth_service: AuthServiceABC = Depends(AuthService)
):
    token = await auth_service.authenticate(login_data.phone, login_data.password)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(AuthService().get_me)):
    return user
