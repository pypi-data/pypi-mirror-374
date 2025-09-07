from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed.dbapi import DBAPIConnection

from pathlib import Path


def init_schema(connection: DBAPIConnection) -> None:
    schema_script = Path(__file__).parent.parent.parent.parent / "init_schema.sql"

    with open(schema_script, "r") as f:
        script = f.read()

    cursor = connection.cursor()
    cursor.execute(script)
    cursor.close()
