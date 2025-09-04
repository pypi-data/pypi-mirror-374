import asyncio
import configparser
import contextlib
import http.server
import io
import math
import multiprocessing
import os
import re
import signal
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from unittest import mock

from .. import (
    cli,
    playbook,
    plotting,
    procfile,
    procrec,
    procret,
    proctree,
    sqliteviz,
    treefarm,
    utility,
)
from . import (
    ChromiumTree,
    assert_wait_predicate,
    filterwarnings,
    get_chromium_node_list,
    is_port_open,
)


try:
    import apsw
except ImportError:
    apsw = None


def setUpModule():
    filterwarnings()


class TestUtility(unittest.TestCase):

    def test_evaluate(self):
        actual = utility.evaluate([
            ('A', 'date -I'),
            ('B', 'echo 42')
        ])
        self.assertEqual({'A': date.today().isoformat(), 'B': '42'}, actual)

        self.assertEqual({}, utility.evaluate([]))

    def test_get_meta(self):
        self.assertEqual(
            {
                'platform_node',
                'platform_platform',
                'page_size',
                'clock_ticks',
                'cpu_count',
                'physical_pages',
                'procfile_list',
                'procpath_version',
                'procfs_path',
                'procfs_target',
            },
            utility.get_meta(['stat'], '/proc', 'process').keys(),
        )


class TestPlotting(unittest.TestCase):

    def test_get_line_distance(self):
        self.assertEqual(10, plotting.get_line_distance((0, 0), (10, 0), (10, 0)))
        self.assertEqual(10, plotting.get_line_distance((0, 0), (10, 0), (10, 10)))

        actual = plotting.get_line_distance((90, 51), (34, 15), (-11, -51))
        self.assertAlmostEqual(25.9886, actual, delta=0.00001)

    def test_decimate(self):
        self.assertEqual([(1, 1)], plotting.decimate([(1, 1)], 0))
        self.assertEqual([(1, 1), (1, 1)], plotting.decimate([(1, 1), (1, 1)], 0))
        self.assertEqual([(1, 1), (1, 1)], plotting.decimate([(1, 1), (1, 1), (1, 1)], 0))

        actual = plotting.decimate([(1, 1), (2, 1.1), (3, 1)], 0.05)
        self.assertEqual([(1, 1), (2, 1.1), (3, 1)], actual)
        actual = plotting.decimate([(1, 1), (2, 1.1), (3, 1)], 0.15)
        self.assertEqual([(1, 1), (3, 1)], actual)

        points = [(x / 10, math.log2(x)) for x in range(1, 100)]
        actual = plotting.decimate(points, 0.3)
        expected = [
            (0.1, 0.0),
            (0.7, 2.807354922057604),
            (2.1, 4.392317422778761),
            (5.0, 5.643856189774724),
            (9.9, 6.6293566200796095),
        ]
        self.assertEqual(expected, actual)

    def test_moving_average(self):
        series = list(zip(range(10), range(10)))
        self.assertEqual([], list(plotting.moving_average([], n=1)))
        self.assertEqual([], list(plotting.moving_average(series, n=11)))
        self.assertEqual(series, list(plotting.moving_average(series, n=1)))

        x, y = zip(*plotting.moving_average(series, n=2))
        expected = (0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5)
        self.assertEqual(tuple(range(1, 10)), x)
        self.assertEqual(expected, y)

        x, y = zip(*plotting.moving_average(series, n=5))
        expected = (2.0, 3.0, 4.0, 5.0, 6.0, 7.0)
        self.assertEqual(tuple(range(2, 8)), x)
        self.assertEqual(expected, y)

        x, y = zip(*plotting.moving_average(series, n=10))
        expected = (4.5,)
        self.assertEqual(tuple(range(5, 6)), x)
        self.assertEqual(expected, y)

        with self.assertRaises(AssertionError):
            list(plotting.moving_average(series, n=0))

    def test_plot(self):
        pid_series = {
            309: [(0, 0), (10, 10), (15, 5)],
            2610: [(0, 0), (10, 10), (25, 10)],
        }
        query = procret.Query('SELECT 1', 'Dummy')
        with tempfile.NamedTemporaryFile() as f:
            plotting.plot([pid_series], [query], f.name, title='Visions')
            svg_bytes = f.read()

        self.assertIn(b'<svg', svg_bytes)
        self.assertIn(b'Visions', svg_bytes)
        self.assertIn(b'309', svg_bytes)
        self.assertIn(b'2610', svg_bytes)
        self.assertEqual(6, svg_bytes.count(b'<g class="dots">'))
        self.assertGreater(len(svg_bytes), 18000)

        with tempfile.NamedTemporaryFile() as f:
            plotting.plot([pid_series], [query], f.name, title='Visions', style='LightGreenStyle')
            svg_green_bytes = f.read()

        self.assertIn(b'<svg', svg_bytes)
        self.assertIn(b'Visions', svg_bytes)
        self.assertIn(b'309', svg_bytes)
        self.assertIn(b'2610', svg_bytes)
        self.assertEqual(6, svg_bytes.count(b'<g class="dots">'))
        self.assertGreater(len(svg_bytes), 18000)
        self.assertNotEqual(svg_bytes, svg_green_bytes)

    def test_plot_no_dots(self):
        pid_series = {
            309: [(0, 0), (10, 10), (15, 5)],
            2610: [(0, 0), (10, 10), (25, 10)],
        }
        query = procret.Query('SELECT 1', 'Dummy')
        with tempfile.NamedTemporaryFile() as f:
            plotting.plot([pid_series], [query], f.name, title='Visions', no_dots=True)
            svg_bytes = f.read()

        self.assertIn(b'<svg', svg_bytes)
        self.assertIn(b'Visions', svg_bytes)
        self.assertIn(b'309', svg_bytes)
        self.assertIn(b'2610', svg_bytes)
        self.assertEqual(0, svg_bytes.count(b'<g class="dots">'))
        self.assertGreater(len(svg_bytes), 18000)

    def test_plot_log_negative(self):
        pid_series = {
            309: [(0, 0), (10, 10), (15, -5)],
            2610: [(0, 0), (10, 10), (25, 10)],
        }
        query = procret.Query('SELECT 1', 'Dummy')
        with tempfile.NamedTemporaryFile() as f:
            plotting.plot([pid_series], [query], f.name, title='Visions', logarithmic=True)
            svg_bytes = f.read()

        self.assertIn(b'<svg', svg_bytes)
        self.assertIn(b'Visions', svg_bytes)
        self.assertIn(b'309', svg_bytes)
        self.assertIn(b'2610', svg_bytes)
        self.assertEqual(3, svg_bytes.count(b'<g class="dots">'))
        self.assertGreater(len(svg_bytes), 18000)

    def test_plot_partially_defined_series(self):
        pid_series1 = {
            309: [(0, 0), (10, 10), (15, -5)],
            2610: [(0, 0), (10, 10), (25, 10), (30, 15), (40, 20)],
        }
        pid_series2 = {
            2610: [(0, 0), (10, 5), (25, 5), (30, 3), (40, 4)],
            5119: [(30, -30), (40, 30)],
        }
        query = procret.Query('SELECT 1', 'Dummy')
        with tempfile.NamedTemporaryFile() as f:
            plotting.plot([pid_series1, pid_series2], [query, query], f.name, title='Visions')
            svg_bytes = f.read()

        self.assertIn(b'<svg', svg_bytes)
        self.assertIn(b'Visions', svg_bytes)
        self.assertIn(b'309', svg_bytes)
        self.assertIn(b'2610', svg_bytes)
        self.assertEqual(14, svg_bytes.count(b'<g class="dots">'))
        self.assertGreater(len(svg_bytes), 18000)

    def test_plot_compact_x_labels(self):
        pid_series = {
            309: [
                ('2022-07-30T10:41:40.336560', 0),
                ('2022-07-30T10:43:20.423570', 1),
                ('2022-07-30T10:45:00.520632', 2),
                ('2022-07-30T10:50:00.793236', 3),
                ('2022-07-31T10:41:40.311577', 4),
                ('2022-07-31T10:41:41.464654', 5),
            ],
        }
        pid_series[309] = [
            (datetime.fromisoformat(dt).replace(tzinfo=timezone.utc).timestamp(), v)
            for dt, v in pid_series[309]
        ]

        query = procret.Query('SELECT 1', 'Dummy')
        with tempfile.NamedTemporaryFile() as f:
            plotting.plot([pid_series], [query], f.name, title='Visions', no_dots=True)
            svg_bytes = f.read()

        self.assertIn(b'<svg', svg_bytes)
        self.assertIn(b'Visions', svg_bytes)
        self.assertIn(b'309', svg_bytes)
        self.assertEqual(1, svg_bytes.count(b'">2022-07-30'))
        self.assertEqual(1, svg_bytes.count(b'">2022-07-31'))
        self.assertGreater(len(svg_bytes), 18000)

    def test_plot_absolute_x_label_formatting(self):
        pid_series = {
            309: [
                ('2022-07-30T10:41:40.322', 0),
                ('2022-07-30T10:41:40.411', 1),
                ('2022-07-30T10:41:40.522', 2),
                ('2022-07-30T10:41:40.611', 3),
                ('2022-07-30T10:41:40.722', 4),
            ],
        }
        pid_series[309] = [
            (datetime.fromisoformat(dt).replace(tzinfo=timezone.utc).timestamp(), v)
            for dt, v in pid_series[309]
        ]

        query = procret.Query('SELECT 1', 'Dummy')
        with tempfile.NamedTemporaryFile() as f:
            plotting.plot([pid_series], [query], f.name, title='Visions', no_dots=True)
            svg_bytes = f.read()

        self.assertIn(b'<svg', svg_bytes)
        self.assertIn(b'Visions', svg_bytes)
        self.assertIn(b'309', svg_bytes)
        self.assertEqual(0, svg_bytes.count(b'2022-07-30T10:41:40.440000'))
        self.assertEqual(1, svg_bytes.count(b'2022-07-30T10:41:40.44'))
        self.assertEqual(0, svg_bytes.count(b'2022-07-30T10:41:40.600000'))
        self.assertEqual(3, svg_bytes.count(b'2022-07-30T10:41:40.6'))

    def test_plot_relative_x_label_formatting(self):
        pid_series = {
            309: [
                ('2022-07-30T10:41:40.322', 0),
                ('2022-07-30T10:41:40.411', 1),
                ('2022-07-30T10:41:40.522', 2),
                ('2022-07-30T10:41:40.611', 3),
                ('2022-07-30T10:41:40.722', 4),
            ],
        }
        pid_series[309] = [
            (datetime.fromisoformat(dt).replace(tzinfo=timezone.utc).timestamp(), v)
            for dt, v in pid_series[309]
        ]

        query = procret.Query('SELECT 1', 'Dummy')
        with tempfile.NamedTemporaryFile() as f:
            plotting.plot(
                [pid_series], [query], f.name, title='Visions', no_dots=True, relative_time=True
            )
            svg_bytes = f.read()

        self.assertIn(b'<svg', svg_bytes)
        self.assertIn(b'Visions', svg_bytes)
        self.assertIn(b'309', svg_bytes)
        self.assertEqual(0, svg_bytes.count(b'2022-07-30'))
        self.assertEqual(2, svg_bytes.count(b'>0:00:00<'))
        self.assertEqual(2, svg_bytes.count(b'0:00:00.04'))
        self.assertEqual(2, svg_bytes.count(b'0:00:00.08'))
        self.assertEqual(2, svg_bytes.count(b'0:00:00.12'))
        self.assertEqual(2, svg_bytes.count(b'0:00:00.16'))
        self.assertEqual(2, svg_bytes.count(b'0:00:00.2<'))
        self.assertEqual(2, svg_bytes.count(b'0:00:00.36'))

    def test_format_x_value_absolute(self):
        actual = plotting.format_x_value_absolute(datetime(2022, 9, 3, 19, 38, 4))
        self.assertEqual('2022-09-03T19:38:04', actual)
        actual = plotting.format_x_value_absolute(datetime(2022, 9, 3, 19, 38, 0, 500000))
        self.assertEqual('2022-09-03T19:38:00.5', actual)
        actual = plotting.format_x_value_absolute(datetime(2022, 9, 3, 19, 38, 0, 1000))
        self.assertEqual('2022-09-03T19:38:00.001', actual)
        actual = plotting.format_x_value_absolute(datetime(2022, 9, 3, 19, 38, 0))
        self.assertEqual('2022-09-03T19:38:00', actual)

    def test_format_x_value_relative(self):
        start = datetime(2022, 7, 30, 10, 41, 40, 322000)

        actual = plotting.format_x_value_relative(start, start)
        self.assertEqual('0:00:00', actual)
        actual = plotting.format_x_value_relative(start, datetime(2022, 7, 30, 10, 41, 40, 411000))
        self.assertEqual('0:00:00.089', actual)
        actual = plotting.format_x_value_relative(start, datetime(2022, 7, 30, 10, 41, 40, 522000))
        self.assertEqual('0:00:00.2', actual)
        actual = plotting.format_x_value_relative(start, datetime(2022, 7, 30, 14, 56, 42))
        self.assertEqual('4:15:01.678', actual)
        actual = plotting.format_x_value_relative(start, datetime(2022, 7, 31, 12, 41, 40))
        self.assertEqual('1 day, 1:59:59.678', actual)


