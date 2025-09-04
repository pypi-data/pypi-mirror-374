import json
from contextlib import closing
from datetime import datetime
from typing import List, Mapping, NamedTuple, Optional


try:
    import apsw as sqlite
    from apsw import SQLError as SqlError
except ImportError:  # nocov
    import sqlite3 as sqlite
    from sqlite3 import OperationalError as SqlError


__all__ = 'create_query', 'query', 'registry', 'Query', 'QueryError', 'QueryExecutionError'

registry = {}


class QueryError(Exception):
    """General query error."""


class QueryExecutionError(Exception):
    """SQL query execution error."""


class Query(NamedTuple):
    query: str
    """The SQL query itself."""

    title: str
    """Query title displayed on a plot."""

    name: Optional[str] = None
    """Short code used by the command-line interface."""

    min_version: tuple = (1,)
    """Minimal SQLite version compatible with the query."""

    procfile_required: frozenset = frozenset()
    """Procfiles required by the query. ``stat`` is assumed."""

    def get_short_query(self, *, ts_as_milliseconds=False) -> str:
        result = self.query.split('-- filter cut line --', 1)[0]
        if ts_as_milliseconds:
            result = result.replace('ts, -- unix timestamp', 'ts * 1000 ts,')

        return result


def create_query(
    value_expr: str, title: str, *, cte='', table='record', procfile_required=None, **kwargs
) -> Query:
    return Query(
        f'''
        {cte.rstrip()}
        SELECT
            ts, -- unix timestamp
            stat_pid pid,
            {value_expr} value
        FROM {table}
        -- filter cut line --
        WHERE
            (:after IS NULL OR :after <= ts)
            AND (:before IS NULL OR ts <= :before)
            AND (:pid_list IS NULL OR instr(:pid_list, ',' || stat_pid || ','))
        ORDER BY stat_pid, record_id
        ''',
        title,
        procfile_required=frozenset(procfile_required or []),
        **kwargs,
    )


def register_query(obj: Query):
    registry[obj.name] = obj


def query(
    database: str,
    query: Query,
    after: Optional[datetime] = None,
    before: Optional[datetime] = None,
    pid_list: Optional[List[int]] = None,
) -> List[Mapping]:
    with closing(sqlite.Connection(database)) as conn:  # type: ignore[module-attr]
        cursor = conn.cursor()

        sqlite_version = cursor.execute('SELECT sqlite_version()').fetchone()[0]
        sqlite_version = tuple(map(int, sqlite_version.split('.')))
        if sqlite_version < query.min_version:
            raise QueryError(
                f'{query.title!r} requires SQLite version >= {query.min_version}, '
                f'installed {sqlite_version}. Install apsw and try again.'
            )

        if query.procfile_required:
            sql = "SELECT value FROM meta WHERE key = 'procfile_list'"
            procfile_list = cursor.execute(sql).fetchone()
            procfile_provided = set(json.loads(procfile_list[0])) if procfile_list else set()
            missing = ', '.join(sorted(query.procfile_required - procfile_provided))
            if missing:
                raise QueryError(
                    f'{query.title!r} requires the following procfiles missing '
                    f'in the database: {missing}'
                )

        row_factory = lambda cur, row: dict(zip([t[0] for t in cur.description], row))
        try:
            conn.row_factory = row_factory
        except AttributeError:
            conn.setrowtrace(row_factory)  # type: ignore[attribute-error]

        cursor = conn.cursor()
        try:
            cursor.execute(query.query, {
                'after': after.timestamp() if after else None,
                'before': before.timestamp() if before else None,
                'pid_list': ',{},'.format(','.join(map(str, pid_list))) if pid_list else None,
            })
        except SqlError as ex:  # type: ignore[mro-error]
            raise QueryExecutionError(str(ex)) from ex
        else:
            return cursor.fetchall()


