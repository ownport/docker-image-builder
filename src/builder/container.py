from __future__ import (absolute_import, division, print_function)

import shlex

from builder.docker import DockerCLI
from builder.modules import facts


class ContainerContext(object):
    def __init__(self, container_name):
        self._cli = DockerCLI()

        containers = [c[u'names'] for c in self._cli.containers_list()]
        if container_name not in containers:
            raise RuntimeError('Container does not exist, %s' % container_name)

        self._container_name = container_name

    def facts(self):
        '''
        Gather facts
        :return: 
        '''
        _facts = dict()
        _facts.update(facts.parse_cpuinfo(self.cmd('cat /proc/cpuinfo')))
        _facts.update(facts.parse_meminfo(self.cmd('cat /proc/meminfo')))
        return _facts

    def cmd(self, command):
        '''
        Execute command
        :param command: command line arguments as string
        :return: command stdout
        '''
        args = shlex.split(command)
        stdout = self._cli.execute(self._container_name, *args)
        return stdout
