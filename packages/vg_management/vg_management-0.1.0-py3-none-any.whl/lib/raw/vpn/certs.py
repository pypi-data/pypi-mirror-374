#!/usr/bin/env python3
import os
import subprocess
import textwrap

from jinja2 import Template
from lib.raw.util.files import read_file_to_string
from lib.raw.vpn.config import VPNConfiguration
from lib.raw.util.types import ErrorList


def create_client_cert(config: VPNConfiguration) -> ErrorList:
    """Create client certificate based on cobfiguration information.

    :param config:      Configuration information.
    :type config:       VPNConfiguration

    :return:            Success flag and list of errors (if any)
    :rtype:             ErrorList
    """

    csr_file = "{}/keys/{}.csr".format(config.openvpn_dir, config.username)
    key_file = "{}/keys/{}.key".format(config.openvpn_dir, config.username)
    cert_file = "{}/keys/{}.crt".format(config.openvpn_dir, config.username)
    ca_cert_file = "{}/keys/ca.crt".format(config.openvpn_dir)
    ca_key_file = "{}/keys/ca-key.pem".format(config.openvpn_dir)
    client_ext_file = "{}/keys/openssl-client.ext".format(config.openvpn_dir)
    openvpn_cfg_file = "{}/{}.ovpn".format(config.client_data_dir, config.username)
    tls_auth_key_file = "{}/keys/ta.key".format(config.openvpn_dir)

    errors = []

    csr_args = [
        "/usr/bin/sudo",
        "/usr/bin/openssl",
        "req",
        "-nodes",
        "-newkey",
        "rsa:4096",
        "-out",
        csr_file,
        "-keyout",
        key_file,
        "-days",
        "3650",
        "-subj",
        "/C=AU/ST=NSW/L=Sydney/O=raw Developments/CN={}/emailAddress={}".format(
            config.username,
            config.cert_email
            )
        ]

    try:

        subprocess.check_call(csr_args, timeout=10)
        csr_ok = True

    except subprocess.CalledProcessError:

        errors.append("Failed to create CSR for user {}".format(config.username))
        csr_ok = False

    except Exception as e:

        errors.append(
            "Unexpected error {} while trying to create CSR for user {}".format(
                str(e),
                config.username
                )
            )
        csr_ok = False

    if csr_ok:

        if not os.path.exists(csr_file):

            errors.append("CSR file '{}' was not generated".format(csr_file))

        elif not os.path.exists(key_file):

            errors.append("Private key file '{}' was not generated".format(key_file))

        else:

            # CSR and private key generated, attempt to sign them

            os.chown(csr_file, 0, 0)
            os.chmod(csr_file, mode=0o640)

            os.chown(key_file, 0, 0)
            os.chmod(key_file, mode=0o600)

            sign_args = [
                "/usr/bin/sudo",
                "/usr/bin/openssl",
                "x509",
                "-req",
                "-in",
                csr_file,
                "-out",
                cert_file,
                "-CA",
                ca_cert_file,
                "-CAkey",
                ca_key_file,
                "-sha256",
                "-days",
                "3650",
                "-CAcreateserial",
                "-extfile",
                client_ext_file
            ]

            try:

                subprocess.check_call(sign_args, timeout=10)
                cert_ok = True

            except subprocess.CalledProcessError:

                errors.append("Failed to sign certificate for user {}".format(config.username))
                cert_ok = False

            except Exception as e:

                errors.append(
                    "Unexpected error '{}' while trying to sign certificate for user '{}'".format(
                        str(e),
                        config.username
                        )
                    )
                cert_ok = False

            if cert_ok:

                if not os.path.exists(cert_file):

                    errors.append("Certificate file '{}' was not generated".format(cert_file))

                else:

                    os.chown(cert_file, 0, 0)
                    os.chmod(cert_file, mode=0o640)

                    ca_data = read_file_to_string(ca_cert_file)

                    user_cert_data = read_file_to_string(cert_file)

                    user_key_data = read_file_to_string(key_file)

                    tls_auth_key_data = read_file_to_string(tls_auth_key_file)

                    openvpn_cfg_template = textwrap.dedent("""
                        remote {{ server_name }} 31194 udp
                        dev tun
                        persist-key
                        persist-tun
                        nobind
                        tls-client
                        verb 4
                        compress lzo
                        auth-user-pass
                        pull
                        remote-cert-tls server
                        key-direction 1
                        auth SHA256
                        keysize 256
                        <ca>
                        {{ ca_cert }}
                        </ca>
                        <cert>
                        {{ user_cert }}
                        </cert>
                        <key>
                        {{ user_key }}
                        </key>
                        <tls-auth>
                        {{ tls_key }}
                        </tls-auth>
                    """)

                    template = Template(openvpn_cfg_template)

                    result = template.render(
                        server_name=config.this_hostname,
                        ca_cert=ca_data,
                        user_cert=user_cert_data,
                        user_key=user_key_data,
                        tls_key=tls_auth_key_data
                        )

                    with open(openvpn_cfg_file, 'w') as cfgfile:

                        cfgfile.write("{}\n".format(result))

                    os.chown(openvpn_cfg_file, 0, 0)
                    os.chmod(openvpn_cfg_file, mode=0o640)

    return (len(errors) == 0), errors
