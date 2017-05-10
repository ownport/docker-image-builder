from __future__ import (absolute_import, division, print_function)

import sys


def clean_syspath():
    ''' Cleaner removes from sys.path any external libs to avoid potential
    # conflicts with existing system libraries 
    
    :return: updated sys.path
    '''
    result = []
    for p in sys.path:
        if p.endswith('site-packages'):
            continue
        if p.endswith('dist-packages'):
            continue
        if p.endswith('lib-old'):
            continue
        if p.endswith('lib-tk'):
            continue
        if p.endswith('gtk-2.0'):
            continue
        result.append(p)
    return result
