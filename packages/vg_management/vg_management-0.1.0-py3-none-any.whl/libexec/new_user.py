#!/usr/bin/env python3
"""
Automatically creates a new virtual site using the specified username and domain name (with optional aliases).
"""

import sys
import argparse
from io import TextIOWrapper

from typing import List

from lib.raw.util.config import auto_add_config_fromfile, DEFAULT_CONFIGURATION_FILE
from lib.raw.util.domain import valid_domain
from lib.raw.util.email import valid_email
from lib.raw.util.files import check_file_exists
from lib.raw.util.ip import domain_names_valid
from lib.raw.util.selinux import restore_selinux_context
from lib.raw.util.systemd import systemctl_command
from lib.raw.util.user import valid_username, create_user, add_user_to_group
from lib.raw.web.apache import test_apache_config, write_apache_config, write_php_fpm_pool_config, activate_site, \
    delete_apache_conf
from lib.raw.web.letsencrypt import get_letsencrypt_cert, letsencrypt_cert_status_for_domains
from lib.raw.web.logging import configure_logging
from lib.raw.web.user import web_user_exists
from lib.raw.web.virtualhost import create_virtualhost_directories
from lib.raw.web.config import WebConfiguration
from lib.raw.web.defaults import *
from lib.raw.web.cron import configure_cron



def parse_command_line(
        config: WebConfiguration
):
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
        help='Directory where php-fpm pool configs are written, /etc/php/8.1/fpm/pool.d by default, change php version in path if needed'
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
        '-l',
        '--letsencrypt',
        default=False,
        action='store_const',
        const=True,
        help='Enable TLS and obtain certificate via letsencrypt'
        )

    parser.add_argument(
        '-c',
        '--certificate',
        default=None,
        action='store',
        help='Enable TLS, path to certificate file'
        )

    parser.add_argument(
        '-k',
        '--privkey',
        default=None,
        action='store',
        help='Enable TLS, path to private key file'
        )

    parser.add_argument(
        '-n',
        '--ca-chain',
        default=None,
        action='store',
        help='Enable TLS, path to CA/chain file'
        )

    parser.add_argument(
        '-s',
        '--https-only',
        default=False,
        action='store_const',
        const=True,
        help='No HTTP site - HTTPS only'
        )

    parser.add_argument(
        '-t',
        '--letsencrypt-test',
        default=False,
        action='store_const',
        const=True,
        help='Obtain letsencrypt test certificate'
        )

    parser.add_argument(
        '-g',
        '--debug-challenges',
        default=False,
        action='store_const',
        const=True,
        help='Debug letsencrypt challenges'
        )

    parser.add_argument(
        '-f',
        '--php-fpm-service',
        default=DEFAULT_PHP_FPM_SERVICE_NAME,
        action='store',
        help='Name of php-fpm service, php8.1-fpm.service is default, change the php version in the name if needed'
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
        '--apache-config',
        default=DEFAULT_APACHE_CONFIG,
        action='store',
        help='Apache2 configuration file'
    )

    parser.add_argument(
        '--uid',
        default=None,
        action='store',
        help='uid for new user'
    )

    parser.add_argument(
        '--gid',
        default=None,
        action='store',
        help='gid for new user'
    )

    parser.add_argument(
        'username_list',
        metavar='username',
        nargs=1,
        action='store',
        help='System username for client'
        )

    parser.add_argument(
        'webmaster_email_list',
        metavar='webmaster_email',
        nargs=1,
        action='store',
        help='Webmaster email address (for letsencrypt emails & server config)'
        )

    parser.add_argument(
        'domain_name_list',
        metavar='domain_name',
        nargs=1,
        action='store',
        help='Primary domain name for client website'
        )

    parser.add_argument(
        'server_alias_list',
        metavar='server_alias',
        nargs='?',
        action='store',
        default=None,
        help='List of (comma-separated) server aliases'
        )

    parser.parse_args(namespace=config)

    config.username = config.username_list[0]
    config.webmaster_email = config.webmaster_email_list[0]
    config.domain_name = config.domain_name_list[0]

    config.domain_list = [config.domain_name]

    if config.server_alias_list is not None:
        config.server_alias = config.server_alias_list
        config.domain_list += config.server_alias.split(',')

    if config.letsencrypt_test:

        config.letsencrypt = True

    config.user_home_dir = f"{config.virtualhosts_root}/{config.username}"

    cert_arg_count = 0

    if config.certificate is not None:
        cert_arg_count += 1

    if config.privkey is not None:
        cert_arg_count += 1

    if config.ca_chain is not None:
        cert_arg_count += 1

    if config.letsencrypt and cert_arg_count > 0:

        raise RuntimeError(
            "Error: --letsencrypt is incompatible with any of --certificate, --privkey or --ca-chain. "
            "You must select automatic letsencrypt certificate management or provide all three manual options."
        )

    if config.letsencrypt and config.https_only:

        raise RuntimeError(
            "Error: --https-only cannot be used with --letsencrypt because certificate validation is via HTTP"
        )

    if config.https_only and (cert_arg_count != 3):

        raise RuntimeError(
            "Error: --https-only requires that all three of --certificate, --privkey & --ca-chain are specified"
        )

    if not ((cert_arg_count == 0) or (cert_arg_count == 3)):

        raise RuntimeError(
            "Error: If any of --certificate, --privkey & --ca_chain are specified then all must be specified"
        )

    for filename, description in [
        (config.certificate, "Certificate file"),
        (config.privkey, "Private Key file"),
        (config.ca_chain, "CA Chain file")
     ]:

        if filename is not None and not check_file_exists(filename):

            raise ValueError(
                f"{description} '{filename}' does not exist.  Aborting."
            )

    config.http = not config.https_only

    config.https = (config.letsencrypt or
                    (config.certificate is not None and config.privkey is not None and config.ca_chain is not None))

    if config.server_alias is not None:
        config.server_alias.replace(',', ' ')


