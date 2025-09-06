#!/usr/bin/env python3
"""
Backup a user's virtualhost/chroot environment.
"""

import sys
import argparse

from lib.raw.util.config import auto_add_config_fromfile, DEFAULT_CONFIGURATION_FILE
from lib.raw.web.defaults import *
from lib.raw.web.config import WebConfiguration
from lib.raw.util.user import valid_username
from lib.raw.util.errors import print_errors
from lib.raw.web.virtualhost import virtualhost_dir_exists, virtualhost_dir, do_backup


def parse_command_line(config: WebConfiguration):
    """Parse command line and return configuration object representing settings.

    :param config:  Configuration object.
    :type config:   WebConfiguration
    """

    auto_add_config_fromfile(sys.argv, DEFAULT_CONFIGURATION_FILE)

    parser = argparse.ArgumentParser(
        description='Configure new virtual host user and domain(s)',
        fromfile_prefix_chars='+'
    )

    parser.add_argument(
        '-r',
        '--virtualhosts-root',
        default=DEFAULT_VIRTUALHOSTS_ROOT,
        action='store',
        help='Directory where virtualhost directories are located'
        )

    parser.add_argument(
        '-d',
        '--debugging',
        default=False,
        action='store_const',
        const=True,
        help='Activate debug output'
        )

    parser.add_argument(
        'username_list',
        metavar='username',
        nargs=1,
        action='store',
        help='System username for client'
        )

    parser.parse_args(namespace=config)

    config.username = config.username_list[0]

    config.user_home_dir = "{}/{}".format(config.virtualhosts_root, config.username)


def main():
    """
    Main program.
    """

    config = WebConfiguration()

    parse_command_line(config)

    config.init_logging()

    config.info(
        f"Command Line: {' '.join(sys.argv)}"
    )

    config.debug_vars()

    if config.debugging:

        print("virtualhosts_root        : '{}'".format(config.virtualhosts_root))
        print("debugging                : '{}'".format(config.debugging))
        print("username                 : '{}'".format(config.username))
        print("")
        print("(apache_vhost_config_dir): '{}'".format(config.apache_vhost_config_dir))
        print("(php_fpm_pool_config_dir): '{}'".format(config.php_fpm_pool_config_dir))
        print("(vg_tools_etc_dir)             : '{}'".format(config.vg_tools_etc_dir))
        print("(domain-name)            : '{}'".format(config.domain_name))
        print("(server-alias)           : '{}'".format(config.server_alias))
        print("(letsencrypt)            : '{}'".format(config.letsencrypt))
        print("(certificate)            : '{}'".format(config.certificate))
        print("(privkey)                : '{}'".format(config.privkey))
        print("(ca_chain)               : '{}'".format(config.ca_chain))
        print("(https_only)             : '{}'".format(config.https_only))

    username_ok, username_errors = valid_username(config.username)

    if not username_ok:

        config.error(
            f"Invalid Username [{config.username}]: {','.join(username_errors)}"
        )

        print_errors(username_errors)
        sys.exit(1)

    if not virtualhost_dir_exists(config):

        config.error(
            f"Virtualhost directory [{virtualhost_dir(config)}] for user [{config.username}] does not exist"
        )

        print("Virtualhost directory ({}) for user '{}' does not exist".format(
            virtualhost_dir(config),
            config.username
            )
        )
        sys.exit(1)

    backup_ok, backup_errors = do_backup(config)

    if not backup_ok:

        config.error(
            f"Backup failed: {','.join(backup_errors)}"
        )

        print_errors(backup_errors)


if __name__ == "__main__":
    main()
