import ipaddress
from typing import List
from app.config import get_settings

settings = get_settings()


def parse_allowed_networks() -> List:
    networks = []
    if not settings.CAFE_ALLOWED_IPS:
        return networks
    for part in settings.CAFE_ALLOWED_IPS.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            if "/" in part:
                networks.append(ipaddress.ip_network(part, strict=False))
            else:
                networks.append(ipaddress.ip_network(f"{part}/32", strict=False))
        except ValueError:
            continue
    return networks


def is_from_cafe_network(client_ip: str) -> bool:
    """Return True if the client IP is inside the allowed cafe networks."""
    if not settings.REQUIRE_CAFE_NETWORK:
        return True
    networks = parse_allowed_networks()
    if not networks:
        # If no IPs configured, allow (for development)
        return True
    try:
        ip = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    return any(ip in net for net in networks)