def new_user(
        config: WebConfiguration,
        messages_file: TextIOWrapper = sys.stdout
):

    check_username(config)

    check_email(config)

    check_domain(config)

    check_user_exists(config)

    create_site(config, messages_file)

    configure_logging(config)

    systemctl_command("restart", "rsyslog")

    configure_cron(config)

    print("", file=messages_file)
    print(
        f"The user has been set up.  The login account ({config.username}) is locked and will remain so until"
        f"a password has been set.  To set a password, execute 'passwd {config.username}' at a root shell prompt.",
        file=messages_file
    )
    print(
        "Remember that there are minimum complexity requirements for passwords - min 12 characters, at least",
        file=messages_file
    )
    print(
        "one uppercase character, one lowercase character and one digit.  Dictionary words are not allowed.",
        file=messages_file
    )
    print("", file=messages_file)


def create_site(
        config: WebConfiguration,
        messages_file: TextIOWrapper = sys.stdout
):

    if not test_apache_config():

        raise RuntimeError(
            f"Apache configuration failed to validate prior to making any changes."
        )

    use_letsencrypt_cert = None

    request_letsencrypt_certs = False

    if config.letsencrypt:

        # Figure out which domains we have certificates for and which we don't
        letsencrypt_certs_used, domains_without_certs = letsencrypt_cert_status_for_domains(config.domain_list)

        if len(letsencrypt_certs_used) == 1 and len(domains_without_certs) == 0:

            # Requested domains are covered by one existing certificate, so use it
            use_letsencrypt_cert = list(letsencrypt_certs_used)[0]
            print(
                f"Specified domains are covered by existing letsencrypt certificate {use_letsencrypt_cert}.\n"
                "Using that certificate instead of requesting a new one.\n",
                file=messages_file
            )

        elif len(letsencrypt_certs_used) > 1:

            raise RuntimeError(
                f"Multiple letsencrypt certs associated with requested domains: {', '.join(config.domain_list)}. "
                f"Existing certs covering those domains: {', '.join(letsencrypt_certs_used)}. "
                f"Domains with no existing certs: {', '.join(domains_without_certs)}. "
                f"Automatic configuration cannot proceed in this situation."
            )

        elif len(letsencrypt_certs_used) == 0:

            # No existing certificates, request them
            print("Checking to ensure domains exist and point to this server in the DNS.", file=messages_file)
            domains_valid, domains_errors = domain_names_valid(config.domain_name, config.server_alias)

            if not domains_valid:

                raise RuntimeError(domains_errors)

            request_letsencrypt_certs = True

        else:

            raise RuntimeError(
                f"Some requested domains have existing certificates but others do not. "
                f"Existing certs covering those domains: {', '.join(letsencrypt_certs_used)}. "
                f"Domains with no existing certs: {', '.join(domains_without_certs)}. "
                f"Automatic configuration cannot proceed in this situation."
            )

    create_user_ok, create_user_errors = create_user(config)

    if not create_user_ok:

        raise RuntimeError(
            f"Failed to create user '{config.username}': {', '.join(create_user_errors)}"
        )

    add_virtualhost_ok, add_virtualhost_errors = add_user_to_group(config.username, "virtualhost")

    if not add_virtualhost_ok:

        raise RuntimeError(
            f"Failed to add '{config.username}' to group 'virtualhost': {', '.join(add_virtualhost_errors)}"
        )

    add_sftp_ok, add_sftp_errors = add_user_to_group(config.username, "sftp")

    if not add_sftp_ok:

        raise RuntimeError(
            f"Failed to add '{config.username}' to group 'sftp': {', '.join(add_sftp_errors)}"
        )

    create_virtualhost_directories(config)

    if request_letsencrypt_certs:

        # Only need to activate the HTTP site at this point so that certbot can authenticate
        # The HTTPS site will be activated later once we have the certs from letsencrypt

        print("Requesting new letsencrypt certificate.", file=messages_file)

        http_only_config = config
        http_only_config.letsencrypt = False
        http_only_config.https_only = False
        http_only_config.certificate = None
        http_only_config.ca_chain = None
        http_only_config.privkey = None
        http_only_config.http = True
        http_only_config.https = False
        write_apache_config(http_only_config)

    elif use_letsencrypt_cert is not None:

        # We are using an existing letsencrypt certificate
        config.certificate = f"/etc/letsencrypt/live/{use_letsencrypt_cert}/cert.pem"
        config.privkey = f"/etc/letsencrypt/live/{use_letsencrypt_cert}/privkey.pem"
        config.ca_chain = f"/etc/letsencrypt/live/{use_letsencrypt_cert}/chain.pem"

        write_apache_config(config)

    elif config.https and config.certificate is not None and config.privkey is not None and config.ca_chain is not None:

        # We are using manually specified certificates
        print("Using manually specified certificate details (in situ, not copying the cert files).", file=messages_file)
        write_apache_config(config)

    else:

        # HTTP only site
        print("HTTP only site - no certificates required.", file=messages_file)
        write_apache_config(config)

    if not test_apache_config():

        delete_apache_conf(
            config.username,
            [config.apache_vhost_config_dir, config.apache_vhost_enabled_dir]
        )

        raise RuntimeError(
            f"Updating the apache configuration (before reloading the server) appears to have "
            f"introduced an error.  To preserve service for other clients this configuration has "
            f"been removed and setup aborted.  Please investigate and correct any issues manually."
        )

    write_php_fpm_pool_config(config)

    restore_selinux_context(config.user_home_dir)

    activate_site(config)

    systemctl_command("reload", config.php_fpm_service_name)

    systemctl_command("reload", "apache2")

    if request_letsencrypt_certs:

        print("Commencing letsencrypt authentication attempt.", file=messages_file)

        certbot_token = get_letsencrypt_cert(config)

        print("Authentication attempt complete.", file=messages_file)

        if certbot_token is not None:

            config.certificate = f"/etc/letsencrypt/live/{certbot_token}/cert.pem"
            config.privkey = f"/etc/letsencrypt/live/{certbot_token}/privkey.pem"
            config.ca_chain = f"/etc/letsencrypt/live/{certbot_token}/chain.pem"
            write_apache_config(config)

            print(f"New letsencrypt certificate {certbot_token}.", file=messages_file)

            if not test_apache_config():

                raise RuntimeError(
                    f"The apache configuration failed to validate after implementing the SSL site. "
                    f"For that reason apache was not reloaded as doing so would interrupt service. "
                    f"Please manually fix the problem. "
                )

            systemctl_command("reload", "apache2")

        else:

            raise RuntimeError(
                f"Failed to get letsencrypt certificate.  Please investigate and fix the problem. "
                f"The HTTPS configuration has not been written to apache."
            )


