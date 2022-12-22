from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from sb_pass import config


@pytest.fixture
def root():
    """Return a tmp path to be a config path root"""
    with NamedTemporaryFile(suffix=".json") as tmp:
        return Path(tmp.name)


@pytest.fixture(autouse=True, scope="session")
def _setup_config_defaults():
    """Set default directories to temp dir's"""
    tmp_store_home = TemporaryDirectory(prefix="store_home_").name
    tmp_gpg_home = TemporaryDirectory(prefix="gpg_home_").name

    config._DEFAULT_GPG_HOME = tmp_gpg_home
    config._DEFAULT_STORE_HOME = tmp_store_home
