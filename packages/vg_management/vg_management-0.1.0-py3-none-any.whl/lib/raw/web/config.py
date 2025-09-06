
from lib.raw.util.config import ProgramConfiguration
from lib.raw.web.defaults import *


class WebConfiguration(ProgramConfiguration):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.virtualhosts_root = DEFAULT_VIRTUALHOSTS_ROOT
        self.apache_config = DEFAULT_APACHE_CONFIG
        self.apache_vhost_config_dir = DEFAULT_APACHE_SITES_AVAILABLE
        self.apache_vhost_enabled_dir = DEFAULT_APACHE_SITES_ENABLED
        self.php_fpm_pool_config_dir = DEFAULT_PHP_FPM_CONFIG_DIR
        self.vg_tools_etc_dir = DEFAULT_VG_TOOLS_ETC_DIR
        self.username = None
        self.webmaster_email = None
        self.domain_name = None
        self.server_alias = None
        self.domain_list = []
        self.certificate = None
        self.privkey = None
        self.ca_chain = None
        self.letsencrypt = False
        self.https_only = False
        self.letsencrypt_test = False
        self.debug_challenges = False
        self.php_fpm_service_name = DEFAULT_PHP_FPM_SERVICE_NAME
        self.rsyslogd_config_dir = DEFAULT_RSYSLOG_CONFIG_DIR
        self.user_home_dir = None
        self.http = False
        self.https = False
        self.uid = None
        self.gid = None


    def dump_for_debugging(self):

        super().dump_for_debugging()

        for p in [
            'virtualhosts_root',
            'apache_config',
            'apache_vhost_config_dir',
            'apache_vhost_enabled_dir',
            'php_fpm_pool_config_dir',
            'vg_tools_etc_dir',
            'username',
            'webmaster_email',
            'domain_name',
            'server_alias',
            'domain_list',
            'certificate',
            'privkey',
            'ca_chain',
            'letsencrypt',
            'https_only',
            'letsencrypt_test',
            'debug_challenges',
            'php_fpm_service_name',
            'rsyslogd_config_dir',
            'user_home_dir',
            'http',
            'https',
            'uid',
            'gid'
        ]:
            self.debug(f"{p} = '{getattr(self, p, '*NOT SET*')}'")
