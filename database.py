import os

from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


load_dotenv(find_dotenv())

engine = create_async_engine(os.getenv('DB_URL'), echo=True)
new_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


class Model(DeclarativeBase):
    pass


class TaskOrm(Model):
    __tablename__ = "address_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str]
    balance: Mapped[float]
    bandwidth: Mapped[float]
    energy: Mapped[float]


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
