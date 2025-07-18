"""Submodule containing all the utilities for validating and parsing the configuration"""

import os
from enum import Enum, auto
from typing import Tuple
import re
from pathlib import Path
import logging as log
from xdg import BaseDirectory
import yaml

from freeports_analysis.i18n import _

from .consts import ENV_PREFIX, PdfFormats

_logger = log.getLogger(__name__)


def _local_config():
    # 1. Check local config file
    patterns = [
        r"^\.?(config|conf)[-\._]?freeports\.ya?ml$",
        r"^\.?freeports[-\._]?(config|conf)\.ya?ml$",
    ]

    for patter in patterns:
        for file_name in os.listdir("."):
            if not re.match(patter, file_name, re.IGNORECASE):
                continue
            local_file = os.path.abspath(file_name)
            if not os.path.isfile(local_file):
                continue
            return Path(local_file)
    return None


def _standard_config():
    config_dirs = []
    # For Linux/Unix-like systems (including macOS)
    # 2. Check XDG config directories for 'freeports.yaml' directly
    if os.name == "posix":
        # XDG config directories
        config_dirs = BaseDirectory.load_config_paths("")

    # For Windows systems
    elif os.name == "nt":
        # Local AppData (user-specific config)
        local_appdata = os.environ.get("LOCALAPPDATA") or os.path.expanduser(
            "~\\AppData\\Local"
        )
        config_dirs.append(local_appdata)

        # ProgramData (system-wide config)
        program_data = os.environ.get("PROGRAMDATA") or "C:\\ProgramData"
        config_dirs.append(program_data)

    for config_dir in config_dirs:
        for file_name in ["freeports.yaml", "freeports.yml"]:
            config_path = os.path.join(config_dir, file_name)
            _logger.debug(
                _("Searching `xdg`/`Windows` compliant conf file: '%s'"), config_path
            )
            if os.path.isfile(config_path):
                return Path(config_path)
    return None


def _system_config():
    system_paths = []
    if os.name == "posix":
        # 3. Fallback to /etc/freeports.yaml
        system_paths = ["/etc/freeports.yaml", "/etc/freeports.yml"]
    elif os.name == "nt":
        system_paths = [
            os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "freeports.yaml"),
            os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "freeports.yml"),
        ]

    for system_path in system_paths:
        _logger.debug("Searching system wise conf file: '%s'", system_path)
        if os.path.isfile(system_path):
            return Path(system_path)
    return None


def _find_config():
    config_file = _local_config()
    if config_file is not None:
        _logger.debug(_("Found local conf file: '%s'"), config_file)
        return config_file

    config_file = _standard_config()
    if config_file is not None:
        _logger.debug(_("Found `xdg`/`Windows` compliant conf file: '%s'"), config_file)
        return config_file

    config_file = _system_config()
    if config_file is not None:
        _logger.debug(_("Found system wise conf file: '%s'"), config_file)
        return config_file

    # 4. Not found
    _logger.debug(
        _("Configuration not found in default location, `CONFIG_FILE` set to `None`")
    )
    return None


DEFAULT_CONFIG = {
    "VERBOSITY": 2,
    # `SEPARATE_OUT_FILES` default to `False` because command line args permits to set only to `True`
    "SEPARATE_OUT_FILES": False,
    "N_WORKERS": os.process_cpu_count(),
    "BATCH": None,
    "PREFIX_OUT": None,
    "OUT_CSV": Path("/dev/stdout")
    if os.name == "posix"
    else "CON"
    if os.name == "nt"
    else None,
    # `SAVE_PDF` default to `True` because command line args permits to set only to `False`
    "SAVE_PDF": True,
    "URL": None,
    "PDF": None,
    "FORMAT": None,
    "CONFIG_FILE": _find_config(),
}


schema_yaml_config = {
    "verbosity": ("VERBOSITY", int),
    "n_workers": ("N_WORKERS", int),
    "pdf": ("PDF", Path),
    "url": ("URL", str),
    "batch_path": ("BATCH", Path),
    "separate_out": ("SEPARATE_OUT_FILES", bool),
    "out_path": ("OUT_CSV", Path),
    "save_pdf": ("SAVE_PDF", bool),
    "format": ("FORMAT", lambda x: PdfFormats.__members__[x.strip()]),
}


def _str_to_bool(string: str) -> bool:
    true_list = ["true", "yes", "on", "t", "y", "1"]
    false_list = ["false", "no", "off", "f", "n", "0"]
    string = string.strip().lower()
    if string in true_list:
        return True
    if string in false_list:
        return False

    error_string = _("'{}' is not castable to `True` {} nor `False` {}").format(
        string, true_list, false_list
    )
    raise ValueError(error_string)


schema_env_config = {
    f"{ENV_PREFIX}URL": ("URL", str),
    f"{ENV_PREFIX}VERBOSITY": ("VERBOSITY", int),
    f"{ENV_PREFIX}N_WORKERS": ("N_WORKERS", int),
    f"{ENV_PREFIX}BATCH": ("BATCH", Path),
    f"{ENV_PREFIX}SEPARATE_OUT": ("SEPARATE_OUT_FILES", _str_to_bool),
    f"{ENV_PREFIX}OUT_CSV": ("OUT_CSV", Path),
    f"{ENV_PREFIX}SAVE_PDF": ("SAVE_PDF", _str_to_bool),
    f"{ENV_PREFIX}FORMAT": ("FORMAT", lambda x: PdfFormats.__members__[x.strip()]),
    f"{ENV_PREFIX}PDF": ("PDF", Path),
    f"{ENV_PREFIX}CONFIG_FILE": ("CONFIG_FILE", Path),
}

