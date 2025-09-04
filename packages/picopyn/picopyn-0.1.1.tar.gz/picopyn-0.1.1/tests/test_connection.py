import asyncio
import os

import pytest
import pytest_asyncio

import picopyn


@pytest_asyncio.fixture(autouse=True)
async def db_conn():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")

    conn = picopyn.Connection(dsn)
    await conn.connect()

    await conn.execute('DROP TABLE IF EXISTS "warehouse";')

    await conn.execute(
        """
        CREATE TABLE "warehouse" (id INTEGER NOT NULL, item TEXT NOT NULL, PRIMARY KEY (id)) USING memtx DISTRIBUTED BY (id) OPTION (TIMEOUT = 3.0);
    """
    )

    yield conn

    await conn.execute('DROP TABLE IF EXISTS "warehouse";')
    await conn.close()


@pytest.mark.asyncio
async def test_simple_connect():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    conn = picopyn.Connection(dsn)
    try:
        await asyncio.wait_for(conn.connect(), timeout=5)
        print("Connected!")
    except TimeoutError:
        print("Timeout during connect()!")
        raise
    finally:
        await conn.close()
        print("Connection closed")


@pytest.mark.asyncio
async def test_connect_to_un_existent_node():
    dsn = "postgresql://admin:T0psecret@non_existent:55432"
    conn = picopyn.Connection(dsn)

    with pytest.raises(
        RuntimeError,
        match=r"Failed to connect to picodata instance using DSN postgresql://admin:T0psecret@non_existent:55432.*",
    ):
        await asyncio.wait_for(conn.connect(), timeout=5)


@pytest.mark.asyncio
async def test_insert_query(db_conn):
    res = await db_conn.execute('INSERT INTO "warehouse" VALUES ($1::int, $2::varchar)', 1, "test")
    assert res == "INSERT 0 1"


@pytest.mark.asyncio
async def test_select_test(db_conn):
    res = await db_conn.execute('INSERT INTO "warehouse" VALUES ($1::int, $2::varchar)', 1, "test")
    assert res == "INSERT 0 1"

    await asyncio.sleep(0.5)

    res = await db_conn.fetchrow("SELECT * FROM warehouse WHERE id = $1::int", 1)
    assert res.get("id") == 1
    assert res.get("item") == "test"


@pytest.mark.asyncio
async def test_delete_test(db_conn):
    res = await db_conn.execute("INSERT INTO warehouse VALUES ($1::int, $2::varchar)", 1, "test")
    assert res == "INSERT 0 1"

    res = await db_conn.fetchrow("SELECT COUNT(*) FROM warehouse;")
    assert res[0] == 1

    res = await db_conn.execute("DELETE FROM warehouse;")
    assert res == "DELETE 1"

    res = await db_conn.fetchrow("SELECT COUNT(*) FROM warehouse;")
    assert res[0] == 0


@pytest.mark.asyncio
async def test_invalid_execute(db_conn):
    with pytest.raises(
        RuntimeError,
        match=r"Failed to execute SQL query: sbroad: space non-existent not found. Query: .*",
    ):
        await db_conn.execute('INSERT INTO "non-existent" VALUES ($1::int, $2::varchar)', 1, "test")


@pytest.mark.asyncio
async def test_invalid_fetch(db_conn):
    with pytest.raises(
        RuntimeError,
        match=r'Failed to execute SQL query and fetch result: sbroad: table with name "non-existent" not found. Query: .*',
    ):
        await db_conn.fetch('SELECT * FROM "non-existent"')


@pytest.mark.asyncio
async def test_invalid_fetchrow(db_conn):
    with pytest.raises(
        RuntimeError,
        match=r'Failed to execute SQL query and fetch row: sbroad: table with name "non-existent" not found. Query: .*',
    ):
        await db_conn.fetchrow('SELECT * FROM "non-existent"')
