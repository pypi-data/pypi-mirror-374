from jinja2 import Template
import os
import subprocess


from lib.raw.web.config import WebConfiguration


def configure_logging(config: WebConfiguration):
    """Create rsyslogd configuration file for user.

    :param config:      Configuration information.
    :type config:       WebConfiguration
    """

    log_conf = "{}/virtualhost_{}.conf".format(config.rsyslogd_config_dir, config.username)
    log_template_file = "{}/rsyslog.conf".format(config.vg_tools_etc_dir)

    config.debug(
        f"configure_logging(username='{config.username}') template='{log_template_file}' output='{log_conf}'"
    )

    try:
        with open(log_template_file, 'r') as tpl:
            log_template_data = tpl.read()
    except Exception as e1:
        config.error(
            f"configure_logging(): EXCEPTION (reading template): {str(e1)}"
        )
        raise e1

    log_template = Template(log_template_data)

    result = log_template.render(
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

    try:
        with open(log_conf, 'w') as outfile:
            outfile.write("{}\n".format(result))
    except Exception as e2:
        config.error(
            f"configure_logging(): EXCEPTION (writing output): {str(e2)}"
        )


def rsyslogd_config(
        config: WebConfiguration,
) -> str:
    """Return fully qualified filename of rsyslogd configuration file for specified user.

    :param config:      Configuration information.
    :type config:       WebConfiguration

    :return:            Fully qualified filename of rsyslogd configuration file for specified user.
    :rtype:             str
    """

    filename = f"{config.rsyslogd_config_dir}/virtualhost_{config.username}.conf"

    config.debug(
        f"rsyslogd_config(username='{config.username}',rsyslogd_config_dir='{config.rsyslogd_config_dir}') = "
        f"'{filename}'"
    )

    return filename


def rsyslogd_config_exists(config: WebConfiguration) -> bool:
    """Check to see if rsyslogd configuration file for specified user exists.

    :param config:      Configuration information.
    :type config:       WebConfiguration

    :return:            True if file exists, False otherwise.
    :rtype:             bool
    """

    conf_file = rsyslogd_config(config)
    exists = os.path.lexists(conf_file)

    config.debug(
        f"rsyslogd_config_exists({conf_file}) = {exists}"
    )

    return exists


def delete_rsyslogd_config(config: WebConfiguration) -> bool:
    """Delete rsyslogd configuration file for specified user.

    :param config:      Configuration information.
    :type config:       WebConfiguration

    :return:            True if deletion successful, False otherwise.
    :rtype:             bool
    """

    try:

        if os.path.exists(rsyslogd_config(config)):
            subprocess.run(
                [
                    "/usr/bin/sudo",
                    "/usr/bin/rm",
                    "-f",
                    rsyslogd_config(config)
                ],
                timeout=10
            )

        result = True

    except subprocess.CalledProcessError as e1:

        config.error(
            f"delete_rsyslogd_config(): EXCEPTION: {str(e1)}"
        )

        result = False

    config.debug(
        f"delete_rsyslogd_config({rsyslogd_config(config)}) = {result}"
    )

    return result
