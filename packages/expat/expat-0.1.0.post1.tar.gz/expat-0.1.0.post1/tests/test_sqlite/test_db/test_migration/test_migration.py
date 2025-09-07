from expat.config import ExpatConfig
from expat.db.migration import get_migrations
from expat.db.migration import Migration, MigrationRow

import sqlite3


def test_get_migrations(test_config: ExpatConfig):
    migrations = get_migrations(test_config.migration_dir)

    assert migrations == [
        Migration(
            migration_path=test_config.migration_dir
            / "20250901113604839_test-migration-1",
            migration_id="20250901113604839",
            migration_name="test-migration-1",
            up_hash="81d645ffc570f1fbf7ae82c9faf6edf7",
            down_hash="b8dc9950943caa3acc3578b2defe60d2",
        ),
        Migration(
            migration_path=test_config.migration_dir
            / "20250901114236057_test-migration-2",
            migration_id="20250901114236057",
            migration_name="test-migration-2",
            up_hash="d41d8cd98f00b204e9800998ecf8427e",
            down_hash="d41d8cd98f00b204e9800998ecf8427e",
        ),
    ]


def test_migration_insert(
    test_migrations: list[Migration], initialized_sqlite_db: sqlite3.Connection
):
    migration = test_migrations[0]

    migration._insert_migration_row(initialized_sqlite_db)

    cursor = initialized_sqlite_db.cursor()
    cursor.execute("SELECT * FROM migrations;")
    result = cursor.fetchall()
    cursor.close()

    migrations = [MigrationRow.from_row(row) for row in result]

    assert migrations == [
        MigrationRow(
            migration_id="20250901113604839",
            migration_name="test-migration-1",
            up_hash="81d645ffc570f1fbf7ae82c9faf6edf7",
            down_hash="b8dc9950943caa3acc3578b2defe60d2",
        )
    ]


def test_migration_delete(
    test_migrations: list[Migration], initialized_sqlite_db: sqlite3.Connection
):
    migration = test_migrations[0]
    migration._insert_migration_row(initialized_sqlite_db)
    migration._delete_migration_row(initialized_sqlite_db)

    cursor = initialized_sqlite_db.cursor()
    cursor.execute("SELECT * FROM migrations;")
    result = cursor.fetchall()
    cursor.close()

    assert len(result) == 0


def test_migration_execute_up(
    test_migrations: list[Migration], initialized_sqlite_db: sqlite3.Connection
):
    migration = test_migrations[0]
    migration._execute_up(initialized_sqlite_db)

    cursor = initialized_sqlite_db.cursor()
    cursor.execute("""
        SELECT
            name,
            type,
            pk
        FROM pragma_table_info('up_table');
    """)
    result = cursor.fetchall()
    cursor.close()

    assert result == [
        ("val", "INT", 0),
    ]


def test_migration_execute_down(
    test_migrations: list[Migration], initialized_sqlite_db: sqlite3.Connection
):
    migration = test_migrations[0]
    migration._execute_down(initialized_sqlite_db)

    cursor = initialized_sqlite_db.cursor()
    cursor.execute("""
        SELECT
            name,
            type,
            pk
        FROM pragma_table_info('down_table');
    """)
    result = cursor.fetchall()
    cursor.close()

    assert result == [
        ("val", "INT", 0),
    ]


def test_migration_is_applied(
    test_migrations: list[Migration], initialized_sqlite_db: sqlite3.Connection
):
    migration = test_migrations[0]

    migration._insert_migration_row(initialized_sqlite_db)

    is_applied = migration._is_applied(initialized_sqlite_db, True)

    assert is_applied
