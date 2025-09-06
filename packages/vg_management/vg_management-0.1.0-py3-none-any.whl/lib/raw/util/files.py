#!/usr/bin/env python3
import os


def read_file_to_string(filename: str) -> str:
    """Open a text file and read content into a string.

    :param filename:    Name of file to open.
    :type filename:     str

    :return:            Contents of file as a string.
    :rtype:             str
    """
    with open(filename, 'r') as f:
        lines = f.read()

    return lines


def check_file_exists(f: str) -> bool:
    """Examine specified file to determine if it exists.

    :param f:       Name of file.
    :type f:        str

    :return:        Boolean indicating whether or not file exists.
    :rtype:         bool
    """

    return (f is not None) and os.path.exists(f)

