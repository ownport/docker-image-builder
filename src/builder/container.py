from __future__ import (absolute_import, division, print_function)

import shlex

from builder.log import Logger
from builder.docker import DockerCLI
from builder.utils import facts as fact_utils

logger = Logger(__name__)


class ContainerContext(object):
    def __init__(self, container_name):
        self._cli = DockerCLI()

        containers = [c[u'names'] for c in self._cli.containers_list()]
        if container_name not in containers:
            raise RuntimeError('Container does not exist, %s' % container_name)

        self._container_name = container_name

    def get_logger(self, name=__name__):
        '''
        return container logger
        
        :return: logger
        '''
        return Logger(name)

    def facts(self, categories=('all',)):
        '''
        Gather facts
        :param categories: the list of categories, default: all (all facts)
            possible values: all, hw, env, release, uname, net
        :return: the dict with facts about container
        '''
        logger.info(msg='Facts gathering')
        _facts = dict()
        if 'all' in categories or 'hw' in categories:
            _facts.update(fact_utils.parse_cpuinfo(self.cmd('cat /proc/cpuinfo')))
            _facts.update(fact_utils.parse_meminfo(self.cmd('cat /proc/meminfo')))

        if 'all' in categories or 'env' in categories:
            _facts.update({u'env': fact_utils.parse_env(self.cmd('env'))})

        if 'all' in categories or 'release' in categories:
            _facts.update({u'release': fact_utils.parse_env(self.shell('cat /etc/*release*'))})

        if 'all' in categories or 'uname' in categories:
            _facts.update({u'uname': {
                u'machine.type': self.cmd('uname -m').strip(),
                u'hardware.platform': self.cmd('uname -i').strip(),
                u'hostname': self.cmd('uname -n').strip(),
                u'kernel.release': self.cmd('uname -r').strip(),
                u'kernel.version': self.cmd('uname -v').strip(),
                u'kernel.name': self.cmd('uname -s').strip(),
                u'processor.type': self.cmd('uname -p').strip(),
                u'os.name': self.cmd('uname -o').strip(),
            }})

        if 'all' in categories or 'net' in categories:
            _facts.update({u'net': {
                u'hostname': self.cmd('cat /etc/hostname').strip()}
            })
            _facts[u'net'].update(fact_utils.parse_resolv(self.cmd('cat /etc/resolv.conf')))
            _facts[u'net'][u'interfaces'] = fact_utils.parse_ifconfig(self.cmd('ifconfig').strip())
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

    def shell(self, command):
        '''
        Execute command via /bin/sh
        
        :param command: command line arguments as string
        :return: command stdout
        '''
        args = ['/bin/sh', '-c', command]
        # args = shlex.split(command)
        stdout = self._cli.execute(self._container_name, *args)
        return stdout

    def copy(self, src, dest, to_container=True):
        '''
        Copy file from/to container
        :param src: source path
        :param dest: destination path
        :param to_container: direction of copying
        :return: True if operation was successful
        '''
        if to_container:
            return self._cli.copy(src, "{}:{}".format(self._container_name, dest))
        else:
            return self._cli.copy("{}:{}".format(self._container_name, src), dest)

    def inspect(self, path):
        '''
        Inspect container details by JSON path
        :param path: JSON path for parameter selection
        :return: Container details
        '''
        return self._cli.inspect(self._container_name, path)
