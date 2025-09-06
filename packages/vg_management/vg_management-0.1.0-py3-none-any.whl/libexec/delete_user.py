#!/usr/bin/env python3
"""
Delete a specified user, their website and associated configuration.  Cannot be undone.
"""

import os
import sys
import subprocess
import argparse

from lib.raw.util.config import auto_add_config_fromfile, DEFAULT_CONFIGURATION_FILE
from lib.raw.web.config import WebConfiguration
from lib.raw.web.defaults import *
from lib.raw.util.user import valid_username, user_account_exists, group_exists, delete_user_account, delete_group
from lib.raw.util.errors import print_errors
from lib.raw.web.virtualhost import virtualhost_dir_exists, delete_virtualhost_dir
from lib.raw.web.apache import apache_conf_exists, php_fpm_conf_exists, delete_apache_conf, delete_php_fpm_conf
from lib.raw.web.logging import rsyslogd_config_exists, delete_rsyslogd_config
from lib.raw.web.cron import cron_file_exists, delete_cron_file_for_user


def mail_file(username: str) -> str:
    """Return path to mail spool file for specified user.

    :param username:    Name of user
    :type username:     str

    :return:            Path to mail spool file for user.
    :rtype:             str
    """

    return "/var/spool/mail/{}".format(username)


def mail_file_exists(username: str) -> bool:
    """Return True if mail spool file for specified user exists.

    :param username:    Name of user
    :type username:     str

    :return:            True if mail spool exists, False otherwise.
    :rtype:             bool
    """

    return os.path.lexists(mail_file(username))


def delete_mail_file(username: str) -> bool:
    """Delete mail spool file for specified user.

    :param username:    Name of user
    :type username:     str

    :return:            True if delete successful, False otherwise.
    :rtype:             bool
    """

    try:

        if os.path.exists(mail_file(username)):

            subprocess.run(
                [
                    "/usr/bin/sudo",
                    "/usr/bin/rm",
                    "-f",
                    mail_file(username)
                ],
                timeout=10
            )

        result = True

    except subprocess.CalledProcessError:

        result = False

    return result


def parse_command_line(config: WebConfiguration):
    """Parse command line and set values in configuration object.

    :param config:      Configuration information (output).
    :type config:       WebConfiguration
    """

    auto_add_config_fromfile(sys.argv, DEFAULT_CONFIGURATION_FILE)

    parser = argparse.ArgumentParser(
        description='Delete virtual hosting user, website and associated configuration',
        fromfile_prefix_chars='+'
    )

    parser.add_argument(
        '-r',
        '--virtualhosts-root',
        action='store',
        default=DEFAULT_VIRTUALHOSTS_ROOT,
        help='Directory where virtualhost directories are located'
        )

    parser.add_argument(
        '-a',
        '--apache-vhost-config-dir',
        action='store',
        default=DEFAULT_APACHE_SITES_AVAILABLE,
        help='Directory where Apache virtualhost configs are written (sites-available)'
        )

    parser.add_argument(
        '-e',
        '--apache-vhost-enabled-dir',
        action='store',
        default=DEFAULT_APACHE_SITES_ENABLED,
        help='Directory where Apache virtualhost symlinks are written (sites-enabled)'
        )

    parser.add_argument(
        '-p',
        '--php-fpm-pool-config-dir',
        action='store',
        default=DEFAULT_PHP_FPM_CONFIG_DIR,
        help='Directory where php-fpm pool configs are written'
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
        'username_list',
        metavar='username',
        nargs=1,
        action='store',
        help='System username for client'
        )

    parser.parse_args(namespace=config)

    config.username = config.username_list[0]



def confirm_delete(config: WebConfiguration) -> bool:
    """Obtain interactive confirmation from user that deletion should proceed.

    :param config:      Configuration information.
    :type config:       WebConfiguration

    :return:            True if deletion should proceed, False otherwise.
    :rtype:             bool
    """

    sys.stderr.flush()
    print("")
    sys.stdout.flush()
    sys.stdin.flush()
    response = None
    try:
        response = input(
            "CONFIRM: Delete user '{}' and all associated website data & configuration? (Y/N): ".format(
                config.username
                )
            )
    # Ensure that CTRL-C is treated as "no"
    except KeyboardInterrupt:
        print("")
        print("Aborted.")
        return False

    except:
        pass

    return not (response is None or response.lower() != "y")


