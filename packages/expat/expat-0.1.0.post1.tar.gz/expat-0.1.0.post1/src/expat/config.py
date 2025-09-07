from pathlib import Path
from pydantic import BaseModel, Field


class ExpatConfig(BaseModel):
    """Primary configuration class for expat.

    Attributes:
        migration_dir (Path, optional): Directory containing migration files. Defaults to
            `./migrations`.
        validate_hashes (bool, optional): Whether or not to verify that migration files in the
            migration directory match the migrations which have been applied to the database. If
            True, expat will raise an error when it encounters a migration which has been applied
            to the database but has since been tampered with. Defaults to True.
    """

    migration_dir: Path = Field(default=Path() / "migrations")
    validate_hashes: bool = Field(default=True)
