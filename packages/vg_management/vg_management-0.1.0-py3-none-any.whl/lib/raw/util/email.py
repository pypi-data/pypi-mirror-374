import re
from .domain import valid_domain
import logging


def valid_email(s: str) -> bool:
    """Examine string to determine if it appears to be a valid email address.

    :param s:   Email address to check.
    :type s:    str

    :return:    Boolean flag - True if appears to be a valid email, False otherwise.
    :rtype:     bool
    """

    if not isinstance(s, str):

        logging.error(
            f"valid_email(): Parameter is {str(type(s))} not str"
        )
        return False

    match = re.search(r'^([^@]+)@(.+)$', s)

    if match is None or match.group(1) is None or match.group(2) is None:

        # print("Failed first parse!")
        return False

    # print(f"group(1) = '{match.group(1)}'")
    # print(f"group(2) = '{match.group(2)}'")

    usermatch = re.search(r'^([a-z0-9\-!#$%&‘*+/=?^_`.{|}~]{1,64})$', match.group(1), re.IGNORECASE)

    if usermatch is None:

        # print("Failed user part parse!")
        return False

    domain_ok, domain_errors = valid_domain(match.group(2))

    if not domain_ok:

        # print(f"Domain errors: {domain_errors}")
        return False

    # print("OK.")

    return True