class TestProctreeForest(unittest.TestCase):

    testee: ChromiumTree

    def setUp(self):
        self.testee = ChromiumTree(procfile.registry)

    def test_get_pid_list(self):
        actual = proctree.Forest({'stat': procfile.registry['stat']})._get_pid_list()
        self.assertTrue(all(isinstance(v, int) for v in actual))
        self.assertEqual(actual, sorted(actual))

    def test_get_pid_list_missing_own_pid_warning(self):
        with mock.patch('os.listdir') as m:
            m.return_value = ['1']
            with self.assertLogs('procpath', 'WARNING') as ctx:
                actual = proctree.Forest({'stat': procfile.registry['stat']})._get_pid_list()

        self.assertEqual(1, len(ctx.records))
        msg = ctx.records[0].message
        self.assertEqual('Procpath process PID was not found in collected PIDs', msg)

        self.assertEqual([1], actual)

    def test_get_pid_list_thread_target(self):
        testee = proctree.Forest({'stat': procfile.registry['stat']}, procfs_target='thread')
        actual = testee._get_pid_list()
        self.assertTrue(all(isinstance(v, int) for v in actual))
        self.assertEqual(actual, sorted(actual))

    def test_get_nodemap(self):
        expected = {p['stat']['pid']: p for p in get_chromium_node_list()}
        expected[1] = {'stat': {'ppid': 0, 'pid': 1}, 'children': [get_chromium_node_list()[0]]}
        actual = self.testee._get_nodemap()
        self.assertEqual(expected, actual)

    def test_get_roots(self):
        expected = [{'stat': {'ppid': 0, 'pid': 1}, 'children': [get_chromium_node_list()[0]]}]
        actual = self.testee.get_roots()
        self.assertEqual(expected, actual)

    def test_get_roots_branch_pids(self):
        node_list = get_chromium_node_list()
        pid_18482 = self.testee.proc_map[18482].copy()
        pid_18482['children'] = [node_list[4]]  # PID 18484 with children
        pid_18467 = self.testee.proc_map[18467].copy()
        pid_18467['children'] = [pid_18482, node_list[3]]  # the second item is PID 18508
        expected = [{'stat': {'ppid': 0, 'pid': 1}, 'children': [pid_18467]}]
        actual = self.testee.get_roots([18484, 18531, 18508])
        self.assertEqual(expected, actual)

    def test_get_roots_branch_pids_noop(self):
        self.assertEqual(self.testee.get_roots(), self.testee.get_roots([1, 2, 3]))

    def test_get_roots_branch_pids_non_existent(self):
        self.assertEqual([], self.testee.get_roots([666]))

    def test_get_roots_branch_pids_hidden_parent(self):
        # For instance, Termux shell knows its PPID but it's not in /proc
        self.testee.proc_map = {
            18571: self.testee.proc_map[18571],
            18503: self.testee.proc_map[18503],
            18517: self.testee.proc_map[18517],
        }
        expected = [
            self.testee.proc_map[18571],
            {
                **self.testee.proc_map[18503],
                'children': [self.testee.proc_map[18517]],
            },
        ]
        actual = self.testee.get_roots()
        self.assertEqual(expected, actual)

    def test_read_process_dict(self):
        testee = proctree.Forest(procfile.registry)
        actual = testee._read_process_dict(os.getpid(), pass_n=0)
        self.assertEqual({'stat'}, actual.keys())
        self.assertIn('rss', actual['stat'])

        actual = testee._read_process_dict(os.getpid(), pass_n=1, raise_on_missing_file=False)
        self.assertEqual({'cmdline', 'io', 'status', 'fd', 'smaps_rollup'}, actual.keys())
        self.assertIn('rchar', actual['io'])
        self.assertIn('vmswap', actual['status'])
        self.assertIn('reg', actual['fd'])
        self.assertIn('swappss', actual['smaps_rollup'])

        testee = proctree.Forest(
            {k: v for k, v in procfile.registry.items() if k in ('stat', 'cmdline')}
        )
        actual = testee._read_process_dict(os.getpid(), pass_n=0)
        actual.update(testee._read_process_dict(os.getpid(), pass_n=1))
        self.assertEqual(['stat', 'cmdline'], list(actual.keys()))

    def test_read_process_dict_permission_error(self):
        testee = proctree.Forest(
            {k: v for k, v in procfile.registry.items() if k in ('stat', 'io')}
        )

        with self.assertLogs('procpath', 'WARNING') as ctx:
            actual = testee._read_process_dict(1, pass_n=1)
        self.assertEqual(1, len(ctx.records))
        msg = ctx.records[0].message
        self.assertTrue(msg.startswith('Storing empty values for pid 1, procfile io because of'))
        self.assertIn('Permission denied', msg)

        self.assertEqual({'io': procfile.registry['io'].empty}, actual)

    def test_read_process_dict_file_not_found_error(self):
        testee = proctree.Forest({k: v for k, v in procfile.registry.items() if k in ('stat',)})

        with self.assertLogs('procpath', 'DEBUG') as ctx:
            actual = testee._read_process_dict(2 ** 15 + 1, pass_n=0, raise_on_missing_file=False)
        self.assertEqual(1, len(ctx.records))
        msg = ctx.records[0].message
        self.assertTrue(msg.startswith('Storing empty values for pid 32769, procfile stat'))
        self.assertIn("No such file or directory: '/proc/32769/stat'", msg)

        self.assertEqual({'stat': procfile.registry['stat'].empty}, actual)

    def test_read_process_dict_corrupted_io(self):
        corrupted_io_sample = (
            b'rchar: 2274068\nwchar: 15681\nsyscr: 377\nsyscw: 10\nread_bytes: '
            b'0\nwrite_bytes:\ncancelled_write_bytes: 0\n'
        )
        with tempfile.TemporaryDirectory() as tmpd:
            root_pid_dir = Path(f'{tmpd}/proc/1')
            root_pid_dir.mkdir(parents=True)
            (root_pid_dir / 'io').write_bytes(corrupted_io_sample)

            testee = proctree.Forest(
                {
                    'stat': procfile.registry['stat'],
                    'io': procfile.registry['io'],
                },
                procfs=f'{tmpd}/proc',
            )

            with self.assertLogs('procpath', 'WARNING') as ctx:
                actual = testee._read_process_dict(1, pass_n=1)

        self.assertEqual(1, len(ctx.records))
        msg = ctx.records[0].message
        self.assertTrue(msg.startswith('Storing empty values for pid 1, procfile io because of'))
        self.assertIn('not enough values to unpack', msg)

        self.assertEqual({'io': procfile.registry['io'].empty}, actual)

    def test_read_process_dict_corrupted_status(self):
        partial_status_sample = (
            b'Name:\tMainThread\n'
            b'Umask:\t0022\n'
            b'State:\tS (sleeping)\n'
            b'Tgid:\t24167\n'
            b'Ngid:\t0\n'
            b'Pid:\t24167\n'
            b'PPid:\t3887\n'
        )
        with tempfile.TemporaryDirectory() as tmpd:
            root_pid_dir = Path(f'{tmpd}/proc/1')
            root_pid_dir.mkdir(parents=True)
            (root_pid_dir / 'status').write_bytes(partial_status_sample)

            testee = proctree.Forest(
                {
                    'stat': procfile.registry['stat'],
                    'status': procfile.registry['status'],
                },
                procfs=f'{tmpd}/proc',
            )

            with self.assertLogs('procpath', 'WARNING') as ctx:
                actual = testee._read_process_dict(1, pass_n=1)

        self.assertEqual(1, len(ctx.records))
        msg = ctx.records[0].message
        self.assertTrue(
            msg.startswith('Storing empty values for pid 1, procfile status because of')
        )
        self.assertIn('missing 15 required positional arguments', msg)

        self.assertEqual({'status': procfile.registry['status'].empty}, actual)

    def test_read_process_dict_corrupted_smaps_rollup(self):
        partial_smaps_rollup_sample = (
            b'c0000000-ffffffffff601000 ---p 00000000 00:00 0                          [rollup]\n'
            b'Rss:             1488628 kB\n'
            b'Pss:             1469668 kB\n'
            b'Shared_Clean:      20388 kB\n'
            b'Shared_Dirty:          X kB\n'
            b'Private_Clean:    167092 kB\n'
            b'Private_Dirty:   1300008 kB\n'
        )
        with tempfile.TemporaryDirectory() as tmpd:
            root_pid_dir = Path(f'{tmpd}/proc/1')
            root_pid_dir.mkdir(parents=True)
            (root_pid_dir / 'smaps_rollup').write_bytes(partial_smaps_rollup_sample)

            testee = proctree.Forest(
                {
                    'stat': procfile.registry['stat'],
                    'smaps_rollup': procfile.registry['smaps_rollup'],
                },
                procfs=f'{tmpd}/proc',
            )

            with self.assertLogs('procpath', 'WARNING') as ctx:
                actual = testee._read_process_dict(1, pass_n=1)

        self.assertEqual(1, len(ctx.records))
        msg = ctx.records[0].message
        self.assertTrue(
            msg.startswith('Storing empty values for pid 1, procfile smaps_rollup because of')
        )
        self.assertIn('invalid literal for int() with base 10:', msg)

        self.assertEqual({'smaps_rollup': procfile.registry['smaps_rollup'].empty}, actual)

    def test_get_roots_do_not_skip_self(self):
        testee = proctree.Forest({'stat': procfile.registry['stat']}, skip_self=False)
        proc_map = {
            1: {'stat': {'ppid': 0}},
            os.getpid(): {'stat': {'ppid': 1}}
        }
        testee._read_process_dict = lambda p, pass_n, **kwargs: {} if pass_n else proc_map[p]
        testee._get_pid_list = lambda: list(proc_map.keys())

        expected = [{'stat': {'ppid': 0}, 'children': [{'stat': {'ppid': 1}}]}]
        self.assertEqual(expected, testee.get_roots())

    def test_invalid_dunder_init_arguments(self):
        with self.assertRaises(proctree.TreeError) as ctx:
            proctree.Forest({'io': procfile.registry['io']})
        self.assertEqual('stat file reader is required', str(ctx.exception))

        with self.assertRaises(proctree.TreeError) as ctx:
            proctree.Forest({'stat': procfile.registry['stat']}, procfs_target='foo')
        self.assertEqual('Procfs target must be process or thread', str(ctx.exception))


class TestProctree(unittest.TestCase):

    def test_flatten(self):
        actual = proctree.flatten(get_chromium_node_list(), ['stat'])

        # trim for brevity
        for d in actual:
            for k in list(d.keys()):
                if k not in ('stat_pid', 'stat_rss', 'stat_state'):
                    d.pop(k)

        expected = [
            {'stat_pid': 18467, 'stat_rss': 53306, 'stat_state': 'S'},
            {'stat_pid': 18482, 'stat_rss': 13765, 'stat_state': 'S'},
            {'stat_pid': 18484, 'stat_rss': 3651, 'stat_state': 'S'},
            {'stat_pid': 18529, 'stat_rss': 19849, 'stat_state': 'S'},
            {'stat_pid': 18531, 'stat_rss': 26117, 'stat_state': 'S'},
            {'stat_pid': 18555, 'stat_rss': 63235, 'stat_state': 'S'},
            {'stat_pid': 18569, 'stat_rss': 18979, 'stat_state': 'S'},
            {'stat_pid': 18571, 'stat_rss': 8825, 'stat_state': 'S'},
            {'stat_pid': 18593, 'stat_rss': 22280, 'stat_state': 'S'},
            {'stat_pid': 18757, 'stat_rss': 12882, 'stat_state': 'S'},
            {'stat_pid': 18769, 'stat_rss': 54376, 'stat_state': 'S'},
            {'stat_pid': 18770, 'stat_rss': 31106, 'stat_state': 'S'},
            {'stat_pid': 18942, 'stat_rss': 27106, 'stat_state': 'S'},
            {'stat_pid': 18503, 'stat_rss': 27219, 'stat_state': 'S'},
            {'stat_pid': 18517, 'stat_rss': 4368, 'stat_state': 'S'},
            {'stat_pid': 18508, 'stat_rss': 20059, 'stat_state': 'S'},
        ]
        self.assertEqual(expected, actual)

    def test_flatten_single_value_procfile(self):
        actual = proctree.flatten(get_chromium_node_list(), ['cmdline'])

        renderer = {'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=renderer ...'}
        expected = [
            {'cmdline': '/usr/lib/chromium-browser/chromium-browser ...'},
            {'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=zygote'},
            {'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=zygote'},
            renderer, renderer, renderer, renderer,
            {'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=utility ...'},
            renderer, renderer, renderer, renderer, renderer,
            {'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=gpu-process ...'},
            {'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=broker'},
            {'cmdline': '/usr/lib/chromium-browser/chromium-browser --type=utility ...'},
        ]
        self.assertEqual(expected, actual)

    def test_flatten_list_value(self):
        actual = proctree.flatten([{
            'stat': {
                'pid': 18467,
                'ppid': 1,
            },
            'status': {
                'name': 'MainThread',
                'umask': 18,
                'state': 'S',
                'tgid': 24167,
                'ngid': 0,
                'pid': 24167,
                'ppid': 3887,
                'tracerpid': 0,
                'uid': (1000, 1000, 1000, 1000),
                'gid': (1000, 1000, 1000, 1000),
                'fdsize': 256,
                'groups': (4, 24, 27, 29, 30, 46, 113, 130, 131, 132, 136, 1000),
            },
        }], ['status'])
        expected = [{
            'status_name': 'MainThread',
            'status_umask': 18,
            'status_state': 'S',
            'status_tgid': 24167,
            'status_ngid': 0,
            'status_pid': 24167,
            'status_ppid': 3887,
            'status_tracerpid': 0,
            'status_uid': '[1000,1000,1000,1000]',
            'status_gid': '[1000,1000,1000,1000]',
            'status_fdsize': 256,
            'status_groups': '[4,24,27,29,30,46,113,130,131,132,136,1000]'
        }]
        self.assertEqual(expected, actual)

    def test_attr_dict(self):
        ad = proctree.AttrDict({'a': 'b'})
        self.assertEqual('b', ad.a)


class TestTreeFarm(unittest.TestCase):
    def test_process_exists(self):
        p = subprocess.Popen(['sleep', '0.05'])
        self.addCleanup(p.terminate)
        time.sleep(0.01)
        self.assertTrue(treefarm.process_exists(p.pid))
        p.wait(1)

        p = subprocess.run('true & echo $!', stdout=subprocess.PIPE, shell=True)
        time.sleep(0.01)
        self.assertFalse(treefarm.process_exists(int(p.stdout)))


