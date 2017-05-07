from __future__ import (absolute_import, division, print_function)

import sys
from builder.utils import clean_syspath

sys.path = clean_syspath()

from builder.cli import CLI
CLI()
