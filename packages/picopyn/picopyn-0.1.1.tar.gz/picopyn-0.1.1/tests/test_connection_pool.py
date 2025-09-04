import asyncio
import os

import pytest
import pytest_asyncio

from picopyn import Connection, Pool


class DummyConnection:
    def __init__(self, name):
        self.name = name

    async def connect(self):
        pass

    async def close(self):
        pass

    async def execute(self, *args):
        return f"Executed on {self.name}"

    async def fetch(self, *args):
        return [f"Fetched from {self.name}"]

    async def fetchrow(self, *args):
        return f"Fetched row from {self.name}"


@pytest_asyncio.fixture(autouse=True)
async def db_pool():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")

    pool = Pool(dsn=dsn)
    await pool.connect()

    await pool.execute('DROP TABLE IF EXISTS "warehouse";')

    await pool.execute(
        """
        CREATE TABLE "warehouse" (
            id INTEGER NOT NULL,
            item TEXT NOT NULL,
            PRIMARY KEY (id)
        ) USING memtx DISTRIBUTED BY (id) OPTION (TIMEOUT = 3.0);
    """
    )

    yield pool

    await pool.execute('DROP TABLE IF EXISTS "warehouse";')
    await pool.close()


@pytest.mark.asyncio
async def test_insert_with_pool(db_pool):
    res = await db_pool.execute('INSERT INTO "warehouse" VALUES ($1::int, $2::varchar)', 1, "test")
    assert res == "INSERT 0 1"


@pytest.mark.asyncio
async def test_select_with_pool(db_pool):
    await db_pool.execute('INSERT INTO "warehouse" VALUES ($1::int, $2::varchar)', 1, "test")
    await asyncio.sleep(0.5)

    row = await db_pool.fetchrow("SELECT * FROM warehouse WHERE id = $1::int", 1)
    assert row.get("id") == 1
    assert row.get("item") == "test"


@pytest.mark.asyncio
async def test_delete_test(db_pool):
    res = await db_pool.execute("INSERT INTO warehouse VALUES ($1::int, $2::varchar)", 1, "test")
    assert res == "INSERT 0 1"

    res = await db_pool.fetchrow("SELECT COUNT(*) FROM warehouse;")
    assert res[0] == 1

    res = await db_pool.execute("DELETE FROM warehouse;")
    assert res == "DELETE 1"

    res = await db_pool.fetchrow("SELECT COUNT(*) FROM warehouse;")
    assert res[0] == 0


@pytest.mark.asyncio
async def test_pool_acquire_release_behavior():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")

    pool = Pool(dsn=dsn, max_size=2)
    await pool.connect()

    # Изначально весь пул свободен
    assert len(pool._pool) == 2
    assert len(pool._used) == 0

    # Получаем соединение
    conn1 = await pool.acquire()
    assert len(pool._pool) == 1
    assert conn1 in pool._used

    # Получаем второе соединение
    conn2 = await pool.acquire()
    assert len(pool._pool) == 0
    assert conn2 in pool._used

    # Возвращаем одно соединение
    await pool.release(conn1)
    assert len(pool._pool) == 1
    assert conn1 not in pool._used

    # Возвращаем второе соединение
    await pool.release(conn2)
    assert len(pool._pool) == 2
    assert conn2 not in pool._used

    await pool.close()


@pytest.mark.asyncio
async def test_release_unknown_connection_is_ignored():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn)
    await pool.connect()

    external_conn = Connection(dsn)
    await external_conn.connect()

    # Попытка вернуть несуществующее соединение (не должно упасть)
    await pool.release(external_conn)

    # Убедимся, что пул не изменился
    assert external_conn not in pool._pool
    assert external_conn not in pool._used

    await external_conn.close()
    await pool.close()


@pytest.mark.asyncio
async def test_pool_close_closes_all_connections():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=2)
    await pool.connect()

    conn1 = await pool.acquire()
    _ = await pool.acquire()

    # Освобождаем одно соединение
    await pool.release(conn1)

    await pool.close()

    # Пул и used должны быть очищены
    assert len(pool._pool) == 0
    assert len(pool._used) == 0


