import os
import subprocess
import logging

from jinja2 import Template

from lib.raw.web.config import WebConfiguration
from lib.raw.util.types import ErrorList

from typing import List


def test_apache_config() -> bool:
    """Test current apache configuration to check for errors.

    :return:    True if configuration is OK, False otherwise.
    :rtype:     bool
    """

    logging.debug(
        f"test_apache_config()"
    )

    result = subprocess.run(
        [
            "/usr/bin/sudo",
            "/usr/sbin/apachectl",
            "configtest",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10
    )

    if result.returncode == 0:

        logging.debug(
            f"test_apache_config() = (OK) {result.stderr.decode('utf-8')}"
        )

    else:

        logging.error(
            f"test_apache_config() = (ERROR) {result.stderr.decode('utf-8')}"
        )

    return (result.returncode == 0) and (result.stderr.decode("utf-8") == "Syntax OK\n")


def make_apache_conffile_list(
        username:       str,
        dirlist:        List[str]) -> List[str]:
    """Make a list of (possible) apache configuration file locations based on username and directory list.

    :param username:    Name of user.
    :type username:     str

    :param dirlist:     List of directory names.
    :type dirlist:      List[str]

    :return:            List of (possible) configuration files
    :rtype:             List[str]
    """

    logging.debug(
        f"make_apache_conffile_list(username='{username}',dirlist={'.'.join(dirlist)})"
    )

    result = []

    for d in dirlist:

        result.append("{}/{}.conf".format(d, username))

    logging.debug(
        f"make_apache_conffile_list() = {','.join(result)}"
    )

    return result


def apache_conf_exists(
        username:       str,
        dirlist:        List[str]) -> bool:
    """Determine whether or not apache configuration file for specified user exists in any listed directory.

    :param username:    Name of user.
    :type username:     str

    :param dirlist:     List of directories to search.
    :type dirlist:      List[str]

    :return:            True if file exists, False otherwise.
    :rtype:             bool
    """

    logging.debug(
        f"apache_conf_exists(username='{username}',dirlist={'.'.join(dirlist)})"
    )

    result = False

    conf_files = make_apache_conffile_list(username, dirlist)

    for f in conf_files:

        if os.path.lexists(f):

            result = True

    logging.debug(
        f"apache_conf_exists() = {result}"
    )

    return result


def php_fpm_conf(
        username:                   str,
        php_fpm_pool_config_dir:    str) -> str:
    """Return filename of php-fpm configuration based on username and directory.

    :param username:                    Name of user.
    :type username:                     str

    :param php_fpm_pool_config_dir:     Directory where php-fpm configuration files are located.
    :type php_fpm_pool_config_dir:      str

    :return:                            Fully qualified filename of configuration file.
    :rtype:                             str
    """

    filename = f"{php_fpm_pool_config_dir}/{username}.conf"

    logging.debug(
        f"php_fpm_conf(username='{username}',php_fpm_pool_config_dir='{php_fpm_pool_config_dir}') = '{filename}'"
    )

    return filename


def php_fpm_conf_exists(
        username:                   str,
        php_fpm_pool_config_dir:    str) -> bool:
    """Determine whether or not php-fpm configuration file exists for specified user.

    :param username:                    Name of user.
    :type username:                     str

    :param php_fpm_pool_config_dir:     Directory where php-fpm configuration files are located.
    :type php_fpm_pool_config_dir:      str

    :return:                            True if configuration file exists, False otherwise.
    :rtype:                             bool
    """

    result = os.path.lexists(php_fpm_conf(username, php_fpm_pool_config_dir))

    logging.debug(
        f"php_fpm_conf_exists(username='{username}',php_fpm_pool_config_dir='{php_fpm_pool_config_dir}') = {result}"
    )

    return result


def write_apache_config(config: WebConfiguration) -> ErrorList:
    """Write apache configuration file based on configuration parameters.

    :param config:      Configuration information.
    :type config:       WebConfiguration

    :return:            Success flag and list of errors (if any)
    :rtype:             ErrorList
    """

    config.debug(
        f"write_apache_config()"
    )

    errors = []

    if (not config.http) and (not config.https):

        errors.append("At least one of HTTP and HTTPS must be enabled")

    else:

        apache_conf = "{}/{}.conf".format(
            config.apache_vhost_config_dir,
            config.username
        )

        apache_template_file = "{}/apache_virtualhost.conf".format(config.vg_tools_etc_dir)

        with open(apache_template_file, 'r') as tpl:
            apache_template_data = tpl.read()

        apache_template = Template(apache_template_data)
        result = apache_template.render(
            username=config.username,
            domain=config.domain_name,
            virtualhosts_root=config.virtualhosts_root,
            apache_vhost_config_dir=config.apache_vhost_config_dir,
            apache_vhost_enabled_dir=config.apache_vhost_enabled_dir,
            php_fpm_pool_config_dir=config.php_fpm_pool_config_dir,
            vg_tools_etc_dir=config.vg_tools_etc_dir,
            webmaster_email=config.webmaster_email,
            server_alias=config.server_alias,
            certificate_file=config.certificate,
            privkey_file=config.privkey,
            ca_chain_file=config.ca_chain,
            letsencrypt=config.letsencrypt,
            https_only=config.https_only,
            letsencrypt_test=config.letsencrypt_test,
            php_fpm_service_name=config.php_fpm_service_name,
            rsyslogd_config_dir=config.rsyslogd_config_dir,
            user_home_dir=config.user_home_dir,
            http=config.http,
            https=config.https,
            )

        with open(apache_conf, 'w') as outfile:
            outfile.write("{}\n".format(result))

    if len(errors) == 0:

        config.debug(f"write_apache_config() OK")

    else:

        config.error(f"write_apache_config() ERRORS: {', '.join(errors)}")

    return (len(errors) == 0), errors


def write_php_fpm_pool_config(config: WebConfiguration):
    """Write php-fpm configuration for user's pool.

    :param config:      Configuration information.
    :type config:       WebConfiguration
    """

    config.debug(f"write_php_fpm_pool_config()")

    php_fpm_template_file = "{}/php-fpm-pool.conf".format(config.vg_tools_etc_dir)

    with open(php_fpm_template_file, 'r') as tpl:
        php_fpm_template_data = tpl.read()

    php_fpm_template = Template(php_fpm_template_data)

    result = php_fpm_template.render(
        username=config.username,
        domain=config.domain_name,
        virtualhosts_root=config.virtualhosts_root,
        apache_vhost_config_dir=config.apache_vhost_config_dir,
        apache_vhost_enabled_dir=config.apache_vhost_enabled_dir,
        php_fpm_pool_config_dir=config.php_fpm_pool_config_dir,
        vg_tools_etc_dir=config.vg_tools_etc_dir,
        webmaster_email=config.webmaster_email,
        server_alias=config.server_alias,
        certificate_file=config.certificate,
        privkey_file=config.privkey,
        ca_chain_file=config.ca_chain,
        letsencrypt=config.letsencrypt,
        https_only=config.https_only,
        letsencrypt_test=config.letsencrypt_test,
        php_fpm_service_name=config.php_fpm_service_name,
        rsyslogd_config_dir=config.rsyslogd_config_dir,
        user_home_dir=config.user_home_dir,
        http=config.http,
        https=config.https,
        )

    with open(php_fpm_conf(config.username, config.php_fpm_pool_config_dir), 'w') as outfile:
        outfile.write("{}\n".format(result))


def activate_site(config: WebConfiguration):
    """Activate apache virtual host for user.

    :param config:      Configuration information.
    :type config:       WebConfiguration
    """

    config.debug(f"activate_site()")

    conf_file = "{}/{}.conf".format(
        config.apache_vhost_config_dir,
        config.username
        )

    link_file = "{}/{}.conf".format(
        config.apache_vhost_enabled_dir,
        config.username
        )

    os.symlink(conf_file, link_file)


def delete_apache_conf(
        username:       str,
        dirlist:        List[str]) -> bool:
    """Delete apache configuration files for specified user in all listed directories.

    :param username:    Name of user.
    :type username:     str

    :param dirlist:     List of directories to search.
    :type dirlist:      List[str]

    :return:            True if deletion successful, False otherwise.
    :rtype:             bool
    """

    logging.debug(
        f"delete_apache_conf(username='{username}',dirlist={','.join(dirlist)})"
    )

    result = True

    conf_files = make_apache_conffile_list(username, dirlist)

    for f in conf_files:

        if os.path.lexists(f):

            try:

                subprocess.run(
                    [
                        "/usr/bin/sudo",
                        "/usr/bin/rm",
                        "-f",
                        f
                    ],
                    timeout=10
                )

            except subprocess.CalledProcessError as e1:

                logging.error(
                    f"delete_apache_conf(): EXCEPTION: {str(e1)}"
                )

                result = False

    return result


def delete_php_fpm_conf(
        username:                   str,
        php_fpm_pool_config_dir:    str) -> bool:
    """Delete php-fpm configuration file for specified user.

    :param username:                    Name of user.
    :type username:                     str

    :param php_fpm_pool_config_dir:     Directory where php-fpm configuration files are located.
    :type php_fpm_pool_config_dir:      str

    :return:                            True if deletion successful, False otherwise.
    :rtype:                             bool
    """

    logging.debug(
        f"delete_php_fpm_conf(username='{username}',php_fpm_pool_config_dir='{php_fpm_pool_config_dir}')"
    )

    try:

        if os.path.exists(php_fpm_conf(username, php_fpm_pool_config_dir)):
            subprocess.run(
                [
                    "/usr/bin/sudo",
                    "/usr/bin/rm",
                    "-f",
                    php_fpm_conf(username, php_fpm_pool_config_dir)
                ],
                timeout=10
            )

        result = True

    except subprocess.CalledProcessError as e1:

        logging.error(
            f"delete_php_fpm_conf(): EXCEPTION: {str(e1)}"
        )
        result = False

    return result
