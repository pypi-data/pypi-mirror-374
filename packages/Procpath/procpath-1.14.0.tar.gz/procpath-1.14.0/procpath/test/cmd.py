import asyncio
import contextlib
import functools
import io
import json
import logging
import multiprocessing
import os
import pty
import signal
import sqlite3
import sys
import tempfile
import textwrap
import threading
import time
import unittest
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path
from unittest import mock

import jsonpyth

from .. import cli, playbook, procfile, procrec, procret, proctree, sqliteviz, treefarm, utility
from ..cmd import CommandError, explore, play, plot, query, record, watch
from . import (
    ChromiumTree,
    assert_lines_match,
    assert_wait_predicate,
    assert_wait_predicate_async,
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


class TestQueryCommand(unittest.TestCase):

    def test_query_query_node_list_json_output(self):
        output_file = io.StringIO()
        query.run(
            procfile_list=['stat'],
            output_file=output_file,
            indent=2,
            procfs='/proc',
            procfs_target='process',
            query='$..children[?(@.stat.pid == {})]'.format(os.getppid()),
        )
        data = json.loads(output_file.getvalue())
        self.assertEqual(1, len(data))

    def test_query_no_query_root_output(self):
        output_file = io.StringIO()
        query.run(
            procfile_list=['stat'],
            procfs='/proc',
            procfs_target='process',
            output_file=output_file,
        )
        roots = json.loads(output_file.getvalue())
        self.assertEqual(1, roots[0]['stat']['pid'])

    def test_query_delimited(self):
        output_file = io.StringIO()
        query.run(
            procfile_list=['stat'],
            output_file=output_file,
            delimiter=',',
            procfs='/proc',
            procfs_target='process',
            query='$..children[?(@.stat.pid == {})]..pid'.format(os.getppid()),
        )
        pids = output_file.getvalue().split(',')
        self.assertGreaterEqual(len(pids), 1)
        self.assertEqual(os.getppid(), int(pids[0]))

    def test_query_jsonpath_syntax_error(self):
        with self.assertRaises(CommandError):
            query.run(
                procfile_list=['stat'],
                output_file=io.StringIO(),
                procfs='/proc',
                procfs_target='process',
                query='$!#',
            )

    def test_query_with_sql(self):
        output_file = io.StringIO()
        query.run(
            procfile_list=['stat', 'cmdline'],
            output_file=output_file,
            indent=2,
            procfs='/proc',
            procfs_target='process',
            query='$..children[?(@.stat.pid == {})]'.format(os.getppid()),
            sql_query='SELECT SUM(stat_rss) / 1024.0 * 4 total FROM record',
        )
        data = json.loads(output_file.getvalue())
        self.assertEqual(1, len(data))
        self.assertEqual(1, len(data[0]))
        self.assertIn('total', data[0])

    def test_query_only_sql(self):
        output_file = io.StringIO()
        query.run(
            procfile_list=['stat', 'cmdline'],
            output_file=output_file,
            indent=2,
            procfs='/proc',
            procfs_target='process',
            query='',
            sql_query='SELECT SUM(stat_rss) / 1024.0 * 4 total FROM record',
        )
        data = json.loads(output_file.getvalue())
        self.assertEqual(1, len(data))
        self.assertEqual(1, len(data[0]))
        self.assertIn('total', data[0])

    def test_query_sql_syntax_error(self):
        with self.assertRaises(CommandError):
            query.run(
                procfile_list=['stat'],
                output_file=io.StringIO(),
                procfs='/proc',
                procfs_target='process',
                sql_query='$!#',
            )

    def test_query_with_envrionment(self):
        output_file = io.StringIO()
        query.run(
            procfile_list=['stat'],
            output_file=output_file,
            indent=2,
            procfs='/proc',
            procfs_target='process',
            environment=[['P', 'echo {}'.format(os.getppid())]],
            query='$..children[?(@.stat.pid == $P)]',
        )
        data = json.loads(output_file.getvalue())
        self.assertEqual(1, len(data))

        output_file = io.StringIO()
        query.run(
            procfile_list=['stat'],
            output_file=output_file,
            indent=2,
            procfs='/proc',
            procfs_target='process',
            environment=[['P', 'echo {}'.format(os.getppid())]],
            sql_query='SELECT * FROM record WHERE stat_pid = $P',
        )
        data = json.loads(output_file.getvalue())
        self.assertEqual(1, len(data))

    def test_query_no_new_line_on_empty_output(self):
        output_file = io.StringIO()
        query.run(
            procfile_list=['stat'],
            output_file=output_file,
            procfs='/proc',
            procfs_target='process',
            delimiter=',',
            query='$..children[?(@.stat.pid == -1)]',
        )
        self.assertEqual('', output_file.getvalue())

    def test_query_thread_target(self):
        evt = threading.Event()
        thread = threading.Thread(target=lambda evt: evt.wait(5), args=(evt,), daemon=True)
        thread.name = 'test_thread'
        thread.start()
        try:
            output_file = io.StringIO()
            query.run(
                procfile_list=['stat', 'status'],
                output_file=output_file,
                indent=2,
                procfs='/proc',
                procfs_target='thread',
                query='$..children[?(@.stat.pid == {})]'.format(os.getppid()),
            )
        finally:
            evt.set()
            thread.join()

        tree = json.loads(output_file.getvalue())
        table = proctree.flatten(tree, ['stat', 'status'])
        threads = [
            r
            for r in table
            if r['status_pid'] != r['status_tgid']
        ]
        self.assertTrue(threads)
        self.assertTrue(any(
            t['status_ppid'] == os.getppid() and t['status_tgid'] == os.getpid() for t in threads
        ))


class TestRecordCommand(unittest.TestCase):

    def test_record_query(self):
        with tempfile.NamedTemporaryFile() as f:
            start = time.time()
            record.run(
                procfile_list=['stat'],
                database_file=f.name,
                interval=1,
                recnum=1,
                query='$..children[?(@.stat.pid == {})]'.format(os.getppid()),
                procfs='/proc',
                procfs_target='process',
            )
            with contextlib.closing(sqlite3.connect(f.name)) as conn:
                conn.row_factory = sqlite3.Row

                cursor = conn.execute('SELECT * FROM record')
                rows = list(map(dict, cursor))
                self.assertGreaterEqual(len(rows), 1)

        actual = rows[0]
        self.assertEqual(1, actual.pop('record_id'))
        self.assertAlmostEqual(start, actual.pop('ts'), delta=0.2)

        self.assertEqual(os.getppid(), actual['stat_pid'])
        self.assertEqual(
            list(procfile.registry['stat'].empty.keys()),
            [k.replace('stat_', '') for k in actual.keys()],
        )

    def test_record_all(self):
        with tempfile.NamedTemporaryFile() as f:
            start = time.time()
            record.run(
                procfile_list=['stat', 'cmdline'],
                database_file=f.name,
                procfs='/proc',
                procfs_target='process',
                interval=1,
                recnum=1,
            )
            with contextlib.closing(sqlite3.connect(f.name)) as conn:
                conn.row_factory = sqlite3.Row

                cursor = conn.execute('SELECT * FROM record')
                rows = list(map(dict, cursor))
                self.assertGreaterEqual(len(rows), 1)

        root = rows[0]
        self.assertEqual(1, root.pop('record_id'))
        self.assertAlmostEqual(start, root.pop('ts'), delta=0.2)

        self.assertEqual(1, root['stat_pid'])
        self.assertEqual(
            ['cmdline'] + list(procfile.registry['stat'].empty.keys()),
            [k.replace('stat_', '') for k in root.keys()],
        )

    @classmethod
    def record_forever(cls, database_file, pid):
        """
        ``multiprocessing.Process`` targe function to run ``recrod``.

        .. note::

           The forked process' stdout and stderr are inherited here.
           ``sys.stdout`` and ``sys.stderr`` can also be instances of
           ``xmlrunner.result._DuplicateWriter`` in the coverage job.

        """

        # Ignore loop iteration warnings and other logging which can't
        # be controller from the test
        logging.getLogger().setLevel(logging.ERROR)
        try:
            record.run(
                procfile_list=['stat'],
                database_file=database_file,
                interval=0.1,
                query=f'$..children[?(@.stat.pid == {pid})]',
                procfs='/proc',
                procfs_target='process',
            )
        except KeyboardInterrupt:
            pass

    def test_record_forever(self):
        with tempfile.NamedTemporaryFile() as f:
            p = multiprocessing.Process(target=self.record_forever, args=(f.name, os.getppid()))
            self.addCleanup(p.terminate)
            start = time.time()
            p.start()

            time.sleep(2)
            os.kill(p.pid, signal.SIGINT)
            p.join(2)  # doesn't raise on timeout
            self.assertFalse(p.is_alive())

            with contextlib.closing(sqlite3.connect(f.name)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM record')
                rows = list(map(dict, cursor))

        self.assertGreaterEqual(sum(1 for r in rows if r['stat_pid'] == os.getppid()), 5)
        for i, row in enumerate(rows):
            self.assertEqual(i + 1, row.pop('record_id'))
            self.assertAlmostEqual(start, row.pop('ts'), delta=2)
            self.assertEqual(
                list(procfile.registry['stat'].empty.keys()),
                [k.replace('stat_', '') for k in row.keys()],
            )

    def test_record_n_times(self):
        with tempfile.NamedTemporaryFile() as f:
            start = time.time()
            try:
                with self.assertLogs('procpath', 'WARNING') as ctx:
                    record.run(
                        procfile_list=['stat'],
                        database_file=f.name,
                        interval=0.01,
                        recnum=4,
                        query='$..children[?(@.stat.pid == {})]'.format(os.getppid()),
                        procfs='/proc',
                        procfs_target='process',
                    )
            except AssertionError as ex:
                self.assertTrue(str(ex).startswith('no logs of level'))
            else:
                self.assertTrue(
                    all(r.message.startswith('Iteration took longer') for r in ctx.records)
                )

            with contextlib.closing(sqlite3.connect(f.name)) as conn:
                conn.row_factory = sqlite3.Row

                cursor = conn.execute('SELECT * FROM record')
                rows = list(map(dict, cursor))

        self.assertEqual(4, sum(1 for r in rows if r['stat_pid'] == os.getppid()))
        for i, row in enumerate(rows):
            self.assertEqual(i + 1, row.pop('record_id'))
            self.assertAlmostEqual(start, row.pop('ts'), delta=1.5)
            self.assertEqual(
                list(procfile.registry['stat'].empty.keys()),
                [k.replace('stat_', '') for k in row.keys()],
            )

    def test_record_environment(self):
        with tempfile.NamedTemporaryFile() as f:
            with tempfile.NamedTemporaryFile() as f_log:
                start = time.time()
                try:
                    with self.assertLogs('procpath', 'WARNING') as ctx:
                        record.run(
                            procfile_list=['stat'],
                            database_file=f.name,
                            interval=0.01,
                            recnum=4,
                            reevalnum=2,
                            environment=[
                                ['P', 'echo {} | tee -a {}'.format(os.getppid(), f_log.name)]
                            ],
                            query='$..children[?(@.stat.pid == $P)]',
                            procfs='/proc',
                            procfs_target='process',
                        )
                except AssertionError as ex:
                    self.assertTrue(str(ex).startswith('no logs of level'))
                else:
                    self.assertTrue(
                        all(r.message.startswith('Iteration took longer') for r in ctx.records)
                    )

                # 2 reevals + pre-loop database-file eval
                self.assertEqual(''.join(['{}\n'.format(os.getppid())] * 3).encode(), f_log.read())

                with contextlib.closing(sqlite3.connect(f.name)) as conn:
                    conn.row_factory = sqlite3.Row

                    cursor = conn.execute('SELECT * FROM record')
                    rows = list(map(dict, cursor))

        self.assertEqual(4, sum(1 for r in rows if r['stat_pid'] == os.getppid()))
        for i, row in enumerate(rows):
            self.assertEqual(i + 1, row.pop('record_id'))
            self.assertAlmostEqual(start, row.pop('ts'), delta=1.5)
            self.assertEqual(
                list(procfile.registry['stat'].empty.keys()),
                [k.replace('stat_', '') for k in row.keys()],
            )

    def test_record_environment_database_file(self):
        with mock.patch('procpath.cmd.record.procrec.SqliteStorage') as m:
            record.run(
                procfile_list=['stat'],
                database_file='/tmp/$V.sqlite',
                interval=0.01,
                recnum=1,
                environment=[['V', 'echo subst']],
                query='$..children[?(@.stat.pid == -1)]',
                procfs='/proc',
                procfs_target='process',
            )
        self.assertEqual('/tmp/subst.sqlite', m.call_args[0][0])

    def test_record_syntax_error(self):
        with self.assertRaises(CommandError):
            record.run(
                procfile_list=['stat'],
                database_file=':memory:',
                interval=1,
                procfs='/proc',
                procfs_target='process',
                query='$!#',
            )

    def test_record_pid_list(self):
        with mock.patch('procpath.cmd.record.proctree.Forest', ChromiumTree):
            with tempfile.NamedTemporaryFile() as f:
                start = time.time()
                record.run(
                    procfile_list=['stat'],
                    database_file=f.name,
                    interval=1,
                    recnum=1,
                    pid_list='18484, 18529, 18503, 18508,',
                    query='$..children[?(@.stat.pid in [18503, 18508])]',
                    procfs='/proc',
                    procfs_target='process',
                )
                with contextlib.closing(sqlite3.connect(f.name)) as conn:
                    conn.row_factory = sqlite3.Row

                    cursor = conn.execute('SELECT * FROM record')
                    rows = list(map(dict, cursor))

        self.assertEqual(3, len(rows))
        for i, row in enumerate(rows):
            self.assertEqual(i + 1, row.pop('record_id'))
            self.assertEqual([18503, 18517, 18508][i], row['stat_pid'])
            self.assertAlmostEqual(start, row.pop('ts'), delta=1.5)
            self.assertEqual(
                list(procfile.registry['stat'].empty.keys()),
                [k.replace('stat_', '') for k in row.keys()],
            )

    def test_record_pid_list_only(self):
        with tempfile.NamedTemporaryFile() as f:
            start = time.time()
            record.run(
                procfile_list=['stat'],
                database_file=f.name,
                environment=[['P', 'echo {}'.format(os.getppid())]],
                interval=1,
                recnum=1,
                pid_list='$P',
                procfs='/proc',
                procfs_target='process',
            )
            with contextlib.closing(sqlite3.connect(f.name)) as conn:
                conn.row_factory = sqlite3.Row

                cursor = conn.execute('SELECT * FROM record')
                rows = list(map(dict, cursor))
                self.assertGreaterEqual(len(rows), 1)

        root = rows[0]
        self.assertEqual(1, root.pop('record_id'))
        self.assertEqual(1, root['stat_pid'])
        self.assertAlmostEqual(start, root.pop('ts'), delta=0.2)
        self.assertEqual(
            list(procfile.registry['stat'].empty.keys()),
            [k.replace('stat_', '') for k in root.keys()],
        )

        for i, row in enumerate(rows):
            if row['stat_pid'] == os.getppid():
                break

            self.assertEqual(1, len([r for r in rows if r['stat_ppid'] == row['stat_pid']]))
        else:
            self.fail('No PPID found')

        self.assertLessEqual(i, len(rows) - 1)

        ppid = os.getppid()
        self.assertTrue(all(r['stat_ppid'] == ppid or r['stat_pid'] == ppid for r in rows[i:]))

    def test_record_stop_without_result(self):
        async def test():
            with tempfile.NamedTemporaryFile() as f:
                target_start = time.time()
                process = await asyncio.create_subprocess_exec('sleep', '0.5')
                await asyncio.sleep(0.25)

                record_start = time.time()
                record_fn = functools.partial(
                    record.run,
                    procfile_list=['stat'],
                    database_file=f.name,
                    interval=0.01,
                    recnum=100,
                    pid_list=str(process.pid),
                    stop_without_result=True,
                    procfs='/proc',
                    procfs_target='process',
                )
                try:
                    with self.assertLogs('procpath', 'WARNING') as ctx:
                        await asyncio.get_running_loop().run_in_executor(None, record_fn)
                except AssertionError as ex:
                    self.assertTrue(str(ex).startswith('no logs of level'))
                else:
                    self.assertTrue(
                        all(r.message.startswith('Iteration took longer') for r in ctx.records)
                    )

                self.assertTrue(target_start + 0.5 <= time.time() < target_start + 1)
                self.assertEqual(0, process.returncode)
                with contextlib.closing(sqlite3.connect(f.name)) as conn:
                    conn.row_factory = sqlite3.Row

                    cursor = conn.execute('SELECT * FROM record')
                    rows = list(map(dict, cursor))
                    self.assertGreaterEqual(len(rows), 1)
                    self.assertLessEqual(len(rows), 25)

                for i, row in enumerate(rows, start=1):
                    self.assertEqual(process.pid, row['stat_pid'])
                    self.assertEqual(i, row.pop('record_id'))
                    self.assertAlmostEqual(record_start, row.pop('ts'), delta=0.4)
                    self.assertEqual(
                        list(procfile.registry['stat'].empty.keys()),
                        [k.replace('stat_', '') for k in row.keys()],
                    )

        asyncio.run(test(), debug=True)

    def test_record_loop_longer_than_interval_warning(self):
        stats = record.RunStats()
        interval = 0.001
        with self.assertLogs('procpath', 'WARNING') as ctx:
            for _start, _count in record._record_loop(interval, stats, recnum=2):
                time.sleep(0.01)

        self.assertEqual(1, len(ctx.records))
        msg = 'Iteration took longer (0.01s) than record interval. Try longer interval.'
        self.assertEqual(msg, ctx.records[0].message)


class TestPlotCommand(unittest.TestCase):

    database_file = None

    @classmethod
    def setUpClass(cls):
        cls.database_file = tempfile.NamedTemporaryFile()
        cls.database_file.__enter__()

        pf_list = ['stat']
        storage = procrec.SqliteStorage(
            cls.database_file.name,
            pf_list,
            utility.get_meta(pf_list, '/proc', 'process'),
        )
        data = proctree.flatten(get_chromium_node_list(), storage._procfile_list)
        with storage:
            for ts in range(1567504800, 1567504800 + 4):
                storage.record(ts, data)
        storage.close()

    @classmethod
    def tearDownClass(cls):
        cls.database_file.close()

    def test_plot(self):
        with tempfile.NamedTemporaryFile() as f:
            plot.run(self.database_file.name, f.name, query_name_list=['rss'])

            svg_bytes = f.read()
            self.assertIn(b'<svg', svg_bytes)
            self.assertIn(b'Resident Set Size, MiB', svg_bytes)
            self.assertGreater(len(svg_bytes), 15_000)

    @unittest.skipUnless(apsw or sqlite3.sqlite_version_info >= (3, 25), 'sqlite3 is too old')
    def test_plot_logarithmic_two_axes(self):
        with tempfile.NamedTemporaryFile() as f:
            plot.run(
                self.database_file.name,
                f.name,
                logarithmic=True,
                query_name_list=['cpu', 'rss'],
                formatter='integer',
                style='LightGreenStyle',
            )

            svg_bytes = f.read()
            self.assertIn(b'<svg', svg_bytes)
            self.assertIn(b'CPU Usage, % vs Resident Set Size, MiB', svg_bytes)
            self.assertGreater(len(svg_bytes), 30_000)

    @unittest.skipUnless(apsw or sqlite3.sqlite_version_info >= (3, 25), 'sqlite3 is too old')
    def test_plot_share_y_axis(self):
        with tempfile.NamedTemporaryFile() as f:
            plot.run(
                self.database_file.name,
                f.name,
                logarithmic=True,
                share_y_axis=True,
                query_name_list=['cpu', 'rss'],
                formatter='integer',
                style='LightGreenStyle',
            )

            svg_bytes = f.read()
            self.assertIn(b'<svg', svg_bytes)
            self.assertIn(b'1. CPU Usage, %', svg_bytes)
            self.assertIn(b'2. Resident Set Size, MiB', svg_bytes)
            self.assertGreater(len(svg_bytes), 30_000)

    def test_plot_query_count_error(self):
        with self.assertRaises(CommandError) as ctx:
            plot.run(self.database_file.name, '/dev/null')
        self.assertEqual('No query to plot', str(ctx.exception))

        with self.assertRaises(CommandError) as ctx:
            plot.run(
                self.database_file.name, '/dev/null', query_name_list=['rss', 'rss', 'rss']
            )
        self.assertEqual('More than 2 queries to plot on 2 Y axes', str(ctx.exception))

    def test_plot_unknown_named_query(self):
        with self.assertRaises(CommandError) as ctx:
            plot.run(self.database_file.name, '/dev/null', query_name_list=['cpu', 'foo'])
        self.assertEqual('Unknown query foo', str(ctx.exception))

    def test_plot_sql_error(self):
        with self.assertRaises(CommandError) as ctx:
            plot.run(self.database_file.name, '/dev/null', custom_value_expr_list=["!@#$"])
        self.assertIn('SQL error:', str(ctx.exception))
        self.assertIn('unrecognized token: "!', str(ctx.exception))

    def test_plot_query_error_missing_requirement(self):
        with self.assertRaises(CommandError) as ctx:
            plot.run(self.database_file.name, '/dev/null', query_name_list=['pss'])
        self.assertEqual(
            "'Proportional Set Size, MiB' requires the following procfiles missing in "
            'the database: smaps_rollup',
            str(ctx.exception),
        )

    def test_plot_query_error_old_sqlite(self):
        query = procret.Query(
            'SELECT COUNT(*) cnt FROM record',
            'Dummy query',
            min_version=(666,),
        )
        with mock.patch.dict(procret.registry, {'foo': query}):
            with self.assertRaises(CommandError) as ctx:
                plot.run(self.database_file.name, '/dev/null', query_name_list=['foo'])
        self.assertIn(
            "'Dummy query' requires SQLite version >= (666,), installed", str(ctx.exception)
        )

    def test_plot_invalid_moving_average_window(self):
        with self.assertRaises(CommandError) as ctx:
            plot.run(
                self.database_file.name,
                '/dev/null',
                query_name_list=['cpu'],
                moving_average_window=0,
            )
        self.assertEqual('Moving average window must be a positive number', str(ctx.exception))

    @mock.patch('procpath.plotting.plot')
    def test_plot_title_override(self, plot_mock):
        plot.run(
            self.database_file.name,
            '/fake',
            query_name_list=['rss'],
            pid_list=[18467],
            title='The Strain',
        )
        plot_mock.assert_called_once_with(
            [{18467: [
                (1567504800.0, 208.2265625),
                (1567504801.0, 208.2265625),
                (1567504802.0, 208.2265625),
                (1567504803.0, 208.2265625),
            ]}],
            [procret.registry['rss']],
            '/fake',
            title='The Strain',
            style=None,
            formatter=None,
            logarithmic=False,
            share_y_axis=False,
            no_dots=False,
            relative_time=False,
        )

    @mock.patch('procpath.plotting.plot')
    def test_plot_custom_query_file(self, plot_mock):
        with tempfile.NamedTemporaryFile() as f:
            sql = '''
                SELECT 1 ts, 2 pid, 3 value
                UNION
                SELECT 2 ts, 2 pid, 4 value
            '''
            f.write(sql.encode())
            f.seek(0)
            custom_query = procret.Query(sql, 'Custom query')

            plot.run(
                self.database_file.name,
                '/fake',
                query_name_list=['rss'],
                pid_list=[2, 18482],
                custom_query_file_list=[f.name],
                title='RSS vs Custom query',
            )
            plot_mock.assert_called_once_with(
                [
                    {
                        18482: [
                            (1567504800.0, 53.76953125),
                            (1567504801.0, 53.76953125),
                            (1567504802.0, 53.76953125),
                            (1567504803.0, 53.76953125),
                        ]
                    },
                    {2: [(1, 3), (2, 4)]},
                ],
                [procret.registry['rss'], custom_query],
                '/fake',
                style=None,
                formatter=None,
                title='RSS vs Custom query',
                share_y_axis=False,
                logarithmic=False,
                no_dots=False,
                relative_time=False,
            )

    @mock.patch('procpath.plotting.plot')
    def test_plot_custom_value_expr(self, plot_mock):
        q1 = procret.create_query('10', 'Custom expression')
        q2 = procret.create_query('stat_minflt / 1000.0', 'Custom expression')

        plot.run(
            self.database_file.name,
            '/fake',
            pid_list=[18467, 18482],
            custom_value_expr_list=['10', 'stat_minflt / 1000.0'],
        )
        plot_mock.assert_called_once_with(
            [
                {
                    18467: [
                        (1567504800, 10),
                        (1567504801, 10),
                        (1567504802, 10),
                        (1567504803, 10),
                    ],
                    18482: [
                        (1567504800, 10),
                        (1567504801, 10),
                        (1567504802, 10),
                        (1567504803, 10),
                    ],
                }, {
                    18467: [
                        (1567504800.0, 51.931),
                        (1567504801.0, 51.931),
                        (1567504802.0, 51.931),
                        (1567504803.0, 51.931),
                    ],
                    18482: [
                        (1567504800.0, 3.572),
                        (1567504801.0, 3.572),
                        (1567504802.0, 3.572),
                        (1567504803.0, 3.572),
                    ],
                },
            ],
            [q1, q2],
            '/fake',
            style=None,
            formatter=None,
            share_y_axis=False,
            logarithmic=False,
            title=None,
            no_dots=False,
            relative_time=False,
        )

    @mock.patch('procpath.plotting.plot')
    def test_plot_rdp_epsilon(self, plot_mock):
        plot.run(
            self.database_file.name,
            '/fake',
            query_name_list=['rss'],
            pid_list=[18467],
            epsilon=0.1,
        )
        plot_mock.assert_called_once_with(
            [{18467: [
                (1567504800.0, 208.2265625),
                (1567504803.0, 208.2265625)
            ]}],
            [procret.registry['rss']],
            '/fake',
            title=None,
            style=None,
            formatter=None,
            share_y_axis=False,
            logarithmic=False,
            no_dots=False,
            relative_time=False,
        )

    @mock.patch('procpath.plotting.plot')
    def test_plot_moving_average_window(self, plot_mock):
        plot.run(
            self.database_file.name,
            '/fake',
            query_name_list=['rss'],
            pid_list=[18467],
            moving_average_window=2,
        )
        plot_mock.assert_called_once_with(
            [{18467: [
                (1567504801.0, 208.2265625),
                (1567504802.0, 208.2265625),
                (1567504803.0, 208.2265625),
            ]}],
            [procret.registry['rss']],
            '/fake',
            title=None,
            style=None,
            formatter=None,
            share_y_axis=False,
            logarithmic=False,
            no_dots=False,
            relative_time=False,
        )


class TestWatchCommand(unittest.TestCase):

    forest: proctree.Forest

    def setUp(self):
        self.forest = proctree.Forest({'stat': procfile.registry['stat']}, skip_self=False)

    @classmethod
    def run_watch(cls, **kwargs):
        try:
            watch.run(**kwargs)
        except KeyboardInterrupt:
            pass

    def get_forest_pids(self, pid=None):
        query = '$..children[?(@.stat.ppid == {})]..pid'.format(pid or os.getpid())
        return jsonpyth.jsonpath(self.forest.get_roots(), query, always_return_list=True)

    def test_watch_verbatim_commands(self):
        with tempfile.NamedTemporaryFile() as f1, tempfile.NamedTemporaryFile() as f2:
            p = multiprocessing.Process(target=self.run_watch, kwargs={
                'interval': 0.3,
                'command_list': [
                    f'sleep 0.4 && echo abc >> {f1.name}',
                    f'sleep 0.4 && echo xyz >> {f2.name}',
                ],
                'procfile_list': ['stat', 'cmdline'],
                'stop_signal': 'SIGINT',
                'repeat': 4,  # two actual repeats given "sleep - interval" margin
                'kill_after': 0.1,
                'procfs': '/proc',
                'procfs_target': 'process',
            })
            self.addCleanup(p.terminate)
            p.start()
            # 1 subprocess, 2 shells, 2 sleeps
            assert_wait_predicate(lambda: len(self.get_forest_pids()) == 5)
            forest_pids = self.get_forest_pids()

            def files_written():
                f1.seek(0)
                f2.seek(0)
                return b'abc\nabc\n' == f1.read() and b'xyz\nxyz\n' == f2.read()

            assert_wait_predicate(files_written)

            os.kill(p.pid, signal.SIGINT)
            p.join(16)  # watch.run finally section can take a while; join doesn't raise on timeout
            self.assertFalse(p.is_alive())
            assert_wait_predicate(
                lambda: all(not treefarm.process_exists(pid) for pid in forest_pids)
            )

    def test_watch_environment(self):
        with tempfile.NamedTemporaryFile() as f1, tempfile.NamedTemporaryFile() as f2:
            p = multiprocessing.Process(target=self.run_watch, kwargs={
                'interval': 0.3,
                'command_list': [
                    f'sleep 0.4 && echo $D0 >> {f1.name}',
                    f'sleep 0.4 && echo $D1 >> {f2.name}',
                ],
                'procfile_list': ['stat'],
                'environment': [['D0', 'echo 1'], ['D1', 'echo ${D0}000']],
                'stop_signal': 'SIGINT',
                'repeat': 4,  # two actual repeats given "sleep - interval" margin
                'kill_after': 0.1,
                'procfs': '/proc',
                'procfs_target': 'process',
            })
            self.addCleanup(p.terminate)
            p.start()
            # 1 subprocess, 2 shells, 2 sleeps
            assert_wait_predicate(lambda: len(self.get_forest_pids()) == 5)
            forest_pids = self.get_forest_pids()

            def files_written():
                f1.seek(0)
                f2.seek(0)
                return b'1\n1\n' == f1.read() and b'1000\n1000\n' == f2.read()

            assert_wait_predicate(files_written)

            # Note that SIGINT does not guarantee that the target
            # process will terminate. There are edge-cases like::
            #
            #   Exception ignored in: <function WeakSet.__init__.<locals>._remove at ...
            #   Traceback (most recent call last):
            #     File "/usr/lib/python3.7/_weakrefset.py", line 38, in _remove
            #       def _remove(item, selfref=ref(self)):
            #   KeyboardInterrupt
            #
            os.kill(p.pid, signal.SIGINT)
            p.join(16)  # watch.run finally section can take a while; join doesn't raise on timeout
            self.assertFalse(p.is_alive())
            self.assertTrue(all(not treefarm.process_exists(pid) for pid in forest_pids))

    def test_watch_query(self):
        with tempfile.NamedTemporaryFile() as f1:
            ppid = os.getppid()
            query = f'$..children[?(@.stat.pid == {ppid})].stat.comm'
            stat_comm = jsonpyth.jsonpath(self.forest.get_roots(), query, always_return_list=True)

            p = multiprocessing.Process(target=self.run_watch, kwargs={
                'interval': 0.1,
                'command_list': [f'sleep 1 && echo $L >> {f1.name}'],
                'procfile_list': ['stat'],
                'environment': [['P', f'echo {ppid}']],
                'query_list': [['L', '$..children[?(@.stat.pid == $P)].stat.comm']],
                'stop_signal': 'SIGINT',
                'kill_after': 0.1,
                'procfs': '/proc',
                'procfs_target': 'process',
            })
            self.addCleanup(p.terminate)
            p.start()
            # 1 subprocess, 1 shells, 1 sleeps
            assert_wait_predicate(lambda: len(self.get_forest_pids()) == 3)
            forest_pids = self.get_forest_pids()

            def file_written():
                f1.seek(0)
                return f'{stat_comm[0]}\n'.encode() == f1.read()

            assert_wait_predicate(file_written)
            os.kill(p.pid, signal.SIGINT)
            p.join(16)  # watch.run finally section can take a while; join doesn't raise on timeout
            self.assertFalse(p.is_alive())
            self.assertTrue(all(not treefarm.process_exists(pid) for pid in forest_pids))

    def test_watch_tree_cleanup_on_sigint(self):
        p = multiprocessing.Process(target=self.run_watch, kwargs={
            'interval': 0.2,
            'command_list': ['sleep 10', 'sleep 10'],
            'procfile_list': ['stat', 'cmdline'],
            'stop_signal': 'SIGINT',
            'kill_after': 0.1,
            'procfs': '/proc',
            'procfs_target': 'process',
        })
        self.addCleanup(p.terminate)
        p.start()
        # 1 subprocess, 2 shells, 2 sleeps
        assert_wait_predicate(lambda: len(self.get_forest_pids()) == 5)
        forest_pids = self.get_forest_pids()

        os.kill(p.pid, signal.SIGINT)
        p.join(16)  # watch.run finally section can take a while; join doesn't raise on timeout
        self.assertFalse(p.is_alive())
        self.assertTrue(all(not treefarm.process_exists(pid) for pid in forest_pids))

    def test_watch_tree_cleanup_on_sigint_shell_first_pty(self):
        with tempfile.NamedTemporaryFile() as f:
            args = [
                sys.executable, '-m', 'procpath', '--logging-level=DEBUG', 'watch',
                '-i', '30',
                '-r', '1',
                '-c', (
                    "sh -cx '"
                    f'trap "echo outer >> {f.name}; exit 1" INT;'
                    fr'''(sh -cx "trap '\''echo inner >> {f.name}; exit 1'\'' INT;'''
                      'sleep 30") & '
                    'sleep 30;'
                    "'"
                ),
                '-s', 'SIGINT',
                '--kill-after', '0.25',
            ]

            pid, fd = pty.fork()
            if pid == 0:
                os.execv(args[0], args)
                sys.exit(0)

            # python -m procpath watch -i 10 -r 1 -c sh -cx 'trap ...
            # └─ /bin/sh -c sh -cx 'trap "echo outer >> /tmp/...
            #    └─ sh -cx trap "echo outer >> /tmp/...
            #       ├─ sh -cx trap 'echo inner >> /tmp/...
            #       │  └─ sleep 30
            #       └─ sleep 30
            assert_wait_predicate(lambda: len(self.get_forest_pids(pid)) == 5)
            subtree_pids = self.get_forest_pids(pid)

            # Simulate Ctrl+C to "procpath watch"
            os.kill(pid, signal.SIGINT)

            child_pid, child_returncode = os.wait()
            self.assertEqual(pid, child_pid)
            self.assertEqual(0, child_returncode)

            log_lines = os.read(fd, 4096).decode().splitlines()
            expected_lines = textwrap.dedent(r'''
                [^A-Z]+ DEBUG   procpath Starting №1: sh -cx 'trap "echo outer >> /tmp/tmp
                [^A-Z]+ DEBUG   procpath Started №1 shell as PID \d+
                [^A-Z]+ WARNING procpath №1: \+ trap echo outer >> /tmp/tmp\w+; exit 1 INT
                [^A-Z]+ WARNING procpath №1: \+ sleep 30
                [^A-Z]+ WARNING procpath №1: \+ sh -cx trap 'echo inner >> /tmp/tmp\w+; exit 1' INT
                [^A-Z]+ WARNING procpath №1: \+ trap echo inner >> /tmp/tmp\w+; exit 1 INT
                [^A-Z]+ WARNING procpath №1: \+ sleep 30
                [^A-Z]+ DEBUG   procpath Forest PIDs to terminate: \d+, \d+, \d+, \d+, \d+
                [^A-Z]+ DEBUG   procpath Sending SIGINT to shell PGRP \d+
                [^A-Z]+ WARNING procpath №1: \+ echo outer
                [^A-Z]+ WARNING procpath №1: \+ exit 1
                [^A-Z]+ DEBUG   procpath Shell processes successfully terminated: \d+
                [^A-Z]+ DEBUG   procpath Killing unterminated descendant PID \d+
                [^A-Z]+ DEBUG   procpath Killing unterminated descendant PID \d+
            ''').strip().splitlines()
            assert_lines_match(log_lines, expected_lines)

            self.assertFalse(treefarm.process_exists(pid))
            subtree_status = {pid: treefarm.process_exists(pid) for pid in subtree_pids}
            self.assertTrue(all(not v for v in subtree_status.values()), subtree_status)

            # Inner process does not receive SIGINT as it's in sub-shell. It is
            # only SIGKILL'ed on the latest step.
            f.seek(0)
            self.assertEqual(b'outer\n', f.read())

    def test_watch_tree_cleanup_on_sigint_shell_first(self):
        with tempfile.NamedTemporaryFile() as f:
            p = multiprocessing.Process(target=self.run_watch, kwargs={
                'interval': 15,
                'repeat': 1,
                'command_list': [
                    fr'''
                    sh -c '
                      trap "echo outer >> {f.name}; exit 1" INT;
                      (sh -c "trap '\''echo inner >> {f.name}; exit 1'\'' INT; sleep 30") &
                      sleep 30;
                    '
                    ''',
                ],
                'procfile_list': ['stat'],
                'stop_signal': 'SIGINT',
                'kill_after': 1,
                'procfs': '/proc',
                'procfs_target': 'process',
            })
            self.addCleanup(p.terminate)
            p.start()
            # 1 procpath command_list shells, 2 "sh -cx", 2 "sleep"
            assert_wait_predicate(lambda: len(self.get_forest_pids(p.pid)) == 5)
            forest_pids = self.get_forest_pids(p.pid)

            os.kill(p.pid, signal.SIGINT)
            p.join(16)  # watch.run finally section can take a while; join doesn't raise on timeout
            self.assertFalse(p.is_alive())
            forest_status = {pid: treefarm.process_exists(pid) for pid in forest_pids}
            self.assertTrue(all(not v for v in forest_status.values()), forest_status)

            # Inner process does not receive SIGINT as it's in sub-shell. It is
            # only SIGKILL'ed on the latest step.
            f.seek(0)
            self.assertEqual(b'outer\n', f.read())

    def test_watch_tree_cleanup_on_sigint_shell_first_kill(self):
        async def test():
            process = await asyncio.create_subprocess_exec(
                *[
                    sys.executable, '-m', 'procpath', '--logging-level=DEBUG', 'watch',
                    '-i', '0.5',
                    '-r', '1',
                    '-c', "sh -cx '(sh -cx \"sleep 30\") & sleep 30;'",
                    '-s', 'SIGCONT',  # no-op signal
                    '--kill-after', '0.1',
                ],
                stderr=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
            )
            # 1 procpath command_list shells, 2 "sh -cx", 2 "sleep"
            await assert_wait_predicate_async(
                lambda: len(self.get_forest_pids(process.pid)) == 5
            )
            forest_pids = self.get_forest_pids(process.pid)

            stdout, stderr = await process.communicate()
            self.assertEqual(b'', stdout)
            log_lines = [line for line in stderr.decode().splitlines()]
            expected_lines = textwrap.dedent(r'''
                [^A-Z]+ DEBUG   procpath Starting №1: sh -cx '\(sh -cx "sleep
                [^A-Z]+ DEBUG   procpath Started №1 shell as PID \d+
                [^A-Z]+ WARNING procpath №1: \+ sleep 30
                [^A-Z]+ WARNING procpath №1: \+ sh -cx sleep 30
                [^A-Z]+ WARNING procpath №1: \+ sleep 30
                [^A-Z]+ DEBUG   procpath Forest PIDs to terminate: \d+, \d+, \d+, \d+, \d+
                [^A-Z]+ DEBUG   procpath Sending SIGCONT to shell PGRP \d+
                [^A-Z]+ DEBUG   procpath Not all shell processes terminated after stop signal
                [^A-Z]+ DEBUG   procpath Killing unterminated shell PID \d+
                [^A-Z]+ DEBUG   procpath Killing unterminated descendant PID \d+
                [^A-Z]+ DEBUG   procpath Killing unterminated descendant PID \d+
                [^A-Z]+ DEBUG   procpath Killing unterminated descendant PID \d+
                [^A-Z]+ DEBUG   procpath Killing unterminated descendant PID \d+
            ''').strip().splitlines()
            assert_lines_match(log_lines, expected_lines)
            self.assertEqual(
                4,
                len([line for line in log_lines if 'Killing unterminated descendant' in line]),
                'Shell should not be terminated twice',
            )

            self.assertTrue(all(not treefarm.process_exists(pid) for pid in forest_pids))

        asyncio.run(test(), debug=True)

    def test_watch_tree_cleanup_on_repeat_end(self):
        p = multiprocessing.Process(target=self.run_watch, kwargs={
            'interval': 0.2,
            'command_list': ['sleep 10', 'sleep 10'],
            'procfile_list': ['stat'],
            'repeat': 1,
            'stop_signal': 'SIGINT',
            'kill_after': 0.1,
            'procfs': '/proc',
            'procfs_target': 'process',
        })
        self.addCleanup(p.terminate)
        p.start()
        # 1 subprocess, 2 shells, 2 sleeps
        assert_wait_predicate(lambda: len(self.get_forest_pids()) == 5)
        forest_pids = self.get_forest_pids()

        p.join(16)  # watch.run finally section can take a while; join doesn't raise on timeout
        self.assertFalse(p.is_alive())
        self.assertTrue(all(not treefarm.process_exists(pid) for pid in forest_pids))

    def test_watch_tree_cleanup_on_error(self):
        async def test():
            with tempfile.NamedTemporaryFile() as f:
                f.write(b'-1')
                f.flush()

                process = await asyncio.create_subprocess_exec(
                    *[
                        sys.executable, '-m', 'procpath', 'watch',
                        '-i', '1',
                        '-e', f'P=cat {f.name}',
                        '-q', 'L=$..children[?(@.stat.pid == $P)]..pid',
                        '-c', 'echo $L',
                        '-c', 'sleep 666',
                    ],
                    stderr=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                )
                await asyncio.sleep(0.5)

                await assert_wait_predicate_async(
                    lambda: len(self.get_forest_pids(process.pid)) == 2
                )
                pids = self.get_forest_pids(process.pid)

            stdout, stderr = await process.communicate()
            self.assertEqual(b'', stdout)
            self.assertIn('Query L evaluated empty', stderr.decode())
            self.assertIn('No such file or directory', stderr.decode())
            self.assertIn('Variable P evaluated empty', stderr.decode())
            self.assertIn('Python syntax error', stderr.decode())

            self.assertTrue(all(not treefarm.process_exists(pid) for pid in pids))

        asyncio.run(test(), debug=True)

    def test_watch_tree_cleanup_by_sigterm(self):
        p = multiprocessing.Process(target=self.run_watch, kwargs={
            'interval': 0.2,
            'command_list': ['sleep 10', 'sleep 10'],
            'procfile_list': ['stat'],
            'repeat': 1,
            'stop_signal': 'SIGTERM',
            'kill_after': 0.1,
            'procfs': '/proc',
            'procfs_target': 'process',
        })
        self.addCleanup(p.terminate)
        p.start()
        # 1 subprocess, 2 shells, 2 sleeps
        assert_wait_predicate(lambda: len(self.get_forest_pids()) == 5)
        forest_pids = self.get_forest_pids()

        p.join(16)  # watch.run finally section can take a while; join doesn't raise on timeout
        self.assertFalse(p.is_alive())
        self.assertTrue(all(not treefarm.process_exists(pid) for pid in forest_pids))

    def test_watch_empty_env_command_result(self):
        with self.assertLogs('procpath', 'INFO') as ctx:
            watch.run(
                interval=0,
                procfile_list=['stat'],
                command_list=['true'],
                environment=[['P', 'echo']],
                repeat=1,
                stop_signal='SIGINT',
                kill_after=0.1,
                procfs='/proc',
                procfs_target='process',
            )
        self.assertEqual(1, len(ctx.records))
        self.assertEqual('Variable P evaluated empty', ctx.records[0].message)

    def test_watch_empty_query_result(self):
        with self.assertLogs('procpath', 'INFO') as ctx:
            watch.run(
                interval=0,
                procfile_list=['stat'],
                command_list=['true'],
                query_list=[['L', '$..children[?(@.stat.pid == -1)].stat.comm']],
                repeat=1,
                stop_signal='SIGINT',
                kill_after=0.1,
                procfs='/proc',
                procfs_target='process',
            )
        self.assertEqual(1, len(ctx.records))
        self.assertEqual('Query L evaluated empty', ctx.records[0].message)

    def test_watch_query_error(self):
        with self.assertRaises(CommandError) as ctx:
            watch.run(
                interval=0,
                procfile_list=['stat'],
                command_list=['true'],
                query_list=[['L', '!@#$']],
                repeat=1,
                stop_signal='SIGINT',
                kill_after=0.1,
                procfs='/proc',
                procfs_target='process',
            )
        self.assertEqual(
            'JSONPath syntax error - Expected {target set | child step | recurse step}, here:'
            '\n!@#$\n^',
            str(ctx.exception),
        )

    def test_watch_std_stream_logging(self):
        with self.assertLogs('procpath', 'INFO') as ctx:
            watch.run(
                interval=0.2,
                procfile_list=['stat'],
                command_list=[
                    'echo "Carousel"',
                    'sleep 0.1 && echo "A Glutton for Punishment" 1>&2',
                ],
                repeat=1,
                stop_signal='SIGINT',
                kill_after=0.2,
                procfs='/proc',
                procfs_target='process',
            )
        self.assertEqual(2, len(ctx.records))
        self.assertEqual('INFO', ctx.records[0].levelname)
        self.assertEqual('№1: Carousel', ctx.records[0].message)
        self.assertEqual('WARNING', ctx.records[1].levelname)
        self.assertEqual('№2: A Glutton for Punishment', ctx.records[1].message)

    def test_watch_std_stream_write_after_stop(self):
        with tempfile.NamedTemporaryFile() as f:
            now = datetime.now().isoformat()
            f.write(now.encode())
            f.flush()

            with self.assertLogs('procpath', 'INFO') as ctx:
                watch.run(
                    interval=0.1,
                    repeat=1,
                    procfile_list=['stat'],
                    command_list=[f'sleep 0.005 && cat {f.name}'],
                    stop_signal='SIGINT',
                    kill_after=0.1,
                    procfs='/proc',
                    procfs_target='process',
                )

        self.assertEqual(1, len(ctx.records))
        self.assertEqual('INFO', ctx.records[0].levelname)
        self.assertEqual(f'№1: {now}', ctx.records[0].message)

    def test_watch_process_pids_exposed(self):
        class serialnumber:
            """RFC 1982 comparison for PIDs."""

            with open('/proc/sys/kernel/pid_max') as f:
                max_pid = int(f.read())

            _half = max_pid // 2

            def __init__(self, i):
                self.i = i

            def __eq__(self, other):
                return self.i == other.i

            def __gt__(self, other):
                return (
                    self.i < other.i and (other.i - self.i > self._half)
                    or self.i > other.i and (self.i - other.i < self._half)
                )

        with tempfile.NamedTemporaryFile() as f:
            watch.run(
                interval=0.1,
                repeat=2,
                procfile_list=['stat'],
                command_list=[
                    'sleep 0.005 && echo "target process 1"',
                    'sleep 0.005 && echo "target process 2"',
                    f'env | grep WPS >> {f.name}',
                ],
                stop_signal='SIGINT',
                kill_after=0.1,
                procfs='/proc',
                procfs_target='process',
            )

            prev_pid = None
            for i, line in enumerate(f.read().decode().splitlines()):
                name, value = line.split('=')
                self.assertEqual('WPS{}'.format(i % 2 + 1), name)

                if prev_pid:
                    self.assertGreater(serialnumber(int(value)), serialnumber(int(prev_pid)))

                prev_pid = int(value)

    def test_watch_no_restart(self):
        with tempfile.NamedTemporaryFile() as f:
            watch.run(
                interval=0,
                repeat=1000,
                procfile_list=['stat'],
                command_list=[
                    f'sleep 0.005 && echo "On to Tarmac" >> {f.name}',
                ],
                stop_signal='SIGINT',
                kill_after=0.1,
                no_restart=True,
                procfs='/proc',
                procfs_target='process',
            )
            self.assertEqual(b'On to Tarmac\n', f.read())

        with tempfile.NamedTemporaryFile() as f:
            watch.run(
                interval=0,
                repeat=1000,
                procfile_list=['stat'],
                command_list=[
                    f'sleep 0.005 && echo "On to Tarmac" >> {f.name}',
                    'sleep 0.2',
                ],
                stop_signal='SIGINT',
                kill_after=0.1,
                no_restart=True,
                procfs='/proc',
                procfs_target='process',
            )
            self.assertEqual(b'On to Tarmac\n', f.read())

    def test_watch_no_restart_no_reeval(self):
        with tempfile.NamedTemporaryFile() as f1, tempfile.NamedTemporaryFile() as f2:
            watch.run(
                interval=0.001,
                procfile_list=['stat'],
                environment=[['P', f'echo reeval >> {f2.name} && echo OK']],
                command_list=[
                    f'''seq 5 | xargs -n1 -- sh -c 'sleep 0.001 && echo "cmd" >> {f1.name}' ''',
                ],
                stop_signal='SIGINT',
                kill_after=1,
                no_restart=True,
                procfs='/proc',
                procfs_target='process',
            )
            self.assertEqual(b'\n'.join([b'cmd'] * 5) + b'\n', f1.read())
            self.assertEqual(b'reeval\n', f2.read())


class TestPlayCommand(unittest.TestCase):

    playbook_file = None

    def setUp(self):
        self.playbook_file = tempfile.NamedTemporaryFile('w')
        self.addCleanup(self.playbook_file.close)
        self.playbook_file.write(r'''
            [group1:query]
            environment:
              L=docker ps -f status=running -f name='^project_name' -q | xargs -I{} -- \
                docker inspect -f '{{.State.Pid}}' {} | tr '\n' ,
              TS=date +%s
            query: $..children[?(@.stat.pid in [$L])]
            sql_query: SELECT SUM(stat_rss) / 1024.0 * 4 total FROM record
            procfile_list: stat,cmdline,status

            [group1:record]
            environment:
              C1=docker inspect -f "{{.State.Pid}}" project_db_1
              C2=docker inspect -f "{{.State.Pid}}" project_app_1
            interval: 1
            recnum: 60
            reevalnum: 30
            database_file: out.sqlite
            query: $..children[?(@.stat.pid in [$C1, $C2])]

            [group1:plot]
            database_file: out.sqlite
            plot_file: rss.svg
            logarithmic: 1
            query_name: rss
            epsilon: 0.5
            moving_average_window: 10

            [group2:watch]
            interval: 601
            environment:
              S1=systemctl show --property MainPID redis-server | cut -d "=" -f 2
              C1=docker inspect -f "{{.State.Pid}}" app_gunicorn_1
            query:
              L1=$..children[?(@.stat.pid == $S1)]..pid
            command:
              smemstat -q -o redis-memdiff-$TS.json -p $L1 30 20
              timeout --foreground --signal SIGINT 600 \
                py-spy record --subprocesses --output app-flamegraph-$TS.svg --pid $C1
        ''')
        self.playbook_file.flush()

    def test_play_all_mocked(self):
        output_file = io.StringIO()
        with contextlib.ExitStack() as stack:
            query_mock = stack.enter_context(mock.patch('procpath.cmd.query.run'))
            record_mock = stack.enter_context(mock.patch('procpath.cmd.record.run'))
            plot_mock = stack.enter_context(mock.patch('procpath.cmd.plot.run'))
            watch_mock = stack.enter_context(mock.patch('procpath.cmd.watch.run'))

            play.run(
                playbook_file=self.playbook_file.name,
                output_file=output_file,
                list_sections=False,
                dry_run=False,
                target=['*'],
            )

            query_mock.assert_called_once_with(
                delimiter=None,
                environment=[
                    [
                        'L',
                        (
                            "docker ps -f status=running -f name='^project_name' -q | xargs"
                            " -I{} -- docker inspect -f '{{.State.Pid}}' {} | tr '\\n' ,"
                        ),
                    ],
                    ['TS', 'date +%s'],
                ],
                indent=None,
                query='$..children[?(@.stat.pid in [$L])]',
                output_file=output_file,
                procfile_list=['stat', 'cmdline', 'status'],
                sql_query='SELECT SUM(stat_rss) / 1024.0 * 4 total FROM record',
                procfs='/proc',
                procfs_target='process',
            )
            record_mock.assert_called_once_with(
                database_file='out.sqlite',
                environment=[
                    ['C1', 'docker inspect -f "{{.State.Pid}}" project_db_1'],
                    ['C2', 'docker inspect -f "{{.State.Pid}}" project_app_1']
                ],
                interval=1.0,
                procfile_list=['stat', 'cmdline'],
                query='$..children[?(@.stat.pid in [$C1, $C2])]',
                recnum=60,
                reevalnum=30,
                pid_list=None,
                stop_without_result=False,
                procfs='/proc',
                procfs_target='process',
            )
            plot_mock.assert_called_once_with(
                after=None,
                before=None,
                custom_query_file_list=None,
                custom_value_expr_list=None,
                database_file='out.sqlite',
                epsilon=0.5,
                formatter=None,
                share_y_axis=False,
                logarithmic=True,
                moving_average_window=10,
                pid_list=None,
                plot_file='rss.svg',
                query_name_list=['rss'],
                style=None,
                title=None,
                no_dots=False,
                relative_time=False,
            )
            watch_mock.assert_called_once_with(
                command_list=[
                    'smemstat -q -o redis-memdiff-$TS.json -p $L1 30 20',
                    (
                        'timeout --foreground --signal SIGINT 600 py-spy record '
                        '--subprocesses --output app-flamegraph-$TS.svg --pid $C1'
                    )
                ],
                environment=[
                    ['S1', 'systemctl show --property MainPID redis-server | cut -d "=" -f 2'],
                    ['C1', 'docker inspect -f "{{.State.Pid}}" app_gunicorn_1']
                ],
                interval=601.0,
                procfile_list=['stat', 'cmdline'],
                query_list=[['L1', '$..children[?(@.stat.pid == $S1)]..pid']],
                repeat=None,
                stop_signal='SIGINT',
                kill_after=10.0,
                no_restart=False,
                procfs='/proc',
                procfs_target='process',
            )

        self.assertEqual('', output_file.getvalue())

    def test_play_list_sections(self):
        output_file = io.StringIO()
        play.run(
            playbook_file=self.playbook_file.name,
            output_file=output_file,
            list_sections=True,
            dry_run=False,
            target=['*'],
        )
        self.assertEqual(
            ['group1:query', 'group1:record', 'group1:plot', 'group2:watch'],
            output_file.getvalue().splitlines(),
        )

        output_file = io.StringIO()
        play.run(
            playbook_file=self.playbook_file.name,
            output_file=output_file,
            list_sections=True,
            dry_run=False,
            target=['group1:*'],
        )
        self.assertEqual(
            ['group1:query', 'group1:record', 'group1:plot'], output_file.getvalue().splitlines()
        )

        output_file = io.StringIO()
        play.run(
            playbook_file=self.playbook_file.name,
            output_file=output_file,
            list_sections=True,
            dry_run=False,
            target=['*:watch'],
        )
        self.assertEqual(['group2:watch'], output_file.getvalue().splitlines())

        output_file = io.StringIO()
        play.run(
            playbook_file=self.playbook_file.name,
            output_file=output_file,
            list_sections=True,
            dry_run=False,
            target=['group1:record', 'group2:watch'],
        )
        self.assertEqual(['group1:record', 'group2:watch'], output_file.getvalue().splitlines())

    def test_play_list_non_command_section(self):
        with tempfile.NamedTemporaryFile('w') as f:
            f.write('''
                [group1:query]
                query: $..children[?(@.stat.pid == 42)]
                procfile_list: stat,status

                [foo]
                a: b

                [bar]
                c: d
            ''')
            f.flush()

            output_file = io.StringIO()
            play.run(
                playbook_file=f.name,
                output_file=output_file,
                list_sections=True,
                dry_run=False,
                target=['*', 'foo'],
            )
            self.assertEqual(['group1:query'], output_file.getvalue().splitlines())

    def test_play_dry_run(self):
        output_file = io.StringIO()
        with self.assertLogs('procpath', 'INFO') as ctx:
            play.run(
                playbook_file=self.playbook_file.name,
                output_file=output_file,
                list_sections=False,
                dry_run=True,
                target=['group1:record', 'group1:plot'],
            )
        self.assertEqual(2, len(ctx.records))
        self.assertEqual('INFO', ctx.records[0].levelname)
        self.assertEqual('Executing section group1:record', ctx.records[0].message)
        self.assertEqual('INFO', ctx.records[1].levelname)
        self.assertEqual('Executing section group1:plot', ctx.records[1].message)

        self.assertEqual([
            '{',
            '  "database_file": "out.sqlite",',
            '  "environment": [',
            '    [',
            '      "C1",',
            '      "docker inspect -f \\"{{.State.Pid}}\\" project_db_1"',
            '    ],',
            '    [',
            '      "C2",',
            '      "docker inspect -f \\"{{.State.Pid}}\\" project_app_1"',
            '    ]',
            '  ],',
            '  "interval": 1.0,',
            '  "pid_list": null,',
            '  "procfile_list": [',
            '    "stat",',
            '    "cmdline"',
            '  ],',
            '  "procfs": "/proc",',
            '  "procfs_target": "process",',
            '  "query": "$..children[?(@.stat.pid in [$C1, $C2])]",',
            '  "recnum": 60,',
            '  "reevalnum": 30,',
            '  "stop_without_result": false',
            '}',
            '{',
            '  "after": null,',
            '  "before": null,',
            '  "custom_query_file_list": null,',
            '  "custom_value_expr_list": null,',
            '  "database_file": "out.sqlite",',
            '  "epsilon": 0.5,',
            '  "formatter": null,',
            '  "logarithmic": true,',
            '  "moving_average_window": 10,',
            '  "no_dots": false,',
            '  "pid_list": null,',
            '  "plot_file": "rss.svg",',
            '  "query_name_list": [',
            '    "rss"',
            '  ],',
            '  "relative_time": false,',
            '  "share_y_axis": false,',
            '  "style": null,',
            '  "title": null',
            '}'
        ], output_file.getvalue().splitlines())

    def test_play_negative_flag(self):
        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f, mock.patch('procpath.cmd.plot.run') as pm:
            f.write('''
                [plot]
                database_file: out.sqlite
                plot_file: rss.svg
                logarithmic: 0
                query_name: cpu
            ''')
            f.flush()

            play.run(
                playbook_file=f.name,
                output_file=output_file,
                list_sections=False,
                dry_run=False,
                target=['plot'],
            )
            pm.assert_called_once_with(
                after=None,
                before=None,
                custom_query_file_list=None,
                custom_value_expr_list=None,
                database_file='out.sqlite',
                epsilon=None,
                formatter=None,
                share_y_axis=False,
                logarithmic=False,
                moving_average_window=None,
                pid_list=None,
                plot_file='rss.svg',
                query_name_list=['cpu'],
                style=None,
                title=None,
                no_dots=False,
                relative_time=False,
            )

        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f, mock.patch('procpath.cmd.record.run') as rm:
            with tempfile.NamedTemporaryFile('w') as db_f:
                f.write(f'''
                    [record]
                    stop_without_result: 1
                    database_file: {db_f.name}
                ''')
                f.flush()
                play.run(
                    playbook_file=f.name,
                    output_file=output_file,
                    list_sections=False,
                    dry_run=False,
                    target=['record'],
                )
            rm.assert_called_once_with(
                database_file=db_f.name,
                environment=None,
                interval=10.0,
                pid_list=None,
                procfile_list=['stat', 'cmdline'],
                query='',
                recnum=None,
                reevalnum=None,
                stop_without_result=True,
                procfs='/proc',
                procfs_target='process',
            )

        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f, mock.patch('procpath.cmd.watch.run') as wm:
            f.write('''
                [watch]
                interval: 1
                command: echo
                no_restart: yes
            ''')
            f.flush()
            play.run(
                playbook_file=f.name,
                output_file=output_file,
                list_sections=False,
                dry_run=False,
                target=['watch'],
            )
            wm.assert_called_once_with(
                command_list=['echo'],
                environment=None,
                interval=1.0,
                no_restart=True,
                procfile_list=['stat', 'cmdline'],
                query_list=None,
                repeat=None,
                stop_signal='SIGINT',
                kill_after=10.0,
                procfs='/proc',
                procfs_target='process',
            )

    def test_play_watch(self):
        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f:
            f.write('''
                [watch]
                environment: V=echo 123
                command: echo $V
                interval: 0.1
                repeat: 1
            ''')
            f.flush()

            with self.assertLogs('procpath', 'INFO') as ctx:
                play.run(
                    playbook_file=f.name,
                    output_file=output_file,
                    list_sections=False,
                    dry_run=False,
                    target=['watch'],
                )
        self.assertEqual(2, len(ctx.records))
        self.assertEqual('INFO', ctx.records[0].levelname)
        self.assertEqual('Executing section watch', ctx.records[0].message)
        self.assertEqual('INFO', ctx.records[1].levelname)
        self.assertEqual('№1: 123', ctx.records[1].message)

        self.assertEqual('', output_file.getvalue())

    def test_play_watch_override(self):
        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f:
            f.write('''
                [watch]
                environment: V=echo 123
                command: echo $V $W $X
                interval: 0.1
                repeat: 1
            ''')
            f.flush()

            with self.assertLogs('procpath', 'INFO') as ctx:
                play.run(
                    playbook_file=f.name,
                    output_file=output_file,
                    list_sections=False,
                    dry_run=False,
                    target=['watch'],
                    option_override_list=[['environment', 'W=echo 234\nX=echo 345']]
                )
        self.assertEqual(2, len(ctx.records))
        self.assertEqual('INFO', ctx.records[0].levelname)
        self.assertEqual('Executing section watch', ctx.records[0].message)
        self.assertEqual('INFO', ctx.records[1].levelname)
        self.assertEqual('№1: 123 234 345', ctx.records[1].message)

        self.assertEqual('', output_file.getvalue())

    def test_play_query(self):
        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f:
            f.write('''
                [foo:query]
                environment:
                  L=echo \\
                    {}
                query: $..children[?(@.stat.pid == $L)]
                sql_query: SELECT SUM(status_vmrss) total FROM record
                procfile_list: stat,status
            '''.format(os.getppid()))
            f.flush()

            with self.assertLogs('procpath', 'INFO') as ctx:
                play.run(
                    playbook_file=f.name,
                    output_file=output_file,
                    list_sections=False,
                    dry_run=False,
                    target=['*:query'],
                )
        self.assertEqual(1, len(ctx.records))
        self.assertEqual('INFO', ctx.records[0].levelname)
        self.assertEqual('Executing section foo:query', ctx.records[0].message)

        actual = json.loads(output_file.getvalue())
        self.assertEqual(1, len(actual))
        self.assertEqual({'total'}, actual[0].keys())
        self.assertGreater(actual[0]['total'], 512)

    def test_play_record_plot(self):
        output_file = io.StringIO()
        with contextlib.ExitStack() as stack:
            playbook_file = stack.enter_context(tempfile.NamedTemporaryFile('w'))
            database_file = stack.enter_context(tempfile.NamedTemporaryFile())
            plot_file = stack.enter_context(tempfile.NamedTemporaryFile())

            playbook_file.write(f'''
                [group1:record]
                interval: 0.1
                recnum: 2
                query: $..children[?(@.stat.pid == {os.getppid()})]

                [group1:plot]
                plot_file: {plot_file.name}
                logarithmic: 1
                query_name:
                  rss
                  rss
            ''')
            playbook_file.flush()

            with self.assertLogs('procpath', 'INFO') as ctx:
                play.run(
                    playbook_file=playbook_file.name,
                    output_file=output_file,
                    list_sections=False,
                    dry_run=False,
                    target=['group1:*'],
                    option_override_list=[['database_file', database_file.name]],
                )

                svg_bytes = plot_file.read()
                self.assertIn(b'<svg', svg_bytes)
                self.assertIn(b'Resident Set Size, MiB', svg_bytes)
                self.assertGreater(len(svg_bytes), 15_000)

        info_records = [r for r in ctx.records if r.levelname == 'INFO']
        self.assertEqual(2, len(info_records))
        self.assertEqual('Executing section group1:record', info_records[0].message)
        self.assertEqual('Executing section group1:plot', info_records[1].message)

        self.assertEqual('', output_file.getvalue())

    def test_play_section_inheritance(self):
        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f, mock.patch('procpath.cmd.query.run') as m:
            f.write(r'''
                [stack_rss]
                environment:
                  L=docker ps -f status=running -f name='^staging' -q | xargs -I{} -- \
                    docker inspect -f '{{.State.Pid}}' {} | tr '\n' ,
                query: $..children[?(@.stat.pid in [$L])]
                procfile_list: stat

                [stack_rss:status]
                extends: stack_rss
                environment: TS=date +%s
                procfile_list: stat,status

                [stack_rss:status:query]
                extends: stack_rss:status
                sql_query: SELECT SUM(status_vmrss) total FROM record

                [stack_rss:stat:query]
                extends: stack_rss
                sql_query: SELECT SUM(stat_rss) * 4 total FROM record
            ''')
            f.flush()

            play.run(
                playbook_file=f.name,
                output_file=output_file,
                list_sections=False,
                dry_run=False,
                target=['stack_rss:*'],
            )

        self.assertEqual(
            [
                mock.call(
                    environment=[
                        [
                            'L',
                            (
                                "docker ps -f status=running -f name='^staging' -q | xargs"
                                " -I{} -- docker inspect -f '{{.State.Pid}}' {} | tr '\\n' ,"
                            )
                        ],
                        ['TS', 'date +%s'],
                    ],
                    query='$..children[?(@.stat.pid in [$L])]',
                    output_file=output_file,
                    procfile_list=['stat', 'status'],
                    sql_query='SELECT SUM(status_vmrss) total FROM record',
                    delimiter=None,
                    indent=None,
                    procfs='/proc',
                    procfs_target='process',
                ),
                mock.call(
                    environment=[
                        [
                            'L',
                            (
                                "docker ps -f status=running -f name='^staging' -q | xargs"
                                " -I{} -- docker inspect -f '{{.State.Pid}}' {} | tr '\\n' ,"
                            )
                        ],
                    ],
                    query='$..children[?(@.stat.pid in [$L])]',
                    output_file=output_file,
                    procfile_list=['stat'],
                    sql_query='SELECT SUM(stat_rss) * 4 total FROM record',
                    delimiter=None,
                    indent=None,
                    procfs='/proc',
                    procfs_target='process',
                )
            ],
            m.call_args_list,
        )

    def test_play_explicit_extends(self):
        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f:
            f.write(r'''
                [rss:query]
                sql_query: SELECT SUM(stat_rss) * 4 total FROM record

                [python]
                environment:
                  PIDS=docker ps -f status=running -f name='^staging' -q | xargs -I{} -- \
                       docker inspect -f '{{.State.Pid}}' {} | tr '\n' ,
                query: $..children[?(@.stat.pid in [$PIDS] and 'python' in @.stat.comm)]

                [container]
                query: $..children[?(@.stat.pid == $P)]

                [container:redis]
                extends: container
                environment:
                  P=docker inspect -f '{{.State.Pid}}' staging_redis_1

                [container:mysql]
                extends: container
                environment:
                  P=docker inspect -f '{{.State.Pid}}' staging_mysql_1

                [container:nginx]
                extends: container
                environment:
                  P=docker inspect -f '{{.State.Pid}}' staging_nginx_1

                [python:rss:query]
                extends:
                  python
                  rss:query

                [container:redis:rss:query]
                extends:
                  container:redis
                  rss:query

                [container:mysql:rss:query]
                extends:
                  container:mysql
                  rss:query

                [container:nginx:rss:query]
                extends:
                  container:nginx
                  rss:query
            ''')
            f.flush()

            with self.assertLogs('procpath', 'INFO') as ctx:
                play.run(
                    playbook_file=f.name,
                    output_file=output_file,
                    list_sections=False,
                    dry_run=True,
                    target=['container:redis:*', 'python:rss:query'],
                )

        self.assertEqual(2, len(ctx.records))
        self.assertEqual('INFO', ctx.records[0].levelname)
        self.assertEqual('Executing section container:redis:rss:query', ctx.records[0].message)
        self.assertEqual('INFO', ctx.records[1].levelname)
        self.assertEqual('Executing section python:rss:query', ctx.records[1].message)

        decoder = json.JSONDecoder()
        actual = []
        idx = 0
        while idx < len(output_file.getvalue()):
            obj, idx = decoder.raw_decode(output_file.getvalue(), idx)
            idx += 1
            actual.append(obj)

        self.assertEqual([
            {
                'delimiter': None,
                'environment': [['P', "docker inspect -f '{{.State.Pid}}' staging_redis_1"]],
                'procfs': '/proc',
                'procfs_target': 'process',
                'indent': None,
                'procfile_list': ['stat', 'cmdline'],
                'query': '$..children[?(@.stat.pid == $P)]',
                'sql_query': 'SELECT SUM(stat_rss) * 4 total FROM record',
            }, {
                'delimiter': None,
                'indent': None,
                'procfs': '/proc',
                'procfs_target': 'process',
                'environment': [
                    [
                        'PIDS',
                        "docker ps -f status=running -f name='^staging' -q | xargs "
                        "-I{} -- docker inspect -f '{{.State.Pid}}' {} | tr '\\n' ,"
                    ]
                ],
                'procfile_list': ['stat', 'cmdline'],
                'query': "$..children[?(@.stat.pid in [$PIDS] and 'python' in @.stat.comm)]",
                'sql_query': 'SELECT SUM(stat_rss) * 4 total FROM record',
            }
        ], actual)

    def test_play_missing_arguments(self):
        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f:
            f.write('[foo:record]\nprocfile_list: stat')
            f.flush()

            with self.assertRaises(CommandError) as ctx:
                play.run(
                    playbook_file=f.name,
                    output_file=output_file,
                    list_sections=False,
                    dry_run=False,
                    target=['*'],
                )
            self.assertEqual(
                'Invalid section: the following arguments are required: database-file',
                str(ctx.exception),
            )
        self.assertEqual('', output_file.getvalue())

    def test_play_unrecognised_arguments(self):
        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f:
            f.write('[foo:query]\nbar: baz')
            f.flush()

            with self.assertRaises(CommandError) as ctx:
                play.run(
                    playbook_file=f.name,
                    output_file=output_file,
                    list_sections=False,
                    dry_run=False,
                    target=['*'],
                )
            self.assertEqual(
                'Invalid section: unrecognized arguments: bar',
                str(ctx.exception),
            )
        self.assertEqual('', output_file.getvalue())

    def test_play_invalid_file(self):
        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f:
            f.write('!@#$')
            f.flush()

            with self.assertRaises(CommandError) as ctx:
                play.run(
                    playbook_file=f.name,
                    output_file=output_file,
                    list_sections=False,
                    dry_run=False,
                    target=['*'],
                )
            self.assertTrue(str(ctx.exception).startswith('File contains no section headers.'))
        self.assertEqual('', output_file.getvalue())

    def test_play_invalid_section(self):
        output_file = io.StringIO()
        with tempfile.NamedTemporaryFile('w') as f:
            f.write('[foo]\n!@#$')
            f.flush()

            with self.assertRaises(CommandError) as ctx:
                play.run(
                    playbook_file=f.name,
                    output_file=output_file,
                    list_sections=False,
                    dry_run=False,
                    target=['*'],
                )
            self.assertTrue(
                str(ctx.exception).startswith(f'Source contains parsing errors: {f.name!r}')
            )
        self.assertEqual('', output_file.getvalue())

    def test_play_absent(self):
        output_file = io.StringIO()
        with self.assertRaises(CommandError) as ctx:
            play.run(
                playbook_file=self.playbook_file.name,
                output_file=output_file,
                list_sections=False,
                dry_run=False,
                target=['foo:bar'],
            )
        self.assertEqual('No section matches the target(s)', str(ctx.exception))

    def test_split_multiline(self):
        self.assertEqual(['foo'], playbook.split_multiline('foo'))
        self.assertEqual(['a', 'b'], playbook.split_multiline('a\nb'))

        expected = [
            "L=docker ps -f status=running -f name='^project_name' -q | xargs -I{} --   "
            "docker inspect -f '{{.State.Pid}}' {} | tr '\\n' ,"
        ]
        actual = playbook.split_multiline(
            "L=docker ps -f status=running -f name='^project_name' -q | xargs -I{} -- \\\n"
            "  docker inspect -f '{{.State.Pid}}' {} | tr '\\n' ,"
        )
        self.assertEqual(expected, actual)

        self.assertEqual(['echo 12', 'echo 3'], playbook.split_multiline("echo 1\\\n2\necho 3"))
        self.assertEqual(['echo \\\\', 'echo /'], playbook.split_multiline('echo \\\\\necho /'))

        with self.assertRaises(ValueError) as ctx:
            playbook.split_multiline("echo 1\\")
        self.assertEqual('Line continuation end expected', str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            playbook.split_multiline("echo '")
        self.assertEqual('No closing quotation', str(ctx.exception))

    def test_play_plot_flag_args_aligned(self):
        self.playbook_file.truncate(0)
        self.playbook_file.seek(0)
        self.playbook_file.write(r'''
            [group1:plot]
            database_file: out.sqlite
            plot_file: rss.svg
            logarithmic: 1
            query_name: rss
            epsilon: 0.5
            moving_average_window: 10
            no_dots: 1
            relative_time: 1
        ''')
        self.playbook_file.flush()

        output_file = io.StringIO()
        play.run(
            playbook_file=self.playbook_file.name,
            output_file=output_file,
            list_sections=False,
            dry_run=True,
            target=['*'],
        )
        expected = {
            'after': None,
            'before': None,
            'custom_query_file_list': None,
            'custom_value_expr_list': None,
            'database_file': 'out.sqlite',
            'epsilon': 0.5,
            'formatter': None,
            'logarithmic': True,
            'moving_average_window': 10,
            'no_dots': True,
            'pid_list': None,
            'plot_file': 'rss.svg',
            'query_name_list': ['rss'],
            'relative_time': True,
            'share_y_axis': False,
            'style': None,
            'title': None,
        }
        self.assertEqual(expected, json.loads(output_file.getvalue()))

    def test_get_special_args(self):
        parser = cli.build_parser()

        expected = ['query', 'sql_query'], [], ['environment']
        self.assertEqual(expected, playbook.get_special_args(parser, 'query'))

        expected = ['query'], ['stop_without_result'], ['environment']
        self.assertEqual(expected, playbook.get_special_args(parser, 'record'))

        expected = (
            [],
            ['share_y_axis', 'logarithmic', 'no_dots', 'relative_time'],
            ['query_name', 'custom_query_file', 'custom_value_expr'],
        )
        self.assertEqual(expected, playbook.get_special_args(parser, 'plot'))

        expected = [], ['no_restart'], ['environment', 'query', 'command']
        self.assertEqual(expected, playbook.get_special_args(parser, 'watch'))


class TestExploreCommand(unittest.TestCase):

    def test_explore(self):
        with tempfile.NamedTemporaryFile() as tmpf:
            with zipfile.ZipFile(tmpf, 'w') as myzip:
                with myzip.open('index.html', 'w') as f:
                    f.write(b'<html/>')
                with myzip.open('inquiries.json', 'w') as f:
                    f.write(b'[]')

            with tempfile.TemporaryDirectory() as tmpd:
                os.environ['XDG_CACHE_HOME'] = tmpd
                with mock.patch('procpath.sqliteviz.serve_dir') as httpd:
                    with mock.patch('procpath.cmd.explore.webbrowser') as webb:
                        with self.assertLogs('procpath', 'INFO') as ctx:
                            explore.run(
                                bind='127.0.0.1',
                                port=1234,
                                reinstall=False,
                                open_in_browser=False,
                                build_url='file://' + tmpf.name,
                            )
                    httpd.assert_called_once_with('127.0.0.1', 1234, f'{tmpd}/procpath/sqliteviz')
                    self.assertEqual([], webb.method_calls)

                self.assertEqual(
                    ['index.html', 'inquiries.json'],
                    sorted(os.listdir(f'{tmpd}/procpath/sqliteviz')),
                )
                with open(f'{tmpd}/procpath/sqliteviz/index.html') as f:
                    self.assertEqual('<html/>', f.read())
                expected = json.dumps(sqliteviz.get_visualisation_bundle(), sort_keys=True)
                with open(f'{tmpd}/procpath/sqliteviz/inquiries.json') as f:
                    self.assertEqual(expected, f.read())

                self.assertEqual(2, len(ctx.records))
                self.assertEqual(
                    f'Downloading file://{tmpf.name} into {tmpd}/procpath/sqliteviz',
                    ctx.records[0].message,
                )
                self.assertEqual(
                    'Serving Sqliteviz at http://127.0.0.1:1234/', ctx.records[1].message
                )

                # Cannot be downloaded again
                tmpf.close()

                with mock.patch('procpath.sqliteviz.serve_dir') as httpd:
                    with mock.patch('procpath.cmd.explore.webbrowser') as webb:
                        with self.assertLogs('procpath', 'INFO') as ctx:
                            explore.run(
                                bind='',
                                port=8000,
                                reinstall=False,
                                open_in_browser=True,
                                build_url='file://' + tmpf.name,
                            )
                    httpd.assert_called_once_with('', 8000, f'{tmpd}/procpath/sqliteviz')
                    self.assertEqual([mock.call.open('http://localhost:8000/')], webb.method_calls)

                self.assertEqual(
                    ['index.html', 'inquiries.json'],
                    sorted(os.listdir(f'{tmpd}/procpath/sqliteviz')),
                )
                with open(f'{tmpd}/procpath/sqliteviz/index.html') as f:
                    self.assertEqual('<html/>', f.read())
                expected = json.dumps(sqliteviz.get_visualisation_bundle(), sort_keys=True)
                with open(f'{tmpd}/procpath/sqliteviz/inquiries.json') as f:
                    self.assertEqual(expected, f.read())

                self.assertEqual(2, len(ctx.records))
                self.assertEqual(
                    f'Serving existing Sqliteviz from {tmpd}/procpath/sqliteviz',
                    ctx.records[0].message,
                )
                self.assertEqual(
                    'Serving Sqliteviz at http://localhost:8000/', ctx.records[1].message
                )

    @classmethod
    def explore(cls, build_url, env):
        os.environ.update(env)
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                explore.run(
                    build_url=build_url,
                    open_in_browser=False,
                    bind='',
                    port=18000,
                    reinstall=False,
                )
        except KeyboardInterrupt:
            pass

    def test_explore_serve(self):
        with tempfile.NamedTemporaryFile() as tmpf:
            with zipfile.ZipFile(tmpf, 'w') as myzip, myzip.open('index.html', 'w') as f:
                f.write(b'<html/>')

            with tempfile.TemporaryDirectory() as tmpd:
                os.environ['XDG_CACHE_HOME'] = tmpd
                p = multiprocessing.Process(
                    target=self.explore, args=('file://' + tmpf.name, os.environ)
                )
                self.addCleanup(p.terminate)
                p.start()
                assert_wait_predicate(lambda: is_port_open('localhost', 18000))

                response = urllib.request.urlopen('http://localhost:18000/')
                self.assertEqual(b'<html/>', response.read())
                self.assertEqual('no-cache', response.headers['Cache-Control'])

                sqliteviz.symlink_database(tmpf.name, Path(tmpd) / 'procpath' / 'sqliteviz')
                response = urllib.request.urlopen('http://localhost:18000/db.sqlite')
                self.assertEqual(b'PK\x03\x04', response.read(4))
                self.assertEqual('no-store', response.headers['Cache-Control'])

                os.kill(p.pid, signal.SIGINT)
                p.join(1)  # join doesn't raise on timeout
                self.assertFalse(p.is_alive())

    def test_explore_preload_database(self):
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch('procpath.sqliteviz.serve_dir'))
            m = stack.enter_context(mock.patch('procpath.cmd.explore.webbrowser'))
            os.environ['XDG_CACHE_HOME'] = stack.enter_context(tempfile.TemporaryDirectory())
            tmpf = stack.enter_context(tempfile.NamedTemporaryFile())

            with zipfile.ZipFile(tmpf, 'w') as myzip, myzip.open('index.html', 'w') as f:
                f.write(b'<html/>')

            explore.run(
                bind='',
                port=18000,
                build_url=f'file://{tmpf.name}',
                reinstall=False,
                open_in_browser=True,
                database_file=tmpf.name,
            )

            m.open.assert_called_once_with(
                'http://localhost:18000/#/load?'
                'data_url=http%3A%2F%2Flocalhost%3A18000%2Fdb.sqlite&data_format=sqlite'
            )
            db_symlink = f'{os.environ["XDG_CACHE_HOME"]}/procpath/sqliteviz/db.sqlite'
            self.assertTrue(os.path.exists(db_symlink))
            self.assertTrue(os.path.islink(db_symlink))
            self.assertEqual(tmpf.name, os.path.realpath(db_symlink))

    def test_explore_preload_database_missing(self):
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch('procpath.sqliteviz.serve_dir'))
            m = stack.enter_context(mock.patch('procpath.cmd.explore.webbrowser'))
            os.environ['XDG_CACHE_HOME'] = stack.enter_context(tempfile.TemporaryDirectory())
            tmpf = stack.enter_context(tempfile.NamedTemporaryFile())

            with zipfile.ZipFile(tmpf, 'w') as myzip, myzip.open('index.html', 'w') as f:
                f.write(b'<html/>')

            with self.assertLogs('procpath', 'WARNING') as logctx:
                explore.run(
                    bind='',
                    port=18000,
                    build_url=f'file://{tmpf.name}',
                    reinstall=False,
                    open_in_browser=True,
                    database_file='/dev/nil',
                )
            self.assertEqual('Database file /dev/nil does not exist', logctx.records[0].message)
            self.assertEqual(1, len(logctx.records))

            m.open.assert_called_once_with('http://localhost:18000/')
            db_symlink = f'{os.environ["XDG_CACHE_HOME"]}/procpath/sqliteviz/db.sqlite'
            self.assertFalse(os.path.exists(db_symlink))

    def test_symlink_database(self):
        with contextlib.ExitStack() as stack:
            tmpd = Path(stack.enter_context(tempfile.TemporaryDirectory()))
            tmpd_nested = tmpd / 'nested'
            tmpd_nested.mkdir()
            tmpf = tmpd_nested / 'test.db'
            tmpf.touch()

            orig_cwd = os.getcwd()
            os.chdir(tmpd_nested)
            try:
                sqliteviz.symlink_database('test.db', tmpd)
            finally:
                os.chdir(orig_cwd)

            db_symlink = tmpd / 'db.sqlite'
            self.assertTrue(db_symlink.exists())
            self.assertTrue(db_symlink.is_symlink())
            self.assertEqual(tmpf, db_symlink.resolve())
