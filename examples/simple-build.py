from __future__ import (absolute_import, division, print_function)

def run(ctxt):
    for ret in ctxt.cmd(*[ 'apk update', 'apk add python']):
        print(ret)
