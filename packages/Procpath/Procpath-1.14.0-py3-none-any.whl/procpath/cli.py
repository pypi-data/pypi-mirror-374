import argparse
import logging
import shutil
import sys
from datetime import datetime, timezone

from . import __version__, cmd, procfile, procret


logger = logging.getLogger(__package__)


def add_query_parser(parent):
    parser = parent.add_parser('query', formatter_class=HelpFormatter, description='''
        Execute given JSONPath and/or SQL query against process tree producing JSON or
        separator-delimited values.
    ''')
    parser.add_argument(
        'query',
        nargs='?',
        help='''
            JSONPath expression, for example this query returns
            PIDs for process subtree including the given root's:

            $..children[?(@.stat.pid == 2610)]..pid
        '''
    )
    parser.add_argument(
        'sql_query',
        nargs='?',
        help='''
            SQL query to further filter and/or aggregate collected
            process nodes. Note that if JSONPath query is present it must
            return full nodes, e.g. $..children[?(@.stat.pid == 2610)].
            For example this query returns total RSS of the processes:

            SELECT SUM(stat_rss) / 1024.0 * 4 total FROM record
        '''
    )
    arguments = parser.add_argument_group('named arguments')
    arguments.add_argument(
        '-f', '--procfile-list',
        default='stat, cmdline',
        type=lambda s: list(map(str.strip, s.split(','))),
        help=f'''
            Procfs files to read per PID.  Comma-separated list. By default: %(default)s.
            Available: {', '.join(procfile.registry.keys())}.
        ''',
    )
    arguments.add_argument(
        '-d', '--delimiter',
        help='Join query result using given delimiter',
    )
    arguments.add_argument(
        '-i', '--indent',
        type=int,
        help='Format result JSON using given indent number',
    )
    arguments.add_argument(
        '-e', '--environment',
        action='append',
        type=lambda s: s.split('=', 1),
        help='''
            Commands to evaluate in the shell and template the queries, like VAR=date.
            Multiple occurrence is possible.
        ''',
    )
    arguments.add_argument(
        '--procfs',
        default='/proc',
        type=lambda s: s.rstrip('/'),
        help='Procfs mount path. By default: %(default)s.',
    )
    arguments.add_argument(
        '--procfs-target',
        default='process',
        type={'process': 'process', 'thread': 'thread'}.__getitem__,
        help='Procfs target object. By default: %(default)s. Available: process, thread.',
    )
    parser.set_defaults(output_file=sys.stdout)


def add_record_parser(parent):
    parser = parent.add_parser('record', formatter_class=HelpFormatter, description='''
        Record the nodes of process tree matching given JSONPath query into a SQLite
        database in given intervals.
    ''')
    parser.add_argument(
        'query',
        nargs='?',
        help='''
            JSONPath expression, for example this query returns
            a node including its subtree for given PID:

            $..children[?(@.stat.pid == 2610)]
        '''
    )
    arguments = parser.add_argument_group('named arguments')
    arguments.add_argument(
        '-f', '--procfile-list',
        default='stat, cmdline',
        type=lambda s: list(map(str.strip, s.split(','))),
        help=f'''
            Procfs files to read per PID.  Comma-separated list. By default: %(default)s.
            Available: {', '.join(procfile.registry.keys())}.
        ''',
    )
    arguments.add_argument(
        '-e', '--environment',
        action='append',
        type=lambda s: s.split('=', 1),
        help='''
            Commands to evaluate in the shell and template the query, like VAR=date.
            Multiple occurrence is possible.
        ''',
    )
    arguments.add_argument(
        '-d', '--database-file',
        required=True,
        help='Path to the recording database file',
    )
    arguments.add_argument(
        '-p', '--pid-list',
        help='''
            Keep only branches with given PIDs in the tree before running query
            against it. Comma-separated list. It can include environment
            variables.
        ''',
    )
    arguments.add_argument(
        '--procfs',
        default='/proc',
        type=lambda s: s.rstrip('/'),
        help='Procfs mount path. By default: %(default)s.',
    )
    arguments.add_argument(
        '--procfs-target',
        default='process',
        type={'process': 'process', 'thread': 'thread'}.__getitem__,
        help='Procfs target object. By default: %(default)s. Available: process, thread.',
    )
    loop_control = parser.add_argument_group('loop control arguments')
    loop_control.add_argument(
        '-i', '--interval',
        type=float,
        default='10',
        help='Interval in second between each recording, %(default)s by default.',
    )
    loop_control.add_argument(
        '-r', '--recnum',
        type=int,
        help='''
            Number of recordings to take at --interval seconds apart.
            If not specified, recordings will be taken indefinitely.
        ''',
    )
    loop_control.add_argument(
        '-v', '--reevalnum',
        type=int,
        help='''
            Number of recordings after which environment must be re-evaluate.
            It's useful when you expect it to change while recordings are
            taken.
        ''',
    )
    loop_control.add_argument(
        '--stop-without-result',
        action='store_true',
        help='''
            Prematurely stop recording when target processes can no longer be found,
            or otherwise when the query and/or PID filter don't yield a result.
        ''',
    )