register_query(create_query(
    "100.0 * tick_diff / (SELECT value FROM meta WHERE key = 'clock_ticks') / ts_diff",
    'CPU Usage, %',
    cte=(
        '''
        WITH diff_all AS (
            SELECT
                record_id,
                ts,
                stat_pid,
                stat_utime + stat_stime - LAG(stat_utime + stat_stime) OVER (
                    PARTITION BY stat_pid
                    ORDER BY record_id
                ) tick_diff,
                ts - LAG(ts) OVER (
                    PARTITION BY stat_pid
                    ORDER BY record_id
                ) ts_diff
            FROM record
        ), diff AS (
            SELECT * FROM diff_all WHERE tick_diff IS NOT NULL
        )
        '''
    ),
    table='diff',
    name='cpu',
    min_version=(3, 25),
))

register_query(create_query(
    "stat_rss / 1024.0 / 1024 * (SELECT value FROM meta WHERE key = 'page_size')",
    'Resident Set Size, MiB',
    name='rss',
))

register_query(create_query(
    "smaps_rollup_pss / 1024.0",
    'Proportional Set Size, MiB',
    name='pss',
    procfile_required=['smaps_rollup'],
))
register_query(create_query(
    "(smaps_rollup_private_clean + smaps_rollup_private_dirty) / 1024.0",
    'Unique Set Size, MiB',
    name='uss',
    procfile_required=['smaps_rollup'],
))
register_query(create_query(
    "smaps_rollup_swap / 1024.0",
    'Swap, MiB',
    name='swap',
    procfile_required=['smaps_rollup'],
))

register_query(create_query(
    'fd_anon + fd_dir + fd_chr + fd_blk + fd_reg + fd_fifo + fd_lnk + fd_sock',
    'Open File Descriptors',
    name='fd',
    procfile_required=['fd'],
))

register_query(create_query(
    'byte_diff / ts_diff',
    'Disk Read, B/s',
    cte=(
        '''
        WITH diff_all AS (
            SELECT
                record_id,
                ts,
                stat_pid,
                io_read_bytes - LAG(io_read_bytes) OVER (
                    PARTITION BY stat_pid
                    ORDER BY record_id
                ) byte_diff,
                ts - LAG(ts) OVER (
                    PARTITION BY stat_pid
                    ORDER BY record_id
                ) ts_diff
            FROM record
        ), diff AS (
            SELECT * FROM diff_all WHERE byte_diff IS NOT NULL
        )
        '''
    ),
    table='diff',
    name='rbs',
    min_version=(3, 25),
    procfile_required=['io'],
))
register_query(create_query(
    'byte_diff / ts_diff',
    'Disk Write, B/s',
    cte=(
        '''
        WITH diff_all AS (
            SELECT
                record_id,
                ts,
                stat_pid,
                io_write_bytes - LAG(io_write_bytes) OVER (
                    PARTITION BY stat_pid
                    ORDER BY record_id
                ) byte_diff,
                ts - LAG(ts) OVER (
                    PARTITION BY stat_pid
                    ORDER BY record_id
                ) ts_diff
            FROM record
        ), diff AS (
            SELECT * FROM diff_all WHERE byte_diff IS NOT NULL
        )
        '''
    ),
    table='diff',
    name='wbs',
    min_version=(3, 25),
    procfile_required=['io'],
))

register_query(create_query(
    "100.0 * tick_diff / (SELECT value FROM meta WHERE key = 'clock_ticks') / ts_diff",
    'I/O wait, %',
    cte=(
        '''
        WITH diff_all AS (
            SELECT
                record_id,
                ts,
                stat_pid,
                stat_delayacct_blkio_ticks - LAG(stat_delayacct_blkio_ticks) OVER (
                    PARTITION BY stat_pid
                    ORDER BY record_id
                ) tick_diff,
                ts - LAG(ts) OVER (
                    PARTITION BY stat_pid
                    ORDER BY record_id
                ) ts_diff
            FROM record
        ), diff AS (
            SELECT * FROM diff_all WHERE tick_diff IS NOT NULL
        )
        '''
    ),
    table='diff',
    name='wait',
    min_version=(3, 25),
))
