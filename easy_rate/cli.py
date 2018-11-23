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
@click.option(
    '-m', '--mode',
    type=click.Choice(['csv', 'json', 'yaml', 'xls', 'df']),
    default='df',
    help='TBD'
)
@click.option('-o', '--output', default='stdout', help='TBD')
@click.option('-c', '--concurrent', type=int, help='TBD')
@click.option('--config-path', help='TBD')
def main(server_list, verbose, mode, concurrent, config_path, output):
    print('config_path', config_path)
    config = Config('easy_rate')
    config.read(config_path)

    concurrent = concurrent or config.concurrent
    mode = mode or config.mode
    print('mode', mode)
    print('concurrent', concurrent)
    print('output', output)

    servers = [x.strip() for x in open(server_list)]
    urls = [
        config.status_url_template.format(server=server)
        for server in servers
    ]
    print('Fetching status from {} urls ...'.format(len(urls)))
    statuses = Entity.get_objs_by_urls(urls, config.schema, concurrent)
    if not statuses:
        print('No available data to display.')
        return

    keys = config.keys
    report = ReportView(statuses)
    data = report.get_data(keys, config.denominator, config.nominator)

    _headers = keys + ['result']
    headers = [config.header_name_dict.get(x, x) for x in _headers]
    dataset = report.get_dataset(data, headers, config.rate_format)

    if output == 'stdout':
        if mode == 'df':
            df = dataset.export(mode)
            # Pretty table via pandas dataframe
            with option_context('display.max_rows', None, 'display.max_columns', None):
                print(df)
        else:
            print(dataset.export(mode))
    else:
        write_mode = 'wb' if mode == 'xls' else 'w'
        with open(output, write_mode) as f:
            f.write(dataset.export(mode))


if __name__ == '__main__':
    main()
