#!/usr/bin/env python
# encoding: utf-8

import logging

import click

from pandas import option_context

from easy_rate.config import Config
from easy_rate.log import logger
from easy_rate.view import ReportView
from easy_rate.model import Entity


@click.command()
@click.option('-L', '--server-list', help='TBD')
@click.option('-v', '--verbose', count=True, help='TBD')
@click.option('-m', '--mode', help='TBD')
@click.option('-c', '--concurrent', type=int, help='TBD')
@click.option('--config-path', help='TBD')
def main(server_list, verbose, mode, concurrent, config_path):
    config = Config('easy_rate')
    config.read(config_path)

    _concurrent = concurrent or config.concurrent
    status_url_template = config.status_url_template
    mode = config.mode
    rate_format = config.rate_format
    _keys = config.keys
    denominator = config.denominator
    nominator = config.nominator
    header_name_dict = config.header_name_dict
    schema = config.schema

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

    urls = [
        status_url_template.format(server=server)
        for server in servers
    ]
    print('Fetching status from {} urls ...'.format(len(urls)))
    statuses = Entity.get_objs_by_urls(urls, schema, _concurrent)
    if not statuses:
        print('No available data to display.')
        return

    _headers = _keys + ['result']
    headers = [header_name_dict.get(x, x) for x in _headers]

    report = ReportView(statuses)
    data = report.get_data(_keys, denominator, nominator)
    dataset = report.get_dataset(data, headers, rate_format)
    df = dataset.export('df')
    # Pretty table via pandas dataframe
    with option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)


if __name__ == '__main__':
    main()
