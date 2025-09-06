import re
import subprocess
import sys
import logging

from typing import Dict, Set, List, Union

from lib.raw.web.config import WebConfiguration


def get_letsencrypt_cert(config: WebConfiguration):
    """Initiate letsencrypt challenge to obtain certificate for user's virtual host.

    :param config:      Configuration information.
    :type config:       WebConfiguration
    """

    config.debug(f"get_letsencrypt_cert(domain_name='{config.domain_name}',server_alias={config.server_alias})")

    domainlist = [config.domain_name]

    if config.server_alias is not None:
        domainlist += config.server_alias.split(",")

    commandline = [
        "/usr/bin/sudo",
        'certbot',
        '--apache',
        'certonly',
        '--agree-tos',
        '-m',
        config.webmaster_email
        ]

    if config.debug_challenges:

        commandline.append('--debug-challenges')

    else:

        commandline.append('-n')

    if config.letsencrypt_test:

        commandline.append('--test-cert')

    for d in domainlist:

        commandline.append('-d')
        commandline.append(d)

    letsencrypt_token = None
    certbot_error = False

    config.debug(
        f"get_letsencrypt_cert(): COMMAND LINE: {' '.join(commandline)}"
    )

    try:

        certbot_output = subprocess.check_output(commandline, timeout=60).decode('utf-8')

        for line in certbot_output.split('\n'):

            match = re.search(r'/etc/letsencrypt/live/([^/]+)/fullchain.pem', line)
            if match is not None:
                letsencrypt_token = match.group(1)
                break

    except subprocess.CalledProcessError as e1:

        config.error(
            f"get_letsencrypt_cert(): EXCEPTION: {str(e1)}"
        )

        certbot_error = True

    except Exception as e2:

        config.error(
            f"get_letsencrypt_cert(): EXCEPTION: {str(e2)}"
        )

        certbot_error = True

    if certbot_error or letsencrypt_token is None:

        print("", file=sys.stderr)
        print("Error: Certificate authentication failed.  Please fix the issue and retry using:", file=sys.stderr)
        print("{}".format(" ".join(commandline)), file=sys.stderr)
        print("", file=sys.stderr)
        print("Once the certificate authentication works you will need to edit the apache configuration at",
              file=sys.stderr)
        print("{}/{}.conf to point to the certificate files in /etc/letsencrypt/live/....".format(
            config.apache_vhost_config_dir,
            config.username
            ), file=sys.stderr)

    elif config.letsencrypt_test:

        print("")
        print("WARNING: Certificate is a TEST CERTIFICATE and will not be trusted by browsers.")
        print("===============================================================================")
        print("")

    config.debug(f"get_letsencrypt_cert() = '{letsencrypt_token}'")

    return letsencrypt_token


def list_letsencrypt_certs() -> Dict[str, dict]:
    """Obtain list of currently issued certificates from certbot - parse and return as dict.

    :return:        Dict representation of currently issued certs.
    :rtype:         dict
    """

    logging.debug(
        f"list_letsencrypt_certs()"
    )

    try:

        output = subprocess.check_output(
            [
                "/usr/bin/sudo",
                "/usr/bin/certbot",
                "certificates"
            ],
            timeout=10
        ).decode("utf-8")

    except Exception as e1:

        logging.error(
            f"list_letsencrypt_certs(): EXCEPTION: {str(e1)}"
        )

        output = None

    certificates = {}

    if output is not None:

        # State 1 - Looking for 'Certificate Name:' line (indentation 2)
        # State 2 - Looking for 'Domains'/'Expiry Date'/'Certificate Path'/'Private Key Path' (indentation 4)

        state = 1
        lines = output.split("\n")
        new_cert = {}

        while len(lines) > 0:

            match = re.search(
                r'^((?: {2}Certificate Name)|(?: {4}Domains)|(?: {4}Expiry Date)|(?: {4}Certificate Path)'
                '|(?: {4}Private Key Path)): (.*)$',
                lines[0]
            )

            if match is not None:

                header = match.group(1)
                value = match.group(2)

                if state == 1:

                    if header == '  Certificate Name':

                        new_cert = {"certificate_name": value}
                        state = 2

                    else:

                        logging.error(
                            f"list_letsencrypt_certs(): Invalid certbot output - expected 'Certificate Name' "
                            f"got '{header.strip()}'"
                        )
                        raise RuntimeError(
                            f"Invalid certbot output - expected 'Certificate Name' got '{header.strip()}'"
                        )

                    del lines[0]

                elif state == 2:

                    if header == '  Certificate Name':

                        certificates[new_cert["certificate_name"]] = new_cert
                        new_cert = {}
                        state = 1

                    elif header == '    Domains':

                        new_cert['domains'] = []
                        for d in value.strip().split(','):
                            new_cert['domains'].append(d.strip())
                        del lines[0]

                    else:

                        new_cert[header.strip().lower().replace(' ', '_')] = value.strip()
                        del lines[0]

            else:

                del lines[0]

        if 'certificate_name' in new_cert:

            certificates[new_cert["certificate_name"]] = new_cert

    logging.debug(
        f"list_letsencrypt_certs() = {','.join(certificates.keys())}"
    )

    return certificates


# d1, d2, d3, ..., dn

# 1. One cert covering all domains

# 2.


def find_letsencrypt_cert_for_domain(domain: str, certlist: Dict[str, dict]) -> Union[str, None]:
    """Search certbot domain list to identify which certificate(s) applies to given domains.

    :param domain:      Domain to search for.
    :type domain:       str

    :param certlist:    Dictionary representation of current letsencrypt certificates, from list_letsencrypt_certs.
    :type certlist:     Dict[str, dict]

    :return:            Name of letsencrypt cert for domain, or None
    :rtype:             Union[str, None]
    """

    for cert_name, cert in certlist.items():

        if 'domains' in cert and domain in cert['domains']:

            logging.debug(
                f"find_letsencrypt_cert_for_domain(domain='{domain}') = '{cert_name}'"
            )

            return cert_name

    logging.debug(
        f"find_letsencrypt_cert_for_domain(domain='{domain}') = None"
    )

    return None


def find_letsencrypt_certs_for_domains(domainlist: List[str], certlist: Dict[str, dict]) -> Dict[str, str]:


    result = {}

    for domain in domainlist:

        cert = find_letsencrypt_cert_for_domain(domain, certlist)

        if cert is not None:

            result[domain] = cert

    logging.debug(
        f"find_letsencrypt_certs_for_domains(domainlist={','.join(domainlist)}) = {','.join(result.keys())}"
    )

    return result


def letsencrypt_cert_status_for_domains(domainlist: List[str]) -> (Set[str], Set[str]):

    logging.debug(
        f"letsencrypt_cert_status_for_domains(domainlist={','.join(domainlist)})"
    )

    # Get list of existing letsencrypt certificates on this host
    certlist = list_letsencrypt_certs()

    # Identify which existing cert, if any, applies to each domain name
    cert_status = find_letsencrypt_certs_for_domains(domainlist, certlist)

    # Figure out if all domains are covered by one existing cert
    certs_used = set([])
    domains_missing = set([])

    for domain in domainlist:

        if domain in cert_status:

            certs_used.add(cert_status[domain])

        else:

            domains_missing.add(domain)

    logging.debug(
        f"letsencrypt_cert_status_for_domains(): certs_used = {','.join(certs_used)}"
    )

    logging.debug(
        f"letsencrypt_cert_status_for_domains(): domains_missing = {','.join(domains_missing)}"
    )

    return certs_used, domains_missing
