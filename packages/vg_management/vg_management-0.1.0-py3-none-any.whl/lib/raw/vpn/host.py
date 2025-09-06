#!/usr/bin/env python3

import os
import pwd
import grp

from .config import VPNConfiguration


def is_vpn_server(config: VPNConfiguration) -> bool:

    try:
        vpn_group = grp.getgrnam(config.vpngroup)
    except:
        vpn_group = None

    try:
        ovpn_user = pwd.getpwnam("openvpn")
    except:
        ovpn_user = None

    try:
        ovpn_dir_exists = os.path.isdir(config.openvpn_dir)
    except:
        ovpn_dir_exists = False

    return (vpn_group is not None) and (ovpn_user is not None) and ovpn_dir_exists

