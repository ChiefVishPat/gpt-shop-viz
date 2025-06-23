import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import URL

from alembic import context  # type: ignore[attr-defined]

# ---- Import your Base.metadata for autogenerate ----
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Load environment variables and build the proper DB URL for migrations
load_dotenv()


def get_database_url(async_driver: bool = True) -> str:
    driver = 'postgresql+asyncpg' if async_driver else 'postgresql+psycopg2'
    return str(
        URL.create(
            drivername=driver,
            username=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            host=os.environ['POSTGRES_HOST'],
            port=int(os.environ['POSTGRES_PORT']),
            database=os.environ['POSTGRES_DB'],
        )
    )


# set SQLAlchemy URL in config for both offline autogenerate and online use
async_url = get_database_url(async_driver=True)
config.set_main_option('sqlalchemy.url', async_url)
config.set_section_option(config.config_ini_section, 'sqlalchemy.url', async_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata is the MetaData object for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # offline use the URL we stored in config (asyncpg)
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        as_sql=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Build synchronous psycopg2 URL directly from environment variables for migrations
    connectable = create_engine(
        URL.create(
            drivername='postgresql+psycopg2',
            username=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            host=os.environ['POSTGRES_HOST'],
            port=int(os.environ['POSTGRES_PORT']),
            database=os.environ['POSTGRES_DB'],
        ),
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
