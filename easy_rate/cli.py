#!/usr/bin/env python
# encoding: utf-8

import logging

import click
import tqdm

from pandas import option_context

from easy_rate.config import Config
from easy_rate.log import setup_logger
from easy_rate.report import RateReport
from easy_rate.status import Status


@click.command()
@click.option(
    '-l', '--server-list',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help='Server list that report status json.'
)
@click.option(
    '-v', '--verbose',
    count=True,
    help='''Verbose.
-v\tWARN log.
-vv\tINFO log.
-vvv\tDEBUG log.
-vvvv\tAll the log.'''
)
@click.option(
    '-f', '--format',
    type=click.Choice(['csv', 'json', 'yaml', 'xls', 'df']),
    default='df',
    help='Output format. Default: df.'
)
@click.option(
    '-o', '--output',
    help='Filepath for output file. None as stdout by default.'
)
@click.option(
    '-n', '--concurrent',
    type=int,
    help=(
        'Value of semaphore to control the concurrency for status fetching.'
        ' Default: 10.'
    )
)
@click.option(
    '-c', '--config-path',
    help='''Configuration file path.
[1] .easy_rate.conf
[2] ~/.easy_rate.conf
[3] --config-path
'''
)
@click.option(
    '--log-file',
    help='Path of log file.'
)
@click.option(
    '--progress/--no-progress',
    default=True,
    help='Show progress bar or not.'
)
def main(
    server_list,
    verbose,
    format,
    concurrent,
    config_path,
    output,
    log_file,
    progress
):
    ''' Query a list of servers to generate rate report base on configuration.
    '''
    logger = setup_logger(__name__, verbose=verbose, log_file=log_file)

    config = Config('easy_rate')
    config.read(config_path)

    concurrent = concurrent or config.concurrent
    format = format or config.format

    logger.info('verbose: {}'.format(verbose))
    logger.info('format: {}'.format(format))
    logger.info('concurrent: {}'.format(concurrent))
    logger.info('output: {}'.format(output or 'stdout'))
    logger.info('progress'.format(progress))

    servers = [x.strip() for x in open(server_list)]
    urls = [
        config.status_url_template.format(server=server)
        for server in servers
    ]
    if progress:
        progressbar = tqdm.tqdm(
            desc='Fetching Statuses',
            total=len(urls),
            unit='reqs'
        )
        def _callback(future):
            if future.result():
                progressbar.update()

        callback = _callback
    else:
        callback = None

    statuses = Status.get_objs_by_urls(
        urls,
        config.schema,
        concurrent,
        callback
    )
    if not statuses:
        logger.info('No available data.')
        return

    report = RateReport(
        statuses,
        config.keys,
        config.denominator,
        config.nominator
    )
    dataset = report.render_dataset(
        config.alias,
        config.rate_format
    )

    if output:
        write_mode = 'wb' if format == 'xls' else 'w'
        with open(output, write_mode) as f:
            f.write(dataset.export(format))
    elif format == 'df':
        df = dataset.export(format)
        with option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)
    else:
        print(dataset.export(format))


if __name__ == '__main__':
    main()
