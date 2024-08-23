from abc import ABC, abstractmethod
from typing import TypeVar, ClassVar

from fastapi import Depends
from sqlalchemy import update, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app_infra.dependencies import get_db_session
from db import async_session_maker
from helpers.exceptions import entity_not_found_exception
from model.orm import Base

T = TypeVar('T')


class RepoABC(ABC):
    model: ClassVar = T

    @abstractmethod
    async def _execute(self, *statements):
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, pk) -> model:
        raise NotImplementedError

    @abstractmethod
    async def add(self, obj) -> model:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, where: dict):
        raise NotImplementedError

    @abstractmethod
    async def update(self, where: dict, values: dict):
        raise NotImplementedError


class Repo(RepoABC):
    model: ClassVar[Base] = Base

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session if isinstance(session, AsyncSession) else async_session_maker()

    async def _execute(self, *statements):
        async with self.session.begin():
            for s in statements:
                await self.session.execute(s)

    async def get_one(self, pk) -> model:
        try:
            return await self.session.get_one(self.model, pk)
        except NoResultFound:
            raise entity_not_found_exception

    async def add(self, obj: Base) -> model:
        async with self.session.begin():
            self.session.add(obj)
        return obj

    async def find_one(self, where: dict) -> model:
        stmt = select(self.model).filter_by(**where)
        return await self.session.scalar(stmt)

    async def update(self, where: dict, values: dict):
        stmt = update(self.model).filter_by(**where).values(**values)
        await self._execute(stmt)
