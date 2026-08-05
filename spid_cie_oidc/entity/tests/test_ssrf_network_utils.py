from unittest.mock import patch

from django.test import TestCase

from spid_cie_oidc.entity.network_utils import (
    is_fetchable_federation_url,
    is_public_ip,
)


class SSRFNetworkUtilsTest(TestCase):
    def test_is_public_ip(self):
        public = ["8.8.8.8", "1.1.1.1", "93.184.216.34", "2001:4860:4860::8888"]
        blocked = [
            "127.0.0.1",       # loopback
            "10.0.0.1",        # private
            "192.168.1.1",     # private
            "172.16.0.1",      # private
            "169.254.169.254",  # link-local / cloud metadata
            "100.64.0.1",      # CGNAT
            "0.0.0.0",         # unspecified
            "::1",             # IPv6 loopback
            "fc00::1",         # IPv6 ULA
            "fe80::1",         # IPv6 link-local
            "not-an-ip",
        ]
        for ip in public:
            self.assertTrue(is_public_ip(ip), ip)
        for ip in blocked:
            self.assertFalse(is_public_ip(ip), ip)

    def test_fetchable_url_scheme_and_ip_literal(self):
        # Non http(s) schemes are refused.
        self.assertFalse(is_fetchable_federation_url("ftp://example.com/x"))
        self.assertFalse(is_fetchable_federation_url("file:///etc/passwd"))
        self.assertFalse(is_fetchable_federation_url("gopher://127.0.0.1/"))

        # IP-literal hosts are classified without DNS.
        self.assertTrue(is_fetchable_federation_url("https://8.8.8.8/.well-known/openid-federation"))
        self.assertFalse(is_fetchable_federation_url("http://127.0.0.1/.well-known/openid-federation"))
        self.assertFalse(is_fetchable_federation_url("http://169.254.169.254/latest/meta-data/"))
        self.assertFalse(is_fetchable_federation_url("http://[::1]/x"))

    def test_fetchable_url_hostname_resolution(self):
        # A hostname resolving to a public address is allowed...
        with patch("socket.getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.216.34", 443))]):
            self.assertTrue(is_fetchable_federation_url("https://rp.example.org/"))

        # ...one resolving (even partly) to an internal address is refused.
        with patch("socket.getaddrinfo", return_value=[(2, 1, 6, "", ("127.0.0.1", 80))]):
            self.assertFalse(is_fetchable_federation_url("http://sneaky.example/"))
        with patch(
            "socket.getaddrinfo",
            return_value=[
                (2, 1, 6, "", ("93.184.216.34", 443)),
                (2, 1, 6, "", ("10.0.0.5", 443)),
            ],
        ):
            self.assertFalse(is_fetchable_federation_url("https://rebind.example/"))

        # Unresolvable host is refused.
        import socket

        with patch("socket.getaddrinfo", side_effect=socket.gaierror):
            self.assertFalse(is_fetchable_federation_url("https://nxdomain.invalid/"))
