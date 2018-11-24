#!/usr/bin/env python
# encoding: utf-8

import configparser
import os

from easy_rate.report import DEFAULT_RATE_FORMAT


DEFAULT_STATUS_URL_TEMPLATE = 'http://{server}/status'


class Config(object):

    def __init__(self, name):
        self.name = name
        self.config = configparser.ConfigParser()

    @property
    def optional_config_paths(self):
        return [
            '.{name}.conf'.format(name=self.name),
            os.path.expanduser(
                '~/.{name}.conf'.format(name=self.name)
            ),
        ]

    def read(self, config_path):
        config_paths = self.optional_config_paths
        if config_path:
            config_paths.append(config_path)

        self.config.read(config_paths)
        return config_paths

    @property
    def concurrent(self):
        return int(
            self.config.get(
                'QUERY',
                'concurrent',
                fallback='10'
            )
        )

    @property
    def status_url_template(self):
        return self.config.get(
            'QUERY',
            'status_url_template',
            fallback=DEFAULT_STATUS_URL_TEMPLATE
        )

    @property
    def format(self):
        return self.config.get(
            'REPORT',
            'format',
            fallback='df'
        )

    @property
    def rate_format(self):
        return self.config.get(
            'REPORT',
            'rate_format',
            fallback=DEFAULT_RATE_FORMAT
        )

    @property
    def keys(self):
        keys = self.config.get(
            'RATE',
            'keys'
        )
        return keys.split(',')

    @property
    def denominator(self):
        return self.config.get(
            'RATE',
            'denominator'
        )

    @property
    def nominator(self):
        return self.config.get(
            'RATE',
            'nominator'
        )

    @property
    def alias(self):
        return dict(self.config['ALIAS'])

    @property
    def schema(self):
        return dict(self.config['SCHEMA'])
