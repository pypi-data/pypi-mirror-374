import json
import logging
import os.path
import platform
import resource
import subprocess
from typing import Dict, List, Tuple

from . import __version__


__all__ = 'evaluate', 'get_meta'

logger = logging.getLogger(__package__)


def evaluate(var_cmd_list: List[Tuple[str, str]]) -> Dict[str, str]:
    """Evaluate given 2-tuple named list of shell commands."""

    script = []
    var_set = set()
    for var_name, command in var_cmd_list:
        var_set.add(var_name)
        script.append(f'{var_name}=$({command})')
        script.append(f'export {var_name}')

    script.append('env')
    env = subprocess.check_output('\n'.join(script), shell=True, encoding='utf-8')

    result = {}
    for line in env.splitlines():
        k, v = line.split('=', 1)
        if k in var_set:
            result[k] = v
            if not v:
                logger.warning('Variable %s evaluated empty', k)
            if len(result) == len(var_set):
                break

    return result


def get_meta(procfile_list: List[str], procfs: str, procfs_target: str) -> Dict[str, object]:
    """Get machine and recording metadata."""

    return {
        'platform_node': platform.node(),
        'platform_platform': platform.platform(),
        'page_size': resource.getpagesize(),
        'clock_ticks': os.sysconf('SC_CLK_TCK'),
        'physical_pages': os.sysconf('SC_PHYS_PAGES'),
        'cpu_count': os.cpu_count(),
        'procfile_list': json.dumps(procfile_list),
        'procpath_version': __version__,
        'procfs_path': os.path.abspath(procfs),
        'procfs_target': procfs_target,
    }
