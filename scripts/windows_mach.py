# SPDX-License-Identifier: MPL-2.0
"""Preserve configure diagnostics when private Windows bootstrap exits early."""
import logging
import re
import runpy
import sys

sys.argv[0] = 'mach'
try:
    runpy.run_path('mach', run_name='__main__')
except SystemExit as error:
    if error.code:
        for handler in logging.getLogger('moz.configure').handlers:
            stream = getattr(handler, 'stream', None)
            if hasattr(stream, 'getvalue'):
                body = re.sub(r'(https?://[^\s?]+)\?\S+', r'\1?[redacted]', stream.getvalue())
                print(body, file=sys.stderr)
    raise