@pytest.mark.asyncio
async def test_reconnect_pool():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=1)

    await pool.connect()
    await pool.close()

    # После повторного connect всё должно работать
    await pool.connect()
    res = await pool.execute("SELECT 1")
    assert res is not None

    await pool.close()


@pytest.mark.asyncio
async def test_acquire_waits_when_pool_is_exhausted():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=1)
    await pool.connect()

    conn1 = await pool.acquire()

    # Попробуем получить второе соединение (оно должно ждать)
    async def try_acquire():
        return await pool.acquire()

    acquire_task = asyncio.create_task(try_acquire())
    # Дать шанс "зависнуть"
    await asyncio.sleep(0.2)

    # Проверяем, что задача ждет
    assert not acquire_task.done()

    # Освобождаем первое соединение, чтобы второе продолжилось
    await pool.release(conn1)
    # Теперь должно завершиться
    conn2 = await acquire_task

    # Уже используется
    assert conn2 not in pool._pool
    await pool.release(conn2)
    await pool.close()


@pytest.mark.asyncio
async def test_pool_blocks_when_empty():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=1)
    await pool.connect()

    conn = await pool.acquire()
    called = False

    async def try_acquire():
        nonlocal called
        conn2 = await pool.acquire()
        called = True
        await pool.release(conn2)

    asyncio.create_task(try_acquire())

    await asyncio.sleep(0.2)
    assert not called, "acquire не должен сработать, пока соединение не вернули"

    await pool.release(conn)
    await asyncio.sleep(0.2)
    assert called, "acquire должен завершиться после release"

    await pool.close()


@pytest.mark.asyncio
async def test_pool_discover_nodes_enabled():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=10, enable_discovery=True)

    await pool.connect()

    assert len(pool._pool) == 10

    # get amount of picodata nodes
    helper_conn = Connection(dsn)
    await helper_conn.connect()
    instances = await helper_conn.fetch(
        """
        SELECT i.name, i.raft_id, i.current_state, p.address
        FROM _pico_instance i
        JOIN _pico_peer_address p ON i.raft_id = p.raft_id
        WHERE p.connection_type = 'pgproto';
    """
    )
    expected_picodata_instance_amount = len(set(instances))

    # check that poll contains connections to all picodata nodes
    unique_addresses = set()
    for conn in pool._pool:
        addr = conn.conn._addr
        unique_addresses.add(addr)

    assert len(unique_addresses) == expected_picodata_instance_amount

    await pool.close()


@pytest.mark.asyncio
async def test_pool_discover_nodes_disabled():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=10, enable_discovery=False)

    await pool.connect()

    assert len(pool._pool) == 10

    # check that poll contains connections to 1 picodata node
    unique_addresses = set()
    for conn in pool._pool:
        addr = conn.conn._addr
        unique_addresses.add(addr)

    assert len(unique_addresses) == 1

    await pool.close()


@pytest.mark.asyncio
async def test_pool_idempotent_connect():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=10, enable_discovery=True)

    await pool.connect()

    original_conns = list(pool._pool)

    await pool.connect()

    second_conns = list(pool._pool)

    # check that second call `connect` does not change anything
    for conn1, conn2 in zip(original_conns, second_conns, strict=False):
        assert conn1 is conn2

    try:
        await pool.close()
        await pool.close()
    except Exception as e:
        pytest.fail(f"Second call close() raised an unexpected error: {e}")


@pytest.mark.asyncio
async def test_pool_all_nodes_work():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=10, enable_discovery=True)

    await pool.connect()

    conns = [await pool.acquire() for _ in range(10)]

    for conn in conns:
        result = await conn.fetch("SELECT 1;")
        assert result == [(1,)]

    for conn in conns:
        await pool.release(conn)

    await pool.close()


@pytest.mark.asyncio
async def test_pool_with_invalid_dsn_and_discover_nodes_enabled():
    dsn = "postgresql://admin:T0psecret@picodata-invalid:5432"
    pool = Pool(dsn=dsn, max_size=10, enable_discovery=True)

    with pytest.raises(RuntimeError) as excinfo:
        await pool.connect()

    assert f"Failed to discover instances using DSN {dsn}" in str(excinfo.value)


