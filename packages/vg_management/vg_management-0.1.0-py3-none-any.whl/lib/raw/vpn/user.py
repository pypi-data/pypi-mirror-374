#!/usr/bin/env python3

import os
import pwd
import grp

from lib.raw.vpn.config import VPNConfiguration
from lib.raw.util.types import ErrorList


def vpn_user_available(config: VPNConfiguration) -> ErrorList:
    """Check to see if a specified user has already been defined

    :param config:      Configuration information.
    :type config:       VPNConfiguration

    :return:            Error flag and list of errors (if any).
    :rtype:             ErrorList
    """

    errors = []
    try:
        pwd.getpwnam(config.username)
        errors.append("Username '{}' already defined".format(config.username))
    except Exception:
        pass

    try:
        grp.getgrnam(config.username)
        errors.append("Group name '{}' already defined".format(config.username))
    except Exception:
        pass

    try:
        user_key = "{}/keys/{}.key".format(config.openvpn_dir, config.username)
        if os.path.exists(user_key):
            errors.append("User key file '{}' already exists".format(user_key))
    except Exception:
        pass

    try:
        user_cert = "{}/keys/{}.crt".format(config.openvpn_dir, config.username)
        if os.path.exists(user_cert):
            errors.append("User certificate file '{}' already exists".format(user_cert))
    except Exception:
        pass

    try:
        user_csr = "{}/keys/{}.csr".format(config.openvpn_dir, config.username)
        if os.path.exists(user_csr):
            errors.append("User CSR file '{}' already exists".format(user_csr))
    except Exception:
        pass

    try:
        ovpn_cfg = "{}/{}.ovpn".format(config.client_data_dir, config.username)
        if os.path.exists(ovpn_cfg):
            errors.append("OpenVPN config '{}' already exists".format(ovpn_cfg))
    except Exception:
        pass

    try:
        mail_file = "/var/spool/mail/{}".format(config.username)
        if os.path.exists(mail_file):
            errors.append("Mail file '{}' exists".format(mail_file))
    except Exception:
        pass

    return (len(errors) == 0), errors
