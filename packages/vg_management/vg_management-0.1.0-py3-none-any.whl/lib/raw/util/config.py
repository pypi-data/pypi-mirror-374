import argparse
import sys
import os
from io import TextIOWrapper
import logging
from logging.handlers import SysLogHandler
import inspect


DEFAULT_CONFIGURATION_FILE = "/etc/vg_tools.conf"


class ProgramConfiguration(argparse.Namespace):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.debugging = False
        self.logger = None
        self.loglevel = 'INFO'
        self.custom_loglevel = None
        self.log_level_numeric = logging.INFO


    @classmethod
    def _caller_details(cls):

        return inspect.stack()[2].filename, inspect.stack()[2].lineno, inspect.stack()[2].function


    def dump_for_debugging(self):

        self.debug(f"debugging = '{self.debugging}'")
        self.debug(f"loglevel = '{self.loglevel}'")
        self.debug(f"custom_loglevel = '{self.custom_loglevel}'")
        self.debug(f"log_level_numeric = '{self.log_level_numeric}'")


    def init_logging(self, program_name=""):

        self.logger = logging.getLogger()

        # Work out a numeric value for the selected log level
        try:
            self.log_level_numeric = getattr(logging, self.loglevel.upper())
        except:
            self.log_level_numeric = logging.INFO

        self.logger.setLevel(self.log_level_numeric)

        # Create syslog handler
        syslog_handler = SysLogHandler(
            address="/dev/log",
            facility=SysLogHandler.LOG_LOCAL6
        )

        syslog_formatter = logging.Formatter(
            f"{program_name}[%(process)d] <%(myfilename)s:%(myfunction)s:%(mylineno)d>: %(levelname)s: %(message)s"
        )

        syslog_handler.setFormatter(syslog_formatter)

        # Create console handler
        console_handler = logging.StreamHandler(stream=sys.stderr)


        console_formatter = logging.Formatter(
            f"{program_name}[%(process)d] <%(myfilename)s:%(myfunction)s:%(mylineno)d>: %(levelname)s: %(message)s"
        )

        console_handler.setFormatter(console_formatter)

        if self.debugging:

            console_handler.setLevel(logging.DEBUG)

        else:

            console_handler.setLevel(logging.WARNING)

        self.logger.addHandler(syslog_handler)
        self.logger.addHandler(console_handler)

        # Set custom log level for specified loggers
        if (self.custom_loglevel is not None and
                isinstance(self.custom_loglevel, dict) and
                len(self.custom_loglevel) > 0):

            for spec in self.custom_loglevel:

                logger_name, new_level = spec.split(':')
                this_logger = logging.getLogger(logger_name)
                numeric_custom_level = getattr(logging, new_level.upper(), None)
                this_logger.setLevel(numeric_custom_level)


    def set_logger(self, logger):

        self.logger = logger


    def debug(self, *args, **kwargs):

        if self.logger is not None:

            file, line, function = ProgramConfiguration._caller_details()
            kwargs["extra"] = dict(myfilename=file, mylineno=line, myfunction=function)
            self.logger.debug(*args, **kwargs)


    def info(self, *args, **kwargs):

        if self.logger is not None:

            file, line, function = ProgramConfiguration._caller_details()
            kwargs["extra"] = dict(myfilename=file, mylineno=line, myfunction=function)
            self.logger.info(*args, **kwargs)


    def warn(self, *args, **kwargs):

        if self.logger is not None:

            file, line, function = ProgramConfiguration._caller_details()
            kwargs["extra"] = dict(myfilename=file, mylineno=line, myfunction=function)
            self.logger.warn(*args, **kwargs)


    def error(self, *args, **kwargs):

        if self.logger is not None:

            file, line, function = ProgramConfiguration._caller_details()
            kwargs["extra"] = dict(myfilename=file, mylineno=line, myfunction=function)
            self.logger.error(*args, **kwargs)


    def critical(self, *args, **kwargs):

        if self.logger is not None:

            file, line, function = ProgramConfiguration._caller_details()
            kwargs["extra"] = dict(myfilename=file, mylineno=line, myfunction=function)
            self.logger.critical(*args, **kwargs)

    def print_vars(self, f: TextIOWrapper):

        for attr in dir(self):

            value = getattr(self, attr)

            if (isinstance(value, str) or
                    isinstance(value, int) or
                    isinstance(value, bool) or
                    isinstance(value, list) or
                    isinstance(value, dict) or
                    isinstance(value, tuple) or
                    value is None):

                print(f"{attr:<25} : {value}", file=f)


    def debug_vars(self):

        for attr in dir(self):

            value = getattr(self, attr)

            if (isinstance(value, str) or
                    isinstance(value, int) or
                    isinstance(value, bool) or
                    isinstance(value, list) or
                    isinstance(value, dict) or
                    isinstance(value, tuple) or
                    value is None):

                self.debug(f"{attr} : {value}")


def auto_add_config_fromfile(argv, config_file, c='+'):

    fromfile_exists = False

    for arg in argv:

        if len(arg) > 0 and arg[0] == c:

            fromfile_exists = True

    if os.path.exists(config_file) and not fromfile_exists:

        argv.insert(1, f"{c}{config_file}")
