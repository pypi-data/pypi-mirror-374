import asyncio
import json
import random
import time
from collections import deque
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

import asyncpg

from .connection import Connection


class Pool:
    """A connection pool.

    Connection pool can be used to manage a set of connections to the database.
    Connections are first acquired from the pool, then used, and then released
    back to the pool

    :param dsn (str):  The data source name (e.g., "postgresql://user:pass@host:port") for the cluster.
    :param balance_strategy (callable, optional): A custom strategy function to select a connection
        from the pool. If None, round-robin strategy is used.
    :param max_size (int): Maximum number of connections in the pool. Must be at least 1.
    :param enable_discovery (bool): If True, the pool will automatically discover available
        picodata instances. If False, only the given `dsn` will be used.
    :param balance_strategy (callable, optional): A function that selects a connection from the pool.
        If None, a default round-robin strategy will be used.
    """

    def __init__(
        self,
        dsn: str,
        max_size: int = 10,
        enable_discovery: bool = False,
        balance_strategy: Callable[[list[Connection]], Connection] | None = None,
        **connect_kwargs: Any,
    ) -> None:
        if max_size < 1:
            raise ValueError("max_size must be at least 1")

        self._dsn = dsn
        self._connect_kwargs = connect_kwargs
        self._max_size = max_size
        self._pool: deque[Connection] = deque()
        self._used: set[Connection] = set()
        self._lock: asyncio.Lock = asyncio.Lock()
        self._default_acquire_timeout_sec = 5
        # node discovery mode
        # if disabled, pool will be filled with given address connections
        # if enabled, pool will be filled with available picodata instances
        self.enable_discovery = enable_discovery
        # load balancing strategy:
        # if None, a simple round-robin strategy will be used.
        # otherwise, the provided callable will be used to select connections.
        if balance_strategy is not None and not callable(balance_strategy):
            raise ValueError("balance_strategy must be callable or None")
        self._balance_strategy = balance_strategy

    async def connect(self) -> None:
        """
        Prepares the pool by opening up to `max_size` connections.

        This should be called before using the pool to ensure connections are available.
        """
        async with self._lock:
            if len(self._pool) == self._max_size:
                return

            # if node discovery is enabled, then connect to all alive picodata instances
            # (if they fit within the max_size limit)
            if self.enable_discovery:
                try:
                    instance_addrs = await self._discover_instances()
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to discover instances using DSN {self._dsn}: {e}"
                    ) from e

                parsed_url = urlparse(self._dsn)

                addr_index = 0
                # fill the connection pool with connections to all available nodes, up to the max_size.
                # this ensures the pool is evenly populated across all nodes.
                # if a node fails to connect, it will be skipped and removed from the list.
                # the loop will exit early if no nodes remain to avoid an infinite loop.
                while len(self._pool) < self._max_size and instance_addrs:
                    address = instance_addrs[addr_index % len(instance_addrs)]
                    dsn = f"{parsed_url.scheme}://{parsed_url.username}:{parsed_url.password}@{address}"

                    try:
                        conn = Connection(dsn, **self._connect_kwargs)
                        await conn.connect()
                        self._pool.append(conn)
                    except Exception as e:
                        print(f"Could not connect to node {address} for pool: {e}")
                        instance_addrs.remove(address)
                        if not instance_addrs:
                            break
                        continue

                    addr_index += 1

            # then fill the connection pool up to max_size with main mode connections
            while len(self._pool) < self._max_size:
                main_node_conn = Connection(self._dsn, **self._connect_kwargs)
                try:
                    await main_node_conn.connect()
                    self._pool.append(main_node_conn)
                except Exception as e:
                    raise RuntimeError(
                        f"Could not connect to main node {self._dsn} for pool: {e}"
                    ) from e

            # rotate the pool to randomize the order of connections.
            # this helps to distribute the initial load more evenly across nodes
            # when using round-robin or when multiple clients start simultaneously.
            shift = random.randint(0, len(self._pool) - 1)
            self._pool.rotate(shift)

            return

    async def _discover_instances(self) -> list[str]:
        # make temporary connection
        temp_conn = Connection(self._dsn, **self._connect_kwargs)

        try:
            await temp_conn.connect()

            # all instance addresses excluding connected node
            alive_instances_info = await temp_conn.fetch(
                """
                WITH my_uuid AS (SELECT instance_uuid() AS uuid)
                SELECT i.name, i.raft_id, i.current_state, p.address
                FROM _pico_instance i
                JOIN _pico_peer_address p ON i.raft_id = p.raft_id
                JOIN my_uuid u ON 1 = 1
                WHERE p.connection_type = 'pgproto' AND i.uuid != u.uuid;
            """
            )

            online_addresses = []
            # place connected node as first node to be sure that
            # it will be in the pool independ on pool size
            parsed_url = urlparse(self._dsn)
            online_addresses.append(f"{parsed_url.hostname}:{parsed_url.port}")
            for r in alive_instances_info:
                if not r.get("current_state", None):
                    continue

                try:
                    current_state = json.loads(r.get("current_state", None))
                except json.JSONDecodeError:
                    print(
                        f"Failed to decode current state of picodata instance {r.get('current_state', None)}"
                    )
                    continue

                if "Online" in current_state:
                    online_addresses.append(r["address"])

            return online_addresses
        finally:
            await temp_conn.close()

    async def acquire(self, timeout: float | None = None) -> Connection:
        """
        Acquire a connection from the pool.

        If no connections are available, this method will wait until one is released.

        :return: A database connection.
        """
        start_time = time.monotonic()
        effective_timeout = timeout if timeout is not None else self._default_acquire_timeout_sec

        while True:
            async with self._lock:
                # сheck if there are any available connections in the pool
                if self._pool:
                    # round-robin strategy
                    if self._balance_strategy is None:
                        conn = self._pool.popleft()
                    # custom strategy
                    else:
                        try:
                            conn = self._balance_strategy(list(self._pool))
                        except Exception as e:
                            raise RuntimeError(f"balance_strategy raised an exception: {e}") from e

                        if conn not in self._pool:
                            raise RuntimeError("balance_strategy returned a connection not in pool")
                        self._pool.remove(conn)

                    # mark it as currently in use
                    self._used.add(conn)
                    return conn

            if (time.monotonic() - start_time) >= effective_timeout:
                raise TimeoutError("Timed out waiting for a free connection in the pool")

            # if no connections are available, wait briefly before retrying
            # this gives other coroutines (like `release`) a chance to return a connection to the pool
            await asyncio.sleep(0.1)

    async def release(self, conn: Connection) -> None:
        """
        Release a previously acquired connection back to the pool.

        :param conn: The connection to release.
        """
        async with self._lock:
            if conn in self._used:
                self._used.remove(conn)
                self._pool.append(conn)

    async def close(self) -> None:
        """
        Closes all connections in the pool.

        This should be called during application shutdown to clean up resources.
        """
        async with self._lock:
            while self._pool:
                conn = self._pool.popleft()
                await conn.close()
            for conn in self._used:
                await conn.close()
            self._used.clear()

    async def execute(self, query: str, *args: Any) -> str:
        """
        Executes a query that does not return rows (e.g. INSERT, UPDATE, DELETE).

        :param query: The SQL query string.
        :param args: Optional parameters for the SQL query.
        :return: The result of the query execution.
        """
        conn = await self.acquire()
        try:
            return await conn.execute(query, *args)
        finally:
            await self.release(conn)

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        """
        Executes a query and fetches all resulting rows.

        :param query: The SQL query string.
        :param args: Optional parameters for the SQL query.
        :return: A list of rows returned by the query.
        """
        conn = await self.acquire()
        try:
            return await conn.fetch(query, *args)
        finally:
            await self.release(conn)

    async def fetchrow(self, query: str, *args: Any) -> asyncpg.Record | None:
        """
        Executes a query and fetches a single row (first row).

        :param query: The SQL query string.
        :param args: Optional parameters for the SQL query.
        :return: A single row returned by the query.
        """
        conn = await self.acquire()
        try:
            return await conn.fetchrow(query, *args)
        finally:
            await self.release(conn)
