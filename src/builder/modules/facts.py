from __future__ import (absolute_import, division, print_function)


def parse_cpuinfo(info):
    '''
    Parse CPU info
    
    :param info: output of "cat /proc/cpuinfo" command
    :return: CPU info details
    '''
    ret = dict()
    for line in info.split('\n'):
        kv = line.split(':')
        if len(kv) != 2:
            continue
        k = kv[0].strip()
        v = kv[1].strip()
        if k == u'processor':
            ret[u'num_cpus'] = int(v) + 1
        elif k == u'model name':
            ret[u'cpu_model'] = v
        elif k == u'flags':
            ret[u'cpu_flags'] = v.split()
        elif k == u'Features':
            ret[u'cpu_flags'] = v.split()
    if 'num_cpus' not in ret:
        ret['num_cpus'] = 0
    if 'cpu_model' not in ret:
        ret['cpu_model'] = 'Unknown'
    if 'cpu_flags' not in ret:
        ret['cpu_flags'] = []
    return ret


def parse_meminfo(info):
    '''
    Parse memory info
    
    :param info: output of "cat /proc/meminfo" command
    :return: CPU info details
    '''
    ret = dict()
    for line in info.split('\n'):
        kv = line.split(':')
        if len(kv) != 2:
            continue
        k = kv[0].strip()
        v = kv[1].strip()
        if k == 'MemTotal':
            ret['mem_total'] = int(v.split()[0]) // 1024
        elif k == 'MemFree':
            ret['mem_free'] = int(v.split()[0]) // 1024
    return ret
