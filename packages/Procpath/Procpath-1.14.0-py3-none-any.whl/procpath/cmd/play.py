import json
import logging
from typing import Optional

from .. import playbook
from . import CommandError, get_command


__all__ = 'run',

logger = logging.getLogger('procpath')


def run(
    playbook_file: str,
    target: list,
    list_sections: bool,
    dry_run: bool,
    output_file,
    option_override_list: Optional[list] = None,
):
    try:
        with open(playbook_file) as f:
            book = playbook.Playbook(f, dict(option_override_list or {}))

        if list_sections:
            output_file.write('\n'.join(book.get_command_sections(target)) + '\n')
            return

        section_names = list(book.get_command_sections(target))
        if not section_names:
            raise CommandError('No section matches the target(s)')

        for section_name in section_names:
            logger.info('Executing section %s', section_name)

            command_kwargs = book.get_command(section_name)
            if 'output_file' in command_kwargs:
                command_kwargs['output_file'] = output_file

            command_fn = get_command(command_kwargs.pop('command'))
            if not dry_run:
                command_fn(**command_kwargs)
            else:
                command_kwargs.pop('output_file', None)
                output = json.dumps(command_kwargs, indent=2, sort_keys=True, ensure_ascii=False)
                output_file.write(output + '\n')

    except playbook.PlaybookError as ex:
        raise CommandError(str(ex)) from ex
