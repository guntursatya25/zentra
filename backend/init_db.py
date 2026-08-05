"""Run at container start: run migrations, then seed."""

import asyncio
import os

from alembic.config import Config
from alembic import command
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Find project root (where alembic.ini lives)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


async def seed_database():
    """Execute seed.sql against the database."""
    db_url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://zentra:zentra@localhost:5432/zentra")
    engine = create_async_engine(db_url)
    seed_path = os.path.join(BASE_DIR, "seed.sql")

    if not os.path.exists(seed_path):
        print(f">>> Seed file not found: {seed_path}")
        return

    with open(seed_path) as f:
        sql = f.read()

    async with engine.connect() as conn:
        # Skip if roles already exist (idempotent)
        result = await conn.execute(text("SELECT EXISTS (SELECT 1 FROM roles)"))
        exists = result.scalar()
        if not exists:
            print(">>> Running seed...")
            for statement in sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    try:
                        await conn.execute(text(stmt))
                    except Exception as e:
                        print(f"  [warn] Seed statement skipped: {e}")
            await conn.commit()
            print(">>> Seed complete.")
        else:
            print(">>> Seed already applied, skipping.")

    await engine.dispose()


def run_migrations():
    """Run Alembic migrations."""
    print(">>> Running Alembic migrations...")
    ini_path = os.path.join(BASE_DIR, "alembic.ini")
    os.chdir(BASE_DIR)  # alembic needs to resolve relative paths
    alembic_cfg = Config(ini_path)
    command.upgrade(alembic_cfg, "head")
    print(">>> Migrations complete.")


if __name__ == "__main__":
    run_migrations()
    asyncio.run(seed_database())
