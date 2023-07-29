__all__ = ('CONFIG',)

from pydantic import BaseSettings, Json


class Config(BaseSettings):
    dsn_by_name: Json = '{"local": "postgres://postgres:postgres@localhost:5432/postgres"}'

    db_pool_min_size: int = 8
    db_pool_max_size: int = 16

    workers: int = 8
    port: int = 44777

    rate_limiting_timespan: int = 300
    rate_limiting_limit: int = 300
    rate_limiting_block_duration: int = 300


CONFIG = Config()
