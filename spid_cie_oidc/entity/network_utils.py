"""
Helpers to keep federation network operations from being turned into an SSRF /
open-proxy primitive.

An OpenID Federation endpoint resolves trust chains by fetching entity
configurations over HTTP. When the subject of such a fetch comes from an
unauthenticated, not-yet-verified request, an attacker can point it at an
address of their choosing. These helpers let callers refuse addresses that must
never be reached this way (loopback, private, link-local incl. the cloud
metadata address, ...) and non-HTTP(S) schemes.
"""

import ipaddress
import socket
from urllib.parse import urlparse


def is_public_ip(ip: str) -> bool:
    """Return True only for a globally routable IP address."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False

    # ip_address.is_global is False for private, loopback, link-local,
    # unspecified, reserved and multicast ranges (incl. 169.254.169.254 and
    # 100.64.0.0/10 CGNAT).
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
        addr = addr.ipv4_mapped

    return addr.is_global


def is_fetchable_federation_url(url: str) -> bool:
    """
    Return True only if ``url`` is an http(s) URL whose host is safe to fetch:
    a public IP literal, or a hostname that resolves exclusively to public
    addresses. Resolving here (and rejecting on any non-public answer) also
    blocks DNS-rebinding style bypasses.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    host = parsed.hostname
    if not host:
        return False

    # Host given as an IP literal: classify it directly.
    try:
        ipaddress.ip_address(host)
        return is_public_ip(host)
    except ValueError:
        pass

    # Host given as a name: every resolved address must be public.
    try:
        infos = socket.getaddrinfo(host, parsed.port or 0, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False

    resolved = {info[4][0] for info in infos}
    if not resolved:
        return False

    return all(is_public_ip(ip) for ip in resolved)