@pytest.mark.asyncio
async def test_pool_with_invalid_dsn_and_discover_nodes_disabled():
    dsn = "postgresql://admin:T0psecret@picodata-invalid:5432"
    pool = Pool(dsn=dsn, max_size=10, enable_discovery=False)

    with pytest.raises(RuntimeError) as excinfo:
        await pool.connect()

    assert f"Could not connect to main node {dsn}" in str(excinfo.value)


@pytest.mark.asyncio
async def test_pool_connection_queue_with_discover_nodes_enabled_and_round_robin_strategy():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=4, enable_discovery=True)

    await pool.connect()

    # get amount of picodata nodes
    helper_conn = Connection(dsn)
    await helper_conn.connect()
    instances = await helper_conn.fetch(
        """
        SELECT i.name, i.raft_id, i.current_state, p.address
        FROM _pico_instance i
        JOIN _pico_peer_address p ON i.raft_id = p.raft_id
        WHERE p.connection_type = 'pgproto';
    """
    )
    expected_picodata_instance_amount = len(set(instances))

    acquired_addrs = []
    for _ in range(8):
        conn = await pool.acquire()
        acquired_addrs.append(conn.conn._addr)
        await pool.release(conn)

    first_cycle = acquired_addrs[:4]
    second_cycle = acquired_addrs[4:]

    assert (
        len(set(first_cycle)) == expected_picodata_instance_amount
    ), f"Expected {expected_picodata_instance_amount} unique connections"
    assert first_cycle == second_cycle, "Connection addresses are not reused in round-robin order"

    await pool.close()


@pytest.mark.asyncio
async def test_pool_with_custom_balance_strategy():
    # custom strategy always choose first connection
    def custom_strategy(pool_conns):
        return pool_conns[0]

    conns = [DummyConnection(f"conn{i}") for i in range(3)]

    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=3, balance_strategy=custom_strategy)
    # fill pool manually
    pool._pool.clear()
    pool._pool.extend(conns)

    conn = await pool.acquire()
    assert conn.name == "conn0"
    await pool.release(conn)


@pytest.mark.asyncio
async def test_pool_with_custom_balance_strategy_raised_exception():
    def custom_strategy(pool_conns):
        return pool_conns[3]

    conns = [DummyConnection(f"conn{i}") for i in range(3)]

    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=3, balance_strategy=custom_strategy)
    # fill pool manually
    pool._pool.clear()
    pool._pool.extend(conns)

    with pytest.raises(
        RuntimeError, match="balance_strategy raised an exception: list index out of range"
    ):
        await pool.acquire()


@pytest.mark.asyncio
async def test_custom_strategy_returns_invalid_connection():
    conns = [DummyConnection(f"conn{i}") for i in range(2)]

    # custom strategy returns connection that doesn't belong to pool
    def bad_strategy(pool_conns):
        return DummyConnection("invalid")

    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")
    pool = Pool(dsn=dsn, max_size=2, balance_strategy=bad_strategy)
    pool._pool.clear()
    pool._pool.extend(conns)

    with pytest.raises(RuntimeError, match="balance_strategy returned a connection not in pool"):
        await pool.acquire()


@pytest.mark.asyncio
async def test_invalid_execute(db_pool):
    with pytest.raises(
        RuntimeError,
        match=r"Failed to execute SQL query: sbroad: space non-existent not found. Query: .*",
    ):
        await db_pool.execute('INSERT INTO "non-existent" VALUES ($1::int, $2::varchar)', 1, "test")


@pytest.mark.asyncio
async def test_invalid_fetch(db_pool):
    with pytest.raises(
        RuntimeError,
        match=r'Failed to execute SQL query and fetch result: sbroad: table with name "non-existent" not found. Query: .*',
    ):
        await db_pool.fetch('SELECT * FROM "non-existent"')


@pytest.mark.asyncio
async def test_invalid_fetchrow(db_pool):
    with pytest.raises(
        RuntimeError,
        match=r'Failed to execute SQL query and fetch row: sbroad: table with name "non-existent" not found. Query: .*',
    ):
        await db_pool.fetchrow('SELECT * FROM "non-existent"')
