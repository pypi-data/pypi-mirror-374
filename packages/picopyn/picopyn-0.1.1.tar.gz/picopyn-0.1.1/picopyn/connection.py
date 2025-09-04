from typing import Any

import asyncpg


class Connection:
    """
    A representation of a database session.

    :param dsn (str):  The data source name (e.g., "postgresql://user:pass@host:port") for the picodata node.
    """

    def __init__(self, dsn: str) -> None:
        if dsn is None:
            raise ValueError("dsn can not be None")
        self.dsn = dsn
        self.conn = None

    async def connect(self) -> None:
        """
        Create new connection to Picodata
        """

        try:
            self.conn = await asyncpg.connect(self.dsn)
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to picodata instance using DSN {self.dsn}: {e}"
            ) from e

    async def execute(self, *args: Any, **kwargs: Any) -> str:
        """
        Execute an SQL command
        """

        if not self.conn:
            raise OSError("No active connection. Try to call .connect() before.")

        try:
            return await self.conn.execute(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to execute SQL query: {e}. Query: {args}") from e

    async def fetchrow(self, *args: Any, **kwargs: Any) -> asyncpg.Record | None:
        """
        Run a query and return the first row.
        """

        if not self.conn:
            raise OSError("No active connection. Try to call .connect() before")

        try:
            return await self.conn.fetchrow(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(
                f"Failed to execute SQL query and fetch row: {e}. Query: {args}"
            ) from e

    async def fetch(self, *args: Any, **kwargs: Any) -> list[asyncpg.Record]:
        """
        Run a query and return the results as a list.
        """

        if not self.conn:
            raise OSError("No active connection. Try to call .connect() before")

        try:
            return await self.conn.fetch(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(
                f"Failed to execute SQL query and fetch result: {e}. Query: {args}"
            ) from e

    async def close(self, *args: Any, **kwargs: Any) -> None:
        """
        Close the connection gracefully.
        """
        if self.conn:
            try:
                return await self.conn.close(*args, **kwargs)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to disconnect from picodata instance {self.dsn}: {e}"
                ) from e
