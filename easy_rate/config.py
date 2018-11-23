#!/usr/bin/env python
# encoding: utf-8

import configparser
import os


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
                'ARGUMENTS',
                'concurrent',
                fallback='10'
            )
        )

    @property
    def status_url_template(self):
        return self.config.get(
            'ARGUMENTS',
            'status_url_template',
            fallback=DEFAULT_STATUS_URL_TEMPLATE
        )

    @property
    def mode(self):
        return self.config.get(
            'ARGUMENTS',
            'mode',
            fallback='normal'
        )

    @property
    def rate_format(self):
        return self.config.get(
            'DISPLAY',
            'rate_format',
            fallback='{:.2%}'
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
    def header_name_dict(self):
        return dict(self.config['DISPLAY HEADERS'])

    @property
    def schema(self):
        return dict(self.config['SCHEMA'])
