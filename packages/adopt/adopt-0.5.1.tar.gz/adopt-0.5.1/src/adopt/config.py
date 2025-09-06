import logging
import os
from pathlib import Path

import toml
from dotenv import dotenv_values, find_dotenv

ADO_PAT_VAR = 'ADOPT_AZURE_DEVOPS_PAT'
ADO_ORG_URL_VAR = 'ADOPT_AZURE_DEVOPS_ORGANIZATION_URL'
ADO_PROJECT_VAR = 'ADOPT_AZURE_DEVOPS_PROJECT_NAME'
ADO_TEAM_VAR = 'ADOPT_AZURE_DEVOPS_TEAM_NAME'

CONFIG_ENV_MAPPING = {
    'token': ADO_PAT_VAR,
    'url': ADO_ORG_URL_VAR,
    'project': ADO_PROJECT_VAR,
    'team': ADO_TEAM_VAR,
}

CONFIG_FILE_NAME = '.adopt'
ADOPT_CONFIG_SECTION = 'adopt'

LOGGER = logging.getLogger(__name__)


def _load_config_in_environment(config: dict[str, str]):
    for key, value in config.items():
        if value is not None:
            env_var = CONFIG_ENV_MAPPING.get(key, key)
            os.environ[env_var] = value


def _load_configuration_from_file(file_path: Path) -> dict:
    config_dict = toml.load(file_path)
    # TODO: Add specific configuration for each command
    return config_dict['adopt']


def _load_global_configuration() -> dict:
    user_path = Path.home()
    global_config_path = user_path / CONFIG_FILE_NAME
    if not global_config_path.exists():
        return {}

    LOGGER.debug(f'Loading global configuration from {global_config_path}')
    return _load_configuration_from_file(global_config_path)


def _load_local_configuration() -> dict:
    local_config_path = Path.cwd() / CONFIG_FILE_NAME
    if not local_config_path.exists():
        return {}

    LOGGER.debug(f'Loading local configuration from {local_config_path}')
    return _load_configuration_from_file(local_config_path)


def _load_env_configuration() -> dict:
    env_file = find_dotenv()
    if not env_file:
        return {}

    LOGGER.debug(f'Loading environment configuration from {env_file}')
    return dotenv_values(env_file)


# TODO: logging here is not affected by the provided log level as it is
# executed before the logging is configured in a command
def initialize_configuration():
    """Initialize the configuration for the Azure DevOps project.

    Different locations are checked for configuration files to then set them
    as environment variables to be consumed by the CLI commands.

    The following locations are considered:
    - global configuration file .adopt in the user's home directory
    - local configuration file .adopt in the current working directory
    - environment variables in .env file in the current working directory
    """
    config = {}

    # Load global configuration
    global_config = _load_global_configuration()
    config.update(global_config)

    # Load local configuration
    local_config = _load_local_configuration()
    config.update(local_config)

    # TODO: separate tokens in env and other settings in config file
    env_config = _load_env_configuration()
    config.update(env_config)

    _load_config_in_environment(config)