schema_job_csv_config = {
    "url": ("URL", str),
    "save pdf": ("SAVE_PDF", _str_to_bool),
    "format": ("FORMAT", lambda x: PdfFormats.__members__[x.strip()]),
    "pdf": ("PDF", Path),
    "prefix out": ("PREFIX_OUT", str),
}


class PossibleLocationConfig(Enum):
    """Rappresent from where the options can come from"""

    DEFAULT = auto()
    CONFIG_FILE = auto()
    ENV_VAR = auto()
    CMD_ARG = auto()
    JOB_OVERWRITE = auto()


DEFAULT_LOCATION_CONFIG = {k: PossibleLocationConfig.DEFAULT for k in DEFAULT_CONFIG}


def log_config(logger: log.Logger, config: dict, config_location: dict):
    """Log with debug priority the configuration provided

    Parameters
    ----------
    logger : log.Logger
        the logger that has to log
    """
    logger.debug(
        _("Resulting config: %s"),
        {k: (v, config_location[k].name) for k, v in config.items()},
    )


def overwrite_with_config_file(
    config: dict, config_location: dict
) -> Tuple[dict, dict]:
    """Overwrite configuration provided and update the dictionary containing
    from where the configuration are loaded from accordingly, using the configuration file

    Parameters
    ----------
    config : dict
        configuration to overwrite
    config_location : dict
        location of configuration to update

    Returns
    -------
    Tuple[dict,dict]
        first `dict` is the new configuration, second is the updated location `dict`
    """
    yaml_from_file = None
    config_file = config["CONFIG_FILE"]
    if config_file is not None:
        with config["CONFIG_FILE"].open("r", encoding="UTF-8") as f:
            yaml_from_file = yaml.safe_load(f)
        for key, v in yaml_from_file.items():
            conf_name, cast = schema_yaml_config[key]
            config[conf_name] = cast(v)
            config_location[conf_name] = PossibleLocationConfig.CONFIG_FILE
    return config, config_location


def overwrite_with_env_vars(config: dict, config_location: dict) -> Tuple[dict, dict]:
    """Overwrite configuration provided and update the dictionary containing
    from where the configuration are loaded from accordingly, using environment variables

    Parameters
    ----------
    config : dict
        configuration to overwrite
    config_location : dict
        location of configuration to update

    Returns
    -------
    Tuple[dict,dict]
        first `dict` is the new configuration, second is the updated location `dict`
    """
    for key, (opt_name, cast) in schema_env_config.items():
        v = os.environ.get(key)
        if v is not None:
            config[opt_name] = cast(v)
            config_location[opt_name] = PossibleLocationConfig.ENV_VAR
    return config, config_location


def apply_config(config: dict, config_location: dict) -> Tuple[dict, dict]:
    """Update configuration and `dict` rappresenting from where the configuration is loaded
    using the configuration file and the environment variables

    Parameters
    ----------
    config : dict
        configuration to overwrite
    config_location : dict
        location of configuration to update

    Returns
    -------
    Tuple[dict,dict]
        first `dict` is the new configuration, second is the updated location `dict`
    """
    config, config_location = overwrite_with_config_file(config, config_location)
    config, config_location = overwrite_with_env_vars(config, config_location)
    return config, config_location


def get_config_file(config: dict, config_location: dict) -> Tuple[dict, dict]:
    """Overwrite the configuration and the `dict` that rappresent from where the configuration
    is loaded on the `CONFIG_FILE` entry. This has to be parsed before overwriting all the other
    options in order to set the correct configuration file to load

    Parameters
    ----------
    config : dict
        configuration to overwrite
    config_location : dict
        location of configuration to update

    Returns
    -------
    Tuple[dict,dict]
        first `dict` is the new configuration, second is the updated location `dict`
    """
    env_conf_file = os.environ.get(f"{ENV_PREFIX}CONFIG_FILE")
    if env_conf_file is not None:
        config["CONFIG_FILE"] = env_conf_file
        config_location["CONFIG_FILE"] = PossibleLocationConfig.ENV_VAR
    return config, config_location


def validate_conf(config: dict):
    """Function that validate the configuration provided

    Parameters
    ----------
    config : dict
        configuration to validate

    Raises
    ------
    ValueError
        verbosity must be in [0:5]
    ValueError
        at least one location for input file (from url or local filesystem) should be specified
    ValueError
        invalid out path
    ValueError
        invalid batch file path
    ValueError
        if in `BATCH MODE` out path has to be directory or `.tar.gz` archive
    """
    verb = config["VERBOSITY"]
    if verb > 5 or verb < 0:
        err_str = _("Verbosity must be between 0 and 5, resulting is {}").format(verb)
        raise ValueError(err_str)
    batch_path = config["BATCH"]
    out_path = config["OUT_CSV"]
    if config["URL"] is None and config["PDF"] is None:
        string = _("You have to specify at least one input option: ")
        string += _("the url or the resource, the pdf file path or both")
        raise ValueError(string)
    if not out_path.parent.exists():
        raise ValueError(
            _("Out path is not valid because directory '{}' doesn't exists").format(
                out_path.parent
            )
        )
    if batch_path is not None:
        if not batch_path.exists() or not batch_path.is_file():
            raise ValueError(_("Batch '{}' has to be existent file").format(batch_path))
        if config["SEPARATE_OUT_FILES"]:
            if "." in out_path.name and not out_path.name.endswith(".tar.gz"):
                err_str = _(
                    "Out file in `BATCH MODE` should be directory or `.tar.gz` file"
                )
                err_str += _(" if `SEPARATE_OUT_FILES` not set to '{}'").format(
                    out_path
                )
                raise ValueError(err_str)
