from typing import Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from Osdental.Exception.ControlledException import DatabaseException
from Osdental.Shared.Enums.Message import Message

class UnitOfWork:
    def __init__(self, session: AsyncSession, repositories: Dict[str, Any] = None):
        self.session = session
        self._repositories = repositories or {}
        self._instances = {}

    def __getattr__(self, item):
        if item in self._instances:
            return self._instances[item]
        raise AttributeError(f"'UnitOfWork' object has no attribute '{item}'")

    @asynccontextmanager
    async def __call__(self):
        try:
            async with self.session.begin():
                self._instances = {name: repo_cls(self.session) for name, repo_cls in self._repositories.items()}
                try:
                    yield self
                except Exception:
                    await self.session.rollback()
                    raise
                else:
                    await self.session.commit()
        except Exception as err:
            raise DatabaseException(message=Message.DATABASE_EXECUTION_ERROR_MSG, error=str(err))
        finally:
            self._instances.clear()
