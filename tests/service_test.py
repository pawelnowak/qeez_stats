# -*- coding: utf-8 -*-

'''qeez_stat.service test module
'''

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

import sys
from binascii import crc32
from functools import partial

import pytest
from mockredis import mock_strict_redis_client

from qeez_stats import service
from qeez_stats.utils import to_bytes

from .config import CFG


def _get_redis():
    '''Returns fake StrictRedis client instance
    '''
    return mock_strict_redis_client()


@pytest.fixture
def client(request):
    service.APP.config['TESTING'] = True
    flask_cli = service.APP.test_client()
    with service.APP.app_context():
        service.get_redis = _get_redis
    return flask_cli


def test_get_redis():
    with service.APP.app_context():
        service.get_redis(CFG['STAT_REDIS'])


def test_not_found(client):
    resp = client.get('/')
    assert resp.data == b'{"error": true, "status": 404}'


def test_method_not_allowed(client):
    resp = client.get('/stats/mput/123')
    assert resp.data == b'{"error": true, "status": 405}'


def test_bad_request(client):
    resp = client.put('/stats/mput/123')
    assert resp.data == b'{"error": true, "status": 400}'


def test_internal_server_error(client):
    with service.APP.app_context():
        resp = service.internal_server_error(None)
        assert resp.data == b'{"error": true, "status": 500}'


def test_stats_put(client):
    _data = b'["a", "b"]'
    checksum = '%08x' % crc32(_data)
    resp = client.put('/stats/put/test_123', data=_data,
                      content_type='application/json')
    assert resp.data == \
        to_bytes('{"checksum": "%s", "error": false}' % checksum)


def test_stats_mput(client):
    _data = b'[["c", "d"],["e", "f"]]'
    checksum = '%08x' % crc32(_data)
    resp = client.put('/stats/mput/test_123', data=_data,
                      content_type='application/json')
    assert resp.data == \
        to_bytes('{"checksum": "%s", "error": false}' % checksum)
