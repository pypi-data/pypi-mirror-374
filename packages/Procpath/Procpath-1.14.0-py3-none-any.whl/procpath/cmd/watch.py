import asyncio
import contextlib
import logging
import signal
import string
import time
from typing import AsyncIterable, Callable, List, Optional, Tuple

from .. import procfile, proctree, treefarm, utility
from . import CommandError


__all__ = 'run',

logger = logging.getLogger('procpath')


async def _watch_loop(
    interval: float,
    all_processes_terminated: Callable[[], bool],
    no_restart: bool = False,
    repeat: Optional[int] = None,
) -> AsyncIterable[int]:
    count = 1
    while True:
        start = time.time()

        if not no_restart or count == 1:
            yield count

        latency = time.time() - start
        await asyncio.sleep(max(0, interval - latency))

        count += 1
        if repeat and count > repeat or no_restart and all_processes_terminated():
            break


async def _watch(
    interval: float,
    command_list: List[str],
    procfile_list: List[str],
    stop_signal: str,
    kill_after: float,
    procfs: str,
    procfs_target: str,
    environment: Optional[List[Tuple[str, str]]] = None,
    query_list: Optional[List[Tuple[str, str]]] = None,
    repeat: Optional[int] = None,
    no_restart: bool = False,
):
    readers = {k: v for k, v in procfile.registry.items() if k in procfile_list}
    forest = proctree.Forest(readers, procfs, procfs_target)
    shell_env = {}
    async with treefarm.TreeFarm(stop_signal, kill_after) as farm:
        async for _ in _watch_loop(interval, farm.is_terminated, no_restart, repeat):
            result_command_list = _evaluate_command_list(
                forest, command_list, environment, query_list
            )
            for i, cmd in enumerate(result_command_list, start=1):
                shell_env.pop(f'WPS{i}', None)
                pid = await farm.spawn_at(i, cmd, shell_env)
                shell_env[f'WPS{i}'] = str(pid)


def _evaluate_command_list(
    forest: proctree.Forest,
    command_list: List[str],
    environment: Optional[List[Tuple[str, str]]] = None,
    query_list: Optional[List[Tuple[str, str]]] = None,
):
    env_dict = {}

    if environment:
        env_dict.update(utility.evaluate(environment))

    if query_list:
        forest_roots = forest.get_roots()
        for query_name, query in query_list:
            query = string.Template(query).safe_substitute(env_dict)
            try:
                query_result = proctree.query(forest_roots, query)
            except proctree.JsonPathQueryError as ex:
                raise CommandError(str(ex)) from ex

            if not query_result:
                logger.warning('Query %s evaluated empty', query_name)

            env_dict[query_name] = ','.join(map(str, query_result))

    return [string.Template(command).safe_substitute(env_dict) for command in command_list]


def run(**kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    watch_fut = asyncio.ensure_future(_watch(**kwargs))
    loop.add_signal_handler(signal.SIGINT, watch_fut.cancel)
    try:
        with contextlib.suppress(asyncio.CancelledError):
            loop.run_until_complete(watch_fut)
    finally:
        loop.remove_signal_handler(signal.SIGINT)

        all_tasks = asyncio.all_tasks(loop)
        if all_tasks:
            task_list = asyncio.gather(*all_tasks, return_exceptions=True)
            task_list_with_timeout = asyncio.wait_for(task_list, timeout=5)
            try:
                loop.run_until_complete(task_list_with_timeout)
            except asyncio.TimeoutError:
                with contextlib.suppress(asyncio.CancelledError):
                    loop.run_until_complete(task_list)

        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