def add_plot_parser(parent):
    parser = parent.add_parser('plot', formatter_class=HelpFormatter, description='''
        Plot previously recorded SQLite database using predefined or custom SQL
        expression or query.
    ''')
    arguments = parser.add_argument_group('named arguments')
    arguments.add_argument(
        '-d', '--database-file',
        required=True,
        help='Path to the database file to read from.',
    )
    arguments.add_argument(
        '-f', '--plot-file',
        default='plot.svg',
        help='Path to the output SVG file, plot.svg by default.',
    )
    query_control = parser.add_argument_group('query control arguments')
    query_control.add_argument(
        '-q', '--query-name',
        action='append',
        dest='query_name_list',
        help=f'''
            Built-in query name. Available: {", ".join(procret.registry.keys())}.
            Without --share-y-axis it can occur once or twice (including other
            query-contributing options). In the latter case, the plot has two
            Y axes.
        ''',
    )
    query_control.add_argument(
        '--custom-query-file',
        action='append',
        dest='custom_query_file_list',
        help='''
            Use custom SQL query in given file.
            The result-set must have 3 columns: ts, pid, value. See procpath.procret.
            Without --share-y-axis it can occur once or twice (including other
            query-contributing options). In the latter case, the plot has two Y axes.
        ''',
    )
    query_control.add_argument(
        '--custom-value-expr',
        action='append',
        dest='custom_value_expr_list',
        help='''
            Use custom SELECT expression to plot as the value.
            Without --share-y-axis it can occur once or twice (including other
            query-contributing options). In the latter case, the plot has two Y axes.
        ''',
    )
    filter_control = parser.add_argument_group('filter control arguments')
    filter_control.add_argument(
        '-a', '--after',
        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc),
        help='Include only points after given UTC date, like 2000-01-01T00:00:00.',
    )
    filter_control.add_argument(
        '-b', '--before',
        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc),
        help='Include only points before given UTC date, like 2000-01-01T00:00:00.',
    )
    filter_control.add_argument(
        '-p', '--pid-list',
        type=lambda s: list(map(int, s.split(','))),
        help='Include only given PIDs. Comma-separated list.',
    )
    plot_control = parser.add_argument_group('plot control arguments')
    plot_control.add_argument(
        '-s', '--share-y-axis',
        action='store_true',
        help='Use the same Y axis for two or more queries.',
    )
    plot_control.add_argument(
        '-l', '--logarithmic',
        action='store_true',
        help='Plot using logarithmic scale.',
    )
    plot_control.add_argument(
        '--style',
        help='Plot using given pygal.style, like LightGreenStyle.',
    )
    plot_control.add_argument(
        '--formatter',
        help='Force given pygal.formatter, like integer.',
    )
    plot_control.add_argument(
        '--title',
        help='Override plot title.',
    )
    plot_control.add_argument(
        '--no-dots',
        action='store_true',
        help='Do not add hover dots to the lines.',
    )
    plot_control.add_argument(
        '--relative-time',
        action='store_true',
        help='Display X axis as time deltas since the first measurement.',
    )
    postprocessing_control = parser.add_argument_group('post-processing control arguments')
    postprocessing_control.add_argument(
        '-e', '--epsilon',
        type=float,
        help='Reduce points using Ramer-Douglas-Peucker algorithm and given ε.',
    )
    postprocessing_control.add_argument(
        '-w', '--moving-average-window',
        type=int,
        help='Smooth the lines using moving average.',
    )


