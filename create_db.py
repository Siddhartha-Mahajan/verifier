import asyncio

import asyncpg
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from config import URL_DATABASE
from models import Base


def _get_async_URL_DATABASE() -> str:
	raw_url = URL_DATABASE
	if not raw_url:
		raise RuntimeError("Missing URL_DATABASE in config/environment.")
	if raw_url.startswith("postgresql://"):
		return raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
	return raw_url


def _quote_identifier(identifier: str) -> str:
	return '"' + identifier.replace('"', '""') + '"'


async def _create_database_if_missing(async_db_url: str) -> tuple[str, bool]:
	target_url = make_url(async_db_url)
	db_name = target_url.database
	if not db_name:
		raise RuntimeError("Database name is missing in URL.")

	admin_url = target_url.set(drivername="postgresql", database="postgres")
	admin_dsn = admin_url.render_as_string(hide_password=False)

	conn = await asyncpg.connect(dsn=admin_dsn)
	try:
		exists = await conn.fetchval(
			"SELECT 1 FROM pg_database WHERE datname = $1",
			db_name,
		)
		if exists:
			return db_name, False

		await conn.execute(f"CREATE DATABASE {_quote_identifier(db_name)}")
	finally:
		await conn.close()

	return db_name, True


async def _create_tables(async_db_url: str) -> None:
	engine = create_async_engine(async_db_url, echo=False)
	try:
		async with engine.begin() as conn:
			await conn.run_sync(Base.metadata.create_all)
	finally:
		await engine.dispose()


async def main() -> None:
	async_db_url = _get_async_URL_DATABASE()
	db_name, created = await _create_database_if_missing(async_db_url)
	if created:
		print(f"Database '{db_name}' created successfully.")
	else:
		print(f"Database '{db_name}' already exists. Skipping database creation.")

	await _create_tables(async_db_url)
	print(f"Tables initialized successfully in database '{db_name}'.")


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except Exception as exc:
		raise SystemExit(f"create_db failed: {exc}")
