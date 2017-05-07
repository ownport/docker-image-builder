from __future__ import (absolute_import, division, print_function)

import json
import logging


class Logger(object):
    def __init__(self, name):
        self._logger = logging.getLogger(name)

    def debug(self, **kwargs):
        self._logger.debug(json.dumps(kwargs))

    def info(self, **kwargs):
        self._logger.info(json.dumps(kwargs))

    def warning(self, **kwargs):
        self._logger.warning(json.dumps(kwargs))

    def error(self, **kwargs):
        self._logger.error(json.dumps(kwargs))
