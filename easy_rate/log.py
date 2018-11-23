#!/usr/bin/env python
# encoding: utf-8

import logging
import sys


logging.basicConfig(
    level=logging.DEBUG,
    format='PID %(process)5s %(name)18s: %(message)s',
    stream=sys.stderr,
)
logger = logging.getLogger('root')
