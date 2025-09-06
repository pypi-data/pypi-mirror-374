import pytest
import sys
import os
import copy
import pwd
import grp
import subprocess
from lib.raw.web.config import WebConfiguration
from lib.raw.web.user import cleanup_user
from lib.raw.util.user import user_account_exists, get_group_members
from lib.raw.util.hashing import sha256_file
from lib.raw.util.systemd import systemctl_command


sys.path.append(os.path.abspath(".."))

from libexec.new_user import create_site


def _writefile(fn: str, data: str):

    with open(fn, "w") as f:
        f.write(data)

    apache = grp.getgrnam("apache")

    os.chown(fn, 0, apache.gr_gid)
    os.chmod(fn, mode=0o644)


@pytest.fixture()
def conf():

    conf: WebConfiguration = WebConfiguration()

    conf.apache_config = "/usr/local/etc/httpd/conf/httpd.conf"
    conf.virtualhosts_root = f"/usr/local/var/virtualhosts"
    conf.apache_vhost_config_dir = f"/usr/local/etc/httpd/sites-available"
    conf.apache_vhost_enabled_dir = f"/usr/local/etc/httpd/sites-enabled"
    conf.php_fpm_pool_config_dir = f"/usr/local/etc/fpm.d"
    conf.vg_tools_etc_dir = f"/usr/local/etc/raw"
    conf.rsyslogd_config_dir = f"/usr/local/etc/rsyslog.d"

    # Horrible hack to avoid the need to install php73-fpm on dev machine
    conf.php_fpm_service_name = "httpd"

    for u in ["httponly", "mancert"]:

        try:
            tmpconf = copy.deepcopy(conf)
            tmpconf.username = u
            cleanup_user(tmpconf)
        except:
            pass

    print("")
    print("Stopping httpd...")
    systemctl_command("stop", "httpd")

    print("")
    print("Killing httpd...")
    subprocess.run(
        [
            "/usr/bin/sudo",
            "/usr/bin/killall",
            "-9",
            "/usr/sbin/httpd"
        ]
    )
    print("")
    print("Starting httpd...")
    systemctl_command("start", "httpd")

    print("")
    print("Reloading httpd...")
    systemctl_command("reload", "httpd")

    yield conf

    for u in ["httponly", "mancert"]:

        try:
            tmpconf = copy.deepcopy(conf)
            tmpconf.username = u
            cleanup_user(tmpconf)
        except:
            pass


def test_new_user_http_only(conf):

    conf.username = "httponly"
    conf.webmaster_email = "webmaster@baldrick.com"
    conf.domain_name = "baldrick.com"
    conf.domain_name_list = [conf.domain_name]
    # noinspection PyTypeChecker
    conf.user_home_dir = f"{conf.virtualhosts_root}/{conf.username}"
    conf.http = True
    conf.https = False

    # noinspection PyTypeChecker
    create_site(conf, sys.stdout)

    for test_dir in [
        (
            f"{conf.virtualhosts_root}/{conf.username}",
            0o750,
            0,
            grp.getgrnam(conf.username).gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/www",
            0o710,
            pwd.getpwnam(conf.username).pw_uid,
            grp.getgrnam(conf.username).gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/logs",
            0o750,
            0,
            grp.getgrnam(conf.username).gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/ssl",
            0o750,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/backup",
            0o750,
            pwd.getpwnam(conf.username).pw_uid,
            grp.getgrnam(conf.username).gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/dev",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/lib",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/lib64",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/usr",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/var",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/bin",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/usr/bin",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/usr/sbin",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/tmp",
            0o1777,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/usr/share/zoneinfo",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/ca-trust",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/ca-trust/extracted",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/ca-trust/source",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/ca-trust/source/anchors",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/fwupd",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/tls",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/tls/certs",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/tls/private",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/java",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/nssdb",
            0o755,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/pki/rpm-gpg",
            0o755,
            0,
            0
        ),
    ]:

        print("")
        print(f"Directory     : {test_dir[0]}")
        print(f"Expected Mode : {test_dir[1]}")
        print(f"Expected uid  : {test_dir[2]}")
        print(f"Expected gid  : {test_dir[3]}")

        statinfo = os.stat(test_dir[0])
        assert statinfo.st_mode & 0o1777 == test_dir[1]
        assert statinfo.st_uid == test_dir[2]
        assert statinfo.st_gid == test_dir[3]

    for test_file in [
        (
            f"{conf.virtualhosts_root}/{conf.username}/logs/{conf.domain_name}-access.log",
            0o660,
            0,
            grp.getgrnam(conf.username).gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/logs/{conf.domain_name}-error.log",
            0o660,
            0,
            grp.getgrnam(conf.username).gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/logs/{conf.domain_name}-fpm-access.log",
            0o660,
            0,
            grp.getgrnam(conf.username).gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/logs/{conf.domain_name}-fpm-error.log",
            0o660,
            0,
            grp.getgrnam(conf.username).gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/bin/sh",
            0o550,
            0,
            grp.getgrnam(conf.username).gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/usr/sbin/sendmail",
            0o550,
            0,
            grp.getgrnam(conf.username).gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/dev/null",
            0o666,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/dev/zero",
            0o666,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/dev/random",
            0o666,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/dev/urandom",
            0o666,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/dev/tty",
            0o666,
            0,
            grp.getgrnam("tty").gr_gid
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/passwd",
            0o444,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/shadow",
            0o400,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/group",
            0o444,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/host.conf",
            0o644,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/hostname",
            0o644,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/hosts",
            0o644,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/networks",
            0o644,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/nsswitch.conf",
            0o644,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/protocols",
            0o644,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/services",
            0o644,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/localtime",
            0o644,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/usr/share/zoneinfo/Etc/UTC",
            0o644,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/resolv.conf",
            0o644,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/lib64/libc.so",
            0o444,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/lib64/libc.so.6",
            0o444,
            0,
            0
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/lib64/libresolv.so",
            0o444,
            0,
            0
        ),
    ]:

        print("")
        print(f"File          : {test_file[0]}")
        print(f"Expected Mode : {test_file[1]}")
        print(f"Expected uid  : {test_file[2]}")
        print(f"Expected gid  : {test_file[3]}")

        statinfo = os.stat(test_file[0])
        assert statinfo.st_mode & 0o1777 == test_file[1]
        assert statinfo.st_uid == test_file[2]
        assert statinfo.st_gid == test_file[3]

    for hashfile in [
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/host.conf",
            "380f5fe21d755923b44203b58ca3c8b9681c485d152bd5d7e3914f67d821d32a"
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/hosts",
            "081ef9d5367595d16e30b4b4549d9f43537320508b4ce0788963e10e4f808857"
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/networks",
            "ae89ab2e35076a070ae7cf5b0edf600c3ea6999e15db9b543ef35dfc76d37cb1"
        ),
        (
            f"{conf.virtualhosts_root}/{conf.username}/etc/nsswitch.conf",
            "dc7535d475d3fa1ac3f1c1be0ca803422ca7a46b888b78235d4b41b36a046ba3"
        ),
    ]:
        assert sha256_file(hashfile[0]) == hashfile[1]

    assert os.path.exists(f"{conf.apache_vhost_config_dir}/{conf.username}.conf")
    assert os.path.lexists(f"{conf.apache_vhost_enabled_dir}/{conf.username}.conf")
    assert os.path.exists(f"{conf.php_fpm_pool_config_dir}/{conf.username}.conf")
    assert user_account_exists(conf.username)
    assert conf.username in get_group_members("virtualhost")
    assert conf.username in get_group_members("sftp")
