from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed.dbapi import DBAPIConnection

from expat.config import ExpatConfig
from expat.db.init_schema import init_schema as _init_schema
from expat.db.migration import get_migrations as _get_migrations


def up(
    connection: DBAPIConnection,
    config: ExpatConfig,
    metadata_connection: DBAPIConnection | None = None,
) -> None:
    """Bring database up to date with current state of migration directory.

    In other words, execute all `up.sql` files in migration directory sequentially from smallest ID
    to largest ID.

    Args:
        connection (DBAPIConnection): A database connection object compliant with PEP 249's DB API
            specification.
        config (ExpatConfig): Expat configuration object.
        metadata_connection (DBAPIConnection | None, optional): Optional additional connection used
            only for managing metadata. Defaults to None.
    """
    migrations = _get_migrations(config.migration_dir)

    if metadata_connection is None:
        metadata_connection = connection

    _init_schema(metadata_connection)

    for migration in migrations:
        migration.apply(connection, metadata_connection, config.validate_hashes)


def down(
    connection: DBAPIConnection,
    config: ExpatConfig,
    metadata_connection: DBAPIConnection | None = None,
) -> None:
    """Tear down database.

    In other words, execute all `down.sql` files in migration directory sequentiallyu from largest
    ID to smallest ID.

    Args:
        connection (DBAPIConnection): A database connection object compliant with PEP 249's DB API
            specification.
        config (ExpatConfig): Expat configuration object.
        metadata_connection (DBAPIConnection | None, optional): Optional additional connection used
            only for managing metadata.
    """
    migrations = _get_migrations(config.migration_dir)
    migrations.reverse()

    if metadata_connection is None:
        metadata_connection = connection

    for migration in migrations:
        migration.rollback(connection, metadata_connection, config.validate_hashes)
