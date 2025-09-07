from expat.db import init_schema

import sqlite3


def test_schema_up(sqlite_db: sqlite3.Connection):
    init_schema.init_schema(sqlite_db)

    cursor = sqlite_db.cursor()
    cursor.execute("""
        SELECT
            name,
            type,
            pk
        FROM pragma_table_info('migrations');
    """)
    result = cursor.fetchall()
    cursor.close()

    assert result == [
        ("migration_id", "VARCHAR(17)", 1),
        ("migration_name", "VARCHAR(1000)", 0),
        ("up_hash", "VARCHAR(32)", 0),
        ("down_hash", "VARCHAR(32)", 0),
    ]
