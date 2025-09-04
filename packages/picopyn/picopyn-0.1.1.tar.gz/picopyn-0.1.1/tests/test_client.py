import asyncio
import os

import pytest
import pytest_asyncio

import picopyn


@pytest_asyncio.fixture(autouse=True)
async def db_client():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")

    client = picopyn.Client(dsn)
    await client.connect()

    await client.execute('DROP TABLE IF EXISTS "warehouse";')

    await client.execute(
        """
        CREATE TABLE "warehouse" (id INTEGER NOT NULL, item TEXT NOT NULL, PRIMARY KEY (id)) USING memtx DISTRIBUTED BY (id) OPTION (TIMEOUT = 3.0);
    """
    )

    yield client

    await client.execute('DROP TABLE IF EXISTS "warehouse";')
    await client.close()


@pytest.mark.asyncio
async def test_simple_connect():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    client = picopyn.Client(dsn)
    try:
        await asyncio.wait_for(client.connect(), timeout=5)
        print("Client connected!")
    except TimeoutError:
        print("Timeout during connect()!")
        raise
    finally:
        await client.close()
        print("Client closed")


@pytest.mark.asyncio
async def test_different_pool_size():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    client = picopyn.Client(dsn, pool_size=100)
    await client.connect()

    assert len(client._pool._pool) == 100


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
async def test_insert_query(db_client):
    res = await db_client.execute(
        'INSERT INTO "warehouse" VALUES ($1::int, $2::varchar)', 1, "test"
    )
    assert res == "INSERT 0 1"


@pytest.mark.asyncio
async def test_select_test(db_client):
    res = await db_client.execute(
        'INSERT INTO "warehouse" VALUES ($1::int, $2::varchar)', 1, "test"
    )
    assert res == "INSERT 0 1"

    await asyncio.sleep(0.5)

    res = await db_client.fetchrow("SELECT * FROM warehouse WHERE id = $1::int", 1)
    assert res.get("id") == 1
    assert res.get("item") == "test"


@pytest.mark.asyncio
async def test_delete_test(db_client):
    res = await db_client.execute("INSERT INTO warehouse VALUES ($1::int, $2::varchar)", 1, "test")
    assert res == "INSERT 0 1"

    res = await db_client.fetchrow("SELECT COUNT(*) FROM warehouse;")
    assert res[0] == 1

    res = await db_client.execute("DELETE FROM warehouse;")
    assert res == "DELETE 1"

    res = await db_client.fetchrow("SELECT COUNT(*) FROM warehouse;")
    assert res[0] == 0


@pytest.mark.asyncio
async def test_invalid_execute(db_client):
    with pytest.raises(
        RuntimeError,
        match=r"Failed to execute SQL query: sbroad: space non-existent not found. Query: .*",
    ):
        await db_client.execute(
            'INSERT INTO "non-existent" VALUES ($1::int, $2::varchar)', 1, "test"
        )


@pytest.mark.asyncio
async def test_invalid_fetch(db_client):
    with pytest.raises(
        RuntimeError,
        match=r'Failed to execute SQL query and fetch result: sbroad: table with name "non-existent" not found. Query: .*',
    ):
        await db_client.fetch('SELECT * FROM "non-existent"')


@pytest.mark.asyncio
async def test_invalid_fetchrow(db_client):
    with pytest.raises(
        RuntimeError,
        match=r'Failed to execute SQL query and fetch row: sbroad: table with name "non-existent" not found. Query: .*',
    ):
        await db_client.fetchrow('SELECT * FROM "non-existent"')
