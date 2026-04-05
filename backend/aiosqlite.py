from __future__ import annotations

import sqlite3
from threading import Thread
from typing import Any

DatabaseError = sqlite3.DatabaseError
Error = sqlite3.Error
IntegrityError = sqlite3.IntegrityError
NotSupportedError = sqlite3.NotSupportedError
OperationalError = sqlite3.OperationalError
ProgrammingError = sqlite3.ProgrammingError
sqlite_version = sqlite3.sqlite_version
sqlite_version_info = sqlite3.sqlite_version_info


class _ImmediateQueue:
    def put_nowait(self, item: tuple[Any, Any]) -> None:
        future, function = item
        try:
            function()
        except Exception as error:
            future.set_exception(error)
        else:
            future.set_result(None)


class Cursor:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    @property
    def description(self):  # type: ignore[no-untyped-def]
        return self._cursor.description

    @property
    def lastrowid(self) -> int | None:
        return self._cursor.lastrowid

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    async def execute(self, operation: Any, parameters: Any = None) -> Cursor:
        if parameters is None:
            self._cursor.execute(operation)
        else:
            self._cursor.execute(operation, parameters)
        return self

    async def executemany(self, operation: Any, seq_of_parameters: Any) -> Cursor:
        self._cursor.executemany(operation, seq_of_parameters)
        return self

    async def fetchone(self) -> Any:
        return self._cursor.fetchone()

    async def fetchmany(self, size: int | None = None) -> list[Any]:
        return self._cursor.fetchmany(size or self._cursor.arraysize)

    async def fetchall(self) -> list[Any]:
        return self._cursor.fetchall()

    async def close(self) -> None:
        self._cursor.close()


class Connection:
    def __init__(self, *args: Any, **kwargs: Any):
        self._args = args
        self._kwargs = kwargs
        self._conn: sqlite3.Connection | None = None
        self._thread = Thread()
        self._tx = _ImmediateQueue()

    def __await__(self):  # type: ignore[no-untyped-def]
        async def _connect() -> Connection:
            if self._conn is None:
                kwargs = dict(self._kwargs)
                kwargs.setdefault("check_same_thread", False)
                self._conn = sqlite3.connect(*self._args, **kwargs)
            return self

        return _connect().__await__()

    @property
    def isolation_level(self) -> str | None:
        self._ensure_connection()
        return self._conn.isolation_level

    @isolation_level.setter
    def isolation_level(self, value: str | None) -> None:
        self._ensure_connection()
        self._conn.isolation_level = value

    async def cursor(self) -> Cursor:
        self._ensure_connection()
        return Cursor(self._conn.cursor())

    async def execute(self, *args: Any, **kwargs: Any) -> Cursor:
        self._ensure_connection()
        cursor = self._conn.execute(*args, **kwargs)
        return Cursor(cursor)

    async def commit(self) -> None:
        self._ensure_connection()
        self._conn.commit()

    async def rollback(self) -> None:
        self._ensure_connection()
        self._conn.rollback()

    async def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    async def create_function(self, *args: Any, **kwargs: Any) -> None:
        self._ensure_connection()
        self._conn.create_function(*args, **kwargs)

    def stop(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _ensure_connection(self) -> None:
        if self._conn is None:
            raise ValueError("no active connection")


def connect(*args: Any, **kwargs: Any) -> Connection:
    return Connection(*args, **kwargs)
