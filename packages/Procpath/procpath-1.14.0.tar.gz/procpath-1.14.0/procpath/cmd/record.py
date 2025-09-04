import logging
import string
import time
from typing import Iterable, List, Optional, Tuple

from .. import procfile, procrec, proctree, utility
from . import CommandError


__all__ = 'run',

logger = logging.getLogger('procpath')


class RunStats:
    node_count: int = 0


def _record_loop(
    interval: float,
    stats: RunStats,
    recnum: Optional[int] = None,
    stop_without_result: bool = False,
) -> Iterable[Tuple[float, int]]:
    count = 1
    while True:
        start = time.time()

        yield start, count

        count += 1
        if recnum and count > recnum or stop_without_result and not stats.node_count:
            break

        latency = time.time() - start
        if latency > interval:
            logger.warning(
                'Iteration took longer (%s) than record interval. Try longer interval.',
                f'{latency:.2f}s'
            )
        time.sleep(max(0, interval - latency))


def run(
    procfile_list: List[str],
    database_file: str,
    interval: float,
    procfs: str,
    procfs_target: str,
    environment: Optional[list] = None,
    query: Optional[str] = None,
    pid_list: Optional[str] = None,
    recnum: Optional[int] = None,
    reevalnum: Optional[int] = None,
    stop_without_result: bool = False,
):
    readers = {k: v for k, v in procfile.registry.items() if k in procfile_list}
    forest = proctree.Forest(readers, procfs, procfs_target)

    query_tpl = string.Template(query)
    pid_list_tpl = string.Template(pid_list)
    database_file_tpl = string.Template(database_file)
    if environment:
        database_file = database_file_tpl.safe_substitute(utility.evaluate(environment))

    meta = utility.get_meta(procfile_list, procfs, procfs_target)
    run_stats = RunStats()
    with procrec.SqliteStorage(database_file, procfile_list, meta) as store:
        for ts, count in _record_loop(interval, run_stats, recnum, stop_without_result):
            if environment and (count == 1 or reevalnum and (count + 1) % reevalnum == 0):
                env_dict = utility.evaluate(environment)
                if query:
                    query = query_tpl.safe_substitute(env_dict)
                if pid_list:
                    pid_list = pid_list_tpl.safe_substitute(env_dict)

            branch_pids = [int(p) for p in pid_list.split(',') if p] if pid_list else None
            result = forest.get_roots(branch_pids)

            if query:
                try:
                    result = proctree.query(result, query)
                except proctree.JsonPathQueryError as ex:
                    raise CommandError(str(ex)) from ex

            flat_node_list = proctree.flatten(result, procfile_list)
            run_stats.node_count = store.record(ts, flat_node_list)
            del branch_pids, result, flat_node_list
