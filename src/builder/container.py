from __future__ import (absolute_import, division, print_function)

import shlex

from builder.docker import DockerCLI

class ContainerContext(object):
    def __init__(self, container_name):
        self._cli = DockerCLI()

        containers = [c[u'names'] for c in self._cli.containers_list()]
        if container_name not in containers:
            raise RuntimeError('Container does not exist, %s' % container_name)

        self._container_name = container_name

    def cmd(self, *args):
        '''
        Run command(-s)
        :param args: command line arguments
        :return: yield of command stdout
        '''
        ret = list()
        for arg in args:
            _args = shlex.split(arg)
            ret.append(self._cli.execute(self._container_name, _args).strip())
        return ret
