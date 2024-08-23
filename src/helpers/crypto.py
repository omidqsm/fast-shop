import dataclasses
from abc import ABC
from datetime import datetime, timedelta

import jwt
from fastapi import Depends
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext

from config import settings
from helpers.exceptions import credentials_exception
from model.orm import User


class CryptoABC(ABC):

    @classmethod
    def verify_hash(cls, string: str, hashed_string: str) -> bool:
        raise NotImplementedError

    @classmethod
    def get_hash(cls, string: str) -> str:
        raise NotImplementedError

    @classmethod
    def create_access_token(cls, user) -> str:
        raise NotImplementedError

    @classmethod
    def parse_token(cls, token: str) -> dict:
        raise NotImplementedError


@dataclasses.dataclass
class Crypto(CryptoABC):
    crypto_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    algorithm = 'HS512'

    @classmethod
    def verify_hash(cls, string: str, hashed_string: str) -> bool:
        return cls.crypto_context.verify(string, hashed_string)

    @classmethod
    def get_hash(cls, string: str) -> str:
        return cls.crypto_context.hash(string)

    @classmethod
    def create_access_token(cls, user: User) -> str:
        exp_datetime = datetime.now(tz=settings.timezone) + timedelta(seconds=settings.token_expire_seconds)
        payload = {'sub': user.id, 'scopes': user.scopes.split(), 'exp': exp_datetime}
        token = jwt.encode(payload, settings.secret_key, algorithm=cls.algorithm)
        return token

    @classmethod
    def parse_token(cls, token: str = Depends(settings.auth_scheme)) -> dict:
        """parses and verifies the access token and returns its payload"""
        try:
            # decode and verify token
            payload = jwt.decode(token, settings.secret_key, algorithms=[cls.algorithm])
            return payload
        except (ExpiredSignatureError, InvalidTokenError):
            raise credentials_exception
