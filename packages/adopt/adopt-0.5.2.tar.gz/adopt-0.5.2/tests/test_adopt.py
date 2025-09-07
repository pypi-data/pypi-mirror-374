import os
import subprocess
import sys

import pytest

from adopt.azure_devops import create_connection
from adopt.config import ADO_ORG_URL_VAR, ADO_PAT_VAR

PYTHON_EXE = sys.executable


def test_connect():
    url = os.getenv(ADO_ORG_URL_VAR)
    token = os.getenv(ADO_PAT_VAR)
    create_connection(organization_url=url, token_password=token)
    # TODO: do better testing on connection


def test_import_package():
    """Test basic import of package."""
    import adopt  # noqa: F401


@pytest.mark.console
def test_console_help():
    """Calls help file of console script and tests for failure."""
    process = subprocess.run(
        [PYTHON_EXE, '-m', 'adopt', '--help'],
        capture_output=True,
        universal_newlines=True,
    )
    assert process.returncode == 0, process.stderr
