#!/usr/bin/env python
# encoding: utf-8

from itertools import groupby
from operator import attrgetter

import tablib


class ReportView(object):

    def __init__(self, statuses):
        self.statuses = statuses

    def get_data(self, keys, denominator, nominator):
        grouped_status_dict = group_statuses(
            self.statuses,
            groupby_key=attrgetter(*keys)
        )
        return {
            ktuple: calculate_rate(self.statuses, denominator, nominator)
            for ktuple, self.statuses in grouped_status_dict.items()
        }

    def get_dataset(self, data, headers, rate_format):
        dataset = tablib.Dataset(
            headers=headers,
        )
        for ktuple in sorted(data.keys()):
            rate = data[ktuple]
            dataset.append(
                ktuple + (rate_format.format(rate),)
            )
        return dataset


def group_statuses(statuses, groupby_key=None):
    r = {}
    statuses = sorted(statuses, key=groupby_key)
    for k, g in groupby(statuses, groupby_key):
        r[k] = list(g)
    return r


def calculate_rate(statuses, denominator, nominator):
    _denominator = sum(getattr(x, denominator) for x in statuses)
    _nominator = sum(getattr(x, nominator) for x in statuses)
    return _nominator / _denominator
