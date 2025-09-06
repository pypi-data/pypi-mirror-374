import subprocess
import logging


def systemctl_command(command: str, service: str):
    """Execute a specified systemctl command on a specified service.

    :param command:     Command to execute (e.g. restart, stop, disable, etc)
    :type command:      str

    :param service:     Name of service that is the subject of the command.
    :type service:      str
    """

    logging.debug(
        f"systemctl_command('systemctl {command} {service}')"
    )

    subprocess.check_call(
        [
            "/usr/bin/sudo",
            "/usr/bin/systemctl",
            command,
            service
        ],
        timeout=20
    )
