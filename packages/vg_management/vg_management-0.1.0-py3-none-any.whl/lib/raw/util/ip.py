import netifaces
import re
import logging

import dns.resolver

from typing import Set
from lib.raw.util.types import ErrorList


def is_martian_ip(s: str) -> bool:
    """Determine if specified IPv4 address is a martian.

    :param s:       IPv4 address.
    :type s:        str

    :return:        True if martian address, False otherwise.
    :rtype:         bool
    """

    martian = (
        (re.search(r'^0\.', s) is not None) or
        (re.search(r'^10\.', s) is not None) or
        (re.search(r'^100\.64\.', s) is not None) or
        (re.search(r'^127\.', s) is not None) or
        (re.search(r'^169\.254\.', s) is not None) or
        (re.search(r'^172.(1[6-9]|2[0-3])\.', s) is not None) or
        (re.search(r'^192\.0\.[02]\.', s) is not None) or
        (re.search(r'^192\.168\.', s) is not None) or
        (re.search(r'^198\.1[89]\.', s) is not None) or
        (re.search(r'^198\.51\.100\.', s) is not None) or
        (re.search(r'^203\.0\.113\.', s) is not None) or
        (re.search(r'^22[4-9]\.', s) is not None) or
        (re.search(r'^2[34][0-9]\.', s) is not None) or
        (re.search(r'^25[0-5]\.', s) is not None)
    )

    logging.debug(
        f"in_martian_ip('{s}'): {martian}"
    )

    return martian


def get_local_ip_addresses() -> Set[str]:
    """Obtain local IP addresses and return as a set of strings.

    :return:    Set of strings representing local IP addresses.
    :rtype:     Set[str]
    """

    local_ips = set([])

    for iface in netifaces.interfaces():

        if iface == 'lo':
            continue

        try:

            iface_addrs = netifaces.ifaddresses(iface)

            if netifaces.AF_INET in iface_addrs:

                for addr in iface_addrs[netifaces.AF_INET]:

                    if 'addr' in addr:

                        ip = addr['addr']
                        if not is_martian_ip(ip):
                            local_ips |= {ip}

        except Exception as e:

            logging.warning(
                f"get_local_ip_addresses(): EXCEPTION(iface='{iface}'): {str(e)}"
            )

    logging.debug(
        f"get_local_ip_addresses() = {str(local_ips)}"
    )

    return local_ips


def domain_names_valid(domain_name: str, server_alias: str) -> ErrorList:
    """Verify that domain names and aliases exist and point to this server.

    :param domain_name:     Domain name to check.
    :type domain_name:      str

    :param server_alias:    Comma-separated list of alias domains to check.
    :type server_alias:     str

    :return:                Tuple - success flag and list of errors (if any).
    :rtype:                 ErrorList
    """

    errors = []

    if domain_name is None or len(domain_name) == 0:
        errors.append("Domain name is empty")

    domains = {domain_name}

    if server_alias is not None and len(server_alias) > 0:

        domains |= set(server_alias.split(","))

    local_ips = get_local_ip_addresses()

    for d in domains:

        answers = None

        try:

            answers = dns.resolver.query(d, 'A')
            exists = True

        except dns.resolver.NXDOMAIN:

            errors.append("Domain '{}' does not exist.".format(d))
            exists = False

        if exists:

            for rdata in answers:
                reply_addr = rdata.to_text()
                if reply_addr not in local_ips:
                    errors.append("Domain '{}' does not reference this server.".format(d))

    if len(errors) > 0:

        logging.warning(
            f"domain_names_valid(domain_name='{domain_name}',server_alias='{server_alias}'): "
            f"ERRORS: {','.join(errors)}"
        )

    return (len(errors) == 0), errors
