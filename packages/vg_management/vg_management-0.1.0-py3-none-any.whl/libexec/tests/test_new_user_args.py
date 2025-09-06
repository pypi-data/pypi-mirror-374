import pytest
import sys
import os
from lib.raw.web.config import WebConfiguration
from lib.raw.web.defaults import *

sys.path.append(os.path.abspath(".."))

from libexec.new_user import parse_command_line


@pytest.mark.parametrize('case', [
    (
        [
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-r",
            "/tmp/blarg",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                "/tmp/blarg",
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-a",
            "/tmp/snarf",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          "/tmp/snarf",
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-e",
            "/tmp/abc123",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         "/tmp/abc123",
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-p",
            "/tmp/blarg99",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          "/tmp/blarg99",
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-x",
            "/tmp/blarg85",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       "/tmp/blarg85",
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-d",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        True,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-l",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      True,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-c",
            "/etc/hosts",
            "-k",
            "/etc/motd",
            "-n",
            "/etc/resolv.conf",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      "/etc/hosts",
            "privkey":                          "/etc/motd",
            "ca_chain":                         "/etc/resolv.conf",
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-s",
            "-c",
            "/etc/hosts",
            "-k",
            "/etc/motd",
            "-n",
            "/etc/resolv.conf",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      "/etc/hosts",
            "privkey":                          "/etc/motd",
            "ca_chain":                         "/etc/resolv.conf",
            "https_only":                       True,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-t",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      True,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 True,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-g",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 True,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "-f",
            "banana",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  "banana",
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "--loglevel",
            "DEBUG",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         "DEBUG",
            "custom_loglevel":                  None,
            "server_alias_list":                None
        }
    ),
    (
        [
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com",
            "alias1.xyz.com,alias2.snarf.com"
        ],
        {
            "username":                         "baldrick",
            "domain_list":                      ["www.baldrick.com", "alias1.xyz.com", "alias2.snarf.com"],
            "webmaster_email":                  "webmaster@baldrick.com",
            "virtualhosts_root":                DEFAULT_VIRTUALHOSTS_ROOT,
            "apache_vhost_config_dir":          DEFAULT_APACHE_SITES_AVAILABLE,
            "apache_vhost_enabled_dir":         DEFAULT_APACHE_SITES_ENABLED,
            "php_fpm_pool_config_dir":          DEFAULT_PHP_FPM_CONFIG_DIR,
            "vg_tools_etc_dir":                       DEFAULT_VG_TOOLS_ETC_DIR,
            "debugging":                        False,
            "letsencrypt":                      False,
            "certificate":                      None,
            "privkey":                          None,
            "ca_chain":                         None,
            "https_only":                       False,
            "letsencrypt_test":                 False,
            "debug_challenges":                 False,
            "php_fpm_service":                  DEFAULT_PHP_FPM_SERVICE_NAME,
            "loglevel":                         DEFAULT_LOGLEVEL,
            "custom_loglevel":                  None,
            "server_alias_list":                "alias1.xyz.com,alias2.snarf.com"
        }
    ),

])
def test_new_user_argparse(case):

    # print("")
    # print(case[0])
    # print("")

    config: WebConfiguration = WebConfiguration()

    # noinspection PyTypeChecker
    parse_command_line(case[0], config)

    for attr in case[1].keys():

        # print(f"attr: '{attr}'; expected: '{case[1][attr]}'; actual: '{getattr(config, attr)}'")
        assert getattr(config, attr) == case[1][attr]


@pytest.mark.parametrize('case', [
    (
        [
            "-s",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "-c",
            "/etc/hosts",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "-k",
            "/etc/hosts",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "-n",
            "/etc/hosts",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "-l",
            "-c",
            "/etc/hosts",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "-l",
            "-k",
            "/etc/hosts",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "-l",
            "-n",
            "/etc/hosts",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "-l",
            "-s",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "--https-only",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "--certificate",
            "/tmp/yadayada123",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "--privkey",
            "/tmp/yadayada123",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),
    (
        [
            "--ca-chain",
            "/tmp/yadayada123",
            "baldrick",
            "webmaster@baldrick.com",
            "www.baldrick.com"
        ],
        RuntimeError
    ),

])
def test_new_user_argparse_fail(case):

    config = WebConfiguration()

    with pytest.raises(case[1]):
        # noinspection PyTypeChecker
        parse_command_line(case[0], config)
