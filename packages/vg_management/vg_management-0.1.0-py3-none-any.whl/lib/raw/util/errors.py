import sys

from typing import List


def print_errors(errlist: List[str], file=sys.stderr):
    """Print, to specified file, a supplied list of errors - one per line.

    :param errlist:     List of errors.
    :type errlist:      List[str]

    :param file:        File to print error messages to (default sys.stderr)
    """
    for err in errlist:

        print("ERROR:   {}".format(err), file=file)
