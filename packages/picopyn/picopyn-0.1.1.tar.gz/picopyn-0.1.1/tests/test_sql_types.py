import datetime
import os

import pytest
import pytest_asyncio

from picopyn import Pool


@pytest_asyncio.fixture(autouse=True)
async def db_pool():
    dsn = os.environ.get("PICODATA_TEST_CONN", "postgresql://admin:T0psecret@localhost:55432")

    pool = Pool(dsn=dsn)
    await pool.connect()

    await pool.execute('DROP TABLE IF EXISTS "different_types";')

    yield pool

    await pool.execute('DROP TABLE IF EXISTS "different_types";')
    await pool.close()


@pytest.mark.asyncio
async def test_date_type(db_pool):
    await db_pool.execute(
        """
        CREATE TABLE "different_types" (
            id INTEGER PRIMARY KEY,
            dt datetime NOT NULL
        ) USING memtx DISTRIBUTED BY (id) OPTION (TIMEOUT = 3.0);
    """
    )

    # check 00 timezone
    await db_pool.execute("insert into \"different_types\" values(1, '2025-06-10 12:10:08+00');")
    row = await db_pool.fetchrow('select * from "different_types" where id = 1;')
    assert row.get("dt") == datetime.datetime(2025, 6, 10, 12, 10, 8, tzinfo=datetime.UTC)

    # check different timezone
    await db_pool.execute("insert into \"different_types\" values(2, '2025-06-10 12:10:08+03');")
    row = await db_pool.fetchrow('select * from "different_types" where id = 2;')
    assert row.get("dt") == datetime.datetime(
        2025, 6, 10, 12, 10, 8, tzinfo=datetime.timezone(datetime.timedelta(hours=3))
    )

    # check millis
    await db_pool.execute(
        "insert into \"different_types\" values(3, '2025-06-10 12:10:08.001+00');"
    )
    row = await db_pool.fetchrow('select * from "different_types" where id = 3;')
    assert row.get("dt") == datetime.datetime(2025, 6, 10, 12, 10, 8, 1000, tzinfo=datetime.UTC)

    await db_pool.execute(
        'insert into "different_types" values(4, $1);', datetime.date(2025, 6, 10)
    )
    row = await db_pool.fetchrow('select * from "different_types" where id = 4;')
    assert row.get("dt") == datetime.datetime(2025, 6, 10, tzinfo=datetime.UTC)

    await db_pool.execute(
        'insert into "different_types" values(5, $1);', datetime.datetime(2025, 6, 10, 12, 10, 8)
    )
    row = await db_pool.fetchrow('select * from "different_types" where id = 5;')
    assert row.get("dt") == datetime.datetime(2025, 6, 10, 12, 10, 8, tzinfo=datetime.UTC)

    await db_pool.execute(
        'insert into "different_types" values(6, $1);',
        datetime.datetime(2025, 6, 10, 12, 10, 8, tzinfo=datetime.UTC),
    )
    row = await db_pool.fetchrow('select * from "different_types" where id = 6;')
    assert row.get("dt") == datetime.datetime(2025, 6, 10, 12, 10, 8, tzinfo=datetime.UTC)

    await db_pool.execute(
        'insert into "different_types" values(7, $1);',
        datetime.datetime.strptime("2025-06-10 12:10:08.001+0000", "%Y-%m-%d %H:%M:%S.%f%z"),
    )
    row = await db_pool.fetchrow('select * from "different_types" where id = 7;')
    assert row.get("dt") == datetime.datetime(2025, 6, 10, 12, 10, 8, 1000, tzinfo=datetime.UTC)
