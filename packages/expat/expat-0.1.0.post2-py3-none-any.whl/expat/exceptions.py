from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expat.db.migration import Migration, MigrationRow


class MigrationValidationError(Exception):
    def __init__(self, repo_migration: Migration, db_migration: MigrationRow):
        self.message = (
            "Migration in repo does not match that which has been applied to database:\n"
            f"    repo: (up_hash: {repo_migration.up_hash}, down_hash: {repo_migration.down_hash})"
            f"\n      db: (up_hash: {db_migration.up_hash}, down_hash: {db_migration.down_hash})"
        )
