import asyncio
import typing as t

from piccolo.table_reflection import TableStorage, get_output_schema
from piccolo.engine import Engine


class EnginedTableStorage(TableStorage):  # https://github.com/piccolo-orm/piccolo/pull/875
    async def reflect(
        self,
        schema_name: str = "public",
        include: t.Union[t.List[str], str, None] = None,
        exclude: t.Union[t.List[str], str, None] = None,
        keep_existing: bool = False,
        engine: t.Union[Engine, None] = None,
    ) -> None:
        """
        Imports tables from the database into ``Table`` objects without
        hard-coding them.

        If a table has a reference to another table, the referenced table will
        be imported too. Reflection can have a performance impact based on the
        number of tables.

        If you want to reflect your whole database, make sure to only do it
        once or use the provided parameters instead of reflecting the whole
        database every time.

        :param schema_name:
            Name of the schema you want to reflect.
        :param include:
            It will only reflect the specified tables. Can be a list of tables
            or a single table.
        :param exclude:
            It won't reflect the specified tables. Can be a list of tables or
            a single table.
        :param keep_existing:
            If True, it will exclude the available tables and reflects the
            currently unavailable ones. Default is False.
        :returns:
            None

        """
        include_list = self._to_list(include)
        exclude_list = self._to_list(exclude)

        if keep_existing:
            exclude += self._schema_tables.get(schema_name, [])

        output_schema = await get_output_schema(
            schema_name=schema_name, include=include_list, exclude=exclude_list, engine=engine,
        )
        add_tables = [
            self._add_table(schema_name=schema_name, table=table)
            for table in output_schema.tables
        ]
        await asyncio.gather(*add_tables)
