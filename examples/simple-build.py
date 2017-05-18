from __future__ import (absolute_import, division, print_function)

import os
from pprint import pprint

def run(ctx, **kwargs):
    # vars = ctx.facts()
    # print(vars)
    # ctx.shell('echo "hosts: files dns" >> /etc/nsswitch.conf')
    # print(ctx.inspect('.NetworkSettings.Networks.bridge.IPAddress'))
    pprint(ctx.inspect('.NetworkSettings.Networks'))
    ctx.copy('README.md', '/tmp/')
    print(ctx.cmd('ls -l /tmp'))
