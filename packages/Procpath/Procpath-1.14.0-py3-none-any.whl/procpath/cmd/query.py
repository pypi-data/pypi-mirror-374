import json
import string
import tempfile
import time
from typing import List, Optional, TextIO, Tuple

from .. import procfile, procrec, procret, proctree, utility
from . import CommandError


__all__ = 'run',


def run(
    procfile_list: List[str],
    output_file: TextIO,
    procfs: str,
    procfs_target: str,
    delimiter: Optional[str] = None,
    indent: Optional[int] = None,
    query: Optional[str] = None,
    sql_query: Optional[str] = None,
    environment: Optional[List[Tuple[str, str]]] = None,
):
    readers = {k: v for k, v in procfile.registry.items() if k in procfile_list}
    forest = proctree.Forest(readers, procfs, procfs_target)
    result = forest.get_roots()

    if environment:
        evaluated = utility.evaluate(environment)
        query = string.Template(query or '').safe_substitute(evaluated)
        sql_query = string.Template(sql_query or '').safe_substitute(evaluated)

    if query:
        try:
            result = proctree.query(result, query)
        except proctree.JsonPathQueryError as ex:
            raise CommandError(str(ex)) from ex

    if sql_query:
        with tempfile.NamedTemporaryFile() as f:
            meta = utility.get_meta(procfile_list, procfs, procfs_target)
            with procrec.SqliteStorage(f.name, procfile_list, meta) as store:
                store.record(time.time(), proctree.flatten(result, procfile_list))
                try:
                    result = procret.query(f.name, procret.Query(sql_query, ''))
                except procret.QueryExecutionError as ex:
                    raise CommandError(f'SQL error: {ex}') from ex

    if delimiter:
        result = delimiter.join(map(str, result))
    else:
        result = json.dumps(result, indent=indent, sort_keys=True, ensure_ascii=False)

    if result:
        output_file.write(f'{result}\n')
