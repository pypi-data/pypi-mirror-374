"""
configurations for this project
"""

import logging
from pytconf import Config, ParamCreator


class ConfigSudo(Config):
    """
    Parameters to control whether we use "sudo" or not
    """
    sudo = ParamCreator.create_bool(
        help_string="use sudo?",
        default=True,
    )


class ConfigFlow(Config):
    """
    Parameters to configure the flow of pydmt
    """
    stop_after_error = ParamCreator.create_bool(
        help_string="Should pydmt stop after first error?",
        default=True,
    )


class ConfigReqs(Config):
    """
    Parameters to configure addgin requirements
    """
    reqs_add_dev = ParamCreator.create_bool(
        help_string="add dev requirements?",
        default=False,
    )


class ConfigVenv(Config):
    """
    Parameters to configure how to create virtual environments
    """
    system_site_packages = ParamCreator.create_bool(
        help_string="Allow access to system packages?",
        default=False,
    )
    upgrade_pip = ParamCreator.create_bool(
        help_string="Upgrade pip on virtualenv creation?",
        default=True,
    )
    incremental = ParamCreator.create_bool(
        help_string="Erase venv or work with existing venv?",
        default=True,
    )
    add_dev = ParamCreator.create_bool(
        help_string="add dev requirements?",
        default=False,
    )


class ConfigOutput(Config):
    """
    Parameters to configure the output of pydmt
    """
    verbose = ParamCreator.create_bool(
        help_string="Should output be verbose?",
        default=True,
    )
    print_not = ParamCreator.create_bool(
        help_string="print out what we are not doing",
        default=False,
    )


class ConfigLogging(Config):
    """
    Parameters to control logging
    """
    loglevel = ParamCreator.create_choice(
        choice_list=[
            logging.getLevelName(logging.NOTSET),
            logging.getLevelName(logging.DEBUG),
            logging.getLevelName(logging.INFO),
            logging.getLevelName(logging.WARNING),
            logging.getLevelName(logging.WARN),
            logging.getLevelName(logging.ERROR),
            logging.getLevelName(logging.FATAL),
            logging.getLevelName(logging.CRITICAL),
        ],
        help_string="What log level to use?",
        default=logging.getLevelName(logging.INFO),
    )


class ConfigSubprocess(Config):
    """
    Parameters to configure how we run subprocess
    """
    print_command = ParamCreator.create_bool(
        help_string="print out commands",
        default=False,
    )
    quiet = ParamCreator.create_bool(
        help_string="Suppress output?",
        default=False,
    )


class ConfigApt(Config):
    """
    Parameters to configure how we run apt
    """
    apt_quiet = ParamCreator.create_bool(
        help_string="pass -q=2 to apt",
        default=False,
    )


class ConfigImport(Config):
    """
    Configure how to set PYTHONPATH
    """
    import_cwd = ParamCreator.create_bool(
        help_string="Add . to PYTHONPATH",
        default=True,
    )
    import_home = ParamCreator.create_bool(
        help_string="Add ~/.config/pydmt to PYTHONPATH",
        default=False,
    )
    import_system = ParamCreator.create_bool(
        help_string="Add /etc/pydmt to PYTHONPATH",
        default=False,
    )
