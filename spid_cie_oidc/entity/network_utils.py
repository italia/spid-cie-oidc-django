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

_PRIVATE_NETWORKS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
)


def _address(ip: str):
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return None
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped is not None:
        return addr.ipv4_mapped
    return addr


def _private_nets_allowed() -> bool:
    """Return True when RFC1918 federation subjects may be fetched."""
    try:
        from django.conf import settings
        from django.core.exceptions import ImproperlyConfigured
    except ImportError:
        return False
    try:
        return bool(getattr(settings, "OIDCFED_FETCH_PRIVATE_NETS", False))
    except ImproperlyConfigured:
        return False


def _is_fetchable_address(ip: str) -> bool:
    addr = _address(ip)
    if addr is None:
        return False
    if addr.is_global:
        return True
    if not _private_nets_allowed():
        return False
    return any(addr in network for network in _PRIVATE_NETWORKS)


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
    addresses. ``OIDCFED_FETCH_PRIVATE_NETS`` also accepts 10.0.0.0/8,
    172.16.0.0/12 and 192.168.0.0/16. Loopback and link-local stay refused.
    Resolving here (and rejecting any other non-public answer) also blocks
    DNS-rebinding style bypasses.
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
        return _is_fetchable_address(host)
    except ValueError:
        pass

    # Host given as a name: every resolved address must be fetchable.
    try:
        infos = socket.getaddrinfo(host, parsed.port or 0, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False

    resolved = {info[4][0] for info in infos}
    if not resolved:
        return False

    return all(_is_fetchable_address(ip) for ip in resolved)
