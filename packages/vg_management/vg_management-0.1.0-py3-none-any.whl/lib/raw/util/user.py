#!/usr/bin/env python3
import subprocess
import re
import pwd
import grp
import logging

from typing import List, Optional

from lib.raw.util.types import ErrorList

from lib.raw.web.config import WebConfiguration


def valid_username(s: str) -> ErrorList:
    """Determine if given string is a valid username.

    :param s:   Username to check
    :type s:    str

    :return:    Flag representing validity of username and list of error messages.
    :rtype:     ErrorList
    """

    errors = []

    if not isinstance(s, str):

        errors.append("Username must be str")

    else:

        if len(s) < 2 or len(s) > 20:

            errors.append("Username must be between 2 and 20 characters in length")

        else:

            if s[0].isdigit():
                errors.append("Username cannot start with a digit")

            if re.search('^[a-z][a-z0-9]{1,19}$', s) is None:
                errors.append("Username is invalid - must be lowercase a-z & digits, 2-20 characters.")

    if len(errors) > 0:

        logging.warning(
            f"valid_username('{s}'): ERRORS: {','.join(errors)}"
        )

    return (len(errors) == 0), errors


def create_user(
        config:         WebConfiguration
        ) -> ErrorList:
    """Create system user account.
    """

    logging.debug(
        f"create_user(username='{config.username}',home_dir='{config.user_home_dir}',gecos='{config.username}')"
    )

    errors = []

    gid_error = None
    create_group = config.gid is not None

    # If a gid is specified, deal with that first
    if config.gid is not None:

        # Does the specified gid exist?
        gr_exists = group_exists_gid(int(config.gid))

        if gr_exists:

            # Group already exists - check to see if group name matches username
            cur_gid = group_get_gid(config.username)
            gid_ok = (cur_gid == int(config.gid))

            if gid_ok:

                create_group = False

            else:

                gid_error = f"Group {config.username} already exists but with gid {cur_gid} not {int(config.gid)}"

    if gid_error is not None:

        errors.append(gid_error)

    else:

        group_ok = True

        if create_group:

            args = [
                "/usr/bin/sudo",
                "/usr/sbin/groupadd",
                "-g",
                str(config.gid),
                config.username
            ]

            logging.debug(
                f"create_user(): COMMAND: {' '.join(args)}"
            )

            try:

                completed_process = subprocess.run(args, timeout=10)

                if completed_process.returncode != 0:

                    errors.append(f"Failed to create group '{config.username} with gid {config.gid} - "
                                  f"process exist code {completed_process.returncode}")
                    group_ok = False

            except subprocess.CalledProcessError as e1:

                logging.error(
                    f"create_user(): EXCEPTION: {str(e1)}"
                )
                errors.append("Failed to create user {}".format(config.username))
                group_ok = False

            except Exception as e2:

                logging.error(
                    f"create_user(): EXCEPTION: {str(e2)}"
                )
                errors.append("Unexpected error {} while trying to create user {}".format(str(e2), config.username))
                group_ok = False

        if group_ok:

            # Execute useradd to create the user
            args = [
                "/usr/bin/sudo",
                "/usr/sbin/useradd",
                "-M",
                "-s",
                "/usr/sbin/nologin",
                ]

            if create_group:

                args += ["-g", config.username]

            if config.uid is not None:

                args += ["-u", str(config.uid)]

            if config.user_home_dir is not None:

                args += ["-d", config.user_home_dir]

            args += ["-c", config.username]

            args += [config.username]

            logging.debug(
                f"create_user(): COMMAND: {' '.join(args)}"
            )

            try:

                completed_process = subprocess.run(args, timeout=10)

                if completed_process.returncode != 0:

                    errors.append(f"Failed to create user '{config.username}' - "
                                  f"process exit code {completed_process.returncode}")

            except subprocess.CalledProcessError as e1:

                logging.error(
                    f"create_user(): EXCEPTION: {str(e1)}"
                )
                errors.append("Failed to create user {}".format(config.username))

            except Exception as e2:

                logging.error(
                    f"create_user(): EXCEPTION: {str(e2)}"
                )
                errors.append("Unexpected error {} while trying to create user {}".format(str(e2), config.username))

    if len(errors) > 0:

        logging.error(
            f"create_user(): ERRORS: {','.join(errors)}"
        )

    return len(errors) == 0, errors


