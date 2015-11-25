# -*- coding: utf-8 -*-

'''Qeez statistics queue module

* queue monitors:
$ rq-dashboard --redis_url=unix:///tmp/redis.sock?db=1 \
    --bind=127.0.0.1 --port=9181 --interval=5000
or
$ rqinfo --url unix:///tmp/redis.sock?db=1

* queue worker:
$ rqworker --url unix:///tmp/redis.sock?db=1 --name my-worker-nr-x --verbose
'''

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    with_statement,
)

from rq import Queue

from qeez_stats.config import CFG
from qeez_stats.stats import STATS_MAP, stat_collector
from qeez_stats.utils import get_redis, to_str


COLL_ID_FMT = 'stat:%s'
STAT_ID_FMT = 'stat:%s:%s'


def enqueue_stat_calc(stat, qeez_token, redis_conn=None):
    '''Enqueues stat for calc
    '''
    if stat not in STATS_MAP:
        return
    if redis_conn is None:
        redis_conn = get_redis(CFG['QUEUE_REDIS'])
    stat_token = STAT_ID_FMT % (stat, qeez_token)
    queue = Queue(connection=redis_conn)
    stat_append = queue.enqueue_call(
        func=stat_collector, args=(stat, stat_token), timeout=30, result_ttl=-1,
        ttl=-1, job_id=COLL_ID_FMT % stat)
    _ = stat_append.id
    return queue.enqueue_call(
        func=STATS_MAP[stat][0], args=(qeez_token,), timeout=30, result_ttl=-1,
        ttl=-1, job_id=stat_token, depends_on=stat_append)


def pull_stat_res(stat, qeez_token, redis_conn=None):
    '''Pulls one stat's result
    '''
    if stat not in STATS_MAP:
        return
    if redis_conn is None:
        redis_conn = get_redis(CFG['QUEUE_REDIS'])
    queue = Queue(connection=redis_conn)
    job = queue.fetch_job(STAT_ID_FMT % (stat, qeez_token))
    res = None
    if job is not None:
        res = job.result
    if res is not None:
        job.ttl = job.result_ttl = 24 * 3600
        job.save()
    return res


def pull_all_stat_res(stat, redis_conn=None):
    '''Pulls all stat results
    '''
    if stat not in STATS_MAP:
        return
    if redis_conn is None:
        redis_conn = get_redis(CFG['QUEUE_REDIS'])
    queue = Queue(connection=redis_conn)
    job = queue.fetch_job(COLL_ID_FMT % stat)
    res = None
    if job is None:
        return
    res = job.result
    if res is None:
        return

    out = []
    for stat_token in res:
        _job = queue.fetch_job(to_str(stat_token))
        _res = None
        if _job is not None:
            _res = _job.result
        if _res is not None:
            out.extend(_res)

    return out
