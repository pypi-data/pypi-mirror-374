import asyncio
import contextlib
import inspect
import os
import re
import socket
import sys
import time
import unittest
import warnings

from .. import proctree


def load_tests(loader, tests, pattern):
    from . import cmd, unit  # noqa: F401

    suite = unittest.TestSuite()
    for m in filter(inspect.ismodule, locals().values()):
        suite.addTests(loader.loadTestsFromModule(m))

    return suite


class ChromiumTree(proctree.Forest):

    proc_map: dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        node_list = get_chromium_node_list()
        proc_list = [{k: v for k, v in p.items() if k != 'children'} for p in node_list]
        self.proc_map = {proc['stat']['pid']: proc for proc in proc_list}
        self.proc_map[1] = {'stat': {'ppid': 0, 'pid': 1}}

    def _read_process_dict(self, p, pass_n, **kwargs):
        return self._dictcls({
            k: self._dictcls(v) if isinstance(v, dict) else v
            for k, v in self.proc_map[p].items()
            if k == ['stat', 'cmdline'][pass_n]
        })

    def _get_pid_list(self):
        return list(self.proc_map.keys()) + ([] if self._skip_self else [os.getpid()])


def get_chromium_node_list():
    """
    Get procpath search sample of Chromium browser process tree.

    ::

        chromium-browser ...
        ├─ chromium-browser --type=utility ...
        ├─ chromium-browser --type=gpu-process ...
        │  └─ chromium-browser --type=broker
        └─ chromium-browser --type=zygote
           └─ chromium-browser --type=zygote
              ├─ chromium-browser --type=renderer ...
              ├─ chromium-browser --type=renderer ...
              ├─ chromium-browser --type=renderer ...
              ├─ chromium-browser --type=renderer ...
              ├─ chromium-browser --type=utility ...
              ├─ chromium-browser --type=renderer ...
              ├─ chromium-browser --type=renderer ...
              ├─ chromium-browser --type=renderer ...
              ├─ chromium-browser --type=renderer ...
              └─ chromium-browser --type=renderer ...

    """

    pid_18467 = {
        'stat': {
            'pid': 18467,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 1,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 4194560,
            'minflt': 51931,
            'cminflt': 24741,
            'majflt': 721,
            'cmajflt': 13,
            'utime': 455,
            'stime': 123,
            'cutime': 16,
            'cstime': 17,
            'priority': 20,
            'nice': 0,
            'num_threads': 40,
            'itrealvalue': 0,
            'starttime': 62870630,
            'vsize': 2981761024,
            'rss': 53306,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser ...',
    }
    pid_18482 = {
        'stat': {
            'pid': 18482,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18467,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 4194560,
            'minflt': 3572,
            'cminflt': 0,
            'majflt': 49,
            'cmajflt': 0,
            'utime': 3,
            'stime': 2,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 1,
            'itrealvalue': 0,
            'starttime': 62870663,
            'vsize': 460001280,
            'rss': 13765,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=zygote',
    }
    pid_18484 = {
        'stat': {
            'pid': 18484,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18482,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 4194624,
            'minflt': 278,
            'cminflt': 4862,
            'majflt': 0,
            'cmajflt': 15,
            'utime': 0,
            'stime': 1,
            'cutime': 27,
            'cstime': 4,
            'priority': 20,
            'nice': 0,
            'num_threads': 1,
            'itrealvalue': 0,
            'starttime': 62870674,
            'vsize': 460001280,
            'rss': 3651,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=zygote',
    }
    pid_18529 = {
        'stat': {
            'pid': 18529,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18484,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936192,
            'minflt': 3285,
            'cminflt': 0,
            'majflt': 78,
            'cmajflt': 0,
            'utime': 16,
            'stime': 3,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 12,
            'itrealvalue': 0,
            'starttime': 62870743,
            'vsize': 5411180544,
            'rss': 19849,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=renderer ...',
    }
    pid_18531 = {
        'stat': {
            'pid': 18531,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18484,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936192,
            'minflt': 18231,
            'cminflt': 0,
            'majflt': 183,
            'cmajflt': 0,
            'utime': 118,
            'stime': 18,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 12,
            'itrealvalue': 0,
            'starttime': 62870744,
            'vsize': 16164175872,
            'rss': 26117,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=renderer ...',
    }
    pid_18555 = {
        'stat': {
            'pid': 18555,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18484,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936192,
            'minflt': 62472,
            'cminflt': 0,
            'majflt': 136,
            'cmajflt': 0,
            'utime': 1166,
            'stime': 59,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 14,
            'itrealvalue': 0,
            'starttime': 62870769,
            'vsize': 14124892160,
            'rss': 63235,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=renderer ...',
    }
    pid_18569 = {
        'stat': {
            'pid': 18569,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18484,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936192,
            'minflt': 2695,
            'cminflt': 0,
            'majflt': 8,
            'cmajflt': 0,
            'utime': 7,
            'stime': 3,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 11,
            'itrealvalue': 0,
            'starttime': 62870779,
            'vsize': 5407739904,
            'rss': 18979,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=renderer ...',
    }
    pid_18571 = {
        'stat': {
            'pid': 18571,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18484,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936192,
            'minflt': 930,
            'cminflt': 0,
            'majflt': 20,
            'cmajflt': 0,
            'utime': 6,
            'stime': 3,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 5,
            'itrealvalue': 0,
            'starttime': 62870781,
            'vsize': 5057503232,
            'rss': 8825,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=utility ...',
    }
    pid_18593 = {
        'stat': {
            'pid': 18593,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18484,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936192,
            'minflt': 12212,
            'cminflt': 0,
            'majflt': 2,
            'cmajflt': 0,
            'utime': 171,
            'stime': 11,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 12,
            'itrealvalue': 0,
            'starttime': 62870786,
            'vsize': 5419442176,
            'rss': 22280,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=renderer ...',
    }
    pid_18757 = {
        'stat': {
            'pid': 18757,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18484,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936192,
            'minflt': 1624,
            'cminflt': 0,
            'majflt': 0,
            'cmajflt': 0,
            'utime': 2,
            'stime': 0,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 11,
            'itrealvalue': 0,
            'starttime': 62871186,
            'vsize': 5389012992,
            'rss': 12882
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=renderer ...'
    }
    pid_18769 = {
        'stat': {
            'pid': 18769,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18484,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936192,
            'minflt': 78483,
            'cminflt': 0,
            'majflt': 3,
            'cmajflt': 0,
            'utime': 906,
            'stime': 34,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 12,
            'itrealvalue': 0,
            'starttime': 62871227,
            'vsize': 5497511936,
            'rss': 54376,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=renderer ...',
    }
    pid_18770 = {
        'stat': {
            'pid': 18770,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18484,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936192,
            'minflt': 24759,
            'cminflt': 0,
            'majflt': 2,
            'cmajflt': 0,
            'utime': 260,
            'stime': 15,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 12,
            'itrealvalue': 0,
            'starttime': 62871228,
            'vsize': 5438599168,
            'rss': 31106,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=renderer ...',
    }
    pid_18942 = {
        'stat': {
            'pid': 18942,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18484,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936192,
            'minflt': 12989,
            'cminflt': 0,
            'majflt': 16,
            'cmajflt': 0,
            'utime': 77,
            'stime': 5,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 12,
            'itrealvalue': 0,
            'starttime': 62871410,
            'vsize': 5436309504,
            'rss': 27106,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=renderer ...',
    }
    pid_18503 = {
        'stat': {
            'pid': 18503,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18467,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 4194304,
            'minflt': 14361,
            'cminflt': 0,
            'majflt': 46,
            'cmajflt': 0,
            'utime': 112,
            'stime': 21,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 6,
            'itrealvalue': 0,
            'starttime': 62870711,
            'vsize': 877408256,
            'rss': 27219,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=gpu-process ...',
    }
    pid_18517 = {
        'stat': {
            'pid': 18517,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18503,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 4194368,
            'minflt': 86,
            'cminflt': 0,
            'majflt': 0,
            'cmajflt': 0,
            'utime': 0,
            'stime': 0,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 1,
            'itrealvalue': 0,
            'starttime': 62870723,
            'vsize': 524230656,
            'rss': 4368,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=broker',
    }
    pid_18508 = {
        'stat': {
            'pid': 18508,
            'comm': 'chromium-browse',
            'state': 'S',
            'ppid': 18467,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 1077936128,
            'minflt': 9993,
            'cminflt': 0,
            'majflt': 55,
            'cmajflt': 0,
            'utime': 151,
            'stime': 47,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 12,
            'itrealvalue': 0,
            'starttime': 62870714,
            'vsize': 1302757376,
            'rss': 20059,
        },
        'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=utility ...',
    }

    # update extra stat fields added in 1.5
    for k, v in locals().items():
        if k.startswith('pid_'):
            v['stat'].update({
                'delayacct_blkio_ticks': None,
                'guest_time': None,
                'cguest_time': None,
            })

    return [
        {
            **pid_18467,
            'children': [
                {
                    **pid_18482,
                    'children': [
                        {
                            **pid_18484,
                            'children': [
                                pid_18529, pid_18531, pid_18555, pid_18569, pid_18571,
                                pid_18593, pid_18757, pid_18769, pid_18770, pid_18942,
                            ]
                        }
                    ]
                },
                {
                    **pid_18503,
                    'children': [pid_18517]
                },
                pid_18508
            ]
        },
        {
            **pid_18482,
            'children': [
                {
                    **pid_18484,
                    'children': [
                        pid_18529, pid_18531, pid_18555, pid_18569, pid_18571,
                        pid_18593, pid_18757, pid_18769, pid_18770, pid_18942,
                    ]
                }
            ]
        },
        {
            **pid_18503,
            'children': [pid_18517]
        },
        pid_18508,
        {
            **pid_18484,
            'children': [
                pid_18529, pid_18531, pid_18555, pid_18569, pid_18571,
                pid_18593, pid_18757, pid_18769, pid_18770, pid_18942,
            ]
        },
        pid_18517,
        pid_18529, pid_18531, pid_18555, pid_18569, pid_18571,
        pid_18593, pid_18757, pid_18769, pid_18770, pid_18942,
    ]


def assert_wait_predicate(predicate, timeout=5, message='Timed out waiting for predicate'):
    start = time.time()
    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            raise AssertionError(message)
        elif predicate():
            break
        else:
            time.sleep(0.001)


async def assert_wait_predicate_async(
    predicate, timeout=5, message='Timed out waiting for predicate'
):
    start = time.time()
    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            raise AssertionError(message)
        elif predicate():
            break
        else:
            await asyncio.sleep(0.001)


def assert_lines_match(lines: list[str], regexes: list[str]):
    """Match lines to regular expressions (without order)."""

    remaining_lines = lines.copy()
    regexes = list(reversed(regexes))
    while regexes:
        expected = regexes.pop()
        if expected == '...':
            continue

        assert remaining_lines, f'No lines left for {expected!r}'
        for actual in remaining_lines:
            if re.search(expected, actual):
                remaining_lines.remove(actual)
                break
        else:
            raise AssertionError('No line matches {0!r}\n{1}'.format(expected, '\n'.join(lines)))


def is_port_open(host: str, port: int) -> bool:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        return s.connect_ex((host, port)) == 0


def filterwarnings():
    # Revise with newer pygal
    if (3, 12) <= sys.version_info:
        warnings.filterwarnings(
            'ignore',
            r'datetime\.datetime\.utcfromtimestamp',
            DeprecationWarning,
            r'pygal\.graph\.time|procpath\.plotting'
        )

    if (3, 10) <= sys.version_info < (3, 12):
        warnings.filterwarnings(
            'ignore',
            r'PluginImportFixer\.find_spec\(\) not found; falling back to find_module\(\)',
            ImportWarning,
            r'importlib\._bootstrap',
        )


class TestEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    def new_event_loop(self):
        loop = super().new_event_loop()
        loop.slow_callback_duration = 0.25  # default 0.1 is too low
        return loop


asyncio.set_event_loop_policy(TestEventLoopPolicy())

unittest.TestCase.maxDiff = None
