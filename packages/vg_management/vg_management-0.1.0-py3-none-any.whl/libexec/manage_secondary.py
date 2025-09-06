#!/usr/bin/env python3
"""
Manage secondary (backup) sites on this server.
"""


import sys
import argparse
import re
import os

from typing import Tuple

from lib.raw.util.config import auto_add_config_fromfile, DEFAULT_CONFIGURATION_FILE
from lib.raw.web.secondary.config import SecondaryConfiguration
from lib.raw.web.secondary.database import SiteDatabase
from lib.raw.web.config import *
from lib.raw.web.secondary.defaults import *
from lib.raw.web.secondary.database import site_database_schema


def parse_command_line(config: SecondaryConfiguration):
    """Parse command line and return configuration object representing settings.

    :param config:  Configuration object.
    :type config:   SecondaryConfiguration
    """

    auto_add_config_fromfile(sys.argv, DEFAULT_CONFIGURATION_FILE)

    parser = argparse.ArgumentParser(
        description='Manage secondary sites on this server',
        fromfile_prefix_chars='+'
    )

    parser.add_argument(
        '--list',
        action='store_const',
        default=False,
        const=True,
        help="List configured secondary sites and rules"
    )

    parser.add_argument(
        '--add',
        action='store_const',
        default=False,
        const=True,
        help="Add new secondary site/rule"
    )

    parser.add_argument(
        '--delete',
        action='store_const',
        default=False,
        const=True,
        help="Delete configured secondary site/rule"
    )

    parser.add_argument(
        '--replicate',
        action='store_const',
        default=False,
        const=True,
        help="Initiate replication according to configured secondary sites/rules"
    )

    parser.add_argument(
        '--createdb',
        action='store_const',
        default=False,
        const=True,
        help='Create user & site database'
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

    parser.add_argument(
        '-f',
        '--php-fpm-service',
        default=DEFAULT_PHP_FPM_SERVICE_NAME,
        action='store',
        help='Name of php-fpm service'
        )

    parser.add_argument(
        '-o',
        '--rsyslogd-config-dir',
        default=DEFAULT_RSYSLOG_CONFIG_DIR,
        action='store',
        help='Directory where rsyslogd configuration files are located'
        )

    parser.add_argument(
        '--database-file',
        default=DEFAULT_VG_TOOLS_SECONDARY_DB_FILENAME,
        action='store',
        help='Location where site configuration database is stored'
    )

    parser.add_argument(
        '--ssh-port',
        default=22,
        action='store',
        help='TCP port to use for SSH connections (when add new user/server)'
    )

    parser.add_argument(
        '--loglevel',
        default='INFO',
        action='store',
        help='Set logging level'
    )

    parser.add_argument(
        '--custom-loglevel',
        action='append',
        help='Custom log level for component(s)'
    )

    parser.add_argument(
        '--ssh-user',
        default='root',
        action='store',
        help='User name to log in as via ssh (when add new user/server)'
    )

    parser.add_argument(
        'remote_spec',
        metavar='remote',
        nargs='?',
        action='store',
        help='Remote site specification'
        )

    parser.parse_args(namespace=config)

    if config.remote_spec is not None:

        config.remote = config.remote_spec

    # Ensure exactly one of --list, --add, --delete and --replicate was specified

    command_count = 0

    if config.list:

        command_count += 1

    if config.add:

        command_count += 1

    if config.delete:

        command_count += 1

    if config.replicate:

        command_count += 1

    if config.createdb:

        command_count += 1

    if command_count != 1:

        print(
            "Error: Must specify exactly one of --list, --add, --delete, --replicate and --createdb",
            file=sys.stderr
        )

        parser.print_usage(sys.stderr)

        sys.exit(1)

    if (config.add or config.delete) and config.remote is None:

        print(
            "Error: Remote specification is required in --add and --delete modes",
            file=sys.stderr
        )

        parser.print_usage(sys.stderr)

        sys.exit(1)


def parse_remote_spec(remote_spec: str) -> Tuple[str, str]:

    match = re.search(r"^([^@]+)?@(.+)$", remote_spec)
    return match.group(1), match.group(2).lower()


def print_record_details(table_name: str, data: dict, f):

    def print_field(descr: str, value: str, indent: int):

        print("{0:{width}}: {1}".format(descr, value, width=indent), file=f)

    object_schema = site_database_schema[table_name]

    longest_field = max(object_schema.keys(), key=lambda x: len(object_schema[x].description))

    max_descr_len = len(object_schema[longest_field].description)

    if max_descr_len < 20:

        max_descr_len = 20

    for k in sorted(filter(lambda v: (object_schema[v].primarykey and v in data), object_schema.keys())):

        print_field(object_schema[k].description, str(data[k]), max_descr_len+2)

    for k in sorted(filter(lambda v: ((not object_schema[v].primarykey) and v in data), object_schema.keys())):

        print_field(object_schema[k].description, str(data[k]), max_descr_len+2)



def list_mode(config: SecondaryConfiguration):

    config.info("list_mode")

    sdb = SiteDatabase(config)

    server_list = sdb.get_servers()

    if len(server_list) > 0:

        config.info(
            f"Servers: {','.join(map(lambda x: x.server_name, server_list))}"
        )

        print("")
        print(f" ----- SERVERS -----")
        print("")

        for server in server_list:

            print_record_details("servers", server.asdict(), sys.stdout)
            print("")

    else:

        print("No servers defined.")

    user_list = sdb.get_users()

    if len(user_list) > 0:

        config.info(
            f"Users: {','.join(map(lambda x: x.user_name, user_list))}"
        )

        print(f" ----- USERS -----")
        print("")

        for user in user_list:

            print_record_details("users", user.asdict(), sys.stdout)
            print("")

    else:

        print("No users defined.")


def add_mode_user(
        config: SecondaryConfiguration,
        user: str,
        server: str
):

    sdb = SiteDatabase(config)

    sdb.create_user(
        user_name=user,
        master_server=server,
        ssh_port=int(config.ssh_port),
        ssh_user=config.ssh_user,
        implicit=False
    )


def add_mode_server(
        config: SecondaryConfiguration,
        server: str
):

    sdb = SiteDatabase(config)

    sdb.create_server(
        server_name=server,
        ssh_port=int(config.ssh_port),
        ssh_user=config.ssh_user
    )


def add_mode(config: SecondaryConfiguration):

    config.info("add_mode")

    user, server = parse_remote_spec(config.remote)

    if (user is None or len(user) == 0) and (server is None or len(server) == 0):

        print(
            "Error: Invalid remote specification",
            file=sys.stderr
        )

        sys.exit(1)

    if user is None or len(user) == 0:

        add_mode_server(config, server)

    else:

        add_mode_user(config, user, server)


def delete_mode_user(
        config: SecondaryConfiguration,
        user: str,
        server: str
):

    sdb = SiteDatabase(config)

    user_list = sdb.get_users(
        user_name=user,
        master_server=server
    )

    if len(user_list) == 0:

        config.error(
            f"User {user} on server {server} not found."
        )

        print(
            f"User {user} on server {server} not found.",
            file=sys.stderr
        )

    elif len(user_list) > 1:

        config.error(
            f"ERROR: Multiple matching records for user {user} on server {server} found."
        )

        print(
            f"ERROR: Multiple matching records for user {user} on server {server} found.",
            file=sys.stderr
        )

    else:

        user_list[0].delete()


def delete_mode_server(
        config: SecondaryConfiguration,
        server: str
):

    sdb = SiteDatabase(config)

    server_list = sdb.get_servers(
        server_name=server
    )

    if len(server_list) == 0:

        config.error(
            f"Server {server} not found"
        )

        print(
            f"Server {server} not found.",
            file=sys.stderr
        )

    elif len(server_list) > 1:

        config.error(
            f"ERROR: Multiple matching records for server {server} found."
        )

        print(
            f"ERROR: Multiple matching records for server {server} found.",
            file=sys.stderr
        )

    else:

        server_list[0].delete()


def delete_mode(config: SecondaryConfiguration):

    config.info("delete_mode")

    user, server = parse_remote_spec(config.remote)

    if (user is None or len(user) == 0) and (server is None or len(server) == 0):

        config.error(
            "Error: Invalid remote specification"
        )

        print(
            "Error: Invalid remote specification",
            file=sys.stderr
        )

        sys.exit(1)

    if user is None or len(user) == 0:

        delete_mode_server(config, server)

    else:

        delete_mode_user(config, user, server)


def replicate_mode_all(config: SecondaryConfiguration):

    config.error(
        "Replication not implemented"
    )
    raise NotImplementedError()


def replicate_mode_user(config: SecondaryConfiguration, user: str, server: str):

    config.error(
        "Replication not implemented"
    )
    raise NotImplementedError()


def replicate_mode_server(config: SecondaryConfiguration, server: str):

    config.error(
        "Replication not implemented"
    )
    raise NotImplementedError()


def replicate_mode(config: SecondaryConfiguration):

    config.info("replicate_mode")

    user, server = parse_remote_spec(config.remote)

    if (user is None or len(user) == 0) and (server is None or len(server) == 0):

        replicate_mode_all(config)

    elif user is None or len(user) == 0:

        replicate_mode_server(config, server)

    else:

        replicate_mode_user(config, user, server)


def createdb_mode(config: SecondaryConfiguration):

    config.info("createdb_mode")

    if os.path.exists(config.database_file):

        config.error(
            f"Cannot create database file {config.database_file} as it already exists"
        )
        raise RuntimeError(f"Cannot create database file {config.database_file} as it already exists")

    SiteDatabase(config, True)


def main():

    config = SecondaryConfiguration()

    parse_command_line(config)

    config.init_logging(os.path.basename(__file__))

    config.info(
        f"Command Line: {' '.join(sys.argv)}"
    )

    config.debug_vars()

    if config.list:

        list_mode(config)

    elif config.add:

        add_mode(config)

    elif config.delete:

        delete_mode(config)

    elif config.replicate:

        replicate_mode(config)

    elif config.createdb:

        createdb_mode(config)

    else:

        raise RuntimeError("Unexpected error - no known mode selected")


if __name__ == "__main__":
    main()
