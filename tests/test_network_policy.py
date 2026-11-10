# SPDX-License-Identifier: MPL-2.0
import unittest
from network_policy import endpoints, forbidden


class NetworkSamplePolicyTests(unittest.TestCase):
    def test_telemetry_subdomains_and_sponsored_hosts_are_detected(self):
        for host in ['incoming.telemetry.mozilla.org', 'INCOMING.TELEMETRY.MOZILLA.ORG.', 'contile.services.mozilla.com']:
            self.assertTrue(forbidden(host))

    def test_security_and_account_services_are_distinct_from_telemetry(self):
        for host in ['firefox.settings.services.mozilla.com', 'accounts.firefox.com', 'telemetry.mozilla.org.example.com', '127.0.0.1']:
            self.assertFalse(forbidden(host))

    def test_endpoint_evidence_omits_queries_and_long_identifiers(self):
        sample = 'uri=http://127.0.0.1:8000/fire-axolotl-network-canary\nuri=https://incoming.telemetry.mozilla.org/submit/0123456789abcdef01234567/ping?private=value'
        self.assertEqual(endpoints(sample), {('127.0.0.1', '/fire-axolotl-network-canary'), ('incoming.telemetry.mozilla.org', '/submit/<redacted>/ping')})
