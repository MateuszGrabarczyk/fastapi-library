import pytest
from sqlalchemy import CheckConstraint, event, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from app import db as app_db
from app.db import Base


@pytest.fixture(scope="session", autouse=True)
async def _create_test_db():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
        poolclass=StaticPool,
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    TestSessionLocal = async_sessionmaker(
        bind=engine, expire_on_commit=False, class_=AsyncSession
    )
    app_db.engine = engine
    app_db.SessionLocal = TestSessionLocal

    for table in Base.metadata.tables.values():
        for c in list(table.constraints):
            if isinstance(c, CheckConstraint) and "~" in str(getattr(c, "sqltext", "")):
                table.constraints.remove(c)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    await engine.dispose()


@pytest.fixture(autouse=True)
async def _clean_and_seed():
    async with app_db.engine.begin() as conn:
        for t in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'DELETE FROM "{t.name}"'))
    from sqlalchemy import insert
    from app.models.user import User

    async with app_db.SessionLocal() as s:
        await s.execute(
            insert(User).values(
                [
                    {"first_name": "U", "last_name": "One", "card_number": "111111"},
                    {"first_name": "U", "last_name": "Two", "card_number": "222222"},
                    {"first_name": "U", "last_name": "Three", "card_number": "333333"},
                ]
            )
        )
        await s.commit()


@pytest.fixture
async def session() -> AsyncSession:  # type: ignore
    async with app_db.SessionLocal() as session:
        yield session  # type: ignore
