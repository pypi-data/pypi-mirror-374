from expat.config import ExpatConfig
from expat.db.init_schema import init_schema
from expat.db.migration import Migration, get_migrations

from pathlib import Path
from pytest import fixture
import sqlite3
from typing import Any, Generator


@fixture
def test_config() -> ExpatConfig:
    return ExpatConfig(
        migration_dir=Path(__file__).parent.parent.parent / "test_data" / "migrations"
    )


@fixture
def sqlite_db() -> Generator[sqlite3.Connection, Any, Any]:
    db_path = Path("test.db")
    connection = sqlite3.connect(db_path)

    yield connection

    connection.close()
    db_path.unlink()


@fixture
def initialized_sqlite_db() -> Generator[sqlite3.Connection, Any, Any]:
    db_path = Path("test.db")
    connection = sqlite3.connect(db_path)
    init_schema(connection)

    yield connection

    connection.close()
    db_path.unlink()


@fixture
def test_migrations(test_config: ExpatConfig) -> list[Migration]:
    return get_migrations(test_config.migration_dir)
