from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed.dbapi import DBAPIConnection

from expat.exceptions import MigrationValidationError
from expat.utils import hash_file

from pathlib import Path
from pydantic import BaseModel
from typing import Self, Type


class Migration(BaseModel):
    migration_path: Path
    migration_id: str
    migration_name: str
    up_hash: str
    down_hash: str

    @classmethod
    def from_path(cls: Type[Self], path: Path) -> Self:
        migration_id, migration_name = path.name.split("_", 1)

        migration = cls(
            migration_path=path,
            migration_id=migration_id,
            migration_name=migration_name,
            up_hash=hash_file(path / "up.sql"),
            down_hash=hash_file(path / "down.sql"),
        )

        return migration

    def apply(
        self,
        connection: DBAPIConnection,
        metadata_connection: DBAPIConnection,
        validate_hashes: bool,
    ) -> None:
        if self._is_applied(metadata_connection, validate_hashes):
            return None

        self._execute_up(connection)
        self._insert_migration_row(metadata_connection)

    def rollback(
        self,
        connection: DBAPIConnection,
        metadata_connection: DBAPIConnection,
        validate_hashes: bool,
    ) -> None:
        if not self._is_applied(metadata_connection, validate_hashes):
            return None

        self._execute_down(connection)
        self._delete_migration_row(metadata_connection)

    def _is_applied(self, connection: DBAPIConnection, validate_hashes: bool) -> bool:
        cursor = connection.cursor()

        cursor.execute(
            f"SELECT * FROM migrations WHERE migration_id = '{self.migration_id}';"
        )
        result = cursor.fetchone()

        cursor.close()

        if result is None:
            return False

        if not isinstance(result, tuple):
            raise ValueError(
                f"Database connections should be configured to return tuples, not {type(result)}"
            )

        migration_row = MigrationRow.from_row(result)

        if validate_hashes:
            if (
                self.up_hash != migration_row.up_hash
                or self.down_hash != migration_row.down_hash
            ):
                raise MigrationValidationError(self, migration_row)

        return True

    def _insert_migration_row(self, connection: DBAPIConnection) -> None:
        cursor = connection.cursor()

        # Have to use f-strings because parameter styles vary by library; not too worried about
        # security here because migrations are usually executed with admin permissions anyway, so
        # no risk of unwanted SQL injection.
        cursor.execute(
            f"""
                INSERT INTO migrations VALUES (
                    '{self.migration_id}',
                    '{self.migration_name}',
                    '{self.up_hash}',
                    '{self.down_hash}'
                );
            """
        )

        cursor.close()

    def _delete_migration_row(self, connection: DBAPIConnection) -> None:
        cursor = connection.cursor()

        cursor.execute(
            f"""
                DELETE FROM migrations
                WHERE migration_id = '{self.migration_id}';
            """
        )

        cursor.close()

    def _execute_up(self, connection: DBAPIConnection) -> None:
        cursor = connection.cursor()

        with open(self.migration_path / "up.sql", "r") as f:
            up_script = f.read()

        cursor.execute(up_script)

        cursor.close()

    def _execute_down(self, connection: DBAPIConnection) -> None:
        cursor = connection.cursor()

        with open(self.migration_path / "down.sql", "r") as f:
            down_script = f.read()

        cursor.execute(down_script)

        cursor.close()


class MigrationRow(BaseModel):
    migration_id: str
    migration_name: str
    up_hash: str
    down_hash: str

    @classmethod
    def from_row(cls: Type[Self], row: tuple[str, str, str, str]) -> Self:
        return cls(
            migration_id=row[0],
            migration_name=row[1],
            up_hash=row[2],
            down_hash=row[3],
        )


def get_migrations(migration_dir: Path) -> list[Migration]:
    migrations: list[Migration] = []

    for dir in sorted(migration_dir.iterdir()):
        if not dir.is_dir():
            continue

        migration = Migration.from_path(dir)

        migrations.append(migration)

    return migrations
