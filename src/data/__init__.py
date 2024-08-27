from abc import ABC, abstractmethod
from typing import TypeVar, ClassVar, Iterable

from fastapi import Depends
from multimethod import multimethod
from sqlalchemy import update, select, delete, exists, BinaryExpression
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
    async def add(self, obj) -> model | list[model]:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, where: dict, not_found_error=False):
        raise NotImplementedError

    @abstractmethod
    async def update(self, where: dict, values: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, where: dict):
        raise NotImplementedError

    @abstractmethod
    async def exists(self, *where) -> bool:
        raise NotImplementedError


class Repo(RepoABC):
    model: ClassVar[Base] = Base

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session if isinstance(session, AsyncSession) else async_session_maker()

    async def _execute(self, *statements):
        # async with self.session.begin():
        #     for s in statements:
        #         await self.session.execute(s)
        for s in statements:
            await self.session.execute(s)
        await self.session.commit()

    async def get_one(self, pk) -> model:
        try:
            return await self.session.get_one(self.model, pk)
        except NoResultFound:
            raise entity_not_found_exception

    @multimethod
    async def add(self, obj):
        pass

    @add.register
    async def _(self, obj: model) -> model:
        async with self.session.begin():
            self.session.add(obj)
        return obj

    @add.register
    async def _(self, obj: Iterable[model]) -> Iterable[model]:
        async with self.session.begin():
            self.session.add_all(obj)
        return obj

    async def find_one(self, where: dict, not_found_error=False) -> model:
        stmt = select(self.model).filter_by(**where)
        async with self.session:
            obj = await self.session.scalar(stmt)
        if not_found_error and not obj:
            raise entity_not_found_exception
        return obj

    async def update(self, where: dict, values: dict) -> None:
        stmt = update(self.model).filter_by(**where).values(**values)
        await self._execute(stmt)

    async def delete(self, where: dict) -> None:
        stmt = delete(self.model).filter_by(**where)
        await self._execute(stmt)

    async def exists(self, *where: BinaryExpression) -> bool:
        stmt = exists(1).where(*where).select()
        async with self.session as s:
            return await s.scalar(stmt)
