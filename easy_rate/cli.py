#!/usr/bin/env python
# encoding: utf-8

import asyncio
import configparser
import logging
import os
import sys
import traceback

from collections import OrderedDict
from functools import partial
from itertools import groupby
from operator import attrgetter

import aiohttp
import click
import tablib

from pandas import option_context
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.before import before_log


logging.basicConfig(
    # level=logging.DEBUG,
    level=logging.INFO,
    format='PID %(process)5s %(name)18s: %(message)s',
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), before=before_log(logger, logging.DEBUG))
async def get_json(url):
    conn = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url) as response:
            return await response.json()


async def fetch(semaphore, url):
    async with semaphore:
        logger.info('Working on {}'.format(url))
        try:
            r = await get_json(url)
        except:
            logger.error('Failed to fetch data from {}. Skipped.'.format(url))
            logger.debug(traceback.format_exc())
            return

        logger.info('Fetched data from {}'.format(url))
        return r


DEFAULT_STATUS_URL_TEMPLATE = 'http://{server}/status'


@click.command()
@click.option('-L', '--server-list', help='TBD')
@click.option('-v', '--verbose', count=True, help='TBD')
@click.option('-m', '--mode', help='TBD')
@click.option('-c', '--concurrent', type=int, help='TBD')
@click.option('--config-path', help='TBD')
def main(server_list, verbose, mode, concurrent, config_path):
    config = configparser.ConfigParser()
    optional_config_paths = [
        '.cli.conf',
        os.path.expanduser('~/.cli.conf'),
    ]
    if config_path:
        optional_config_paths.append(config_path)
    config.read(optional_config_paths)
    _concurrent = concurrent \
        or int(config.get('ARGUMENTS', 'concurrent', fallback='10'))
    status_url_template = config.get(
        'ARGUMENTS',
        'status_url_template',
        fallback=DEFAULT_STATUS_URL_TEMPLATE
    )
    mode = config.get(
        'ARGUMENTS',
        'mode',
        fallback='normal'
    )
    rate_format = config.get(
        'DISPLAY',
        'rate_format',
        fallback='{:.2%}'
    )
    keys = config.get(
        'RATE',
        'keys'
    )
    _keys = keys.split(',')

    denominator = config.get(
        'RATE',
        'denominator'
    )
    nominator = config.get(
        'RATE',
        'nominator'
    )
    header_name_dict = dict(config['DISPLAY HEADERS'])

    print('keys', _keys)
    print('denominator', denominator)
    print('nominator', nominator)
    print('headers', header_name_dict)
    print('rate_format', rate_format)
    print('mode', mode)
    print('config', config_path)
    print('concurrent', _concurrent)
    print('status_url_template', status_url_template)

    servers = [x.strip() for x in open(server_list)]

    print(servers)
    urls = [
        status_url_template.format(server=server)
        for server in servers
    ]
    print('Fetching status from {} urls ...'.format(len(urls)))
    semaphore = asyncio.Semaphore(_concurrent)
    fetch_under_control = partial(fetch, semaphore)
    coroutines = map(fetch_under_control, urls)
    tasks = [asyncio.ensure_future(coroutine) for coroutine in coroutines]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    status_list = [t.result() for t in tasks]

    schema = dict(config['SCHEMA'])
    statuses = [Entity(schema, x) for x in status_list if x]
    if not statuses:
        print('No available data to display.')
        return

    # Data
    grouped_status_dict = group_statuses(
        statuses,
        groupby_key=attrgetter(*_keys)
    )
    data = {
        ktuple: calculate_rate(_statuses, denominator, nominator)
        for ktuple, _statuses in grouped_status_dict.items()
    }

    _headers = _keys + ['result']
    headers = [header_name_dict.get(x, x) for x in _headers]
    print(headers)
    # View
    dataset = tablib.Dataset(
        headers=headers,
    )
    print(data)
    for ktuple in sorted(data.keys()):
        rate = data[ktuple]
        print(ktuple, rate)
        dataset.append(
            ktuple + (rate_format.format(rate),)
        )

    df = dataset.export('df')
    # Pretty table via pandas dataframe
    with option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)


class Entity(dict):

    def __init__(self, schema, data):
        self.schema = schema
        self.data = data
        super().__init__(data)

    def __getattr__(self, attr):
        return self.get_attribute(attr)

    def get_attribute(self, attr):
        dpath = self.schema.get(attr)
        if dpath:
            return get_value_by_dpath(self, dpath)


def get_value_by_dpath(dictionary, dpath):
    items = dpath.split('.')
    r = dictionary
    for item in items[1:]:
        r = r[item]

    return r


def group_statuses(statuses, groupby_key=None):
    r = {}
    statuses = sorted(statuses, key=groupby_key)
    for k, g in groupby(statuses, groupby_key):
        r[k] = list(g)
    return r


class Formula(object):

    @staticmethod
    def calculate_rate(statuses, denominator, nominator):
        _denominator = sum(getattr(x, denominator) for x in statuses)
        _nominator = sum(getattr(x, nominator) for x in statuses)
        return _nominator / _denominator


if __name__ == '__main__':
    main()
