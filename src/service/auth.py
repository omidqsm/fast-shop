import dataclasses
import itertools
from abc import ABC, abstractmethod
from fastapi import Depends, status, HTTPException
from fastapi.security import SecurityScopes
from sqlalchemy.exc import IntegrityError

from data.user import UserRepoABC, UserRepo
from helpers.crypto import Crypto, CryptoABC
from helpers.exceptions import credentials_exception, access_forbidden_exception
from model.model import User, UserIn


@dataclasses.dataclass
class AuthServiceABC(ABC):
    user_repo: UserRepoABC
    crypto: CryptoABC

    @staticmethod
    @abstractmethod
    def get_current_user_id(payload: dict):
        raise NotImplementedError

    @abstractmethod
    async def authenticate(self, phone: str, password: str):
        raise NotImplementedError

    @abstractmethod
    async def signup(self, user_in):
        raise NotImplementedError

    @abstractmethod
    async def get_me(self, pk):
        raise NotImplementedError

class AuthService(AuthServiceABC):

    def __init__(self, user_repo: UserRepoABC = Depends(UserRepo), crypto: CryptoABC = Depends(Crypto)):
        self.user_repo = user_repo if isinstance(user_repo, UserRepoABC) else UserRepo()
        self.crypto = crypto if isinstance(crypto, CryptoABC) else Crypto()

    @staticmethod
    def get_current_user_id(
        payload: dict = Depends(Crypto.parse_token)
    ) -> int:
        user_id = payload.get('sub')
        if user_id is None:
            raise credentials_exception
        return user_id

    @staticmethod
    def authorize(
        security_scopes: SecurityScopes,
        payload: dict = Depends(Crypto.parse_token)
    ):
        # check scopes (permissions)
        user_scopes = payload.get('scopes')
        for scope in security_scopes.scopes:
            if scope not in user_scopes:
                raise access_forbidden_exception

    async def authenticate(self, phone: str, password: str) -> str:
        user = await self.user_repo.get_one_by_phone(phone)
        if not user or not self.crypto.verify_hash(password, user.password):
            raise credentials_exception
        return self.crypto.create_access_token(user)

    async def signup(self, user_in: UserIn) -> User:
        user = User.model_validate(user_in)
        user.password = self.crypto.get_hash(user_in.password.get_secret_value())
        try:
            return await self.user_repo.add(user)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')

    async def get_me(self, pk: int = Depends(get_current_user_id)) -> User:
        return await self.user_repo.get_one(id=pk)
