#!/usr/bin/env python
# encoding: utf-8

import logging
import traceback

import aiohttp
import tqdm

from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.before import before_log


@retry(
    stop=stop_after_attempt(3),
    before=before_log(logging.getLogger(), logging.DEBUG)
)
async def http_get_json(session, url):
    logging.debug('Start to send request asynchronously to {}'.format(url))
    async with session.get(url) as response:
        return await response.json()


async def fetch(semaphore, session, url):
    async with semaphore:
        logging.debug('Start to fetch {}'.format(url))
        try:
            r = await http_get_json(session, url)
        except:
            logging.error(
                'Failed to fetch data from {}.'
                ' Please check debug level log for details.'
                ' Ignored.'.format(url))
            logging.debug(traceback.format_exc())
            return

        logging.debug('Fetched data successfully from {}'.format(url))
        return r
