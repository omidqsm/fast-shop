from abc import ABC, abstractmethod
from typing import ClassVar, Iterable

from fastapi import Depends
from multimethod import multimethod
from sqlalchemy import update, select, delete, Delete, Update, Insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app_infra.dependencies import get_db_session
from db import async_session_maker
from helpers.exceptions import entity_not_found_exception
from model.model import Base


class RepoABC[T](ABC):
    model: ClassVar = T

    @abstractmethod
    async def _execute(self, *statements):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **where):
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, **where):
        raise NotImplementedError

    @abstractmethod
    async def get_by_ids(self, ids: list):
        raise NotImplementedError

    @abstractmethod
    async def add(self, obj) -> model | list[model]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, where: dict, values: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **where):
        raise NotImplementedError

    @abstractmethod
    async def exists(self, **where) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def in_tran(self, *objects):
        raise NotImplementedError


class Repo(RepoABC):
    model: ClassVar[Base] = Base

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session if isinstance(session, AsyncSession) else async_session_maker()

    async def _execute(self, *statements):
        async with self.session.begin():
            for s in statements:
                await self.session.execute(s)
        # for s in statements:
        #     await self.session.execute(s)
        # await self.session.commit()

    async def get_one(self, **where):
        try:
            stmt = select(self.model).filter_by(**where)
            async with self.session as s:
                return (await s.scalars(stmt)).one()
        except NoResultFound:
            raise entity_not_found_exception

    async def get_by_ids(self, ids: list[int]) -> Iterable[model]:
        from sqlmodel import col
        stmt = select(self.model).where(col(self.model.id).in_(ids))
        async with self.session as s:
            return (await s.scalars(stmt)).all()

    async def find_one(self, **where) -> model:
        stmt = select(self.model).filter_by(**where)
        async with self.session:
            return await self.session.scalar(stmt)

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

    async def update(self, where: dict, values: dict) -> None:
        stmt = update(self.model).filter_by(**where).values(**values)
        await self._execute(stmt)

    async def delete(self, **where) -> None:
        stmt = delete(self.model).filter_by(**where)
        await self._execute(stmt)

    async def exists(self, **where) -> bool:
        # stmt = exists(1).where(*where).select()  # second way
        stmt = select(self.model.id).filter_by(**where).exists()
        async with self.session as s:
            return await s.scalar(select(stmt))

    async def in_tran(self, *objects: SQLModel | Insert | Update | Delete):
        async with self.session.begin():
            for obj in objects:
                if isinstance(obj, SQLModel):
                    self.session.add(obj)
                else:
                    await self.session.execute(obj)