def check_user_exists(config):

    user_exists, user_errors = web_user_exists(config)

    if user_exists:

        raise RuntimeError(
            f"Cannot create user '{config.username}' because one or more configuration elements for user exists: "
            f"{', '.join(user_errors)}"
        )


def check_domain(config):

    domain_ok, domain_errors = valid_domain(config.domain_name)

    if not domain_ok:

        raise RuntimeError(
            f"Cannot configure domain name '{config.domain_name}': {', '.join(domain_errors)}"
        )


def check_email(config):

    email_ok = valid_email(config.webmaster_email)

    if not email_ok:

        raise RuntimeError(
            f"Webmaster email '{config.webmaster_email}' is invalid."
        )


def check_username(config):

    username_ok, username_errors = valid_username(config.username)

    if not username_ok:

        raise RuntimeError(
            f"username '{config.username}' is invalid: {','.join(username_errors)}"
        )


def main():
    """Main program.
    """

    config = WebConfiguration()

    parse_command_line(config)

    config.init_logging()

    config.info(
        f"Command Line: {' '.join(sys.argv)}"
    )

    config.debug_vars()

    if config.debugging:

        config.print_vars(sys.stdout)

    config.debug_vars()

    new_user(config, messages_file=sys.stdout)


if __name__ == "__main__":
    main()