def add_watch_parser(parent):
    parser = parent.add_parser('watch', formatter_class=HelpFormatter, description='''
        Execute given commands in given intervals. It has similar purpose to
        procps watch, but allows JSONPath queries to the process tree to choose
        processes of interest.

        In each next process' environment exist variables WSP1, WSP2 and so on
        containing PIDs of previous shells that run watched processes.
    ''')
    cmd_control = parser.add_argument_group('command control arguments')
    cmd_control.add_argument(
        '-e', '--environment',
        action='append',
        type=lambda s: s.split('=', 1),
        help='''
            Commands to evaluate in the shell, like
            C1='docker inspect -f "{{.State.Pid}}" nginx' or D='date +%%s'.
            Multiple occurrence is possible.
        ''',
    )
    cmd_control.add_argument(
        '-q', '--query',
        action='append',
        dest='query_list',
        type=lambda s: s.split('=', 1),
        help='''
            JSONPath expressions that typically evaluate into a list of PIDs.
            The environment defined with -e can be used like
            L1='$..children[?(@.stat.pid == $C1)]..pid'.
            Multiple occurrence is possible.
        ''',
    )
    cmd_control.add_argument(
        '-c', '--command',
        required=True,
        dest='command_list',
        action='append',
        help='''
            Target command to "watch" in the shell. The environment and query
            results can be used like 'smemstat -o smemstat-$D.json -p $L1'.
            Query result lists are joined with comma. Multiple occurrence is
            possible.
        ''',
    )
    loop_control = parser.add_argument_group('loop control arguments')
    loop_control.add_argument(
        '-i', '--interval',
        required=True,
        type=float,
        help='''
            Interval in second after which to re-evaluate the environment and the
            queries, and re-run each command if one has finished.
        ''',
    )
    loop_control.add_argument(
        '-r', '--repeat',
        type=int,
        help='Fixed number of iterations instead of infinite watch.',
    )
    loop_control.add_argument(
        '--no-restart',
        action='store_true',
        help='''
            Do not restart watched processes when they stop, and stop watching once no
            watched process is running.
        ''',
    )
    loop_control.add_argument(
        '-s', '--stop-signal',
        default='SIGINT',
        help='Signal to send to the spawned processes on watch stop. By default: %(default)s.',
    )
    loop_control.add_argument(
        '--kill-after',
        type=float,
        default='10',
        help='''
            Kill all remaining descendant processes after this many seconds after the stop signal
            has been sent. By default: %(default)s.',
        ''',
    )
    arguments = parser.add_argument_group('named arguments')
    arguments.add_argument(
        '-f', '--procfile-list',
        default='stat, cmdline',
        type=lambda s: list(map(str.strip, s.split(','))),
        help=f'''
            Procfs files to read per PID.  Comma-separated list. By default: %(default)s.
            Available: {', '.join(procfile.registry.keys())}.
        ''',
    )
    arguments.add_argument(
        '--procfs',
        default='/proc',
        type=lambda s: s.rstrip('/'),
        help='Procfs mount path. By default: %(default)s.',
    )
    arguments.add_argument(
        '--procfs-target',
        default='process',
        type={'process': 'process', 'thread': 'thread'}.__getitem__,
        help='Procfs target object. By default: %(default)s. Available: process, thread.',
    )


