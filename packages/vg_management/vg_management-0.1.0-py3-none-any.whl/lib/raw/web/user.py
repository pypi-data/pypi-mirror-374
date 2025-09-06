import os
import re
import shutil
import copy

from typing import List

from lib.raw.web.config import WebConfiguration

from lib.raw.util.types import ErrorList

from lib.raw.util.user import user_account_exists, group_exists, valid_username, delete_user_account

from lib.raw.web.cron import cron_file_exists, cron_file_for_user

from lib.raw.web.logging import rsyslogd_config


def web_user_exists(config: WebConfiguration) -> ErrorList:
    """Check to see if a specified user has already been defined.

    :param config:      Configuration information.
    :type config:       WebConfiguration

    :return:            Success flag and list of errors (if any).
    :rtype:             ErrorList
    """

    config.debug(
        f"web_user_exists(username='{config.username}')"
    )

    username_valid, errors = valid_username(config.username)

    if username_valid:

        if user_account_exists(config.username):
            errors.append("Username '{}' already defined".format(config.username))

        if group_exists(config.username):
            errors.append("Group name '{}' already defined".format(config.username))

        virtual_dir = "{}/{}".format(config.virtualhosts_root, config.username)
        if os.path.isdir(virtual_dir):
            errors.append("Virtualhost directory ({}) already exists".format(virtual_dir))

        apache_conf = "{}/{}.conf".format(config.apache_vhost_config_dir, config.username)
        if os.path.exists(apache_conf):
            errors.append("Apache virtualhost configuration file ({}) already exists".format(apache_conf))

        php_fpm_conf = "{}/{}.conf".format(config.php_fpm_pool_config_dir, config.username)
        if os.path.exists(php_fpm_conf):
            errors.append("PHP-FPM pool configuration ({}) already exists".format(php_fpm_conf))

        mail_file = "/var/spool/mail/{}".format(config.username)
        if os.path.exists(mail_file):
            errors.append("Mail file ({}) exists".format(mail_file))

        rsyslogd_file = rsyslogd_config(config)
        if os.path.exists(rsyslogd_file):
            errors.append("rsyslogd file ({}) exists".format(rsyslogd_file))

        if cron_file_exists(config.username):
            errors.append(f"Cron file {cron_file_for_user(config.username)} exists")

    else:

        config.error(
            f"web_user_exists(): username_valid = {username_valid}"
        )

    if len(errors) > 0:

        config.error(
            f"web_user_exists(): ERRORS: {','.join(errors)}"
        )

    return len(errors) > 0, errors


def list_usernames(config: WebConfiguration) -> List[str]:

    config.debug(
        f"list_usernames(apache_vhost_config_dir='{config.apache_vhost_config_dir}')"
    )

    conf_files = os.listdir(config.apache_vhost_config_dir)

    result = list()

    for f in conf_files:

        match = re.search(r"^(.+)\.conf$", f)

        if match is not None:

            tmpconfig = copy.deepcopy(config)
            tmpconfig.username = match.group(1)
            flag, errorlist = web_user_exists(tmpconfig)

            if len(errorlist) >= 8:

                result.append(match.group(1))

    config.debug(
        f"list_usernames() = {','.join(result)}"
    )

    return result


def cleanup_user(config: WebConfiguration):

    config.debug(
        f"cleanup_user(username='{config.username}')"
    )

    username_valid, errors = valid_username(config.username)

    if username_valid:

        try:
            if user_account_exists(config.username):
                delete_user_account(config.username)
        except Exception as e1:
            config.warn(
                f"cleanup_user(username='{config.username}'): EXCEPTION (delete user account): {str(e1)}"
            )

        try:
            virtual_dir = "{}/{}".format(config.virtualhosts_root, config.username)
            if os.path.isdir(virtual_dir):
                shutil.rmtree(virtual_dir)
        except Exception as e1:
            config.warn(
                f"cleanup_user(username='{config.username}'): EXCEPTION (delete virtualhost): {str(e1)}"
            )

        try:
            apache_conf = "{}/{}.conf".format(config.apache_vhost_config_dir, config.username)
            if os.path.exists(apache_conf):
                os.remove(apache_conf)
        except Exception as e1:
            config.warn(
                f"cleanup_user(username='{config.username}'): EXCEPTION (delete apache sites available): {str(e1)}"
            )

        try:
            apache_conf = "{}/{}.conf".format(config.apache_vhost_enabled_dir, config.username)
            if os.path.lexists(apache_conf):
                os.remove(apache_conf)
        except Exception as e1:
            config.warn(
                f"cleanup_user(username='{config.username}'): EXCEPTION (delete apache sites enabled): {str(e1)}"
            )

        try:
            php_fpm_conf = "{}/{}.conf".format(config.php_fpm_pool_config_dir, config.username)
            if os.path.exists(php_fpm_conf):
                os.remove(php_fpm_conf)
        except Exception as e1:
            config.warn(
                f"cleanup_user(username='{config.username}'): EXCEPTION (delete php-fpm conf): {str(e1)}"
            )

        try:
            mail_file = "/var/spool/mail/{}".format(config.username)
            if os.path.exists(mail_file):
                os.remove(mail_file)
        except Exception as e1:
            config.warn(
                f"cleanup_user(username='{config.username}'): EXCEPTION (delete mail spool): {str(e1)}"
            )

        try:
            rsyslogd_file = rsyslogd_config(config)
            if os.path.exists(rsyslogd_file):
                os.remove(rsyslogd_file)
        except Exception as e1:
            config.warn(
                f"cleanup_user(username='{config.username}'): EXCEPTION (delete rsyslogd conf): {str(e1)}"
            )

        try:
            if cron_file_exists(config.username):
                os.remove(cron_file_for_user(config.username))
        except Exception as e1:
            config.warn(
                f"cleanup_user(username='{config.username}'): EXCEPTION (delete cron file): {str(e1)}"
            )
