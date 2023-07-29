__all__ = ('build_app',)

import asyncio

from blacksheep import Application
from blacksheep.plugins import json
from orjson import loads, dumps
from piccolo.engine import PostgresEngine
from piccolo_api.crud.endpoints import PiccoloCRUD
from piccolo_api.rate_limiting.middleware import RateLimitingMiddleware, InMemoryLimitProvider

from config import CONFIG
from piccolo_fixes import EnginedTableStorage

json.use(
    loads=loads,
    dumps=lambda *args, **kwargs: dumps(*args, **kwargs).decode('utf-8'),
    pretty_dumps=lambda *args, **kwargs: dumps(*args, **kwargs).decode('utf-8'),
)


def _add_db_pool(app: Application, engine: PostgresEngine) -> None:
    app.on_start(lambda *_, **__: engine.start_connection_pool(min_size=CONFIG.db_pool_min_size,
                                                               max_size=CONFIG.db_pool_max_size))
    app.on_stop(lambda *_, **__: engine.close_connection_pool())


def _wrap_rate_limit(app: Application) -> RateLimitingMiddleware:
    return RateLimitingMiddleware(
        app,
        provider=InMemoryLimitProvider(
            limit=CONFIG.rate_limiting_limit,
            timespan=CONFIG.rate_limiting_timespan,
            block_duration=CONFIG.rate_limiting_block_duration,
        ),
    )


def build_app() -> Application:
    app = Application()

    for dsn_name, dsn in CONFIG.dsn_by_name.items():
        dsn_app = Application()

        dsn_pe = PostgresEngine(config={'dsn': dsn})

        _add_db_pool(dsn_app, dsn_pe)

        dsn_tables_store = EnginedTableStorage()
        asyncio.run(dsn_tables_store.reflect(engine=dsn_pe))

        for dsn_table_name, dsn_table in dsn_tables_store.tables.items():
            dsn_table._meta.db = dsn_pe
            dsn_app.mount(f'/{dsn_table_name}', PiccoloCRUD(table=dsn_table, read_only=False, allow_bulk_delete=True))

        app.mount(f'/{dsn_name}', _wrap_rate_limit(dsn_app))

    return app
