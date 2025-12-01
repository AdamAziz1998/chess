from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Your provided settings
DB_SETTINGS = {
    "dbname": "chessdb",
    "user": "adamAziz",
    "password": "PACIFICPUNCH1998!",
    "host": "localhost",
    "port": "5432"
}

# CONSTRUCTED URL
# We use an f-string to inject the values from the dictionary above
DATABASE_URL = (
    f"postgresql+asyncpg://{DB_SETTINGS['user']}:{DB_SETTINGS['password']}"
    f"@{DB_SETTINGS['host']}:{DB_SETTINGS['port']}/{DB_SETTINGS['dbname']}"
)

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session