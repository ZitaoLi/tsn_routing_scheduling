# -*- coding: utf-8 -*-
import re
import sys

from mypy.dmypy import console_entry

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(console_entry())
