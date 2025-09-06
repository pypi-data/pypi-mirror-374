from jinja2 import Template
import os
import subprocess
import logging


from lib.raw.web.config import WebConfiguration


def cron_file_for_user(username: str) -> str:

    filename = f"/etc/cron.weekly/vh_{username}.sh"

    logging.debug(
        f"cron_file_for_user(username='{username}') = '{filename}'"
    )

    return filename


def cron_file_exists(username: str) -> bool:

    result = os.path.exists(cron_file_for_user(username))

    logging.debug(
        f"cron_file_exists(username='{username}') [{cron_file_for_user(username)}] = {result}"
    )

    return result


def delete_cron_file_for_user(username: str) -> bool:

    logging.debug(
        f"delete_cron_file_for_user(username='{username}')"
    )

    try:

        if os.path.exists(cron_file_for_user(username)):
            subprocess.run(
                [
                    "/usr/bin/sudo",
                    "/usr/bin/rm",
                    "-f",
                    cron_file_for_user(username)
                ],
                timeout=10
            )

        result = True

    except subprocess.CalledProcessError as e1:

        logging.error(
            f"delete_cron_file_for_user(): EXCEPTION: {str(e1)}"
        )
        result = False

    return result


def configure_cron(config: WebConfiguration):
    """Create cron configuration for user.
    """

    config.debug(f"configure_cron(username='{config.username}')")

    cron_conf = cron_file_for_user(config.username)
    cron_template_file = f"{config.vg_tools_etc_dir}/vh_cron.sh"

    with open(cron_template_file, 'r') as tpl:
        cron_template_data = tpl.read()

    cron_template = Template(cron_template_data)

    result = cron_template.render(
        username=config.username,
        domain=config.domain_name,
        virtualhosts_root=config.virtualhosts_root,
        apache_vhost_config_dir=config.apache_vhost_config_dir,
        apache_vhost_enabled_dir=config.apache_vhost_enabled_dir,
        php_fpm_pool_config_dir=config.php_fpm_pool_config_dir,
        vg_tools_etc_dir=config.vg_tools_etc_dir,
        webmaster_email=config.webmaster_email,
        server_alias=config.server_alias,
        certificate_file=config.certificate,
        privkey_file=config.privkey,
        ca_chain_file=config.ca_chain,
        letsencrypt=config.letsencrypt,
        https_only=config.https_only,
        letsencrypt_test=config.letsencrypt_test,
        php_fpm_service_name=config.php_fpm_service_name,
        rsyslogd_config_dir=config.rsyslogd_config_dir,
        user_home_dir=config.user_home_dir,
        http=config.http,
        https=config.https,
    )

    with open(cron_conf, 'w') as outfile:
        outfile.write(f"{result}\n")

    os.chown(cron_conf, 0, 0)
    os.chmod(cron_conf, mode=0o555)
