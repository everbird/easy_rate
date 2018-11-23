#!/usr/bin/env python
# encoding: utf-8


import asyncio

from easy_rate.request import fetch


class Entity(dict):

    def __init__(self, schema, data):
        self.schema = schema
        self.data = data
        super().__init__(data)

    def __getattr__(self, attr):
        dpath = self.schema.get(attr)
        if dpath:
            return get_value_by_dpath(self, dpath)
        super().__getattr__(attr)

    @classmethod
    def get_objs_by_urls(cls, urls, schema, concurrent):
        semaphore = asyncio.Semaphore(concurrent)
        tasks = [
            asyncio.ensure_future(
                fetch(semaphore, url)
            )
            for url in urls
        ]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        results = (t.result() for t in tasks)
        return [cls(schema, x) for x in results if x]


def get_value_by_dpath(dictionary, dpath):
    items = dpath.split('.')
    r = dictionary
    for item in items[1:]:
        r = r[item]

    return r
