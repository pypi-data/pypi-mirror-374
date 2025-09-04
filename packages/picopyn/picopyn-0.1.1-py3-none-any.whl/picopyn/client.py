from collections.abc import Callable
from typing import Any

import asyncpg

from .connection import Connection
from .pool import Pool


class Client:
    """
    Async client for managing connections to a picodata cluster using a connection pool.

    This client handles connection pooling, automatic node discovery (if enabled),
    and supports load balancing strategies for query distribution.

    :param dsn (str): The data source name (e.g., "postgresql://user:pass@host:port") for the cluster.
    :param balance_strategy (callable, optional): A custom strategy function to select a connection
        from the pool. If None, round-robin strategy is used.
    :param connect_kwargs: Additional keyword arguments passed to each connection.

    Example:
        >>> def random_strategy(connections):
        ...     import random
        ...     return random.choice(connections)

        >>> client = Client(
        ...     dsn="postgresql://admin:pass@localhost:5432",
        ...     balance_strategy=random_strategy
        ... )
    """

    def __init__(
        self,
        dsn: str,
        pool_size: int | None = None,
        balance_strategy: Callable[[list[Connection]], Connection] | None = None,
        **connect_kwargs: Any,
    ) -> None:
        self._pool = Pool(
            dsn=dsn,
            max_size=pool_size or 10,
            enable_discovery=True,
            balance_strategy=balance_strategy,
            **connect_kwargs,
        )

    async def connect(self) -> None:
        """
        Prepares the client by connection connection pool.

        This should be called before using the client to ensure connections are available.
        """
        await self._pool.connect()

    async def execute(self, query: str, *args: Any) -> str:
        """
        Executes a query that does not return rows (e.g. INSERT, UPDATE, DELETE).

        :param query: The SQL query string.
        :param args: Optional parameters for the SQL query.
        :return: The result of the query execution.
        """
        return await self._pool.execute(query, *args)

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        """
        Executes a query and fetches all resulting rows.

        :param query: The SQL query string.
        :param args: Optional parameters for the SQL query.
        :return: A list of rows returned by the query.
        """
        return await self._pool.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> asyncpg.Record | None:
        """
        Executes a query and fetches a single row (first row).

        :param query: The SQL query string.
        :param args: Optional parameters for the SQL query.
        :return: A single row returned by the query.
        """
        return await self._pool.fetchrow(query, *args)

    async def close(self) -> None:
        """
        Closes all connections in the pool.

        This should be called during application shutdown to clean up resources.
        """
        await self._pool.close()
