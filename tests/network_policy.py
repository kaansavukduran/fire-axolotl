# SPDX-License-Identifier: MPL-2.0
"""Classify a bounded fresh-profile HTTP log without retaining URL queries."""
import re
from urllib.parse import urlsplit

FORBIDDEN = {'telemetry.mozilla.org', 'telemetry.mozilla.com', 'datareporting.mozilla.org', 'healthreport.mozilla.org', 'normandy.cdn.mozilla.net', 'normandy.services.mozilla.com', 'contile.services.mozilla.com', 'spocs.getpocket.com'}


def forbidden(host):
    host = host.lower().rstrip('.')
    return any(host == domain or host.endswith('.' + domain) for domain in FORBIDDEN)


def endpoints(text):
    result = set()
    for raw in re.findall(r'https?://[^\s\"\'<>]+', text):
        try:
            url = urlsplit(raw.rstrip('],;)'))
            if url.hostname:
                host = url.hostname.lower().rstrip('.')
                path = re.sub(r'(?i)(?<=/)(?:[a-f0-9-]{20,}|[0-9]{10,})(?=/|$)', '<redacted>', url.path)
                result.add((host, path))
        except ValueError:
            continue
    return result
