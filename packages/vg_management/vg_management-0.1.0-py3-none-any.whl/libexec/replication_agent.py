#!/usr/bin/env python3
"""
Agent for replication of (master) sites on this host to other hosts.
"""

import os
import sys
import argparse
import json
import re

from typing import Union, Dict

from lib.raw.util.config import auto_add_config_fromfile, DEFAULT_CONFIGURATION_FILE
from lib.raw.web.config import *
from lib.raw.web.user import list_usernames
from lib.raw.web.apache import test_apache_config


def parse_command_line(config: WebConfiguration):
    """Parse command line and return configuration object representing settings.

    :param config:  Configuration object.
    :type config:   WebConfiguration
    """

    auto_add_config_fromfile(sys.argv, DEFAULT_CONFIGURATION_FILE)

    parser = argparse.ArgumentParser(
        description='Local agent for remote site replication',
        fromfile_prefix_chars='+'
    )

    parser.add_argument(
        '--list-sites',
        action='store_const',
        default=False,
        const=True,
        help="List local (master) sites"
    )

    parser.add_argument(
        '--get-config',
        action='store',
        default=None,
        metavar='username',
        help="Dump configuration files for specified user"
    )

    parser.add_argument(
        '-r',
        '--virtualhosts-root',
        default=DEFAULT_VIRTUALHOSTS_ROOT,
        action='store',
        help='Directory where virtualhost directories are located'
        )

    parser.add_argument(
        '-a',
        '--apache-vhost-config-dir',
        default=DEFAULT_APACHE_SITES_AVAILABLE,
        action='store',
        help='Directory where Apache virtualhost configs are written (sites-available)'
        )

    parser.add_argument(
        '-e',
        '--apache-vhost-enabled-dir',
        default=DEFAULT_APACHE_SITES_ENABLED,
        action='store',
        help='Directory where Apache virtualhost symlinks are written (sites-enabled)'
        )

    parser.add_argument(
        '-p',
        '--php-fpm-pool-config-dir',
        default=DEFAULT_PHP_FPM_CONFIG_DIR,
        action='store',
        help='Directory where php-fpm pool configs are written'
        )

    parser.add_argument(
        '-x',
        '--raw-etc-dir',
        default=DEFAULT_VG_TOOLS_ETC_DIR,
        action='store',
        help='VG_TOOLS config directory'
        )

    parser.add_argument(
        '-d',
        '--debugging',
        default=False,
        action='store_const',
        const=True,
        help='Activate debug output'
        )

    parser.parse_args(namespace=config)

    command_count = 0

    if config.list_sites:

        command_count += 1

    if config.get_config is not None:

        command_count += 1

    if command_count != 1:

        print(
            "Error: Must specify exactly one of --list-sites or --replicate",
            file=sys.stderr
        )

        parser.print_usage(file=sys.stderr)

        sys.exit(1)


def list_sites_mode(config: WebConfiguration):

    site_list = list_usernames(config)

    for u in site_list:

        print(f"  {u}")


def read_file(filename: str) -> Union[None, str]:

    try:

        with open(filename, "r") as f:
            result = f.read()

    except:

        result = None

    return result


def get_certificates(virtualhost_config: str) -> Dict[str, str]:

    result = dict()

    for line in virtualhost_config.split("\n"):

        match = re.search(
            r"^\s*(SSLCertificateFile|SSLCertificateKeyFile|SSLCertificateChainFile)\s+([^#]+)(#.*)?$",
            line
        )

        if match is not None:

            fn = match.group(2).strip()
            if os.path.exists(fn):

                file_data = read_file(fn)
                if file_data is not None:

                    result[match.group(1)] = file_data

    return result


def config_dump_mode(config: WebConfiguration):

    site_list = list_usernames(config)

    if config.get_config not in site_list:

        print(
            f"Error: Site '{config.get_config}' is not a master site on this server",
            file=sys.stderr
        )

        sys.exit(1)

    user_configs = {
        "virtualhosts_root":                config.virtualhosts_root,
        "rsyslogd_config_dir":              config.rsyslogd_config_dir,
        "php_fpm_pool_config_dir":          config.php_fpm_pool_config_dir,
        "apache_vhost_config_dir":          config.apache_vhost_config_dir,
        "vg_tools_etc_dir":                       config.vg_tools_etc_dir,
        "php_fpm_service_name":             config.php_fpm_service_name,
        "apache_vhost_enabled_dir":         config.apache_vhost_enabled_dir,
    }

    # Check apache configuration - only back up virtualhost config if test passes

    virtualhost_config_file = f"{config.apache_vhost_config_dir}/{config.get_config}.conf"

    if test_apache_config(config.apache_config) and os.path.exists(virtualhost_config_file):

        virtualhost_data = read_file(virtualhost_config_file)

        if virtualhost_data is not None:

            user_configs["virtualhost_config"] = virtualhost_data

            user_configs.update(get_certificates(virtualhost_data))

    for tag, filename in [
        ("php_fpm_pool_config", f"{config.php_fpm_pool_config_dir}/{config.get_config}.conf"),
        ("rsyslog_config", f"{config.rsyslogd_config_dir}/virtualhost_{config.get_config}.conf"),
    ]:
        if os.path.exists(filename):
            data = read_file(filename)
            if data is not None:
                user_configs[tag] = data

    print(json.dumps(user_configs, indent=4, sort_keys=True))


def main():

    config = WebConfiguration()

    parse_command_line(config)

    config.init_logging()

    if config.debugging:

        print("list_sites               : '{}'".format(config.list_sites))
        print("get_config               : '{}'".format(config.get_config))
        print("virtualhosts_root        : '{}'".format(config.virtualhosts_root))
        print("apache_vhost_config_dir  : '{}'".format(config.apache_vhost_config_dir))
        print("php_fpm_pool_config_dir  : '{}'".format(config.php_fpm_pool_config_dir))
        print("vg_tools_etc_dir               : '{}'".format(config.vg_tools_etc_dir))
        print("debugging                : '{}'".format(config.debugging))

    if config.list_sites:

        list_sites_mode(config)

    elif config.get_config is not None:

        config_dump_mode(config)

    else:

        raise RuntimeError("Unexpected mode selection")


if __name__ == "__main__":
    main()