class TestProcrecSqliteStorage(unittest.TestCase):

    testeee = None

    def setUp(self):
        self.testee = procrec.SqliteStorage(':memory:', ['stat', 'cmdline'], {})
        self.addCleanup(self.testee.close)

    def test_create_schema_all(self):
        testee = procrec.SqliteStorage(
            ':memory:',
            ['stat', 'cmdline', 'io', 'status', 'fd', 'smaps_rollup'],
            utility.get_meta(['stat'], '/proc', 'process'),
        )
        self.addCleanup(testee.close)
        testee.create_schema()

        cursor = testee._conn.execute('''
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite%'
        ''')
        self.assertEqual([('record',), ('meta',)], cursor.fetchall())

        cursor = testee._conn.execute('''
            SELECT sql
            FROM sqlite_master
            WHERE name  = 'record'
        ''')
        expected = '''
            CREATE TABLE record (
                record_id INTEGER PRIMARY KEY NOT NULL,
                ts        REAL NOT NULL,
                cmdline TEXT,
                fd_anon INTEGER,
                fd_dir INTEGER,
                fd_chr INTEGER,
                fd_blk INTEGER,
                fd_reg INTEGER,
                fd_fifo INTEGER,
                fd_lnk INTEGER,
                fd_sock INTEGER,
                io_rchar INTEGER,
                io_wchar INTEGER,
                io_syscr INTEGER,
                io_syscw INTEGER,
                io_read_bytes INTEGER,
                io_write_bytes INTEGER,
                io_cancelled_write_bytes INTEGER,
                smaps_rollup_rss INTEGER,
                smaps_rollup_pss INTEGER,
                smaps_rollup_shared_clean INTEGER,
                smaps_rollup_shared_dirty INTEGER,
                smaps_rollup_private_clean INTEGER,
                smaps_rollup_private_dirty INTEGER,
                smaps_rollup_referenced INTEGER,
                smaps_rollup_anonymous INTEGER,
                smaps_rollup_lazyfree INTEGER,
                smaps_rollup_anonhugepages INTEGER,
                smaps_rollup_shmempmdmapped INTEGER,
                smaps_rollup_shared_hugetlb INTEGER,
                smaps_rollup_private_hugetlb INTEGER,
                smaps_rollup_swap INTEGER,
                smaps_rollup_swappss INTEGER,
                smaps_rollup_locked INTEGER,
                stat_pid INTEGER,
                stat_comm TEXT,
                stat_state TEXT,
                stat_ppid INTEGER,
                stat_pgrp INTEGER,
                stat_session INTEGER,
                stat_tty_nr INTEGER,
                stat_tpgid INTEGER,
                stat_flags INTEGER,
                stat_minflt INTEGER,
                stat_cminflt INTEGER,
                stat_majflt INTEGER,
                stat_cmajflt INTEGER,
                stat_utime INTEGER,
                stat_stime INTEGER,
                stat_cutime INTEGER,
                stat_cstime INTEGER,
                stat_priority INTEGER,
                stat_nice INTEGER,
                stat_num_threads INTEGER,
                stat_itrealvalue INTEGER,
                stat_starttime INTEGER,
                stat_vsize INTEGER,
                stat_rss INTEGER,
                stat_delayacct_blkio_ticks INTEGER,
                stat_guest_time INTEGER,
                stat_cguest_timeINTEGER,
                status_name TEXT,
                status_umask INTEGER,
                status_state TEXT,
                status_tgid INTEGER,
                status_ngid INTEGER,
                status_pid INTEGER,
                status_ppid INTEGER,
                status_tracerpid INTEGER,
                status_uid TEXT,
                status_gid TEXT,
                status_fdsize INTEGER,
                status_groups TEXT,
                status_nstgid TEXT,
                status_nspid TEXT,
                status_nspgid TEXT,
                status_nssid TEXT,
                status_vmpeak INTEGER,
                status_vmsize INTEGER,
                status_vmlck INTEGER,
                status_vmpin INTEGER,
                status_vmhwm INTEGER,
                status_vmrss INTEGER,
                status_rssanon INTEGER,
                status_rssfile INTEGER,
                status_rssshmem INTEGER,
                status_vmdata INTEGER,
                status_vmstk INTEGER,
                status_vmexe INTEGER,
                status_vmlib INTEGER,
                status_vmpte INTEGER,
                status_vmpmd INTEGER,
                status_vmswap INTEGER,
                status_hugetlbpages INTEGER,
                status_coredumping INTEGER,
                status_threads INTEGER,
                status_sigq TEXT,
                status_sigpnd INTEGER,
                status_shdpnd INTEGER,
                status_sigblk INTEGER,
                status_sigign INTEGER,
                status_sigcgt INTEGER,
                status_capinh INTEGER,
                status_capprm INTEGER,
                status_capeff INTEGER,
                status_capbnd INTEGER,
                status_capamb INTEGER,
                status_nonewprivs INTEGER,
                status_seccomp INTEGER,
                status_speculation_store_bypass TEXT,
                status_cpus_allowed INTEGER,
                status_cpus_allowed_list TEXT,
                status_mems_allowed TEXT,
                status_mems_allowed_list TEXT,
                status_voluntary_ctxt_switches INTEGER,
                status_nonvoluntary_ctxt_switches INTEGER
            )
        '''
        self.assertEqual(re.sub(r'\s+', '', expected), re.sub(r'\s+', '', cursor.fetchone()[0]))

        cursor = testee._conn.execute('''
            SELECT sql
            FROM sqlite_master
            WHERE name  = 'meta'
        ''')
        expected = '''
            CREATE TABLE meta (
                key   TEXT PRIMARY KEY NOT NULL,
                value TEXT NOT NULL
            )
        '''
        self.assertEqual(re.sub(r'\s+', '', expected), re.sub(r'\s+', '', cursor.fetchone()[0]))

        cursor = testee._conn.execute('SELECT * FROM meta')
        actual = dict(list(cursor))
        actual['page_size'] = int(actual['page_size'])
        actual['clock_ticks'] = int(actual['clock_ticks'])
        actual['physical_pages'] = int(actual['physical_pages'])
        actual['cpu_count'] = int(actual['cpu_count'])
        self.assertEqual(utility.get_meta(['stat'], '/proc', 'process'), actual)

    def test_create_schema_one(self):
        testee = procrec.SqliteStorage(':memory:', ['cmdline'], {})
        self.addCleanup(testee.close)
        testee.create_schema()

        cursor = testee._conn.execute('''
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite%'
        ''')
        self.assertEqual([('record',), ('meta',)], cursor.fetchall())

        cursor = testee._conn.execute('''
            SELECT sql
            FROM sqlite_master
            WHERE name  = 'record'
        ''')
        expected = '''
            CREATE TABLE record (
                record_id INTEGER PRIMARY KEY NOT NULL,
                ts        REAL NOT NULL,
                cmdline   TEXT
            )
        '''
        self.assertEqual(re.sub(r'\s+', '', expected), re.sub(r'\s+', '', cursor.fetchone()[0]))

    def test_record(self):
        ts = 1594483603.109486
        data = proctree.flatten(get_chromium_node_list(), self.testee._procfile_list)
        with self.testee:
            self.testee.record(ts, data)

            self.testee._conn.row_factory = sqlite3.Row
            cursor = self.testee._conn.execute('SELECT * FROM record')
            expected = [dict(d, record_id=i + 1, ts=ts) for i, d in enumerate(data)]
            self.assertEqual(expected, list(map(dict, cursor)))

        with self.assertRaises(sqlite3.ProgrammingError) as ctx:
            self.testee._conn.execute('SELECT * FROM record')
        self.assertEqual('Cannot operate on a closed database.', str(ctx.exception))

    def test_record_unsigned_bigint(self):
        ts = 1594483603.109486
        data = proctree.flatten(get_chromium_node_list(), self.testee._procfile_list)

        data[0]['stat_vsize'] = 2 ** 63  # observed for status_vmlib in the wild
        with self.testee:
            self.testee.record(ts, data)

            self.testee._conn.row_factory = sqlite3.Row
            cursor = self.testee._conn.execute('SELECT * FROM record')
            expected = [dict(d, record_id=i + 1, ts=ts) for i, d in enumerate(data)]
            self.assertEqual(expected, list(map(dict, cursor)))

    def test_record_empty(self):
        ts = 1594483603.109486
        with self.testee:
            self.testee.record(ts, [])
            cursor = self.testee._conn.execute('SELECT * FROM record')
            self.assertEqual([], cursor.fetchall())


class TestProcret(unittest.TestCase):

    database_file = None

    @classmethod
    def setUpClass(cls):
        cls.database_file = tempfile.NamedTemporaryFile()
        cls.database_file.__enter__()

        procfile_list = ['stat', 'cmdline']
        storage = procrec.SqliteStorage(
            cls.database_file.name,
            procfile_list,
            utility.get_meta(procfile_list, '/proc', 'process'),
        )
        data = proctree.flatten(get_chromium_node_list(), storage._procfile_list)
        with storage:
            for i, ts in enumerate(range(1567504800, 1567504800 + 7200, 60)):
                data = [
                    dict(d, stat_utime=d['stat_utime'] + i / 4) if d['stat_pid'] == 18467 else d
                    for d in data
                ]
                storage.record(ts, data)
        storage.close()

    @classmethod
    def tearDownClass(cls):
        cls.database_file.close()

    def test_rss(self):
        rows = procret.query(self.database_file.name, procret.registry['rss'])
        self.assertEqual(1920, len(rows))
        self.assertEqual({'ts': 1567504800.0, 'pid': 18467, 'value': 208.2265625}, rows[0])

    def test_rss_filter_ts(self):
        rows = procret.query(
            self.database_file.name,
            procret.registry['rss'],
            after=datetime(2019, 9, 3, 10, 30, tzinfo=timezone.utc),
            before=datetime(2019, 9, 3, 11, 30, tzinfo=timezone.utc),
        )
        self.assertEqual(976, len(rows))
        self.assertEqual({'ts': 1567506600.0, 'pid': 18467, 'value': 208.2265625}, rows[0])

        rows = procret.query(
            self.database_file.name,
            procret.registry['rss'],
            after=datetime(2019, 9, 3, 12, 30, tzinfo=timezone.utc),
            before=datetime(2019, 9, 3, 13, 30, tzinfo=timezone.utc),
        )
        self.assertEqual([], rows)

    def test_rss_filter_pid(self):
        rows = procret.query(
            self.database_file.name,
            procret.registry['rss'],
            pid_list=[18508, 18555, 18757],
        )
        self.assertEqual(360, len(rows))
        self.assertEqual({'pid': 18508, 'ts': 1567504800.0, 'value': 78.35546875}, rows[0])

        rows = procret.query(
            self.database_file.name,
            procret.registry['rss'],
            pid_list=[666],
        )
        self.assertEqual([], rows)

    def test_rss_filter_pid_short_and_long(self):
        with tempfile.NamedTemporaryFile() as f:
            testee = procrec.SqliteStorage(
                f.name, ['stat'], utility.get_meta(['stat'], '/proc', 'process')
            )
            self.addCleanup(testee.close)

            node_list = proctree.flatten(get_chromium_node_list(), testee._procfile_list)
            node = node_list[0]
            self.assertEqual(18467, node['stat_pid'])
            ts = 1594483603.109486
            with testee:
                for i in range(5, 0, -1):
                    testee.record(ts, [dict(node, stat_pid=node['stat_pid'] % 10 ** i)])

            rows = procret.query(f.name, procret.registry['rss'], pid_list=[node['stat_pid']])
            self.assertEqual([{'ts': ts, 'pid': 18467, 'value': 208.2265625}], rows)

    @unittest.skipUnless(apsw or sqlite3.sqlite_version_info >= (3, 25), 'sqlite3 is too old')
    def test_cpu(self):
        rows = procret.query(self.database_file.name, procret.registry['cpu'])
        self.assertEqual(1904, len(rows))
        self.assertEqual(
            [
                {'pid': 18467, 'ts': 1567504860.0, 'value': 0.004166666666666667},
                {'pid': 18467, 'ts': 1567504920.0, 'value': 0.008333333333333333},
                {'pid': 18467, 'ts': 1567504980.0, 'value': 0.0125},
                {'pid': 18467, 'ts': 1567505040.0, 'value': 0.016666666666666666},
                {'pid': 18467, 'ts': 1567505100.0, 'value': 0.020833333333333332},
                {'pid': 18467, 'ts': 1567505160.0, 'value': 0.025},
                {'pid': 18467, 'ts': 1567505220.0, 'value': 0.029166666666666667},
                {'pid': 18467, 'ts': 1567505280.0, 'value': 0.03333333333333333},
                {'pid': 18467, 'ts': 1567505340.0, 'value': 0.0375},
                {'pid': 18467, 'ts': 1567505400.0, 'value': 0.041666666666666664},
                {'pid': 18467, 'ts': 1567505460.0, 'value': 0.04583333333333333},
                {'pid': 18467, 'ts': 1567505520.0, 'value': 0.05},
                {'pid': 18467, 'ts': 1567505580.0, 'value': 0.05416666666666667},
                {'pid': 18467, 'ts': 1567505640.0, 'value': 0.058333333333333334},
                {'pid': 18467, 'ts': 1567505700.0, 'value': 0.0625},
                {'pid': 18467, 'ts': 1567505760.0, 'value': 0.06666666666666667},
                {'pid': 18467, 'ts': 1567505820.0, 'value': 0.07083333333333333},
                {'pid': 18467, 'ts': 1567505880.0, 'value': 0.075},
                {'pid': 18467, 'ts': 1567505940.0, 'value': 0.07916666666666666},
                {'pid': 18467, 'ts': 1567506000.0, 'value': 0.08333333333333333},
                {'pid': 18467, 'ts': 1567506060.0, 'value': 0.0875},
                {'pid': 18467, 'ts': 1567506120.0, 'value': 0.09166666666666666},
                {'pid': 18467, 'ts': 1567506180.0, 'value': 0.09583333333333334},
                {'pid': 18467, 'ts': 1567506240.0, 'value': 0.1},
            ],
            rows[:24],
        )

    @unittest.skipUnless(apsw or sqlite3.sqlite_version_info >= (3, 25), 'sqlite3 is too old')
    def test_cpu_filter_ts(self):
        rows = procret.query(
            self.database_file.name,
            procret.registry['cpu'],
            after=datetime(2019, 9, 3, 10, 30, tzinfo=timezone.utc),
            before=datetime(2019, 9, 3, 11, 30, tzinfo=timezone.utc),
        )
        self.assertEqual(976, len(rows))
        self.assertEqual({'pid': 18467, 'ts': 1567506600.0, 'value': 0.125}, rows[0])

        rows = procret.query(
            self.database_file.name,
            procret.registry['cpu'],
            after=datetime(2019, 9, 3, 12, 30, tzinfo=timezone.utc),
            before=datetime(2019, 9, 3, 13, 30, tzinfo=timezone.utc),
        )
        self.assertEqual([], rows)

    @unittest.skipUnless(apsw or sqlite3.sqlite_version_info >= (3, 25), 'sqlite3 is too old')
    def test_cpu_filter_pid(self):
        rows = procret.query(
            self.database_file.name,
            procret.registry['cpu'],
            pid_list=[18508, 18555, 18757],
        )
        self.assertEqual({'pid': 18508, 'ts': 1567504860.0, 'value': 0.0}, rows[0])

        rows = procret.query(
            self.database_file.name,
            procret.registry['cpu'],
            pid_list=[666],
        )
        self.assertEqual([], rows)

    def test_create_query(self):
        query = procret.create_query('260 / 10', title='Custom query')
        rows = procret.query(
            self.database_file.name,
            query,
            after=datetime(2019, 9, 3, 10, 30, tzinfo=timezone.utc),
            before=datetime(2019, 9, 3, 11, 30, tzinfo=timezone.utc),
            pid_list=[18508, 18555, 18757],
        )
        self.assertEqual(183, len(rows))
        self.assertEqual({'ts': 1567506600.0, 'pid': 18508, 'value': 26}, rows[0])
        self.assertEqual({'ts': 1567510200.0, 'pid': 18757, 'value': 26}, rows[-1])

    def test_query_get_short_query(self):
        query = procret.create_query('46.2', title='Custom query')

        expected = textwrap.dedent('''
            SELECT
                ts, -- unix timestamp
                stat_pid pid,
                46.2 value
            FROM record
        ''').strip()
        actual = textwrap.dedent(query.get_short_query()).strip()
        self.assertEqual(expected, actual)

        expected = textwrap.dedent('''
            SELECT
                ts * 1000 ts,
                stat_pid pid,
                46.2 value
            FROM record
        ''').strip()
        actual = textwrap.dedent(query.get_short_query(ts_as_milliseconds=True)).strip()
        self.assertEqual(expected, actual)

    def test_query_procfile_required(self):
        query = procret.Query(
            'SELECT COUNT(*) cnt FROM record',
            'Dummy query',
            procfile_required=frozenset(['status', 'io']),
        )
        with tempfile.NamedTemporaryFile() as f:
            procfile_list = ['stat', 'status', 'io']
            storage = procrec.SqliteStorage(
                f.name, procfile_list, utility.get_meta(procfile_list, '/proc', 'process')
            )
            with storage:
                pass

            self.assertEqual([{'cnt': 0}], procret.query(f.name, query))

    def test_query_procfile_required_missing(self):
        query = procret.Query(
            'SELECT COUNT(*) cnt FROM record',
            'Dummy query',
            procfile_required=frozenset(['status', 'io', 'fd']),
        )
        with tempfile.NamedTemporaryFile() as f:
            procfile_list = ['stat', 'status', 'smaps_rollup']
            storage = procrec.SqliteStorage(
                f.name, procfile_list, utility.get_meta(procfile_list, '/proc', 'process')
            )
            with storage:
                pass

            with self.assertRaises(procret.QueryError) as ctx:
                procret.query(f.name, query)
            self.assertEqual(
                "'Dummy query' requires the following procfiles missing in the database: fd, io",
                str(ctx.exception),
            )

    def test_query_procfile_required_missing_old_db(self):
        query = procret.Query(
            'SELECT COUNT(*) cnt FROM record',
            'Dummy query',
            procfile_required=frozenset(['io', 'fd']),
        )
        with tempfile.NamedTemporaryFile() as f:
            storage = procrec.SqliteStorage(
                f.name, ['stat'], utility.get_meta(['stat'], '/proc', 'process')
            )
            with storage, storage._conn:
                storage._conn.execute("DELETE FROM meta WHERE key = 'procfile_list'")

            with self.assertRaises(procret.QueryError) as ctx:
                procret.query(f.name, query)
            self.assertEqual(
                "'Dummy query' requires the following procfiles missing in the database: fd, io",
                str(ctx.exception),
            )


