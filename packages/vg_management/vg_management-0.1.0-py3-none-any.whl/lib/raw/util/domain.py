import re
import logging

from lib.raw.util.types import ErrorList


def valid_domain(s: str) -> ErrorList:
    """Determine if given string is a valid domain name.

    :param s:   Domain name to check
    :type s:    str

    :return:    Tuple - success/failure flag and list of errors (if any)
    :rtype:     ErrorList
    """

    errors = []

    if not isinstance(s, str):

        errors.append("Value is not a str")

    else:

        if len(s) > 253:

            errors.append(
                "Domain name is too long ({} characters) - maximum length is 253 characters".format(len(s))
                )

        components = s.split(".")

        if len(components) < 2:

            errors.append("Domain name must have at least two components separated by '.'")

        allowed = re.compile(r'(?!-)[A-Z0-9-]{1,63}(?<!-)$', re.IGNORECASE)

        if not all(allowed.match(x) for x in components):

            errors.append("Domain component invalid - empty, too long or contains invalid characters")

    if len(errors) > 0:

        logging.warning(
            f"valid_domain('{s}'): ERRORS: {','.join(errors)}"
        )

    return (len(errors) == 0), errors
