#!/usr/bin/env python
# encoding: utf-8

import json
import os

from http.server import HTTPServer, SimpleHTTPRequestHandler

import click


@click.command()
@click.option(
    '-l', '--servers-file',
    type=click.File(),
    default='servers.txt',
    help='Server list.'
)
@click.option(
    '-r', '--responses-file',
    type=click.File(),
    default='responses.txt',
    help='Response list.'
)
@click.option(
    '-t', '--tmp-dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    help='Directory to store the tmp json files for data serving.'
)
@click.option('-p', '--port', type=int, default=8000, help='Port')
@click.option('-h', '--host', default='127.0.0.1', help='Host')
def main(servers_file, responses_file, tmp_dir, host, port):
    ''' Run a simple http server to serve json files to simulate status
    response for status query.

    The Server list and Response list should match.
    '''
    servers = [x.strip() for x in servers_file]
    responses = json.load(responses_file)

    for server, response in zip(servers, responses):
        filename = '{}.status.json'.format(server)
        with open(os.path.join(tmp_dir, filename), 'w') as w:
            w.write(json.dumps(response))
    print(
        '{} status json files have been created in directory: {}'
        .format(len(servers) ,tmp_dir)
    )

    class HTTPRequestHandler(SimpleHTTPRequestHandler):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=tmp_dir, **kwargs)

    with HTTPServer((host, port), HTTPRequestHandler) as httpd:
        print("Serving at {}:{} for directory: {}".format(host, port, tmp_dir))
        httpd.serve_forever()


if __name__ == '__main__':
    main()
