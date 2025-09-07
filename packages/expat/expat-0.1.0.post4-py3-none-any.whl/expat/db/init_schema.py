from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed.dbapi import DBAPIConnection

from pathlib import Path


def init_schema(connection: DBAPIConnection) -> None:
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            migration_id VARCHAR(17) PRIMARY KEY,
            migration_name VARCHAR(1000),
            up_hash VARCHAR(32),
            down_hash VARCHAR(32)
        );
    """)
    cursor.close()
