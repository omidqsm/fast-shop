from abc import ABC

from sqlalchemy import select

from data import RepoABC, Repo
from model.orm import User


class UserRepoABC(RepoABC, ABC):
    async def get_one_by_phone(self, phone: str):
        raise NotImplementedError


class UserRepo(Repo, UserRepoABC):
    model = User

    async def get_one_by_phone(self, phone: str) -> User:
        stmt = select(User).where(User.phone == phone)
        user = await self.session.scalar(stmt)
        return user
