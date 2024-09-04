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
    async def find_one(self, **where):
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, **where):
        raise NotImplementedError

    @abstractmethod
    async def get_by_ids(self, ids: list):
        raise NotImplementedError

    @abstractmethod
    async def get(self, limit, offset, **where):
        raise NotImplementedError

    @abstractmethod
    def update(self, where: dict, values: dict):
        raise NotImplementedError

    @abstractmethod
    def delete(self, **where):
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

    async def get(self, limit=10, offset=0, **where):
        stmt = select(self.model).where(**where).offset(offset).limit(limit)
        async with self.session as s:
            return (await s.scalars(stmt)).all()

    async def find_one(self, **where) -> model:
        stmt = select(self.model).filter_by(**where)
        async with self.session:
            return await self.session.scalar(stmt)

    async def exists(self, **where) -> bool:
        # stmt = exists(1).where(*where).select()  # second way
        stmt = select(self.model.id).filter_by(**where).exists()
        async with self.session as s:
            return await s.scalar(select(stmt))

    def update(self, where: dict, values: dict) -> Update:
        stmt = update(self.model).filter_by(**where).values(**values)
        return stmt

    def delete(self, **where) -> Delete:
        stmt = delete(self.model).filter_by(**where)
        return stmt

    async def in_tran(self, *objects: SQLModel | Insert | Update | Delete):
        async with self.session.begin():
            for obj in objects:
                if isinstance(obj, SQLModel):
                    self.session.add(obj)
                else:
                    await self.session.execute(obj)
