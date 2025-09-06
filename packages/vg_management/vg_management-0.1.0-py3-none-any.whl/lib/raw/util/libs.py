import re
import subprocess
import logging
from typing import Set


def get_libraries(filename: str) -> Set[str]:
    """Identify dynamic libraries used by specified executable.

    :param filename:    Filename of executable to examine.
    :type filename:     str

    :return:            Set represeting dynamic libraries (filenames as str) used by executable.
    :rtype:             set
    """

    result = set()

    try:
        command_output = subprocess.check_output(
            [
                "/usr/bin/sudo",
                "/usr/bin/ldd",
                filename
            ],
            timeout=10
        ).decode('utf-8')

        for line in command_output.splitlines():

            match = re.search(r'.* => ([^ ]+) \(', line)

            if match is not None:
                result.add(match.group(1))

    except Exception as e:

        logging.error(
            f"get_libraries('{filename}'): EXCEPTION: {str(e)}"
        )

    logging.debug(
        f"get_libraries('{filename}'): {','.join(result)}"
    )

    return result