def main():

    config = WebConfiguration()

    parse_command_line(config)

    config.init_logging()

    config.info(
        f"Command Line: {' '.join(sys.argv)}"
    )

    config.debug_vars()

    if config.debugging:

        print("virtualhosts_root        : '{}'".format(config.virtualhosts_root))
        print("apache_vhost_config_dir  : '{}'".format(config.apache_vhost_config_dir))
        print("apache_vhost_enabled_dir : '{}'".format(config.apache_vhost_enabled_dir))
        print("php_fpm_pool_config_dir  : '{}'".format(config.php_fpm_pool_config_dir))
        print("debugging                : '{}'".format(config.debugging))
        print("username                 : '{}'".format(config.username))
        print("")

    valid_username_ok, valid_username_errors = valid_username(config.username)

    if not valid_username_ok:

        config.error(
            f"Invalid Username [{config.username}]: {','.join(valid_username_errors)}"
        )

        print_errors(valid_username_errors)
        sys.exit(1)

    # Make sure user isn't trying to delete an important system account

    if config.username in ["root", "nobody", "sshd", "apache", "mysql"]:
        config.error(
            f"System account [{config.username}] specified - aborting"
        )
        print("Error: System account specified.", file=sys.stderr)
        sys.exit(1)

    print("")

    account_exists = user_account_exists(config.username)
    config.debug(
        f"account_exists = {account_exists}"
    )
    print("User account exists      : {}".format(account_exists))

    grp_exists = group_exists(config.username)
    config.debug(
        f"grp_exists = {grp_exists}"
    )
    print("Group exists             : {}".format(grp_exists))

    virtualhost_exists = virtualhost_dir_exists(config)
    config.debug(
        f"virtualhost_exists = {virtualhost_exists}"
    )
    print("Virtualhost dir exists   : {}".format(virtualhost_exists))

    apache_exists = apache_conf_exists(
        config.username,
        [config.apache_vhost_config_dir, config.apache_vhost_enabled_dir]
        )
    config.debug(
        f"apache_exists = {apache_exists}"
    )
    print("Apache config exists     : {}".format(apache_exists))

    php_fpm_exists = php_fpm_conf_exists(config.username, config.php_fpm_pool_config_dir)
    config.debug(
        f"php_fpm_exists = {php_fpm_exists}"
    )
    print("php-fpm config exists    : {}".format(php_fpm_exists))

    mail_exists = mail_file_exists(config.username)
    config.debug(
        f"mail_exists = {mail_exists}"
    )
    print("Mail file exists         : {}".format(mail_exists))

    rsyslogd_exists = rsyslogd_config_exists(config)
    config.debug(
        f"rsyslogd_exists = {rsyslogd_exists}"
    )
    print("rsyslogd config exists   : {}".format(rsyslogd_exists))

    cron_exists = cron_file_exists(config.username)
    config.debug(
        f"cron_exists = {cron_exists}"
    )
    print("Cron file exists         : {}".format(cron_exists))


    if not (account_exists or
            grp_exists or
            virtualhost_exists or
            apache_exists or
            php_fpm_exists or
            mail_exists or
            cron_exists or
            rsyslogd_exists):

        print("")
        print("No elements associated with user '{}' located - nothing to delete.".format(config.username))
        config.info(
            f"No elements associated with user [{config.username}] located - nothing to delete"
        )

    else:

        if confirm_delete(config):

            if account_exists:
                account_result = delete_user_account(config.username)
                config.debug(
                    f"account_result = {account_result}"
                )
                print("User account deleted OK  : {}".format(account_result))

            if grp_exists and not account_exists:
                grp_result = delete_group(config.username)
                config.debug(
                    f"grp_result = {grp_result}"
                )
                print("System group deleted OK  : {}".format(grp_result))

            if virtualhost_exists:
                virtualhost_del_ok, virtualhost_del_errors = delete_virtualhost_dir(config)
                config.debug(
                    f"virtualhost_del_ok = {virtualhost_del_ok}"
                )
                print("Virtualhost deleted OK   : {}".format(virtualhost_del_ok))

            if apache_exists:
                apache_result = delete_apache_conf(
                    config.username,
                    [config.apache_vhost_config_dir, config.apache_vhost_enabled_dir]
                    )
                config.debug(
                    f"apache_result = {apache_result}"
                )
                print("Apache config deleted OK : {}".format(apache_result))

            if php_fpm_exists:
                php_fpm_result = delete_php_fpm_conf(config.username, config.php_fpm_pool_config_dir)
                config.debug(
                    f"php_fpm_result = {php_fpm_result}"
                )
                print("php-fpm config deleted OK: {}".format(php_fpm_result))

            if mail_exists:
                mail_result = delete_mail_file(config.username)
                config.debug(
                    f"mail_result = {mail_result}"
                )
                print("Mail file deleted OK     : {}".format(mail_result))

            if rsyslogd_exists:
                rsyslogd_result = delete_rsyslogd_config(config)
                config.debug(
                    f"rsyslogd_result = {rsyslogd_result}"
                )
                print("rsyslogd config deleted OK:{}".format(rsyslogd_result))

            if cron_exists:
                cron_result = delete_cron_file_for_user(config.username)
                config.debug(
                    f"cron_result = {cron_result}"
                )
                print("Cron file deleted OK     : {}".format(cron_result))


if __name__ == "__main__":
    main()
