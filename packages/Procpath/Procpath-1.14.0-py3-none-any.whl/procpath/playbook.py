import argparse
import configparser
import fnmatch
import itertools
import shlex
from functools import partial
from typing import Optional

from . import cli


__all__ = 'Playbook', 'PlaybookError'


def read(
    command_name: str,
    section: configparser.SectionProxy,
    overrides: dict,
) -> dict:
    """
    Read a playbook section.

    Parent sections are taken into account. Result values are taken
    reusing the CLI.
    """

    parser = cli.build_parser(cls=RaisingArgumentParser)
    positional_args, flag_args, multivalue_args = get_special_args(parser, command_name)
    special_args = {*positional_args, *flag_args, *multivalue_args}

    cmd = [command_name]
    getarg = lambda k: '--{}'.format(k.replace('_', '-'))
    section_chain = SectionProxyChain.fromsection(section, overrides=overrides)
    for n, v in section_chain.items():
        if n not in special_args:
            cmd.extend((getarg(n), v))

    for n in flag_args:
        value = [b for b in section_chain.getboolean(n) if b is not None]
        if value and value[0]:
            cmd.append(getarg(n))

    for n in multivalue_args:
        # Lines are retrieved traversing the chain bottom-up, but
        # should be interpreted in top-down order
        for line in itertools.chain(*reversed(section_chain.getlines(n, fallback=[]))):
            cmd.extend((getarg(n), line))

    for n in positional_args:
        cmd.append(section_chain.get(n, ''))

    result = vars(parser.parse_args(cmd))
    result.pop('logging_level')
    return result


def get_section_value_key(a: argparse.Action) -> str:
    if a.option_strings:
        return a.option_strings[-1].strip('-').replace('-', '_')
    else:
        return a.dest


def get_special_args(parser: argparse.ArgumentParser, section: str) -> tuple:
    subparser = parser._get_positional_actions()[0].choices[section]

    positional = list(map(get_section_value_key, subparser._get_positional_actions()))
    flag = [
        get_section_value_key(a)
        for a in subparser._get_optional_actions()
        if isinstance(a, (argparse._StoreTrueAction, argparse._StoreFalseAction))
    ]
    multivalue = [
        get_section_value_key(a)
        for a in subparser._get_optional_actions()
        if isinstance(a, argparse._AppendAction)
    ]
    return positional, flag, multivalue


def split_multiline(s: str) -> list:
    result = []
    linebuf = []
    for line in s.splitlines():
        if not line:
            continue

        try:
            shlex.split(line)
        except ValueError as ex:
            if ex.args[0] != 'No escaped character':
                raise
            to_be_continued = True
        else:
            to_be_continued = False

        if to_be_continued:
            linebuf.append(line[:-1])
        elif linebuf:
            linebuf.append(line)
            result.append(''.join(linebuf))
            linebuf.clear()
        else:
            result.append(line)

    if linebuf:
        raise ValueError('Line continuation end expected')

    return result


class SectionProxyChain:
    """
    ``configparser.SectionProxy`` chain.

    The purpose of this class is to provide option inheritance. For
    ``items`` and ``get`` the first found key in the chain wins.
    Converters, like ``getint``, return all the value across the chain.
    """

    _sections: list

    _unset = object()

    def __init__(self, *sections):
        self._sections = list(sections)

    def __getattr__(self, name):
        def getall(*args, **kwargs):
            return [getattr(section, name)(*args, **kwargs) for section in self._sections]
        return getall

    def items(self):
        visited = set(['extends'])  # "extends" is a meta-key hence it's skipped
        for k in itertools.chain(*self._sections):
            if k not in visited:
                yield k, self.get(k)
                visited.add(k)

    def get(self, key, default=_unset):
        for section in self._sections:
            if key in section:
                return section[key]
        else:
            return default if default is not self._unset else None

    @staticmethod
    def _c3_merge(seqs) -> list:
        """
        Do C3 linearisation merge [1]_, on list of object lists.

        .. [1] https://www.python.org/download/releases/2.3/mro/
        """

        result = []
        while True:
            nonemptyseqs = [seq for seq in seqs if seq]
            if not nonemptyseqs:
                return result

            for seq in nonemptyseqs:  # find merge candidates among seq heads
                candidate = seq[0]
                nothead = [s for s in nonemptyseqs if candidate in s[1:]]
                if nothead:
                    candidate = None  # reject candidate
                else:
                    break

            if not candidate:
                raise ValueError('Inconsistent hierarchy')
            result.append(candidate)

            for seq in nonemptyseqs:  # remove candidate
                if seq[0] == candidate:
                    seq.pop(0)

    @classmethod
    def _get_mro(cls, section: configparser.SectionProxy) -> list:
        parent_sections = [section.parser[n] for n in section.getlines('extends', fallback=[])]
        return cls._c3_merge(
            [[section]]
            + list(map(cls._get_mro, parent_sections))
            + [parent_sections]
        )

    @classmethod
    def fromsection(cls, section: configparser.SectionProxy, *, overrides: Optional[dict] = None):
        """
        Create section proxy chain object.

        The chain has the following precedence:

            - command-line overrides as a section
            - given ``section``
            - parent sections

        """

        parent_sections = cls._get_mro(section)[1:]

        # Default converters (getint, getboolean, etc) are None
        converters = {
            n: fn
            for n, fn in section.parser.converters.items()  # type: ignore[attribute-error]
            if fn is not None
        }
        override_parser = configparser.RawConfigParser(
            converters=converters, default_section='overrides', defaults=overrides
        )
        override_section = override_parser['overrides']

        return cls(override_section, section, *parent_sections)


class PlaybookError(Exception):
    """Generic playbook error."""


class RaisingArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        parts = message.rsplit(':', 1)
        if len(parts) == 2:
            message = '{}: {}'.format(parts[0], parts[1].rsplit('--', 1)[-1]).strip()

        raise PlaybookError(f'Invalid section: {message}')


class Playbook:

    _parser = None
    _overrides = None

    _command_section_readers = {
        'query': partial(read, 'query'),
        'record': partial(read, 'record'),
        'plot': partial(read, 'plot'),
        'watch': partial(read, 'watch'),
    }

    def __init__(self, fp, overrides: dict):
        self._overrides = overrides

        self._parser = configparser.RawConfigParser(  # type: ignore[wrong-arg-types]
            default_section=None,
            comment_prefixes=('#',),
            delimiters=(':',),
            converters={'lines': split_multiline},
        )
        try:
            self._parser.read_file(fp)
        except configparser.Error as ex:
            raise PlaybookError(str(ex)) from ex

    def _get_command_name(self, section_name):
        return section_name.rsplit(':', 1)[-1]

    def get_command_sections(self, patterns: list):
        for pattern in patterns:
            for section_name in fnmatch.filter(filter(bool, self._parser), pattern):
                if self._get_command_name(section_name) in self._command_section_readers:
                    yield section_name

    def get_command(self, section_name) -> dict:
        command_name = self._get_command_name(section_name)
        section = self._parser[section_name]
        reader_fn = self._command_section_readers[command_name]

        return reader_fn(section, self._overrides)
