"""
Alembic environment — connects to MySQL and runs migrations.
"""
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Make sure Python can find our app modules
sys.path.append(str(Path(__file__).resolve().parents[2]))

load_dotenv()

# Import all models so Alembic can detect schema changes
from backend.api.models.dataset import Dataset, OperationalRecord, DataQualityLog, ClaudeQuery
from backend.utils.database import Base

# Alembic config object
config = context.config

# Override sqlalchemy.url with value from .env
db_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/civiclens")
config.set_main_option("sqlalchemy.url", db_url)

# Set up logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point Alembic at our ORM metadata so it can auto-detect changes
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL scripts)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the live database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
