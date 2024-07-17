from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

class Lead(Base):
    __tablename__ = 'leads'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
class Admin(Base):
    __tablename__ = 'admins'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20))
    server: Mapped[int] = mapped_column()
    level: Mapped[int] = mapped_column()
    tg_id = mapped_column(BigInteger)
    position: Mapped[str] = mapped_column(String(20))


class Blacklist(Base):
    __tablename__ = 'blacklist'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    reason: Mapped[str] = mapped_column(String(20))
    datetime: Mapped[str] = mapped_column(String(20))


class Messages(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(25))
    message: Mapped[str] = mapped_column(String(800))
    category: Mapped[int] = mapped_column()
    msg_id: Mapped[int] = mapped_column()

class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    description: Mapped[str] = mapped_column(String(800))
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    chat: Mapped[int] = mapped_column()
    thread: Mapped[int] = mapped_column()
    from_admin: Mapped[bool] = mapped_column()


class Mettings_Info(Base):
    __tablename__ = 'meetings'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20))
    server: Mapped[int] = mapped_column()
    level: Mapped[int] = mapped_column()
    datetime_meeting: Mapped[str] = mapped_column(String(25))
    description: Mapped[str] = mapped_column(String(2000))
    tg_id = mapped_column(BigInteger)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)