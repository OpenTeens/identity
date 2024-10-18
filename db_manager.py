from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(
    "sqlite+aiosqlite:///data.db",
    echo=True,
    future=True,
    connect_args={"check_same_thread": False},
)

session_maker = async_sessionmaker(engine)


async def get_db():
    async with session_maker() as db:
        yield db
