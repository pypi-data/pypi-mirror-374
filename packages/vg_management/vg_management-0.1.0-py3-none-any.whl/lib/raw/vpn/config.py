
import socket

from lib.raw.util.config import ProgramConfiguration
from lib.raw.vpn.defaults import *


class VPNConfiguration(ProgramConfiguration):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.username = None
        self.gecos = None
        self.openvpn_dir = DEFAULT_OPENVPN_DIR
        self.client_data_dir = DEFAULT_CLIENT_DATA_DIR
        self.vpngroup = DEFAULT_VPN_GROUP
        self.this_hostname = socket.gethostname()
        self.cert_email = DEFAULT_CERT_EMAIL

        if self.this_hostname is None or ('.' not in self.this_hostname):
            raise RuntimeError("Unable to get hostname of this computer")
