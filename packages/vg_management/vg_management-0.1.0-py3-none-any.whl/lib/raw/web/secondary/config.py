
from typing import Optional

from raw.util.config import ProgramConfiguration
from raw.web.secondary.defaults import *
from raw.web.defaults import *


class SecondaryConfiguration(ProgramConfiguration):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.database_file: str = DEFAULT_VG_TOOLS_SECONDARY_DB_FILENAME
        self.remote: Optional[str] = None
        self.list: bool = False
        self.add: bool = False
        self.delete: bool = False
        self.replicate: bool = False
        self.virtualhosts_root: str = DEFAULT_VIRTUALHOSTS_ROOT
        self.apache_vhost_config_dir: str = DEFAULT_APACHE_SITES_AVAILABLE
        self.apache_vhost_enabled_dir: str = DEFAULT_APACHE_SITES_ENABLED
        self.php_fpm_pool_config_dir: str = DEFAULT_PHP_FPM_CONFIG_DIR
        self.vg_tools_etc_dir: str = DEFAULT_VG_TOOLS_ETC_DIR
        self.php_fpm_service: str = DEFAULT_PHP_FPM_SERVICE_NAME
        self.rsyslogd_config_dir: str = DEFAULT_RSYSLOG_CONFIG_DIR
        self.ssh_port = 22
        self.ssh_user = "root"


    def dump_for_debugging(self):

        super().dump_for_debugging()

        for p in [
            'database_file',
            'remote',
            'list',
            'add',
            'delete',
            'replicate',
            'virtualhosts_root',
            'apache_vhost_config_dir',
            'apache_vhost_enabled_dir',
            'php_fpm_pool_config_dir',
            'vg_tools_etc_dir',
            'php_fpm_service',
            'rsyslogd_config_dir',
            'ssh_port',
            'ssh_user'
        ]:
            self.debug(f"{p} = '{getattr(self, p, '*NOT SET*')}'")
