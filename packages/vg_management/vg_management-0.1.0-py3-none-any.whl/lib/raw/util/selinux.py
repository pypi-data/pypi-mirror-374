import subprocess
import logging


def restore_selinux_context(dirname: str):
    """Execute restorecon to restore SElinux context in/under specified directory.

    :param dirname:     Name of directory.
    :type dirname:      str
    """

    logging.debug(
        f"restore_selinux_context('{dirname}')"
    )

#    subprocess.check_call(
#        [
#            "/usr/bin/sudo",
#            "/usr/sbin/restorecon",
#            "-r",
#            dirname
#        ],
#        timeout=10
#   )
