import sqlite3
from collections import defaultdict
from typing import List, Optional

from . import procfile


__all__ = 'SqliteStorage',


class SqliteStorage:

    _conn = None

    _procfile_list: List[str]
    _meta: dict

    _file_columns = None

    _column_mapping = defaultdict(lambda: 'TEXT', {int: 'INTEGER', Optional[int]: 'INTEGER'})

    def __init__(self, database: str, procfile_list: List[str], meta: dict):
        self._procfile_list = procfile_list
        self._meta = meta

        self._conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)

    def create_schema(self):
        table_columns = []
        self._file_columns = []
        for procfile_name in sorted(self._procfile_list):
            schema = procfile.registry[procfile_name].schema
            if isinstance(schema, str):
                table_columns.append(f'{procfile_name} TEXT')
                self._file_columns.append(procfile_name)
            else:
                field_types = schema.__annotations__
                for field_name, field_type in field_types.items():
                    column_name = f'{procfile_name}_{field_name}'
                    table_columns.append('{column} {type}'.format(
                        column=column_name, type=self._column_mapping[field_type]
                    ))
                    self._file_columns.append(column_name)

        sql = '''
            CREATE TABLE IF NOT EXISTS record (
                record_id INTEGER PRIMARY KEY NOT NULL,
                ts        REAL NOT NULL,
                {columns}
            )
        '''.format(columns=',\n'.join(table_columns))
        self._conn.execute(sql)

        sql = '''
            CREATE TABLE IF NOT EXISTS meta (
                key   TEXT PRIMARY KEY NOT NULL,
                value TEXT NOT NULL
            )
        '''
        self._conn.execute(sql)
        if self._meta:
            sql = 'REPLACE INTO meta VALUES(?, ?)'
            with self._conn:
                self._conn.executemany(sql, self._meta.items())

        self._conn.commit()

    def record(self, ts: float, node_list: List[dict]) -> int:
        if not node_list:
            return 0

        sql = 'INSERT INTO record(ts, {columns}) VALUES({ts:f}, {placeholders})'.format(
            columns=','.join(self._file_columns),
            ts=ts,
            placeholders=','.join(f':{c}' for c in self._file_columns),
        )
        with self._conn:
            cursor = self._conn.executemany(sql, node_list)
        return cursor.rowcount

    def close(self):
        self._conn.close()

    def __enter__(self):
        self.create_schema()
        return self

    def __exit__(self, *exc_args):
        self.close()


MAX_SQLITE_INT = 2 ** 63 - 1

sqlite3.register_adapter(int, lambda x: hex(x) if x > MAX_SQLITE_INT else x)
sqlite3.register_converter('integer', lambda b: int(b, 16 if b[:2] == b'0x' else 10))