class TestCli(unittest.TestCase):

    def test_build_parser_record(self):
        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            'record',
            '-f', 'stat,cmdline',
            '-e', 'N=\'docker inspect -f "{{.State.Pid}}" project_nginx_1\'',
            '-i', '10',
            '-r', '100',
            '-v', '25',
            '-d', 'db.sqlite',
            '$..children[?(@.stat.pid == $N)]',
        ]))
        expected = {
            'command': 'record',
            'procfile_list': ['stat', 'cmdline'],
            'environment': [['N', '\'docker inspect -f "{{.State.Pid}}" project_nginx_1\'']],
            'interval': 10.0,
            'recnum': 100,
            'reevalnum': 25,
            'pid_list': None,
            'database_file': 'db.sqlite',
            'query': '$..children[?(@.stat.pid == $N)]',
            'logging_level': 'INFO',
            'stop_without_result': False,
            'procfs': '/proc',
            'procfs_target': 'process',
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            'record',
            '-e', 'N=\'docker inspect -f "{{.State.Pid}}" project_nginx_1\'',
            '-p', '1,$N',
            '-d', 'db.sqlite',
            '--stop-without-result',
            '--procfs', '/mnt/remot_proc',
            '--procfs-target', 'thread',
        ]))
        expected = {
            'command': 'record',
            'procfile_list': ['stat', 'cmdline'],
            'environment': [['N', '\'docker inspect -f "{{.State.Pid}}" project_nginx_1\'']],
            'interval': 10.0,
            'recnum': None,
            'reevalnum': None,
            'pid_list': '1,$N',
            'database_file': 'db.sqlite',
            'query': None,
            'logging_level': 'INFO',
            'stop_without_result': True,
            'procfs': '/mnt/remot_proc',
            'procfs_target': 'thread',
        }
        self.assertEqual(expected, actual)

    def test_build_parser_query(self):
        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            'query',
            '-f', 'stat',
            '-d', ',',
            '$..children[?(@.stat.pid == 666)]..pid',
        ]))
        expected = {
            'command': 'query',
            'procfile_list': ['stat'],
            'delimiter': ',',
            'indent': None,
            'query': '$..children[?(@.stat.pid == 666)]..pid',
            'output_file': sys.stdout,
            'sql_query': None,
            'logging_level': 'INFO',
            'environment': None,
            'procfs': '/proc',
            'procfs_target': 'process',
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            'query',
            '-f', 'stat',
            '-i', '2',
            '$..children[?(@.stat.pid == 666)]..pid',
        ]))
        expected = {
            'command': 'query',
            'procfile_list': ['stat'],
            'delimiter': None,
            'indent': 2,
            'query': '$..children[?(@.stat.pid == 666)]..pid',
            'output_file': sys.stdout,
            'sql_query': None,
            'logging_level': 'INFO',
            'environment': None,
            'procfs': '/proc',
            'procfs_target': 'process',
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            '--logging-level', 'ERROR',
            'query',
            '-f', 'stat',
            '-i', '2',
            '--procfs', '/foo/bar/',
            '--procfs-target', 'thread',
            '$..children[?(@.stat.pid == 666)]',
            'SELECT SUM(stat_rss) / 1024.0 * 4 FROM record',
        ]))
        expected = {
            'command': 'query',
            'procfile_list': ['stat'],
            'delimiter': None,
            'indent': 2,
            'query': '$..children[?(@.stat.pid == 666)]',
            'output_file': sys.stdout,
            'sql_query': 'SELECT SUM(stat_rss) / 1024.0 * 4 FROM record',
            'logging_level': 'ERROR',
            'environment': None,
            'procfs': '/foo/bar',
            'procfs_target': 'thread',
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            'query',
            '-f', 'stat',
            '-i', '2',
            '-e', 'I=echo 123',
            '-e', 'D=date',
            '',
            'SELECT SUM(stat_rss) / 1024.0 * 4 FROM record',
        ]))
        expected = {
            'command': 'query',
            'procfile_list': ['stat'],
            'delimiter': None,
            'indent': 2,
            'query': '',
            'output_file': sys.stdout,
            'sql_query': 'SELECT SUM(stat_rss) / 1024.0 * 4 FROM record',
            'logging_level': 'INFO',
            'environment': [['I', 'echo 123'], ['D', 'date']],
            'procfs': '/proc',
            'procfs_target': 'process',
        }
        self.assertEqual(expected, actual)

    def test_build_parser_plot(self):
        parser = cli.build_parser()
        actual = vars(parser.parse_args(['plot', '-d', 'db.sqite']))
        expected = {
            'command': 'plot',
            'database_file': 'db.sqite',
            'plot_file': 'plot.svg',
            'query_name_list': None,
            'after': None,
            'before': None,
            'pid_list': None,
            'epsilon': None,
            'moving_average_window': None,
            'share_y_axis': False,
            'logarithmic': False,
            'style': None,
            'formatter': None,
            'title': None,
            'no_dots': False,
            'relative_time': False,
            'custom_query_file_list': None,
            'custom_value_expr_list': None,
            'logging_level': 'INFO',
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args(['plot', '-d', 'db.sqite', '-q', 'cpu']))
        expected = {
            'command': 'plot',
            'database_file': 'db.sqite',
            'plot_file': 'plot.svg',
            'query_name_list': ['cpu'],
            'after': None,
            'before': None,
            'pid_list': None,
            'epsilon': None,
            'moving_average_window': None,
            'share_y_axis': False,
            'logarithmic': False,
            'style': None,
            'formatter': None,
            'title': None,
            'no_dots': False,
            'relative_time': False,
            'custom_query_file_list': None,
            'custom_value_expr_list': None,
            'logging_level': 'INFO',
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            '--logging-level', 'WARNING',
            'plot',
            '-d', 'db.sqite',
            '-f', 'rss.svg',
            '--query-name', 'rss',
            '--query-name', 'cpu',
            '--log',
            '-p', '1,2,3',
            '--epsilon', '26.1089',
            '-w', '10',
            '--style', 'LightGreenStyle',
            '--formatter', 'integer',
            '--title', 'Visions',
            '--no-dots',
            '--share-y-axis',
            '--relative-time',
        ]))
        expected = {
            'command': 'plot',
            'database_file': 'db.sqite',
            'plot_file': 'rss.svg',
            'query_name_list': ['rss', 'cpu'],
            'after': None,
            'before': None,
            'pid_list': [1, 2, 3],
            'epsilon': 26.1089,
            'moving_average_window': 10,
            'share_y_axis': True,
            'logarithmic': True,
            'style': 'LightGreenStyle',
            'formatter': 'integer',
            'title': 'Visions',
            'no_dots': True,
            'relative_time': True,
            'custom_query_file_list': None,
            'custom_value_expr_list': None,
            'logging_level': 'WARNING',
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            'plot',
            '-d', 'db.sqite',
            '--title', 'Custom',
            '--after', '2000-01-01T00:00:00',
            '--before', '2020-01-01T00:00:00',
            '--custom-query-file', 'query1.sql',
            '--custom-query-file', 'query2.sql',
        ]))
        expected = {
            'command': 'plot',
            'database_file': 'db.sqite',
            'plot_file': 'plot.svg',
            'query_name_list': None,
            'after': datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc),
            'before': datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            'pid_list': None,
            'epsilon': None,
            'moving_average_window': None,
            'share_y_axis': False,
            'logarithmic': False,
            'style': None,
            'formatter': None,
            'title': 'Custom',
            'no_dots': False,
            'relative_time': False,
            'custom_query_file_list': ['query1.sql', 'query2.sql'],
            'custom_value_expr_list': None,
            'logging_level': 'INFO',
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            'plot',
            '-d', 'db.sqite',
            '--title', 'Custom',
            '--after', '2000-01-01T00:00:00',
            '--before', '2020-01-01T00:00:00',
            '--custom-value-expr', 'stat_majflt / 1000.0',
            '--custom-value-expr', 'stat_minflt / 1000.0',
        ]))
        expected = {
            'command': 'plot',
            'database_file': 'db.sqite',
            'plot_file': 'plot.svg',
            'query_name_list': None,
            'after': datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc),
            'before': datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            'pid_list': None,
            'epsilon': None,
            'moving_average_window': None,
            'share_y_axis': False,
            'logarithmic': False,
            'style': None,
            'formatter': None,
            'title': 'Custom',
            'no_dots': False,
            'relative_time': False,
            'custom_query_file_list': None,
            'custom_value_expr_list': ['stat_majflt / 1000.0', 'stat_minflt / 1000.0'],
            'logging_level': 'INFO',
        }
        self.assertEqual(expected, actual)

    def test_build_parser_watch(self):
        parser = cli.build_parser()
        actual = vars(parser.parse_args(['watch', '-c', 'echo 1', '-i', '10']))
        expected = {
            'command': 'watch',
            'environment': None,
            'query_list': None,
            'command_list': ['echo 1'],
            'interval': 10.0,
            'kill_after': 10.0,
            'repeat': None,
            'procfile_list': ['stat', 'cmdline'],
            'stop_signal': 'SIGINT',
            'logging_level': 'INFO',
            'no_restart': False,
            'procfs': '/proc',
            'procfs_target': 'process',
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            'watch',
            '-e', 'D=date +%s',
            '-c', 'echo 1',
            '-c', 'echo $D',
            '--interval', '30',
            '-r', '1',
            '-s', 'SIGTERM',
        ]))
        expected = {
            'command': 'watch',
            'environment': [['D', 'date +%s']],
            'query_list': None,
            'command_list': ['echo 1', 'echo $D'],
            'interval': 30.0,
            'repeat': 1,
            'procfile_list': ['stat', 'cmdline'],
            'stop_signal': 'SIGTERM',
            'kill_after': 10.0,
            'logging_level': 'INFO',
            'no_restart': False,
            'procfs': '/proc',
            'procfs_target': 'process',
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            '--logging-level', 'ERROR',
            'watch',
            '--procfile-list', 'stat,status',
            '--interval', '30',
            '--environment', 'C=docker inspect -f "{{.State.Pid}}" stack_postgres_1',
            '--environment', 'S=systemctl show --property MainPID nginx.service | cut -d "=" -f 2',
            '--environment', 'D=date +%s',
            '--query', 'L1=$..children[?(@.stat.pid == $C)]..pid',
            '--query', 'L2=$..children[?(@.stat.pid == $S)]..pid',
            '--command', "pidstat -dru -hl -p $L1 10 30 >> 'record-$D.pidstat",
            '--command', 'smemstat -o smemstat-$D.json -p $L2',
            '--no-restart',
            '--kill-after', '666',
            '--procfs', '/mnt/remot_proc/',
            '--procfs-target', 'thread',
        ]))
        expected = {
            'command': 'watch',
            'environment': [
                ['C', 'docker inspect -f "{{.State.Pid}}" stack_postgres_1'],
                ['S', 'systemctl show --property MainPID nginx.service | cut -d "=" -f 2'],
                ['D', 'date +%s'],
            ],
            'query_list': [
                ['L1', '$..children[?(@.stat.pid == $C)]..pid'],
                ['L2', '$..children[?(@.stat.pid == $S)]..pid']
            ],
            'command_list': [
                "pidstat -dru -hl -p $L1 10 30 >> 'record-$D.pidstat",
                'smemstat -o smemstat-$D.json -p $L2'
            ],
            'interval': 30.0,
            'procfile_list': ['stat', 'status'],
            'repeat': None,
            'stop_signal': 'SIGINT',
            'kill_after': 666.0,
            'logging_level': 'ERROR',
            'no_restart': True,
            'procfs': '/mnt/remot_proc',
            'procfs_target': 'thread',
        }
        self.assertEqual(expected, actual)

    def test_build_parser_play(self):
        parser = cli.build_parser()
        actual = vars(parser.parse_args(['play', '-f', 'jigsaw.procfile', '*']))
        expected = {
            'logging_level': 'INFO',
            'command': 'play',
            'target': ['*'],
            'playbook_file': 'jigsaw.procfile',
            'list_sections': False,
            'dry_run': False,
            'option_override_list': None,
            'output_file': sys.stdout,
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            'play', '-f', 'jigsaw.procfile', '-n', 'river:watch', 'river:plot'
        ]))
        expected = {
            'logging_level': 'INFO',
            'command': 'play',
            'target': ['river:watch', 'river:plot'],
            'playbook_file': 'jigsaw.procfile',
            'list_sections': False,
            'dry_run': True,
            'option_override_list': None,
            'output_file': sys.stdout,
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            'play', '-f', 'jigsaw.procfile', '-l', 'river:watch', 'river:plot'
        ]))
        expected = {
            'logging_level': 'INFO',
            'command': 'play',
            'target': ['river:watch', 'river:plot'],
            'playbook_file': 'jigsaw.procfile',
            'list_sections': True,
            'dry_run': False,
            'option_override_list': None,
            'output_file': sys.stdout,
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            '--logging-level', 'ERROR',
            'play',
            '-f', 'jigsaw.procfile',
            '-l',
            '--option', 'epsilon=0.1',
            '--option', 'database_file=desert_island_disk.sqlite',
            '*:plot'
        ]))
        expected = {
            'logging_level': 'ERROR',
            'command': 'play',
            'target': ['*:plot'],
            'playbook_file': 'jigsaw.procfile',
            'list_sections': True,
            'dry_run': False,
            'option_override_list': [
                ['epsilon', '0.1'],
                ['database_file', 'desert_island_disk.sqlite'],
            ],
            'output_file': sys.stdout,
        }
        self.assertEqual(expected, actual)

    def test_build_parser_explore(self):
        parser = cli.build_parser()
        actual = vars(parser.parse_args(['explore']))
        expected = {
            'logging_level': 'INFO',
            'command': 'explore',
            'reinstall': False,
            'build_url': 'https://github.com/lana-k/sqliteviz/releases/latest/download/dist.zip',
            'bind': '',
            'port': 8000,
            'open_in_browser': True,
            'database_file': None,
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args(['explore', '-p', '8080', '--bind', '127.0.0.1']))
        expected = {
            'logging_level': 'INFO',
            'command': 'explore',
            'reinstall': False,
            'build_url': 'https://github.com/lana-k/sqliteviz/releases/latest/download/dist.zip',
            'bind': '127.0.0.1',
            'port': 8080,
            'open_in_browser': True,
            'database_file': None,
        }
        self.assertEqual(expected, actual)

        parser = cli.build_parser()
        actual = vars(parser.parse_args([
            '--logging-level', 'ERROR',
            'explore',
            '--reinstall',
            '--build-url', 'https://github.com/lana-k/sqliteviz/releases/download/0.6.0/dist.zip',
            '--database-file', '/tmp/foo.sqlite',
        ]))
        expected = {
            'logging_level': 'ERROR',
            'command': 'explore',
            'reinstall': True,
            'build_url': 'https://github.com/lana-k/sqliteviz/releases/download/0.6.0/dist.zip',
            'bind': '',
            'port': 8000,
            'open_in_browser': True,
            'database_file': '/tmp/foo.sqlite',
        }
        self.assertEqual(expected, actual)

    def test_cli(self):
        subprocess.check_output(
            [sys.executable, '-m', 'procpath', 'query', '$..children[?(@.stat.pid == -1)]..pid'],
            env=os.environ,
        )

    def test_cli_help(self):
        subprocess.check_output(
            [sys.executable, '-m', 'procpath', 'plot', '--help'],
            env=os.environ,
        )

    def test_cli_missing_command(self):
        with self.assertRaises(subprocess.CalledProcessError) as ctx:
            subprocess.check_output(
                [sys.executable, '-m', 'procpath'], stderr=subprocess.PIPE, env=os.environ
            )
        self.assertTrue(
            ctx.exception.stderr.endswith(
                b'error: the following arguments are required: command\n'
            )
        )

    def test_cli_command_error(self):
        with self.assertRaises(subprocess.CalledProcessError) as ctx:
            subprocess.check_output(
                [sys.executable, '-m', 'procpath', 'query', '!@#$'],
                stderr=subprocess.PIPE,
                env=os.environ,
            )
        self.assertEqual(1, ctx.exception.returncode)
        self.assertIn(b'JSONPath syntax error', ctx.exception.stderr)

    def test_cli_logging_level(self):
        output = subprocess.check_output(
            [
                sys.executable, '-m', 'procpath', 'watch',
                '-i', '0.2',
                '-r', '1',
                '-c', 'echo Carousel',
                '-c', 'sleep 0.1 && echo "A Glutton for Punishment" 1>&2',
            ],
            stderr=subprocess.STDOUT,
            env=dict(os.environ, PYTHONASYNCIODEBUG=''),
            encoding='utf-8',
        )
        lines = output.splitlines()
        self.assertEqual(2, len(lines), lines)
        self.assertIn('INFO    procpath №1: Carousel', lines[0])
        self.assertIn('WARNING procpath №2: A Glutton for Punishment', lines[1])

        output = subprocess.check_output(
            [
                sys.executable, '-m', 'procpath', '--logging-level', 'WARNING', 'watch',
                '-i', '0',
                '-r', '1',
                '-c', 'echo Carousel',
                '-c', 'echo "A Glutton for Punishment" 1>&2',
            ],
            stderr=subprocess.STDOUT,
            env=dict(os.environ, PYTHONASYNCIODEBUG=''),
            encoding='utf-8',
        )
        lines = output.splitlines()
        self.assertEqual(1, len(lines), lines)
        self.assertIn('WARNING procpath №2: A Glutton for Punishment', lines[0])

    def test_cli_clean_sigint_stop(self):
        async def test():
            with tempfile.NamedTemporaryFile() as f:
                process = await asyncio.create_subprocess_exec(
                    *[sys.executable, '-m', 'procpath', 'record', '-p', '1', '-d', f.name],
                    env=os.environ,
                )
                process.send_signal(signal.SIGINT)
                stdout_data, stderr_data = await process.communicate()

            self.assertIsNotNone(process.returncode)
            self.assertNotEqual(0, process.returncode)
            self.assertIsNone(stdout_data)
            self.assertIsNone(stderr_data)

        asyncio.run(test(), debug=True)


