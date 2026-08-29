import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

import db.session as session_module


@pytest.mark.asyncio
async def test_init_db_creates_all_tables(monkeypatch):
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    monkeypatch.setattr(session_module, "engine", test_engine)

    await session_module.init_db()

    async with test_engine.connect() as conn:
        table_names = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())

    assert set(table_names) == {"users", "chats", "messages", "business_connections"}

    await test_engine.dispose()


def test_async_session_local_has_expire_on_commit_disabled():
    assert session_module.AsyncSessionLocal.kw.get("expire_on_commit") is False
