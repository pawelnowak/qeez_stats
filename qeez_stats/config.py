# -*- coding: utf-8 -*-

'''Qeez statistics config module
'''

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import os

try:
    from raven import Client
    USE_RAVEN = True
except ImportError:
    USE_RAVEN = False


AUTHS_DIR = os.environ.get('AUTHS_DIR', '.')
os.sys.path.append(AUTHS_DIR)

try:
    from auth_settings import (
        RAVEN_DSN,
    )
except ImportError:
    RAVEN_DSN = None

REDIS_HOST, REDIS_PORT = os.environ.get('REDIS_ADDRESS', '127.0.0.1:6379').split(':')

CFG = dict(
    DEBUG=False,
    HOST='127.0.0.1',
    PORT=9100,
    JSONIFY_PRETTYPRINT_REGULAR=False,
    STAT_REDIS={
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 0,
    },
    QUEUE_REDIS={
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 1,
    },
    SAVE_REDIS={
        'HOST': REDIS_HOST,
        'PORT': REDIS_PORT,
        'DB': 2,
    },
    ENV_PREPARE_FN='qeez.utils.models.prepare_env',
    STAT_SAVE_FN='qeez.api.models.stat_data_save',
    RAVEN_CLI=Client(RAVEN_DSN) if USE_RAVEN and RAVEN_DSN else None,
)
