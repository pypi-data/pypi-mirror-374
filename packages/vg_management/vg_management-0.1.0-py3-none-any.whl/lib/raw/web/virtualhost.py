import os
import shutil
import socket
import subprocess
import pwd
import grp
from datetime import datetime

from lib.raw.util.device import mknod
from lib.raw.util.libs import get_libraries
from lib.raw.web.config import WebConfiguration
from lib.raw.util.types import ErrorList


def virtualhost_dir(config: WebConfiguration) -> str:
    """Return virtualhost directory for user.

    :param config:      Configuration information.
    :type config:       WebConfiguration

    :return:            Virtualhost directory for user.
    :rtype:             str
    """

    vh_dir = "{}/{}".format(config.virtualhosts_root, config.username)

    config.debug(
        f"virtualhost_dir(username='{config.username}') = '{vh_dir}'"
    )

    return vh_dir


def virtualhost_dir_exists(config: WebConfiguration) -> bool:
    """Determine if user's virtualhost directory exists.

    :param config:      Configuration information.
    :type config:       WebConfiguration

    :return:            True if directory exists, False otherwise.
    :rtype:             bool
    """

    vh_dir = virtualhost_dir(config)

    result = os.path.isdir(vh_dir)

    config.debug(
        f"virtualhost_dir_exists(username='{config.username}') [{vh_dir}] = {result}"
    )

    return result


def create_virtualhost_directories(config: WebConfiguration):
    """Create chroot environment for user.

    :param config:      Configuration information.
    :type config:       WebConfiguration
    """

    config.debug(
        f"create_virtualhost_directories(username='{config.username}') [{config.user_home_dir}]"
    )

    user_virtualhost_www = "{}/www".format(config.user_home_dir)
    user_virtualhost_logs = "{}/logs".format(config.user_home_dir)
    user_virtualhost_ssl = "{}/ssl".format(config.user_home_dir)
    user_virtualhost_backup = "{}/backup".format(config.user_home_dir)

    required_libraries = set()

    user_pwnam = pwd.getpwnam(config.username)
    user_grnam = grp.getgrnam(config.username)

    tty_grnam = grp.getgrnam("tty")

    if not os.path.isdir(config.user_home_dir):

        config.debug(
            f"create_virtualhost_directories(): Creating '{config.user_home_dir}'"
        )
        os.makedirs(config.user_home_dir, mode=0o750)

    os.chown(config.user_home_dir, 0, user_grnam.gr_gid)
    os.chmod(config.user_home_dir, mode=0o755)

    os.mkdir(user_virtualhost_www, mode=0o755)
    os.chown(user_virtualhost_www, user_pwnam.pw_uid, user_grnam.gr_gid)
    os.chmod(user_virtualhost_www, mode=0o755)

    os.mkdir(user_virtualhost_logs, mode=0o750)
    os.chown(user_virtualhost_logs, 0, user_grnam.gr_gid)
    os.chmod(user_virtualhost_logs, mode=0o750)

    # Create empty apache access log and give it the correct permissions
    open("{}/{}-access.log".format(user_virtualhost_logs, config.domain_name), 'a').close()
    os.chown("{}/{}-access.log".format(user_virtualhost_logs, config.domain_name), 0, user_grnam.gr_gid)
    os.chmod("{}/{}-access.log".format(user_virtualhost_logs, config.domain_name), mode=0o660)

    # Create empty apache error log and give it the correct permissions
    open("{}/{}-error.log".format(user_virtualhost_logs, config.domain_name), 'a').close()
    os.chown("{}/{}-error.log".format(user_virtualhost_logs, config.domain_name), 0, user_grnam.gr_gid)
    os.chmod("{}/{}-error.log".format(user_virtualhost_logs, config.domain_name), mode=0o660)

    # Create empty access log for php-fpm and give it the correct permissions
    open("{}/{}-fpm-access.log".format(user_virtualhost_logs, config.domain_name), 'a').close()
    os.chown("{}/{}-fpm-access.log".format(user_virtualhost_logs, config.domain_name), 0, user_grnam.gr_gid)
    os.chmod("{}/{}-fpm-access.log".format(user_virtualhost_logs, config.domain_name), mode=0o660)

    # Create empty error log for php-fpm and give it the correct permissions
    open("{}/{}-fpm-error.log".format(user_virtualhost_logs, config.domain_name), 'a').close()
    os.chown("{}/{}-fpm-error.log".format(user_virtualhost_logs, config.domain_name), 0, user_grnam.gr_gid)
    os.chmod("{}/{}-fpm-error.log".format(user_virtualhost_logs, config.domain_name), mode=0o660)

    os.mkdir(user_virtualhost_ssl, mode=0o750)
    os.chown(user_virtualhost_ssl, 0, 0)
    os.chmod(user_virtualhost_ssl, mode=0o750)

    os.mkdir(user_virtualhost_backup, mode=0o750)
    os.chown(user_virtualhost_backup, user_pwnam.pw_uid, user_grnam.gr_gid)
    os.chmod(user_virtualhost_backup, mode=0o750)

    # Set up chroot environment


