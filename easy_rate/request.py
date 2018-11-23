#!/usr/bin/env python
# encoding: utf-8

import logging
import traceback

import aiohttp

from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.before import before_log

from easy_rate.log import logger


@retry(stop=stop_after_attempt(3), before=before_log(logger, logging.DEBUG))
async def get_json(url):
    conn = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url) as response:
            return await response.json()


async def fetch(semaphore, url):
    async with semaphore:
        logger.info('Working on {}'.format(url))
        try:
            r = await get_json(url)
        except:
            logger.error('Failed to fetch data from {}. Skipped.'.format(url))
            logger.debug(traceback.format_exc())
            return

        logger.info('Fetched data from {}'.format(url))
        return r
