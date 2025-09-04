import logging
import os
import shutil
import threading
import webbrowser
from functools import partial
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

from .. import sqliteviz


__all__ = 'run',

logger = logging.getLogger('procpath')


def run(
    bind: str,
    port: int,
    open_in_browser: bool,
    reinstall: bool,
    build_url: str,
    database_file: Optional[str] = None,
):
    user_cache_dir = Path(os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache')))
    sqliteviz_dir = user_cache_dir / 'procpath' / 'sqliteviz'
    if not sqliteviz_dir.exists() or reinstall:
        shutil.rmtree(sqliteviz_dir, ignore_errors=True)
        sqliteviz_dir.mkdir(parents=True)
        logger.info('Downloading %s into %s', build_url, sqliteviz_dir)
        sqliteviz.install_sqliteviz(build_url, sqliteviz_dir)
    else:
        logger.info('Serving existing Sqliteviz from %s', sqliteviz_dir)

    url = 'http://{host}:{port}/'.format(port=port, host=bind or 'localhost')
    logger.info('Serving Sqliteviz at %s', url)

    server_fn = partial(sqliteviz.serve_dir, bind, port, str(sqliteviz_dir))
    server = threading.Thread(target=server_fn, daemon=True)
    server.start()

    if database_file:
        try:
            sym_path = sqliteviz.symlink_database(database_file, sqliteviz_dir)
        except FileNotFoundError:
            logger.warning('Database file %s does not exist', database_file)
        else:
            params = urlencode({'data_url': url + sym_path.name, 'data_format': 'sqlite'})
            url += f'#/load?{params}'

    if open_in_browser:
        webbrowser.open(url)

    server.join()
