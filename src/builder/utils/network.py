from __future__ import (absolute_import, division, print_function)


def ipv4_to_bits(ipaddr):
    '''
    Accepts an IPv4 dotted quad and returns a string representing its binary
    counterpart
    '''
    # Taken from SaltStack salt/utils/network.py
    return ''.join([bin(int(x))[2:].rjust(8, '0') for x in ipaddr.split('.')])


def number_of_set_bits(x):
    '''
    Returns the number of bits that are set in a 32bit int
    '''
    # Taken from http://stackoverflow.com/a/4912729. Many thanks!
    # Taken from SaltStack salt/utils/network.py
    x -= (x >> 1) & 0x55555555
    x = ((x >> 2) & 0x33333333) + (x & 0x33333333)
    x = ((x >> 4) + x) & 0x0f0f0f0f
    x += x >> 8
    x += x >> 16
    return x & 0x0000003f


def cidr_to_ipv4_netmask(cidr_bits):
    '''
    Returns an IPv4 netmask
    
    # Taken from SaltStack salt/utils/network.py 
    '''
    try:
        cidr_bits = int(cidr_bits)
        if not 1 <= cidr_bits <= 32:
            return ''
    except ValueError:
        return ''

    netmask = ''
    for idx in range(4):
        if idx:
            netmask += '.'
        if cidr_bits >= 8:
            netmask += '255'
            cidr_bits -= 8
        else:
            netmask += '{0:d}'.format(256 - (2 ** (8 - cidr_bits)))
            cidr_bits = 0
    return netmask


def number_of_set_bits_to_ipv4_netmask(set_bits):
    '''
    Returns an IPv4 netmask from the integer representation of that mask.

    Ex. 0xffffff00 -> '255.255.255.0'
    '''
    # Taken from SaltStack salt/utils/network.py
    return cidr_to_ipv4_netmask(number_of_set_bits(set_bits))