class TestProcfile(unittest.TestCase):

    def test_read_stat(self):
        content = (
            b'32222 (python3.7) R 29884 337 337 0 -1 4194304 3765 0 1 0 19 3 0 '
            b'0 20 0 2 0 89851404 150605824 5255 18446744073709551615 4194304 '
            b'8590100 140727866261328 0 0 0 4 553652224 2 0 0 0 17 2 0 0 1 0 0 '
            b'10689968 11363916 15265792 140727866270452 140727866270792 '
            b'140727866270792 140727866273727 0\n'
        )
        expected = {
            'pid': 32222,
            'comm': 'python3.7',
            'state': 'R',
            'ppid': 29884,
            'pgrp': 337,
            'session': 337,
            'tty_nr': 0,
            'tpgid': -1,
            'flags': 4194304,
            'minflt': 3765,
            'cminflt': 0,
            'majflt': 1,
            'cmajflt': 0,
            'utime': 19,
            'stime': 3,
            'cutime': 0,
            'cstime': 0,
            'priority': 20,
            'nice': 0,
            'num_threads': 2,
            'itrealvalue': 0,
            'starttime': 89851404,
            'vsize': 150605824,
            'rss': 5255,
            'delayacct_blkio_ticks': 1,
            'guest_time': 0,
            'cguest_time': 0,
        }
        actual = procfile.read_stat(content)
        self.assertEqual(expected, actual)

    def test_read_stat_kernel_2_6_8(self):
        content = (
            b'6794 (udpkg) S 499 498 498 34816 498 256 315 0 0 0 0 0 0 0 16 0 '
            b'1 0 3791 3862528 172 18446744073709551615 4194304 4207180 '
            b'548682071216 18446744073709551615 182896967110 0 0 0 0 '
            b'18446744071563316617 0 0 17 0 0 0\n'
        )
        expected = {
            'pid': 6794,
            'comm': 'udpkg',
            'state': 'S',
            'ppid': 499,
            'pgrp': 498,
            'session': 498,
            'tty_nr': 34816,
            'tpgid': 498,
            'flags': 256,
            'minflt': 315,
            'cminflt': 0,
            'majflt': 0,
            'cmajflt': 0,
            'utime': 0,
            'stime': 0,
            'cutime': 0,
            'cstime': 0,
            'priority': 16,
            'nice': 0,
            'num_threads': 1,
            'itrealvalue': 0,
            'starttime': 3791,
            'vsize': 3862528,
            'rss': 172,
            'delayacct_blkio_ticks': None,
            'guest_time': None,
            'cguest_time': None
        }
        actual = procfile.read_stat(content)
        self.assertEqual(expected, actual)

    def test_read_cmdline(self):
        content = b'python3.7\x00-Wa\x00-u\x00'
        expected = 'python3.7 -Wa -u'
        actual = procfile.read_cmdline(content)
        self.assertEqual(expected, actual)

    def test_read_io(self):
        content = (
            b'rchar: 2274068\nwchar: 15681\nsyscr: 377\nsyscw: 10\nread_bytes: '
            b'0\nwrite_bytes: 20480\ncancelled_write_bytes: 0\n'
        )
        expected = {
            'rchar': 2274068,
            'wchar': 15681,
            'syscr': 377,
            'syscw': 10,
            'read_bytes': 0,
            'write_bytes': 20480,
            'cancelled_write_bytes': 0
        }
        actual = procfile.read_io(content)
        self.assertEqual(expected, actual)

    def test_read_status_4_13(self):
        content = (
            b'Name:\tMainThread\n'
            b'Umask:\t0022\n'
            b'State:\tS (sleeping)\n'
            b'Tgid:\t24167\n'
            b'Ngid:\t0\n'
            b'Pid:\t24167\n'
            b'PPid:\t3887\n'
            b'TracerPid:\t0\n'
            b'Uid:\t1000    1000    1000    1000\n'
            b'Gid:\t1000    1000    1000    1000\n'
            b'FDSize:\t256\n'
            b'Groups:\t4 24 27 29 30 46 113 130 131 132 136 1000\n'
            b'NStgid:\t24167\n'
            b'NSpid:\t24167\n'
            b'NSpgid:\t2287\n'
            b'NSsid:\t2287\n'
            b'VmPeak:\t  19488708 kB\n'
            b'VmSize:\t  3523068 kB\n'
            b'VmLck:\t         0 kB\n'
            b'VmPin:\t         0 kB\n'
            b'VmHWM:\t    608460 kB\n'
            b'VmRSS:\t    520744 kB\n'
            b'RssAnon:\t          370924 kB\n'
            b'RssFile:\t           73148 kB\n'
            b'RssShmem:\t          76672 kB\n'
            b'VmData:\t   578248 kB\n'
            b'VmStk:\t       132 kB\n'
            b'VmExe:\t      1972 kB\n'
            b'VmLib:\t    232128 kB\n'
            b'VmPTE:\t      2604 kB\n'
            b'VmPMD:\t       280 kB\n'
            b'VmSwap:\t        0 kB\n'
            b'HugetlbPages:\t          0 kB\n'
            b'Threads:\t57\n'
            b'SigQ:\t1/31038\n'
            b'SigPnd:\t0000000000000000\n'
            b'ShdPnd:\t0000000000000000\n'
            b'SigBlk:\t0000000000000000\n'
            b'SigIgn:\t0000000021001000\n'
            b'SigCgt:\t0000000f800044ff\n'
            b'CapInh:\t0000000000000000\n'
            b'CapPrm:\t0000000000000000\n'
            b'CapEff:\t0000000000000000\n'
            b'CapBnd:\t0000003fffffffff\n'
            b'CapAmb:\t0000000000000000\n'
            b'NoNewPrivs:\t0\n'
            b'Seccomp:\t0\n'
            b'Speculation_Store_Bypass:\tthread vulnerable\n'
            b'Cpus_allowed:\tff\n'
            b'Cpus_allowed_list:\t0-7\n'
            b'Mems_allowed:\t00000000,00000000,00000000,00000000,00000000,00000000,00000000,'
            b'00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,'
            b'00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,'
            b'00000000,00000000,00000000,00000000,00000000,00000000,00000001\n'
            b'Mems_allowed_list:\t0\n'
            b'voluntary_ctxt_switches:\t1443497\n'
            b'nonvoluntary_ctxt_switches:\t724507\n'
        )
        expected = {
            'name': 'MainThread',
            'umask': 18,
            'state': 'S',
            'tgid': 24167,
            'ngid': 0,
            'pid': 24167,
            'ppid': 3887,
            'tracerpid': 0,
            'uid': (1000, 1000, 1000, 1000),
            'gid': (1000, 1000, 1000, 1000),
            'fdsize': 256,
            'groups': (4, 24, 27, 29, 30, 46, 113, 130, 131, 132, 136, 1000),
            'nstgid': (24167,),
            'nspid': (24167,),
            'nspgid': (2287,),
            'nssid': (2287,),
            'vmpeak': 19488708,
            'vmsize': 3523068,
            'vmlck': 0,
            'vmpin': 0,
            'vmhwm': 608460,
            'vmrss': 520744,
            'rssanon': 370924,
            'rssfile': 73148,
            'rssshmem': 76672,
            'vmdata': 578248,
            'vmstk': 132,
            'vmexe': 1972,
            'vmlib': 232128,
            'vmpte': 2604,
            'vmpmd': 280,
            'vmswap': 0,
            'hugetlbpages': 0,
            'coredumping': None,
            'threads': 57,
            'sigq': (1, 31038),
            'sigpnd': 0,
            'shdpnd': 0,
            'sigblk': 0,
            'sigign': 553652224,
            'sigcgt': 66572010751,
            'capinh': 0,
            'capprm': 0,
            'capeff': 0,
            'capbnd': 274877906943,
            'capamb': 0,
            'nonewprivs': 0,
            'seccomp': 0,
            'speculation_store_bypass': 'thread vulnerable',
            'cpus_allowed': 255,
            'cpus_allowed_list': '0-7',
            'mems_allowed': (
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
            ),
            'mems_allowed_list': '0',
            'voluntary_ctxt_switches': 1443497,
            'nonvoluntary_ctxt_switches': 724507
        }
        actual = procfile.read_status(content)
        self.assertEqual(expected, actual)

    def test_read_status_3_16(self):
        content = (
            b'Name:\tpython3.7\n'
            b'State:\tS (sleeping)\n'
            b'Tgid:\t28463\n'
            b'Ngid:\t0\n'
            b'Pid:\t28463\n'
            b'PPid:\t28445\n'
            b'TracerPid:\t0\n'
            b'Uid:\t689824  689824  689824  689824\n'
            b'Gid:\t689824  689824  689824  689824\n'
            b'FDSize:\t64\n'
            b'Groups:\t689824 689825 689826 689827 689828 689830 '
            b'689834 689835 689844 689850 689851\n'
            b'VmPeak:\t    42152 kB\n'
            b'VmSize:\t    42152 kB\n'
            b'VmLck:\t         0 kB\n'
            b'VmPin:\t         0 kB\n'
            b'VmHWM:\t     29940 kB\n'
            b'VmRSS:\t     19220 kB\n'
            b'VmData:\t    31784 kB\n'
            b'VmStk:\t       132 kB\n'
            b'VmExe:\t         8 kB\n'
            b'VmLib:\t      4912 kB\n'
            b'VmPTE:\t       100 kB\n'
            b'VmSwap:\t    10772 kB\n'
            b'Threads:\t7\n'
            b'SigQ:\t0/7968\n'
            b'SigPnd:\t0000000000000000\n'
            b'ShdPnd:\t0000000000000000\n'
            b'SigBlk:\t0000000000000000\n'
            b'SigIgn:\t0000000001001000\n'
            b'SigCgt:\t0000000000000002\n'
            b'CapInh:\t00000000a80425fb\n'
            b'CapPrm:\t00000000a80425fb\n'
            b'CapEff:\t00000000a80425fb\n'
            b'CapBnd:\t00000000a80425fb\n'
            b'Seccomp:\t0\n'
            b'Cpus_allowed:\t1\n'
            b'Cpus_allowed_list:\t0\n'
            b'Mems_allowed:\t00000000,00000001\n'
            b'Mems_allowed_list:\t0\n'
            b'voluntary_ctxt_switches:\t288015\n'
            b'nonvoluntary_ctxt_switches:\t60055\n'
        )
        expected = {
            'name': 'python3.7',
            'umask': None,
            'state': 'S',
            'tgid': 28463,
            'ngid': 0,
            'pid': 28463,
            'ppid': 28445,
            'tracerpid': 0,
            'uid': (689824, 689824, 689824, 689824),
            'gid': (689824, 689824, 689824, 689824),
            'fdsize': 64,
            'groups': (
                689824, 689825, 689826, 689827, 689828, 689830, 689834,
                689835, 689844, 689850, 689851,
            ),
            'nstgid': None,
            'nspid': None,
            'nspgid': None,
            'nssid': None,
            'vmpeak': 42152,
            'vmsize': 42152,
            'vmlck': 0,
            'vmpin': 0,
            'vmhwm': 29940,
            'vmrss': 19220,
            'rssanon': None,
            'rssfile': None,
            'rssshmem': None,
            'vmdata': 31784,
            'vmstk': 132,
            'vmexe': 8,
            'vmlib': 4912,
            'vmpte': 100,
            'vmpmd': None,
            'vmswap': 10772,
            'hugetlbpages': None,
            'coredumping': None,
            'threads': 7,
            'sigq': (0, 7968),
            'sigpnd': 0,
            'shdpnd': 0,
            'sigblk': 0,
            'sigign': 16781312,
            'sigcgt': 2,
            'capinh': 2818844155,
            'capprm': 2818844155,
            'capeff': 2818844155,
            'capbnd': 2818844155,
            'capamb': None,
            'nonewprivs': None,
            'seccomp': 0,
            'speculation_store_bypass': None,
            'cpus_allowed': 1,
            'cpus_allowed_list': '0',
            'mems_allowed': (0, 1),
            'mems_allowed_list': '0',
            'voluntary_ctxt_switches': 288015,
            'nonvoluntary_ctxt_switches': 60055
        }
        actual = procfile.read_status(content)
        self.assertEqual(expected, actual)

    def test_read_status_3_2(self):
        content = (
            b'Name:\tnginx\n'
            b'State:\tS (sleeping)\n'
            b'Tgid:\t2913\n'
            b'Pid:\t2913\n'
            b'PPid:\t1\n'
            b'TracerPid:\t0\n'
            b'Uid:\t0       0       0       0\n'
            b'Gid:\t0       0       0       0\n'
            b'FDSize:\t32\n'
            b'Groups:\t\n'
            b'VmPeak:\t    10448 kB\n'
            b'VmSize:\t    10448 kB\n'
            b'VmLck:\t         0 kB\n'
            b'VmPin:\t         0 kB\n'
            b'VmHWM:\t      1212 kB\n'
            b'VmRSS:\t       680 kB\n'
            b'VmData:\t      748 kB\n'
            b'VmStk:\t       136 kB\n'
            b'VmExe:\t       740 kB\n'
            b'VmLib:\t      8164 kB\n'
            b'VmPTE:\t        32 kB\n'
            b'VmSwap:\t      488 kB\n'
            b'Threads:\t1\n'
            b'SigQ:\t0/3939\n'
            b'SigPnd:\t0000000000000000\n'
            b'ShdPnd:\t0000000000000000\n'
            b'SigBlk:\t0000000000000000\n'
            b'SigIgn:\t0000000040001000\n'
            b'SigCgt:\t0000000198016a07\n'
            b'CapInh:\t0000000000000000\n'
            b'CapPrm:\tffffffffffffffff\n'
            b'CapEff:\tffffffffffffffff\n'
            b'CapBnd:\tffffffffffffffff\n'
            b'Cpus_allowed:\t1\n'
            b'Cpus_allowed_list:\t0\n'
            b'Mems_allowed:\t1\n'
            b'Mems_allowed_list:\t0\n'
            b'voluntary_ctxt_switches:\t767\n'
            b'nonvoluntary_ctxt_switches:\t3\n'
        )
        expected = {
            'name': 'nginx',
            'umask': None,
            'state': 'S',
            'tgid': 2913,
            'ngid': None,
            'pid': 2913,
            'ppid': 1,
            'tracerpid': 0,
            'uid': (0, 0, 0, 0),
            'gid': (0, 0, 0, 0),
            'fdsize': 32,
            'groups': (),
            'nstgid': None,
            'nspid': None,
            'nspgid': None,
            'nssid': None,
            'vmpeak': 10448,
            'vmsize': 10448,
            'vmlck': 0,
            'vmpin': 0,
            'vmhwm': 1212,
            'vmrss': 680,
            'rssanon': None,
            'rssfile': None,
            'rssshmem': None,
            'vmdata': 748,
            'vmstk': 136,
            'vmexe': 740,
            'vmlib': 8164,
            'vmpte': 32,
            'vmpmd': None,
            'vmswap': 488,
            'hugetlbpages': None,
            'coredumping': None,
            'threads': 1,
            'sigq': (0, 3939),
            'sigpnd': 0,
            'shdpnd': 0,
            'sigblk': 0,
            'sigign': 1073745920,
            'sigcgt': 6845196807,
            'capinh': 0,
            'capprm': 18446744073709551615,
            'capeff': 18446744073709551615,
            'capbnd': 18446744073709551615,
            'capamb': None,
            'nonewprivs': None,
            'seccomp': None,
            'speculation_store_bypass': None,
            'cpus_allowed': 1,
            'cpus_allowed_list': '0',
            'mems_allowed': (1,),
            'mems_allowed_list': '0',
            'voluntary_ctxt_switches': 767,
            'nonvoluntary_ctxt_switches': 3
        }
        actual = procfile.read_status(content)
        self.assertEqual(expected, actual)

        content += b'Foo: Bar\n'
        actual = procfile.read_status(content)
        self.assertEqual(expected, actual)

    def test_read_status_kthread(self):
        content = (
            b'Name:\tkthreadd\n'
            b'Umask:\t0000\n'
            b'State:\tS (sleeping)\n'
            b'Tgid:\t2\n'
            b'Ngid:\t0\n'
            b'Pid:\t2\n'
            b'PPid:\t0\n'
            b'TracerPid:\t0\n'
            b'Uid:\t0    0    0    0\n'
            b'Gid:\t0    0    0    0\n'
            b'FDSize:\t64\n'
            b'Groups:\t\n'
            b'NStgid:\t2\n'
            b'NSpid:\t2\n'
            b'NSpgid:\t0\n'
            b'NSsid:\t0\n'
            b'Threads:\t1\n'
            b'SigQ:\t0/31038\n'
            b'SigPnd:\t0000000000000000\n'
            b'ShdPnd:\t0000000000000000\n'
            b'SigBlk:\t0000000000000000\n'
            b'SigIgn:\tffffffffffffffff\n'
            b'SigCgt:\t0000000000000000\n'
            b'CapInh:\t0000000000000000\n'
            b'CapPrm:\t0000003fffffffff\n'
            b'CapEff:\t0000003fffffffff\n'
            b'CapBnd:\t0000003fffffffff\n'
            b'CapAmb:\t0000000000000000\n'
            b'NoNewPrivs:\t0\n'
            b'Seccomp:\t0\n'
            b'Speculation_Store_Bypass:\tthread vulnerable\n'
            b'Cpus_allowed:\tff\n'
            b'Cpus_allowed_list:\t0-7\n'
            b'Mems_allowed:\t00000000,00000000,00000000,00000000,00000000,'
            b'00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,'
            b'00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,'
            b'00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,'
            b'00000000,00000000,00000001\n'
            b'Mems_allowed_list:\t0\n'
            b'voluntary_ctxt_switches:\t3649\n'
            b'nonvoluntary_ctxt_switches:\t203\n'
        )
        expected = {
            'name': 'kthreadd',
            'umask': 0,
            'state': 'S',
            'tgid': 2,
            'ngid': 0,
            'pid': 2,
            'ppid': 0,
            'tracerpid': 0,
            'uid': (0, 0, 0, 0),
            'gid': (0, 0, 0, 0),
            'fdsize': 64,
            'groups': (),
            'nstgid': (2,),
            'nspid': (2,),
            'nspgid': (0,),
            'nssid': (0,),
            'vmpeak': None,
            'vmsize': None,
            'vmlck': None,
            'vmpin': None,
            'vmhwm': None,
            'vmrss': None,
            'rssanon': None,
            'rssfile': None,
            'rssshmem': None,
            'vmdata': None,
            'vmstk': None,
            'vmexe': None,
            'vmlib': None,
            'vmpte': None,
            'vmpmd': None,
            'vmswap': None,
            'hugetlbpages': None,
            'coredumping': None,
            'threads': 1,
            'sigq': (0, 31038),
            'sigpnd': 0,
            'shdpnd': 0,
            'sigblk': 0,
            'sigign': 18446744073709551615,
            'sigcgt': 0,
            'capinh': 0,
            'capprm': 274877906943,
            'capeff': 274877906943,
            'capbnd': 274877906943,
            'capamb': 0,
            'nonewprivs': 0,
            'seccomp': 0,
            'speculation_store_bypass': 'thread vulnerable',
            'cpus_allowed': 255,
            'cpus_allowed_list': '0-7',
            'mems_allowed': (
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
            ),
            'mems_allowed_list': '0',
            'voluntary_ctxt_switches': 3649,
            'nonvoluntary_ctxt_switches': 203
        }
        actual = procfile.read_status(content)
        self.assertEqual(expected, actual)

    def test_read_status_multiple_ns(self):
        content = (
            b'Name:\tpython\n'
            b'Umask:\t0022\n'
            b'State:\tS (sleeping)\n'
            b'Tgid:\t15648\n'
            b'Ngid:\t0\n'
            b'Pid:\t15648\n'
            b'PPid:\t15625\n'
            b'TracerPid:\t0\n'
            b'Uid:\t0\t0\t0\t0\n'
            b'Gid:\t0\t0\t0\t0\n'
            b'FDSize:\t64\n'
            b'Groups:\t0 1 2 3 4 6 10 11 20 26 27\n'
            b'NStgid:\t15648\t1\n'
            b'NSpid:\t15648\t1\n'
            b'NSpgid:\t15648\t1\n'
            b'NSsid:\t15648\t1\n'
            b'VmPeak:\t   24240 kB\n'
            b'VmSize:\t   24240 kB\n'
            b'VmLck:\t       0 kB\n'
            b'VmPin:\t       0 kB\n'
            b'VmHWM:\t   21876 kB\n'
            b'VmRSS:\t   21876 kB\n'
            b'RssAnon:\t   16676 kB\n'
            b'RssFile:\t    5200 kB\n'
            b'RssShmem:\t       0 kB\n'
            b'VmData:\t   16824 kB\n'
            b'VmStk:\t     132 kB\n'
            b'VmExe:\t       8 kB\n'
            b'VmLib:\t    3504 kB\n'
            b'VmPTE:\t      60 kB\n'
            b'VmPMD:\t      12 kB\n'
            b'VmSwap:\t       0 kB\n'
            b'HugetlbPages:\t       0 kB\n'
            b'Threads:\t1\n'
            b'SigQ:\t0/31038\n'
            b'SigPnd:\t0000000000000000\n'
            b'ShdPnd:\t0000000000000000\n'
            b'SigBlk:\t0000000000000000\n'
            b'SigIgn:\t0000000001001000\n'
            b'SigCgt:\t0000000000004002\n'
            b'CapInh:\t00000000a80425fb\n'
            b'CapPrm:\t00000000a80425fb\n'
            b'CapEff:\t00000000a80425fb\n'
            b'CapBnd:\t00000000a80425fb\n'
            b'CapAmb:\t0000000000000000\n'
            b'NoNewPrivs:\t0\n'
            b'Seccomp:\t2\n'
            b'Speculation_Store_Bypass:\tthread force mitigated\n'
            b'Cpus_allowed:\t0f\n'
            b'Cpus_allowed_list:\t0-3\n'
            b'Mems_allowed:\t00000000,00000000,00000000,00000000,00000000,00000000,00000000,'
            b'00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,'
            b'00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,'
            b'00000000,00000000,00000000,00000000,00000000,00000000,00000001\n'
            b'Mems_allowed_list:\t0\n'
            b'voluntary_ctxt_switches:\t1194\n'
            b'nonvoluntary_ctxt_switches:\t440\n'
        )
        expected = {
            'name': 'python',
            'umask': 18,
            'state': 'S',
            'tgid': 15648,
            'ngid': 0,
            'pid': 15648,
            'ppid': 15625,
            'tracerpid': 0,
            'uid': (0, 0, 0, 0),
            'gid': (0, 0, 0, 0),
            'fdsize': 64,
            'groups': (0, 1, 2, 3, 4, 6, 10, 11, 20, 26, 27),
            'nstgid': (15648, 1),
            'nspid': (15648, 1),
            'nspgid': (15648, 1),
            'nssid': (15648, 1),
            'vmpeak': 24240,
            'vmsize': 24240,
            'vmlck': 0,
            'vmpin': 0,
            'vmhwm': 21876,
            'vmrss': 21876,
            'rssanon': 16676,
            'rssfile': 5200,
            'rssshmem': 0,
            'vmdata': 16824,
            'vmstk': 132,
            'vmexe': 8,
            'vmlib': 3504,
            'vmpte': 60,
            'vmpmd': 12,
            'vmswap': 0,
            'hugetlbpages': 0,
            'coredumping': None,
            'threads': 1,
            'sigq': (0, 31038),
            'sigpnd': 0,
            'shdpnd': 0,
            'sigblk': 0,
            'sigign': 16781312,
            'sigcgt': 16386,
            'capinh': 2818844155,
            'capprm': 2818844155,
            'capeff': 2818844155,
            'capbnd': 2818844155,
            'capamb': 0,
            'nonewprivs': 0,
            'seccomp': 2,
            'speculation_store_bypass': 'thread force mitigated',
            'cpus_allowed': 15,
            'cpus_allowed_list': '0-3',
            'mems_allowed': (
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
            ),
            'mems_allowed_list': '0',
            'voluntary_ctxt_switches': 1194,
            'nonvoluntary_ctxt_switches': 440
        }
        actual = procfile.read_status(content)
        self.assertEqual(expected, actual)

    def test_read_fd(self):
        with tempfile.NamedTemporaryFile() as f:
            p = subprocess.Popen(
                ['timeout', '0.25', 'tail', '---disable-inotify', '-f', f'{f.name}', f.name],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.addCleanup(p.terminate)
            time.sleep(0.1)

            query = '$..children[?(@.stat.pid == {})]..pid'.format(p.pid)
            forest = proctree.Forest({'stat': procfile.registry['stat']}, skip_self=False)
            pids = proctree.query(forest.get_roots(), query)
            tail_pid = pids[1]

            expected = {
                'anon': 0,
                'dir': 0,
                'chr': 3,  # standard streams
                'blk': 0,
                'reg': 2,  # f twice
                'fifo': 0,
                'lnk': 0,
                'sock': 0,
            }
            actual = procfile.read_fd(f'/proc/{tail_pid}/fd')
            self.assertEqual(expected, actual)

        p.wait(1)

    def test_read_fd_unknown_descriptor_type(self):
        expected = {
            'anon': 0, 'dir': 0, 'chr': 0, 'blk': 0, 'reg': 0, 'fifo': 0, 'lnk': 0, 'sock': 0
        }
        with mock.patch.object(procfile.Fd, '_lookup', {}):
            actual = procfile.read_fd('/proc/{0}/fd'.format(os.getpid()))
        self.assertEqual(expected, actual)

    def test_read_smaps_rollup(self):
        content = b'\n'.join([
            b'00400000-ffffffffff601000 ---p 00000000 00:00 0                          [rollup]',
            b'Rss:                5584 kB',
            b'Pss:                1226 kB',
            b'Shared_Clean:       4444 kB',
            b'Shared_Dirty:          0 kB',
            b'Private_Clean:       136 kB',
            b'Private_Dirty:      1004 kB',
            b'Referenced:         5564 kB',
            b'Anonymous:          1140 kB',
            b'LazyFree:              0 kB',
            b'AnonHugePages:         0 kB',
            b'ShmemPmdMapped:        0 kB',
            b'Shared_Hugetlb:        0 kB',
            b'Private_Hugetlb:       0 kB',
            b'Swap:                 44 kB',
            b'SwapPss:            2616 kB',
            b'Locked:                0 kB',
        ])
        expected = {
            'anonhugepages': 0,
            'anonymous': 1140,
            'lazyfree': 0,
            'locked': 0,
            'private_clean': 136,
            'private_dirty': 1004,
            'private_hugetlb': 0,
            'pss': 1226,
            'referenced': 5564,
            'rss': 5584,
            'shared_clean': 4444,
            'shared_dirty': 0,
            'shared_hugetlb': 0,
            'shmempmdmapped': 0,
            'swap': 44,
            'swappss': 2616,
        }
        actual = procfile.read_smaps_rollup(content)
        self.assertEqual(expected, actual)

    def test_read_smaps_rollup_kthread(self):
        expected = {
            'anonhugepages': None,
            'anonymous': None,
            'lazyfree': None,
            'locked': None,
            'private_clean': None,
            'private_dirty': None,
            'private_hugetlb': None,
            'pss': None,
            'referenced': None,
            'rss': None,
            'shared_clean': None,
            'shared_dirty': None,
            'shared_hugetlb': None,
            'shmempmdmapped': None,
            'swap': None,
            'swappss': None,
        }
        actual = procfile.read_smaps_rollup(b'')
        self.assertEqual(expected, actual)

    def test_read_smaps_rollup_unknown(self):
        content = b'\n'.join([
            b'00400000-ffffffffff601000 ---p 00000000 00:00 0                          [rollup]',
            b'Rss:                5584 kB',
            b'Foo:                   0 kB',
        ])
        expected = {
            'rss': 5584,
            'anonhugepages': None,
            'anonymous': None,
            'lazyfree': None,
            'locked': None,
            'private_clean': None,
            'private_dirty': None,
            'private_hugetlb': None,
            'pss': None,
            'referenced': None,
            'shared_clean': None,
            'shared_dirty': None,
            'shared_hugetlb': None,
            'shmempmdmapped': None,
            'swap': None,
            'swappss': None,
        }
        actual = procfile.read_smaps_rollup(content)
        self.assertEqual(expected, actual)


class TestSectionProxyChain(unittest.TestCase):

    parser = None

    def setUp(self):
        cfg = '''
            [a]
            x: 1
            y: foo

            [a:b]
            extends: a
            y: bar
            z: True

            [a:b:c]
            extends: a:b
            z: False

            [b]
            x: 2

            [b:c]
            extends: b
            x: 3
            y: 5
        '''
        self.parser = configparser.RawConfigParser(
            default_section=None,
            comment_prefixes=('#',),
            delimiters=(':',),
            converters={'lines': playbook.split_multiline},
        )
        self.parser.read_string(cfg)

    def test_converter(self):
        testee = playbook.SectionProxyChain.fromsection(self.parser['a'])
        self.assertEqual([None, 1], testee.getint('x'))
        self.assertEqual([None, None], testee.getint('z'))
        self.assertEqual([None, True], testee.getboolean('x'))
        self.assertEqual([None, None], testee.getboolean('z'))

        testee = playbook.SectionProxyChain.fromsection(
            self.parser['a'], overrides={'x': '0', 'z': '1'}
        )
        self.assertEqual([0, 1], testee.getint('x'))
        self.assertEqual([1, None], testee.getint('z'))
        self.assertEqual([False, True], testee.getboolean('x'))
        self.assertEqual([True, None], testee.getboolean('z'))

        testee = playbook.SectionProxyChain.fromsection(self.parser['a:b'])
        self.assertEqual([None, None, 1], testee.getint('x'))
        self.assertEqual([None, None, None], testee.getint('zz'))
        self.assertEqual([None, None, True], testee.getboolean('x'))
        self.assertEqual([None, True, None], testee.getboolean('z'))

        testee = playbook.SectionProxyChain.fromsection(self.parser['a:b:c'])
        self.assertEqual([None, None, None, 1], testee.getint('x'))
        self.assertEqual([None, None, None, None], testee.getint('zz'))
        self.assertEqual([None, None, None, True], testee.getboolean('x'))
        self.assertEqual([None, False, True, None], testee.getboolean('z'))

        testee = playbook.SectionProxyChain.fromsection(self.parser['b:c'])
        self.assertEqual([None, 3, 2], testee.getint('x'))
        self.assertEqual([None, 5, None], testee.getint('y'))
        self.assertEqual([None, None, None], testee.getint('z'))

    def test_get(self):
        testee = playbook.SectionProxyChain.fromsection(self.parser['a'])
        self.assertEqual(None, testee.get('z'))
        self.assertEqual('bar', testee.get('z', 'bar'))
        self.assertEqual('1', testee.get('x'))
        self.assertEqual('foo', testee.get('y'))

        testee = playbook.SectionProxyChain.fromsection(self.parser['a:b'])
        self.assertEqual('True', testee.get('z'))
        self.assertEqual('1', testee.get('x'))
        self.assertEqual('bar', testee.get('y'))

        testee = playbook.SectionProxyChain.fromsection(self.parser['a:b:c'])
        self.assertEqual('False', testee.get('z'))
        self.assertEqual('1', testee.get('x'))
        self.assertEqual('bar', testee.get('y'))

        testee = playbook.SectionProxyChain.fromsection(
            self.parser['a:b:c'], overrides={'x': '15'}
        )
        self.assertEqual('False', testee.get('z'))
        self.assertEqual('15', testee.get('x'))
        self.assertEqual('bar', testee.get('y'))

        testee = playbook.SectionProxyChain.fromsection(self.parser['b:c'])
        self.assertEqual(None, testee.get('z'))
        self.assertEqual('3', testee.get('x'))
        self.assertEqual('5', testee.get('y'))

    def test_items(self):
        testee = playbook.SectionProxyChain.fromsection(self.parser['a'])
        self.assertEqual([('x', '1'), ('y', 'foo')], list(testee.items()))

        testee = playbook.SectionProxyChain.fromsection(self.parser['a:b'])
        self.assertEqual([('y', 'bar'), ('z', 'True'), ('x', '1')], list(testee.items()))

        testee = playbook.SectionProxyChain.fromsection(self.parser['a:b:c'])
        self.assertEqual([('z', 'False'), ('y', 'bar'), ('x', '1')], list(testee.items()))

        testee = playbook.SectionProxyChain.fromsection(
            self.parser['a:b:c'], overrides={'x': '15'}
        )
        self.assertEqual([('x', '15'), ('z', 'False'), ('y', 'bar')], list(testee.items()))

        testee = playbook.SectionProxyChain.fromsection(self.parser['b:c'])
        self.assertEqual([('x', '3'), ('y', '5')], list(testee.items()))

    def test_mro(self):
        # See "ex_9" in https://www.python.org/download/releases/2.3/mro/
        cfg = '''
            [a]
            v: a
            [b]
            v: b
            [c]
            v: c
            [d]
            v: d
            [e]
            v: e
            [k1]
            extends:
              a
              b
              c
            v: k1
            [k2]
            extends:
              d
              b
              e
            v: k2
            [k3]
            extends:
              d
              a
            v: k3
            [z]
            extends:
              k1
              k2
              k3
            v: z
        '''

        [self.parser.remove_section(s) for s in list(self.parser)]
        self.parser.read_string(cfg)

        testee = playbook.SectionProxyChain.fromsection(self.parser['z'])
        self.assertEqual(
            [None, ['z'], ['k1'], ['k2'], ['k3'], ['d'], ['a'], ['b'], ['c'], ['e']],
            testee.getlines('v'),
        )


class TestSqlitevizQuery(unittest.TestCase):

    @unittest.skipUnless(sqlite3.sqlite_version_info >= (3, 32), 'sqlite3 is too old')
    def test_process_tree_sankey_indices(self):
        bundle = sqliteviz.get_visualisation_bundle()
        inquiry = [inq for inq in bundle['inquiries'] if inq['name'] == 'Process Tree'][0]

        database_file = tempfile.NamedTemporaryFile()
        database_file.__enter__()
        self.addCleanup(database_file.close)

        procfile_list = ['stat', 'cmdline']
        storage = procrec.SqliteStorage(
            database_file.name, procfile_list, utility.get_meta(procfile_list, '/proc', 'process')
        )
        data = proctree.flatten(get_chromium_node_list(), storage._procfile_list)
        with storage:
            # Parent PID as is
            storage.record(1567504800, data)
            # Parent PID changed to 1, e.g. because the parent process was killed
            data = [dict(d, stat_ppid=1) if d['stat_pid'] == 18517 else d for d in data]
            storage.record(1567504800 + 15, data)

            actual = storage._conn.execute(inquiry['query']).fetchall()

        # A PID is numbered and has exactly one parent (or is a root)
        self.assertEqual(list(range(len(actual))), [r[0] for r in actual])

        root_cmd = '/usr/lib/chromium-browser/chromium-browser ...'
        broker_cmd = '/usr/lib/chromium-browser/chromium-browser --type=broker'
        gpu_cmd = '/usr/lib/chromium-browser/chromium-browser --type=gpu-process ...'
        renderer_cmd = '/usr/lib/chromium-browser/chromium-browser --type=renderer ...'
        utility_cmd = '/usr/lib/chromium-browser/chromium-browser --type=utility ...'
        zygote_cmd = '/usr/lib/chromium-browser/chromium-browser --type=zygote'
        expected = [
            (0, None, '18467 chromium-browse', root_cmd, 1),
            (1, 0, '18482 chromium-browse', zygote_cmd, 1),
            (2, 1, '18484 chromium-browse', zygote_cmd, 1),
            (3, 0, '18503 chromium-browse', gpu_cmd, 1),
            (4, 0, '18508 chromium-browse', utility_cmd, 1),
            (5, 3, '18517 chromium-browse', broker_cmd, 1),  # first parent is shown
            (6, 2, '18529 chromium-browse', renderer_cmd, 1),
            (7, 2, '18531 chromium-browse', renderer_cmd, 1),
            (8, 2, '18555 chromium-browse', renderer_cmd, 1),
            (9, 2, '18569 chromium-browse', renderer_cmd, 1),
            (10, 2, '18571 chromium-browse', utility_cmd, 1),
            (11, 2, '18593 chromium-browse', renderer_cmd, 1),
            (12, 2, '18757 chromium-browse', renderer_cmd, 1),
            (13, 2, '18769 chromium-browse', renderer_cmd, 1),
            (14, 2, '18770 chromium-browse', renderer_cmd, 1),
            (15, 2, '18942 chromium-browse', renderer_cmd, 1),
        ]
        self.assertEqual(expected, actual)

    @unittest.skipUnless(sqlite3.sqlite_version_info >= (3, 32), 'sqlite3 is too old')
    def test_process_timeline_pid(self):
        bundle = sqliteviz.get_visualisation_bundle()
        inquiry = [inq for inq in bundle['inquiries'] if inq['name'] == 'Process Timeline, PID'][0]

        database_file = tempfile.NamedTemporaryFile()
        database_file.__enter__()
        self.addCleanup(database_file.close)

        procfile_list = ['stat', 'cmdline']
        storage = procrec.SqliteStorage(
            database_file.name, procfile_list, utility.get_meta(procfile_list, '/proc', 'process')
        )
        data = proctree.flatten(get_chromium_node_list(), storage._procfile_list)
        with storage:
            storage.record(1567504800, data)
            storage.record(1567504800 + 15, data)

            actual = storage._conn.execute(inquiry['query']).fetchall()

        root_cmd = '/usr/lib/chromium-browser/chromium-browser ...'
        broker_cmd = '/usr/lib/chromium-browser/chromium-browser --type=broker'
        gpu_cmd = '/usr/lib/chromium-browser/chromium-browser --type=gpu-process ...'
        renderer_cmd = '/usr/lib/chromium-browser/chromium-browser --type=renderer ...'
        big_subtree_path = '18484 chromium-browse / 18482 chromium-browse / 18467 chromium-browse'
        utility_cmd = '/usr/lib/chromium-browser/chromium-browser --type=utility ...'
        zygote_cmd = '/usr/lib/chromium-browser/chromium-browser --type=zygote'
        expected = [
            (
                1567504800000.0,
                18467,
                '18467 chromium-browse',
                f'{root_cmd}<br>18467 chromium-browse',
            ),
            (
                1567504800000.0,
                18482,
                '18482 chromium-browse',
                f'{zygote_cmd}<br>18482 chromium-browse / 18467 chromium-browse',
            ),
            (
                1567504800000.0,
                18484,
                '18484 chromium-browse',
                (
                    f'{zygote_cmd}<br>'
                    '18484 chromium-browse / 18482 chromium-browse / 18467 chromium-browse'
                ),
            ),
            (
                1567504800000.0,
                18529,
                '18529 chromium-browse',
                f'{renderer_cmd}<br>18529 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504800000.0,
                18531,
                '18531 chromium-browse',
                f'{renderer_cmd}<br>18531 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504800000.0,
                18555,
                '18555 chromium-browse',
                f'{renderer_cmd}<br>18555 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504800000.0,
                18569,
                '18569 chromium-browse',
                f'{renderer_cmd}<br>18569 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504800000.0,
                18571,
                '18571 chromium-browse',
                f'{utility_cmd}<br>18571 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504800000.0,
                18593,
                '18593 chromium-browse',
                f'{renderer_cmd}<br>18593 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504800000.0,
                18757,
                '18757 chromium-browse',
                f'{renderer_cmd}<br>18757 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504800000.0,
                18769,
                '18769 chromium-browse',
                f'{renderer_cmd}<br>18769 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504800000.0,
                18770,
                '18770 chromium-browse',
                f'{renderer_cmd}<br>18770 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504800000.0,
                18942,
                '18942 chromium-browse',
                f'{renderer_cmd}<br>18942 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504800000.0,
                18503,
                '18503 chromium-browse',
                f'{gpu_cmd}<br>18503 chromium-browse / 18467 chromium-browse',
            ),
            (
                1567504800000.0,
                18517,
                '18517 chromium-browse',
                (
                    f'{broker_cmd}<br>'
                    '18517 chromium-browse / 18503 chromium-browse / 18467 chromium-browse'
                ),
            ),
            (
                1567504800000.0,
                18508,
                '18508 chromium-browse',
                f'{utility_cmd}<br>18508 chromium-browse / 18467 chromium-browse',
            ),
            (
                1567504815000.0,
                18467,
                '18467 chromium-browse',
                '/usr/lib/chromium-browser/chromium-browser ...<br>18467 chromium-browse',
            ),
            (
                1567504815000.0,
                18482,
                '18482 chromium-browse',
                f'{zygote_cmd}<br>18482 chromium-browse / 18467 chromium-browse',
            ),
            (
                1567504815000.0,
                18484,
                '18484 chromium-browse',
                f'{zygote_cmd}<br>{big_subtree_path}',
            ),
            (
                1567504815000.0,
                18529,
                '18529 chromium-browse',
                f'{renderer_cmd}<br>18529 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504815000.0,
                18531,
                '18531 chromium-browse',
                f'{renderer_cmd}<br>18531 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504815000.0,
                18555,
                '18555 chromium-browse',
                f'{renderer_cmd}<br>18555 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504815000.0,
                18569,
                '18569 chromium-browse',
                f'{renderer_cmd}<br>18569 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504815000.0,
                18571,
                '18571 chromium-browse',
                f'{utility_cmd}<br>18571 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504815000.0,
                18593,
                '18593 chromium-browse',
                f'{renderer_cmd}<br>18593 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504815000.0,
                18757,
                '18757 chromium-browse',
                f'{renderer_cmd}<br>18757 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504815000.0,
                18769,
                '18769 chromium-browse',
                f'{renderer_cmd}<br>18769 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504815000.0,
                18770,
                '18770 chromium-browse',
                f'{renderer_cmd}<br>18770 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504815000.0,
                18942,
                '18942 chromium-browse',
                f'{renderer_cmd}<br>18942 chromium-browse / {big_subtree_path}',
            ),
            (
                1567504815000.0,
                18503,
                '18503 chromium-browse',
                f'{gpu_cmd}<br>18503 chromium-browse / 18467 chromium-browse',
            ),
            (
                1567504815000.0,
                18517,
                '18517 chromium-browse',
                (
                    f'{broker_cmd}<br>'
                    '18517 chromium-browse / 18503 chromium-browse / 18467 chromium-browse'
                ),
            ),
            (
                1567504815000.0,
                18508,
                '18508 chromium-browse',
                f'{utility_cmd}<br>18508 chromium-browse / 18467 chromium-browse',
            ),
        ]
        self.assertEqual(expected, actual)

    @unittest.skipUnless(sqlite3.sqlite_version_info >= (3, 32), 'sqlite3 is too old')
    def test_process_timeline_cpu(self):
        bundle = sqliteviz.get_visualisation_bundle()
        inquiry = [inq for inq in bundle['inquiries'] if inq['name'] == 'Process Timeline, CPU'][0]

        database_file = tempfile.NamedTemporaryFile()
        database_file.__enter__()
        self.addCleanup(database_file.close)

        procfile_list = ['stat', 'cmdline']
        storage = procrec.SqliteStorage(
            database_file.name, procfile_list, utility.get_meta(procfile_list, '/proc', 'process')
        )
        data = proctree.flatten(get_chromium_node_list(), storage._procfile_list)
        with storage:
            storage.record(1567504800, data)
            data[1]['stat_utime'] += 10
            data[2]['stat_utime'] += 20
            data[4]['stat_utime'] += 40
            storage.record(1567504800 + 15, data)

            actual = storage._conn.execute(inquiry['query']).fetchall()

        renderer_cmd = '/usr/lib/chromium-browser/chromium-browser --type=renderer ...'
        zygote_cmd = '/usr/lib/chromium-browser/chromium-browser --type=zygote'
        expected = [
            (
                1567504815000.0,
                18482,
                '18482 chromium-browse',
                0.6729713331080575,
                0.6666666666666666,
                f'{zygote_cmd}<br>18482 '
                'chromium-browse / 18467 chromium-browse<br>CPU, %: 0.67<br>priority: 20',
            ),
            (
                1567504815000.0,
                18484,
                '18484 chromium-browse',
                0.6729713331080575,
                1.3333333333333333,
                f'{zygote_cmd}<br>18484 '
                'chromium-browse / 18482 chromium-browse / 18467 chromium-browse<br>CPU, %: '
                '1.33<br>priority: 20',
            ),
            (
                1567504815000.0,
                18531,
                '18531 chromium-browse',
                0.6729713331080575,
                2.6666666666666665,
                f'{renderer_cmd}<br>18531 '
                'chromium-browse / 18484 chromium-browse / 18482 chromium-browse / 18467 '
                'chromium-browse<br>CPU, %: 2.67<br>priority: 20',
            ),
        ]
        self.assertEqual(expected, actual)

    def test_total_memory_consumption(self):
        bundle = sqliteviz.get_visualisation_bundle()
        inquiry = [
            inq for inq in bundle['inquiries'] if inq['name'] == 'Total Resident Set Size, MiB'
        ][0]

        database_file = tempfile.NamedTemporaryFile()
        database_file.__enter__()
        self.addCleanup(database_file.close)

        procfile_list = ['stat', 'cmdline']
        storage = procrec.SqliteStorage(
            database_file.name, procfile_list, utility.get_meta(procfile_list, '/proc', 'process')
        )
        data = proctree.flatten(get_chromium_node_list(), storage._procfile_list)
        with storage:
            storage.record(1567504800, data)
            # Add 1 MiB RSS to PID 18517
            data = [
                dict(d, stat_rss=d['stat_rss'] + 256) if d['stat_pid'] == 18517 else d
                for d in data
            ]
            storage.record(1567504800 + 30, data)

            actual = storage._conn.execute(inquiry['query']).fetchall()

        expected = [
            (1567504800000.0, 'chromium-browse', 1590.32421875, 'total: 1590.3 MiB'),
            (1567504830000.0, 'chromium-browse', 1591.32421875, 'total: 1591.3 MiB'),
        ]
        self.assertEqual(expected, actual)

    def test_total_cpu_usage(self):
        bundle = sqliteviz.get_visualisation_bundle()
        inquiry = [inq for inq in bundle['inquiries'] if inq['name'] == 'Total CPU Usage, %'][0]

        database_file = tempfile.NamedTemporaryFile()
        database_file.__enter__()
        self.addCleanup(database_file.close)

        procfile_list = ['stat', 'cmdline']
        storage = procrec.SqliteStorage(
            database_file.name, procfile_list, utility.get_meta(procfile_list, '/proc', 'process')
        )
        data = proctree.flatten(get_chromium_node_list(), storage._procfile_list)
        with storage:
            storage.record(1567504800, data)
            storage.record(1567504800 + 15, data)
            # Add 1000 ticks to PID 18517
            data = [
                dict(d, stat_utime=d['stat_utime'] + 1000) if d['stat_pid'] == 18517 else d
                for d in data
            ]
            storage.record(1567504800 + 30, data)

            actual = storage._conn.execute(inquiry['query']).fetchall()

        expected = [
            (1567504810000.0, 'chromium-browse', 0.0, 'total: 0.0 %'),
            (1567504830000.0, 'chromium-browse', 50.0, 'total: 50.0 %'),
        ]
        self.assertEqual(expected, actual)

    def test_total_disk_io(self):
        bundle = sqliteviz.get_visualisation_bundle()
        inquiry = [
            inq
            for inq in bundle['inquiries']
            if inq['name'] == 'Total Disk IO, B/s and % IO wait'
        ][0]

        database_file = tempfile.NamedTemporaryFile()
        database_file.__enter__()
        self.addCleanup(database_file.close)

        procfile_list = ['stat', 'cmdline', 'io']
        storage = procrec.SqliteStorage(
            database_file.name, procfile_list, utility.get_meta(procfile_list, '/proc', 'process')
        )

        data = proctree.flatten(get_chromium_node_list(), storage._procfile_list)
        start_state = {
            'io_rchar': 103268752,
            'io_wchar': 1712121,
            'io_syscr': 27515,
            'io_syscw': 1218,
            'io_read_bytes': 39814656,
            'io_write_bytes': 1863680,
            'io_cancelled_write_bytes': 24576,
            'stat_delayacct_blkio_ticks': 0,
        }
        for row in data:
            row.update(start_state)

        with storage:
            storage.record(1567504800, data)
            storage.record(1567504800 + 15, data)
            # Add 1MB read, 2MB write and 1000 wait ticks to PID 18517
            data = [
                dict(
                    d,
                    io_read_bytes=d['io_read_bytes'] + 10 ** 6,
                    io_write_bytes=d['io_write_bytes'] + 2 * 10 ** 6,
                    stat_delayacct_blkio_ticks=d['stat_delayacct_blkio_ticks'] + 1000,
                )
                if d['stat_pid'] == 18517 else d
                for d in data
            ]
            storage.record(1567504800 + 30, data)

            actual = storage._conn.execute(inquiry['query']).fetchall()

        expected = [
            (1567504810000, 'chromium-browse', 0.0, 0.0, 0.0),
            (1567504830000, 'chromium-browse', 50000.0, -100000.0, 50.0),
        ]
        self.assertEqual(expected, actual)

class TestSqlitevizServer(unittest.TestCase):

    @classmethod
    def serve_dir(self, path):
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                sqliteviz.serve_dir('', 18000, path, server_cls=http.server.HTTPServer)
        except KeyboardInterrupt:
            pass

    def test_serve_dir(self):
        with tempfile.TemporaryDirectory() as tmpd:
            tmpd_path = Path(tmpd)
            (tmpd_path / 'index.html').write_text('<html/>')
            (tmpd_path / 'db.sqlite').write_text('...')

            p = multiprocessing.Process(target=self.serve_dir, args=(tmpd,))
            self.addCleanup(p.terminate)
            p.start()
            assert_wait_predicate(lambda: is_port_open('localhost', 18000))

            response = urllib.request.urlopen('http://localhost:18000/')
            self.assertEqual(b'<html/>', response.read())
            self.assertEqual('no-cache', response.headers['Cache-Control'])

            response = urllib.request.urlopen('http://localhost:18000/db.sqlite')
            self.assertEqual(b'...', response.read())
            self.assertEqual('no-store', response.headers['Cache-Control'])

            os.kill(p.pid, signal.SIGINT)
            p.join(1)
            self.assertFalse(p.is_alive())
