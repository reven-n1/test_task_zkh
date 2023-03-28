from sqlalchemy.ext.asyncio.engine import create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.pool import NullPool
import sqlalchemy
import asyncio
from config import ProductionConfig as config

Base = declarative_base()
metadata = Base.metadata


class AsyncObj:
    def __init__(self, *args, **kwargs):
        """ Standard constructor used for arguments pass """
        self.__storedargs = args, kwargs
        self.async_initialized = False

    async def __ainit__(self, *args, **kwargs):
        """ Async constructor, you should implement this """

    async def __initobj(self):
        """ Crutch used for __await__ after spawning """
        assert not self.async_initialized
        self.async_initialized = True
        await self.__ainit__(*self.__storedargs[0], **self.__storedargs[1])
        return self

    def __await__(self):
        return self.__initobj().__await__()

    def __init_subclass__(cls, **kwargs):
        assert asyncio.iscoroutinefunction(cls.__ainit__)

    @property
    def async_state(self):
        if not self.async_initialized:
            return "[initialization pending]"
        return "[initialization done and successful]"


class Database(AsyncObj):
    _instance: 'Database' = None

    async def __ainit__(self):
        self.__config = config
        self.__engine: AsyncEngine = create_async_engine(self.prepare_connection_string(), poolclass=NullPool, echo=False)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    @classmethod
    async def get_class_session(cls) -> AsyncSession:
        cls_obj = await cls()
        return cls_obj.__get_session()

    def __get_session(self) -> AsyncSession:
        return sqlalchemy.orm.sessionmaker(bind=self.__engine, class_=AsyncSession)()

    def prepare_connection_string(self) -> str:
        """ returns connection string """
        return f"mysql+aiomysql://{self.__config.login}:{self.__config.password}@{self.__config.url}:" \
               f"{self.__config.port}/{self.__config.db}"