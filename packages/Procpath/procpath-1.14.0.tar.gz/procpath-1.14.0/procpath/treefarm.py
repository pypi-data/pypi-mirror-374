import asyncio.subprocess
import contextlib
import logging
import os
import signal
import sys
from typing import Dict, List

from . import procfile, proctree


__all__ = 'process_exists', 'TreeFarm',

logger = logging.getLogger(__package__)


class TreeFarm:
    """
    An asynchronous process collection manager.

    Each watched command is spawned in a separate shell in a separate
    process group [#]_ [#]_. Without separate process groups the
    behaviour would have been different in foreground and background
    cases, from getpgrp(2):

        A session can have a controlling terminal. At any time, one
        (and only one) of the process groups in the session can be the
        foreground process group for the terminal; the remaining
        process groups are in the background. If a signal is generated
        from the terminal (e.g., typing the interrupt key to generate
        SIGINT), that signal is sent to the foreground process group.

    Thus without separate process groups in the foreground case
    ``watch`` process would only get control in its ``SIGINT`` handler
    at the same time (there's race but the handler usually loses it)
    as its shell processes. And in background ``SIGINT`` would only
    terminate the outer sessions leaving the command trees orphaned.

    .. [#] https://pymotw.com/2/subprocess/#process-groups-sessions
    .. [#] https://stackoverflow.com/q/1046933
    """

    _stop_signal: signal.Signals
    _kill_after: float

    _process_list: List[asyncio.subprocess.Process]

    def __init__(self, stop_signal: str, kill_after: float):
        self._stop_signal = signal.Signals[stop_signal]
        self._kill_after = kill_after

        self._process_list = []

    async def _forward_stream(self, stream_reader: asyncio.StreamReader, number: int, level: int):
        async for line in stream_reader:
            logger.log(level, '№%d: %s', number, line.strip().decode())

    async def _spawn(self, cmd: str, number: int, env: dict) -> asyncio.subprocess.Process:
        logger.debug('Starting №%d: %s', number, cmd)
        process = await asyncio.create_subprocess_shell(
            cmd,
            env=dict(os.environ, **env),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            # Start each shell in its own process group and be the
            # group leader. "start_new_session=True" or
            # "preexec_fn=os.setsid" would have achieved the same
            # result (new process group created), but the session is
            # not needed here. In Python 3.11+ there's "process_group"
            # argument that is recommended instead of "preexec_fn".
            preexec_fn=os.setpgrp,
        )
        logger.debug('Started №%d shell as PID %s', number, process.pid)
        asyncio.ensure_future(self._forward_stream(process.stdout, number, logging.INFO))
        asyncio.ensure_future(self._forward_stream(process.stderr, number, logging.WARNING))
        return process

    async def spawn_at(self, number: int, cmd: str, shell_env: Dict[str, str]) -> int:
        try:
            process = self._process_list[number - 1]
        except IndexError:
            process = await self._spawn(cmd, number, shell_env)
            self._process_list.append(process)
        else:
            if process.returncode is not None:
                logger.info('№%d exited with code %d, restarting', number, process.returncode)
                process = await self._spawn(cmd, number, shell_env)
                self._process_list[number - 1] = process

        return process.pid

    def is_terminated(self) -> bool:
        return all(p.returncode is not None for p in self._process_list)

    async def terminate(self):
        """
        Interrupt shell processes by sending stop signal, then SIGKILL.

        Interruption is done in two phases. First, all top-level shell
        process groups receive the stop signal and are given
        ``kill_after`` seconds to terminate, hopefully with all their
        descendants. Second, each process of the forest that existed at
        the start of the call, that is still alive, is killed.
        """

        forest = proctree.Forest({'stat': procfile.registry['stat']}, skip_self=False)
        query = '$..children[?(@.stat.ppid == {})]..stat.pid'.format(os.getpid())
        forest_pids = proctree.query(forest.get_roots(), query)
        logger.debug('Forest PIDs to terminate: %s', ', '.join(map(str, forest_pids)))

        await self._destroy_shells()

        for pid in [p for p in forest_pids if process_exists(p)]:
            logger.debug('Killing unterminated descendant PID %s', pid)
            with contextlib.suppress(ProcessLookupError):  # in case it has just terminated
                os.kill(pid, signal.SIGKILL)

    def _is_kill_on_tight_loop(self):
        """
        Workaround tight `.asyncio` loop after process killing.

        Asyncio subprocess functionality hasn't been stable recently:
        GH-88050, GH-100133, GH-109490, GH-109538, GH-114177. Here it
        manifests with the ``shell_proc.wait()`` not cleaning up itself
        after the process has just been killed. Python 3.10 and earlier
        are good, whereas newer ones seem suffice with a bit of space
        on the loop as a workaround.
        """

        return (3, 11) <= sys.version_info < (3, 14)

    async def _destroy_shells(self):
        for shell_proc in self._process_list:
            logger.debug('Sending %s to shell PGRP %s', self._stop_signal.name, shell_proc.pid)
            with contextlib.suppress(ProcessLookupError):
                os.killpg(shell_proc.pid, self._stop_signal)

        if self._is_kill_on_tight_loop():
            await asyncio.sleep(0.001)  # <= 0 is a short-circuited sleep

        shell_wait = asyncio.gather(*[sp.wait() for sp in self._process_list])
        try:
            await asyncio.wait_for(shell_wait, timeout=self._kill_after)
        except asyncio.TimeoutError:
            logger.debug('Not all shell processes terminated after stop signal')
            with contextlib.suppress(asyncio.CancelledError):
                await shell_wait
        else:
            shell_pids = [sp.pid for sp in self._process_list]
            logger.debug(
                'Shell processes successfully terminated: %s', ', '.join(map(str, shell_pids))
            )

        for shell_proc in self._process_list:
            if shell_proc.returncode is None:
                logger.debug('Killing unterminated shell PID %s', shell_proc.pid)
                with contextlib.suppress(ProcessLookupError):  # in case it has just terminated
                    shell_proc.kill()

                    if self._is_kill_on_tight_loop():
                        await asyncio.sleep(0.001)  # <= 0 is a short-circuited sleep

                    await shell_proc.wait()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.terminate()


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True
