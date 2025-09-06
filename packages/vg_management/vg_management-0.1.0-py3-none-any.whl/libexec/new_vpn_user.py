#!/usr/bin/env python3
"""
Automatically create a new VPN user.
"""

import sys
import argparse

from lib.raw.vpn.config import VPNConfiguration
from lib.raw.util.user import valid_username, create_user, add_user_to_group
from lib.raw.vpn.certs import create_client_cert
from lib.raw.vpn.user import vpn_user_available
from lib.raw.vpn.defaults import *
from lib.raw.util.errors import print_errors


def parse_command_line(config: VPNConfiguration):
    """Parse command line and store details into config.

    :param config:      Destination for configuration information.
    :type config:       VPNConfiguration
    """

    parser = argparse.ArgumentParser(
        description='Create new VPN user account',
        fromfile_prefix_chars='+'
    )

    parser.add_argument(
        '-o',
        '--openvpn-root',
        action='store',
        default=DEFAULT_OPENVPN_DIR,
        help='Directory where OpenVPN configs are located'
        )

    parser.add_argument(
        '-c',
        '--client-data-dir',
        action='store',
        default=DEFAULT_CLIENT_DATA_DIR,
        help='Directory where client data is staged'
        )

    parser.add_argument(
        '-g',
        '--group',
        action='store',
        default=DEFAULT_VPN_GROUP,
        help='System group to use for VPN authentication'
        )

    parser.add_argument(
        '-d',
        '--debugging',
        action='store_const',
        const=True,
        default=False,
        help='Activate debug output'
        )

    parser.add_argument(
        '-e',
        '--cert-email',
        action='store',
        default=DEFAULT_CERT_EMAIL,
        help='Email address to associate with user certificate'
        )

    parser.add_argument(
        'username',
        nargs=1,
        action='store',
        help='System username for client'
        )

    parser.add_argument(
        'gecos',
        nargs=1,
        action='store',
        help='Real name of user'
        )

    parser.parse_args(namespace=config)



def main():
    """Main program.
    """

    config = VPNConfiguration()

    parse_command_line(config)

    config.init_logging()

    config.info(
        f"Command Line: {' '.join(sys.argv)}"
    )

    config.debug_vars()

    if config.debugging:

        print("username                 : '{}'".format(config.username))
        print("gecos                    : '{}'".format(config.gecos))
        print("openvpn_dir              : '{}'".format(config.openvpn_dir))
        print("client_data_dir          : '{}'".format(config.client_data_dir))
        print("vpngroup                 : '{}'".format(config.vpngroup))
        print("this_hostname            : '{}'".format(config.this_hostname))

    username_ok, username_errors = valid_username(config.username)

    if not username_ok:

        print_errors(username_errors)
        sys.exit(1)

    user_available, user_available_errors = vpn_user_available(config)

    if not user_available:

        print_errors(user_available_errors)
        sys.exit(1)

    create_user_ok, create_user_errors = create_user(config.username)

    if not create_user_ok:

        print_errors(create_user_errors)
        sys.exit(1)

    addgroup_ok, addgroup_errors = add_user_to_group(config.username, config.vpngroup)

    if not addgroup_ok:

        print_errors(addgroup_errors)
        sys.exit(1)

    create_cert_ok, create_cert_errors = create_client_cert(config)

    if not create_cert_ok:

        print_errors(create_cert_errors)
        sys.exit(1)

    print("")
    print("You must now set a password for user {} by running, as root:".format(config.username))
    print("")
    print("    passwd {}".format(config.username))
    print("")


if __name__ == "__main__":
    main()