def copy_certs(config: WebConfiguration):
    """Copy certificate files from existing location to correct location to be used by Apache.

    :param config:      Configuration information.
    :type config:       WebConfiguration
    """

    config.debug(
        f"copy_certs(username='{config.username}',certificate='{config.certificate}',privkey='{config.privkey}',"
        f"ca_chain='{config.ca_chain}')"
    )

    user_virtualhost_ssl = "{}/ssl".format(config.virtualhosts_root)

    user_grnam = grp.getgrnam(config.username)

    try:

        shutil.copy2(
            config.certificate,
            "{}/certificate.pem".format(user_virtualhost_ssl)
            )

        os.chown(
            "{}/certificate.pem".format(user_virtualhost_ssl),
            0,
            user_grnam.gr_gid
            )

        os.chmod(
            "{}/certificate.pem".format(user_virtualhost_ssl),
            mode=0o644
            )

    except Exception as e1:

        config.error(
            f"copy_certs(): EXCEPTION (copying certificate): {str(e1)}"
        )

        raise e1

    try:
        shutil.copy2(
            config.privkey,
            "{}/privkey.pem".format(user_virtualhost_ssl)
            )

        os.chown(
            "{}/privkey.pem".format(user_virtualhost_ssl),
            0,
            user_grnam.gr_gid
            )

        os.chmod(
            "{}/privkey.pem".format(user_virtualhost_ssl),
            mode=0o440
            )

    except Exception as e1:

        config.error(
            f"copy_certs(): EXCEPTION (copying privkey): {str(e1)}"
        )

        raise e1


    try:
        shutil.copy2(
            config.ca_chain,
            "{}/ca_chain.pem".format(user_virtualhost_ssl)
            )

        os.chown(
            "{}/ca_chain.pem".format(user_virtualhost_ssl),
            0,
            user_grnam.gr_gid
            )

        os.chmod(
            "{}/ca_chain.pem".format(user_virtualhost_ssl),
            mode=0o444
            )

    except Exception as e1:

        config.error(
            f"copy_certs(): EXCEPTION (copying ca_chain): {str(e1)}"
        )

        raise e1


def delete_virtualhost_dir(config: WebConfiguration) -> ErrorList:
    """Delete user's chroot environment and all web content, logs and backups.

    :param config:      Configuration information.
    :type config:       WebConfiguration

    :return:            Success flag and list of errors encountered (if any).
    :rtype:             ErrorList
    """

    config.debug(
        f"delete_virtualhost_dir(username='{config.username}') [{virtualhost_dir(config)}]"
    )

    errors = []

    try:

        if os.path.isdir(virtualhost_dir(config)):
            result = subprocess.run(
                [
                    "/usr/bin/sudo",
                    "/usr/bin/rm",
                    "-fr",
                    virtualhost_dir(config)
                ],
                timeout=20
            )
            if result.returncode != 0:
                errors.append("Failed to delete directory subtree '{}' ({})".format(
                    virtualhost_dir(config),
                    result.returncode
                    )
                )

    except subprocess.CalledProcessError as e1:

        config.error(
            f"delete_virtualhost_dir(username='{config.username}') [{virtualhost_dir(config)}]: EXCEPTION: {str(e1)}"
        )

        errors.append("Failed to delete directory subtree '{}' ({})".format(
            virtualhost_dir(config),
            str(e1)
            )
        )

    except Exception as e1:

        config.error(
            f"delete_virtualhost_dir(username='{config.username}') [{virtualhost_dir(config)}]: EXCEPTION: {str(e1)}"
        )

        errors.append("Unexpected exception ({}) while trying to delete directory subtree '{}'".format(
            str(e1),
            virtualhost_dir(config)
            )
        )

    if len(errors) > 0:

        config.error(
            f"delete_virtualhost_dir(username='{config.username}'): ERRORS: {','.join(errors)}"
        )

    return (len(errors) == 0), errors


def do_backup(config: WebConfiguration) -> ErrorList:
    """Make backup of user's web content.

    :param config:      Configuration information.
    :type config:       WebConfiguration

    :return:            Flag indicating success (True)/failure (False), list of errors (if any).
    :type:              ErrorList
    """

    config.debug(
        f"do_backup(username='{config.username}')"
    )

    errors = []

    user_pwnam = pwd.getpwnam(config.username)
    user_grnam = grp.getgrnam(config.username)

    backup_dir = "{}/backup".format(virtualhost_dir(config))

    config.debug(
        f"do_backup(): backup_dir='{backup_dir}'"
    )

    if not os.path.isdir(backup_dir):

        config.debug(
            f"do_backup(): Creating backup directory"
        )
        os.mkdir(backup_dir, mode=0o750)
        os.chown(backup_dir, user_pwnam.pw_uid, user_grnam.gr_gid)
        os.chmod(backup_dir, mode=0o750)

    now_utc = datetime.utcnow()
    now_utc_str = now_utc.isoformat(sep='_')

    this_backup_filename = "{}/{}_{}.7z".format(
        backup_dir,
        config.username,
        now_utc_str
        )

    config.debug(
        f"do_backup(): backup filename = '{this_backup_filename}'"
    )

    args = [
        "/usr/bin/sudo",
        "/usr/bin/7za",
        "a",
        "-bd",
        "-r",
        "-snl",
        "-ssc",
        "-y",
        this_backup_filename,
        "{}/www".format(virtualhost_dir(config))
    ]

    config.debug(
        f"do_backup(): args = {' '.join(args)}"
    )

    try:

        subprocess.run(args, timeout=1200)

    except subprocess.CalledProcessError as e:

        config.error(
            f"do_backup(username='{config.username}'): EXCEPTION: {str(e)}"
        )

        errors.append("Compressor invocation failed trying to back up virtualhost for '{}': {}".format(
            config.username,
            str(e)
            )
        )

    except Exception as e:

        config.error(
            f"do_backup(username='{config.username}'): EXCEPTION: {str(e)}"
        )

        errors.append(
            "Unexpected exception ({}) attempting to invoke compressor to back up virtualhost for '{}'".format(
                str(e),
                config.username
                )
        )

    if len(errors) > 0:

        config.error(
            f"do_backup(username='{config.username}'): ERRORS: {','.join(errors)}"
        )

    return (len(errors) == 0), errors
