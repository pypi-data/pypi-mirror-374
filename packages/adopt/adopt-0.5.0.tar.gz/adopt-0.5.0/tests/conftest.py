import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from adopt.config import ADO_ORG_URL_VAR, ADO_PAT_VAR, ADO_PROJECT_VAR, ADO_TEAM_VAR

TEST_DIR = Path(__file__).parent
PROJECT_DIR = TEST_DIR.parent
TEST_ENV_FILE = PROJECT_DIR / '.test_env'

__all__ = ['url', 'token', 'project', 'team']


@pytest.fixture(scope='session', autouse=True)
def load_test_env():
    load_dotenv(dotenv_path=TEST_ENV_FILE)


@pytest.fixture(scope='session')
def url(load_test_env):
    return os.environ[ADO_ORG_URL_VAR]


@pytest.fixture(scope='session')
def token(load_test_env):
    return os.environ[ADO_PAT_VAR]


@pytest.fixture(scope='session')
def project(load_test_env):
    return os.environ[ADO_PROJECT_VAR]


@pytest.fixture(scope='session')
def team(load_test_env):
    return os.environ[ADO_TEAM_VAR]
