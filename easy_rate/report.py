#!/usr/bin/env python
# encoding: utf-8

from itertools import groupby
from operator import attrgetter

import tablib


DEFAULT_RATE_FORMAT = '{:.2%}'


class RateReport(object):
    rate_key = 'rate'

    def __init__(self, statuses, keys, denominator, nominator):
        self.statuses = statuses
        self.keys = keys
        self.denominator = denominator
        self.nominator = nominator

    @property
    def headers(self):
        return list(self.keys) + [self.rate_key]

    @property
    def rate_data(self):
        r = {}
        key_func = attrgetter(*self.keys)
        statuses = sorted(self.statuses, key=key_func)
        for ktuple, g in groupby(statuses, key_func):
            r[ktuple] = calculate_rate(
                list(g),
                self.denominator,
                self.nominator
            )
        return r

    def render_dataset(self, alias=None, rate_format=DEFAULT_RATE_FORMAT):
        headers = self.headers
        if alias:
            headers = [alias.get(x, x) for x in headers]

        dataset = tablib.Dataset(
            headers=headers,
        )
        data = self.rate_data
        for ktuple in sorted(data.keys()):
            rate = data[ktuple]
            dataset.append(
                ktuple + (rate_format.format(rate),)
            )
        return dataset


def calculate_rate(statuses, denominator, nominator):
    _denominator = sum(getattr(x, denominator) for x in statuses)
    _nominator = sum(getattr(x, nominator) for x in statuses)
    return _nominator / _denominator