def add_user_to_group(user: str, group: str) -> ErrorList:
    """Add specified system user to named system group.

    :param user:    User account that is to be added to group.
    :type user:     str

    :param group:   Name of group that user is to be added to.
    :type group:    str

    :return:        Success flag and list of errors (if any)
    :rtype:         (bool, list[str])
    """

    logging.debug(
        f"add_user_to_group(user='{user}',group='{group}')"
    )

    errors = []

    try:

        subprocess.check_call(
            [
                "/usr/bin/sudo",
                "/usr/sbin/usermod",
                "-a",
                "-G",
                group,
                user
            ],
            timeout=10
        )

    except subprocess.CalledProcessError as e1:

        logging.error(
            f"add_user_to_group(): EXCEPTION: {str(e1)}"
        )
        errors.append("Failed to add user {} to group {}".format(user, group))

    except Exception as e2:

        logging.error(
            f"add_user_to_group(): EXCEPTION: {str(e2)}"
        )
        errors.append("Unexpected error {} while trying to add user {} to group {}".format(
            str(e2), user, group)
        )

    return (len(errors) == 0), errors


def user_account_exists(username: str) -> bool:
    """Check to see if specified user account exists.

    :param username:    Name of user account.
    :type username:     str

    :return:            True if user account exists, False otherwise.
    :rtype:             bool
    """

    try:

        pwd.getpwnam(username)
        exists = True

    except KeyError:

        exists = False

    logging.debug(
        f"user_account_exists('{username}'): {exists}"
    )

    return exists


def group_exists(groupname: str) -> bool:
    """Check to see if specified system group exists.

    :param groupname:   Name of group.
    :type groupname:    str

    :return:            True if group exists, False otherwise.
    :rtype:             bool
    """

    try:

        grp.getgrnam(groupname)
        exists = True

    except KeyError:

        exists = False

    logging.debug(
        f"group_exists('{groupname}'): {exists}"
    )

    return exists


def group_get_gid(groupname: str) -> Optional[int]:
    """Check to see if specified system group exists.

    :param groupname:   Name of group.
    :type groupname:    str

    :return:            gid of group (if exists, otherwise None)
    :rtype:             bool
    """

    try:

        g = grp.getgrnam(groupname)
        return g.gr_gid

    except Exception:

        pass

    return None


def group_exists_gid(gid: int) -> bool:
    """Check to see if specified system group exists.

    :param gid:         Group ID
    :type gid:          int

    :return:            True if group exists, False otherwise.
    :rtype:             bool
    """

    try:

        grp.getgrgid(gid)
        exists = True

    except KeyError:

        exists = False

    logging.debug(
        f"group_exists('{gid}'): {exists}"
    )

    return exists


def delete_user_account(username: str) -> bool:
    """Delete user account.

    :param username:    Name of user to delete.
    :type username:     str

    :return:            True if deletion successful, False otherwise.
    :rtype:             bool
    """

    logging.debug(
        f"delete_user_account('{username}')"
    )

    if username.lower() in [
        "root",
        "bin",
        "daemon",
        "adm",
        "lp",
        "sync",
        "shutdown",
        "halt",
        "mail",
        "operator",
        "games",
        "ftp",
        "nobody",
        "dbus",
        "systemd-coredump",
        "systemd-network",
        "systemd-resolve",
        "tss",
        "unbound",
        "polkitd",
        "rtkit",
        "usbmuxd",
        "openvpn",
        "nm-openvpn",
        "geoclue",
        "colord",
        "nm-openconnect",
        "pulse",
        "pipewire",
        "apache",
        "dnsmasq",
        "systemd-timesync",
        "tinyproxy",
        "user",
        "redis",
        "postgres",
        "davfs2"
    ]:

        logging.error(
            f"delete_user_account('{username}'): Attempt to delete protected account denied"
        )
        raise ValueError(f"Deletion of user '{username}' is not permitted")

    try:

        subprocess.run(
            [
                "/usr/bin/sudo",
                "/usr/sbin/userdel",
                "-f",
                username
            ],
            timeout=10
        )
        result = True

    except subprocess.CalledProcessError as e1:

        logging.error(
            f"delete_user_account('{username}'): EXCEPTION: {str(e1)}"
        )
        result = False

    return result


def delete_group(groupname: str) -> bool:
    """Delete system group.

    :param groupname:    Name of system group to delete.
    :type groupname:     str

    :return:            True if deletion successful, False otherwise.
    :rtype:             bool
    """

    logging.debug(
        f"delete_group('{groupname})"
    )

    try:

        subprocess.run(
            [
                "/usr/sbin/groupdel",
                groupname
            ],
            timeout=10
        )
        result = True

    except subprocess.CalledProcessError as e1:

        logging.error(
            f"delete_group('{groupname}'): EXCEPTION: {str(e1)}"
        )
        result = False

    return result


def get_group_members(groupname: str) -> Optional[List[str]]:

    logging.debug(
        f"get_group_members('{groupname}')"
    )

    try:

        group = grp.getgrnam(groupname)

        if group is None:

            return None

        return group.gr_mem

    except Exception as e1:

        logging.error(
            f"get_group_members('{groupname}'): EXCEPTION: {str(e1)}"
        )

    return None