def add_play_parser(parent):
    parser = parent.add_parser('play', formatter_class=HelpFormatter, description='''
        Play one or more sections from given playbook.
    ''')
    parser.add_argument(
        'target',
        nargs='+',
        help='''Name or glob-expression of the section from the playbook.'''
    )
    arguments = parser.add_argument_group('named arguments')
    arguments.add_argument(
        '-f', '--playbook-file',
        required=True,
        help='Path to the playbook to play.',
    )
    arguments.add_argument(
        '-l', '--list-sections',
        action='store_true',
        help='List matching sections in the playbook.',
    )
    arguments.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Collect and print target sections.',
    )
    arguments.add_argument(
        '-o', '--option',
        action='append',
        dest='option_override_list',
        type=lambda s: s.split('=', 1),
        help='''
            A key-value pair to override the option in the playbook, like
            database_file=db.sqlite. Multiple occurrence is possible.
        ''',
    )
    parser.set_defaults(output_file=sys.stdout)


def add_explore_parser(parent):
    parser = parent.add_parser('explore', formatter_class=HelpFormatter, description='''
        Serve a Sqliteviz build from a local web-server for exploratory or
        ad-hoc visualisation.

        On first invocation Sqliteviz is downloaded and saved locally for
        later offline use. Procpath exports pre-defined queries into Sqliteviz.
    ''')
    arguments = parser.add_argument_group('named arguments')
    arguments.add_argument(
        '--reinstall',
        action='store_true',
        help='Remove local copy and fetch Sqliteviz build again.',
    )
    arguments.add_argument(
        '--build-url',
        default='https://github.com/lana-k/sqliteviz/releases/latest/download/dist.zip',
        help='Sqliteviz build URL. By default: %(default)s.',
    )
    arguments.add_argument(
        '-b', '--bind',
        default='',
        metavar='ADDRESS',
        help='Specify alternate bind address. By default: all interfaces.',
    )
    arguments.add_argument(
        '-p', '--port',
        default=8000,
        type=int,
        help='Specify alternate port. By default: %(default)s.',
    )
    arguments.add_argument(
        '--no-browser',
        dest='open_in_browser',
        action='store_false',
        help='Do not open a browser after startup.',
    )
    arguments.add_argument(
        '-d', '--database-file',
        help='Database file to pre-load into Sqliteviz.',
    )


class HelpFormatter(argparse.HelpFormatter):

    def __init__(self, prog, indent_increment=2, max_help_position=24, width=None):
        if not width:
            width = min(100, shutil.get_terminal_size((80, 20)).columns)

        super().__init__(prog, indent_increment, max_help_position, width)

    def _format_usage(self, usage, actions, groups, prefix):
        banner = (
            r'     ___   ___   ___   __    ___    __   _____  _   ''\n'
            r'    | |_) | |_) / / \ / /`  | |_)  / /\   | |  | |_|''\n'
            r'    |_|   |_| \ \_\_/ \_\_, |_|   /_/--\  |_|  |_| |''\n\n'
            r'                   a process tree analysis workbench''\n'
        )
        result = super()._format_usage(usage, actions, groups, prefix)
        if actions:
            result = '{}\n{}'.format(banner, result)

        return result

    def _get_default_metavar_for_optional(self, action):
        return action.option_strings[-1].strip('-').upper()


def build_parser(*, cls=argparse.ArgumentParser):
    parser = cls(formatter_class=HelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '--logging-level',
        help='Logging level. By default: %(default)s.',
        default='INFO',
    )

    cmd_funcs = [
        add_query_parser,
        add_record_parser,
        add_plot_parser,
        add_explore_parser,
        add_watch_parser,
        add_play_parser,
    ]
    parent = parser.add_subparsers(dest='command', required=True)
    [fn(parent) for fn in cmd_funcs]

    return parser


def is_not_jsonpyth_debug_noise(record: logging.LogRecord) -> bool:
    is_jsonpyth_debug_noise = (
        record.module == 'jsonpyth'
        and record.levelno == logging.DEBUG
        and record.name == 'root'
    )
    return not is_jsonpyth_debug_noise


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-7s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logging.getLogger().addFilter(is_not_jsonpyth_debug_noise)

    kwargs = vars(build_parser().parse_args())
    logging.root.setLevel(kwargs.pop('logging_level'))
    try:
        cmd.get_command(kwargs.pop('command'))(**kwargs)
    except KeyboardInterrupt:
        pass
    except cmd.CommandError as ex:
        logger.error(ex)
        sys.exit(1)
