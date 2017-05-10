from __future__ import (absolute_import, division, print_function)

import re

from builder.utils import network as network_utils


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
            # ret[u'cpu_flags'] = v.split()
            ret[u'cpu_flags'] = v
        elif k == u'Features':
            ret[u'cpu_flags'] = v.split()
    if 'num_cpus' not in ret:
        ret[u'num_cpus'] = 0
    if 'cpu_model' not in ret:
        ret[u'cpu_model'] = 'Unknown'
    if 'cpu_flags' not in ret:
        ret[u'cpu_flags'] = []
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
            ret[u'mem_total'] = int(v.split()[0]) // 1024
        elif k == 'MemFree':
            ret[u'mem_free'] = int(v.split()[0]) // 1024
    return ret


def parse_env(envs):
    '''
    Parse environment details
    
    :param info: output of "env" command
    :return: the k/v of env details
    '''
    ret = dict()
    for line in envs.split('\n'):
        kv = line.split('=', 1)
        if len(kv) != 2:
            continue
        ret[kv[0].strip()] = kv[1].strip()
    return ret


def parse_release(details):
    '''
    Parse `/etc/*release*` details
    
    :param details: output of "cat /etc/*release*" command
    :return: the k/v of release details
    '''
    ret = dict()
    for line in details.split('\n'):
        kv = line.split('=', 1)
        if len(kv) != 2:
            continue
        ret[kv[0].strip()] = kv[1].strip()
    return ret


def parse_resolv(output):
    '''
    Parse a resolver configuration file (traditionally /etc/resolv.conf)
        
    :param output: stdout of cat /etc/resolv.conf
    :return: the dict of DNS details
    '''
    # Taken from SaltStack salt/utils/network.py

    nameservers = []
    search = []
    sortlist = []
    domain = ''
    options = []

    for line in output.split('\n'):
        line = line.strip().split()
        if not line:
            continue
        # # Drop everything after # or ; (comments)
        if line[0] in ('#', ';'):
            continue
        try:
            (k, v) = (line[0].lower(), line[1:])
            if k == 'nameserver':
                if v[0] not in nameservers:
                    nameservers.append(v[0])
            elif k == 'domain':
                domain = v[0]
            elif k == 'search':
                search = v
            elif k == 'sortlist':
                for ip in v:
                    if ip not in sortlist:
                        sortlist.append(ip)
            elif k == 'options':
                if v[0] not in options:
                    options.append(v[0])
        except IndexError:
            continue

    return {
        u'nameservers': nameservers,
        u'sortlist': sortlist,
        u'domain': domain,
        u'search': search,
        u'options': options
    }


def parse_ifconfig(output):
    '''
    Uses ifconfig to return a dictionary of interfaces with various information
    about each (up/down state, ip address, netmask, and hwaddr)
    
    :param output: stdout of ifconfig command
    :return: the dict of interfaces details
    '''
    # Taken from SaltStack salt/utils/network.py

    ret = dict()

    piface = re.compile(r'^([^\s:]+)')
    pmac = re.compile('.*?(?:HWaddr|ether|address:|lladdr) ([0-9a-fA-F:]+)')
    pip = re.compile(r'.*?(?:inet addr:|inet [^\d]*)(.*?)\s')
    pip6 = re.compile('.*?(?:inet6 addr: (.*?)/|inet6 )([0-9a-fA-F:]+)')
    pmask6 = re.compile(
        r'.*?(?:inet6 addr: [0-9a-fA-F:]+/(\d+)|prefixlen (\d+))(?: Scope:([a-zA-Z]+)| scopeid (0x[0-9a-fA-F]))?')
    pmask = re.compile(r'.*?(?:Mask:|netmask )(?:((?:0x)?[0-9a-fA-F]{8})|([\d\.]+))')
    pupdown = re.compile('UP')
    pbcast = re.compile(r'.*?(?:Bcast:|broadcast )([\d\.]+)')

    groups = re.compile('\r?\n(?=\\S)').split(output)
    for group in groups:
        iface = ''
        data = dict()
        updown = False
        for line in group.splitlines():
            miface = piface.match(line)
            if piface.match(line):
                iface = miface.group(1)

            mmac = pmac.match(line)
            if mmac:
                data['hwaddr'] = mmac.group(1)

            mip = pip.match(line)
            if mip:
                if 'inet' not in data:
                    data['inet'] = list()
                addr_obj = dict()
                addr_obj['address'] = mip.group(1)
                mmask = pmask.match(line)
                if mmask:
                    if mmask.group(1):
                        mmask = network_utils.number_of_set_bits_to_ipv4_netmask(int(mmask.group(1), 16))
                    else:
                        mmask = mmask.group(2)
                    addr_obj['netmask'] = mmask
                mbcast = pbcast.match(line)
                if mbcast:
                    addr_obj['broadcast'] = mbcast.group(1)
                data['inet'].append(addr_obj)

            mip6 = pip6.match(line)
            if mip6:
                if 'inet6' not in data:
                    data['inet6'] = list()
                addr_obj = dict()
                addr_obj['address'] = mip6.group(1) or mip6.group(2)
                mmask6 = pmask6.match(line)
                if mmask6:
                    addr_obj['prefixlen'] = mmask6.group(1) or mmask6.group(2)

            mupdown = pupdown.search(line)
            if mupdown:
                updown = True

            data['up'] = updown
            if iface in ret:
                # merge items with higher priority for older values
                # after that merge the inet and inet6 sub items for both
                ret[iface] = dict(list(data.items()) + list(ret[iface].items()))
                if 'inet' in data:
                    ret[iface]['inet'].extend(x for x in data['inet'] if x not in ret[iface]['inet'])
                if 'inet6' in data:
                    ret[iface]['inet6'].extend(x for x in data['inet6'] if x not in ret[iface]['inet6'])
            else:
                ret[iface] = data
    return ret
