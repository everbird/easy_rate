#!/usr/bin/env python
# encoding: utf-8


import asyncio
from contextlib import closing

import aiohttp

from easy_rate.request import fetch


class Status(dict):

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
    def get_objs_by_urls(cls, urls, schema, concurrent, callback=None):
        semaphore = asyncio.Semaphore(concurrent)
        with closing(asyncio.get_event_loop()) as loop:
            results = [
                tgt for tgt in loop.run_until_complete(
                    async_bulk_fetch(loop, semaphore, urls, callback)
                )
            ]
            return [cls(schema, x) for x in results if x]


async def async_bulk_fetch(loop, semaphore, urls, callback):
    async with aiohttp.ClientSession(loop=loop) as session:
        futures = [
            asyncio.ensure_future(fetch(semaphore, session, url))
            for url in urls
        ]

        if callback:
            for f in futures:
                f.add_done_callback(callback)

        return await asyncio.gather(*futures)


def get_value_by_dpath(dictionary, dpath):
    items = dpath.split('.')
    r = dictionary
    for item in items[1:]:
        r = r[item]

    return r
