import subprocess
import logging


def mknod(
        path: str,
        devtype: str,
        major: int,
        minor: int) -> int:
    """Create a device node in the file system.

    :param path:    Location of device node in filesystem.
    :type path:     str

    :param devtype: Type of device node (c = character, b = block).
    :type devtype:  str

    :param major:   Major number of device node.
    :type major:    int

    :param minor:   Minor number of device node.
    :type minor:    int

    :return:        Exit code of mknod process
    :rtype:         int
    """

    logging.debug(
        f"mknod(path='{path}',devtype='{devtype}',major={major},minor={minor})"
    )

    result = subprocess.run(
        [
            "/usr/bin/sudo",
            "/usr/bin/mknod",
            path,
            devtype,
            str(major),
            str(minor)
        ],
        timeout=10
    )

    return result.returncode


