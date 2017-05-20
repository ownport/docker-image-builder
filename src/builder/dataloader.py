# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import copy
import json
import yaml

from six import text_type

from builder.log import Logger
logger = Logger(__name__)


class DataLoader(object):

    '''
    The DataLoader class is used to load and parse YAML/JSON content,
    either from a given file name or from a string that was previously
    read in through other means. 

    Data read from files will also be cached, so the file will never be
    read from disk more than once.

    Usage:

        dl = DataLoader()
        ds = dl.load('...')
        ds = dl.load_from_file('/path/to/file')
    '''

    def __init__(self):
        self._cache = dict()

    def load(self, data):
        '''  Creates a python datastructure from the given data, which can be either a JSON/YAML string.
        '''
        if not data:
            logger.warning(msg=u'Empty data passed to the dataloader')
            return None

        try:
            # we first try to load this data as JSON
            result = json.loads(data)
            result = [result,] if isinstance(result, dict) else result
        except:
            # must not be JSON, let the rest try
            in_data = text_type(data) if isinstance(data, unicode) else data
            try:
                result = [d for d in yaml.load_all(in_data) if d]
            except:
                logger.error(**{ u'msg': u'Cannot detect file format', u'date.format': type(data)})
                result = None
        return result

    def load_from_file(self, filename):
        ''' Loads data from a file, which can contain either JSON or YAML.  '''
        if not os.path.exists(filename) or not os.path.isfile(filename):
            raise IOError('The file does not exist, %s' % filename)

        # if the file has already been read in and cached, we'll
        # return those results to avoid more file/vault operations
        if filename in self._cache:
            parsed_data = self._cache[filename]
        else:
            with open(filename) as data:
                parsed_data = self.load(data=data.read())

            # cache the file contents for next time
            self._cache[filename] = parsed_data

        # return a deep copy here, so the cache is not affected
        return copy.deepcopy(parsed_data)

