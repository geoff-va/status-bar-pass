import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from sb_pass import config
from sb_pass.config import Config


@pytest.fixture
def conf(root):
    return config.Config(root)


class TestGettingDefaults:
    """Tests for default values when existing entries do not exist"""

    def test_empty_config(self, conf: Config):
        assert conf._settings == {}
        assert conf.reload_settings() == {}

    def test_default_store_home(self, conf: Config):
        assert conf.store_home == config._DEFAULT_STORE_HOME

    def test_default_gpg_home(self, conf: Config):
        assert conf.gpg_home == config._DEFAULT_GPG_HOME

    def test_default_max_recent_items(self, conf: Config):
        assert conf.max_recent_items == config._DEFAULT_MAX_RECENT_ITEMS

    def test_default_gpg_binary_path(self, conf: Config):
        assert conf.gpg_binary_path == config._DEFAULT_GPG_BINARY_PATH


class TestSettingConfigValues:
    """Tests for setting config values"""

    def test_setting_store_home(self, conf: Config):
        expected = "/some/test/new_store_home/"

        conf.store_home = expected

        assert conf.store_home == expected
        assert conf.reload_settings() == {conf.STORE_HOME: expected}

    def test_setting_gpg_home(self, conf: Config):
        expected = "/some/test/new_gpg_home/"

        conf.gpg_home = expected

        assert conf.gpg_home == expected
        assert conf.reload_settings() == {conf.GPG_HOME: expected}

    def test_setting_gpg_binary_path(self, conf: Config):
        expected = "/some/test/gpg_binary_path"

        conf.gpg_binary_path = expected

        assert conf.gpg_binary_path == expected
        assert conf.reload_settings() == {conf.GPG_BINARY_PATH: expected}


def test_store_settings_commits_settings(conf: Config):
    """_store_settings sets internal dict value and commits it"""
    key = "new-setting"
    value = "new-value"

    conf._store_setting(key, value)

    assert conf._settings[key] == value
    assert conf.reload_settings() == {key: value}


def test_existing_settings_are_loaded():
    """When settings already exist, they are loaded"""
    existing = {
        Config.GPG_BINARY_PATH: "/some/gpg/binary/path",
        Config.GPG_HOME: "/some/gpg/home/path/",
        Config.STORE_HOME: "/some/store/home/path/",
    }
    with NamedTemporaryFile(prefix="settings_", suffix=".json", mode="w") as settings:
        with open(settings.name, "w") as fout:
            json.dump(existing, fout)

        conf = Config(Path(settings.name))

        assert conf._settings == existing
