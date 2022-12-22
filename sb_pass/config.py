import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_WHICH_GPG = shutil.which("gpg")
_DEFAULT_GPG_HOME = os.path.expanduser("~/.gnupg")
_DEFAULT_STORE_HOME = os.path.expanduser("~/.password-store")
_DEFAULT_GPG_BINARY_PATH = "" if _WHICH_GPG is None else _WHICH_GPG
_DEFAULT_MAX_RECENT_ITEMS = 10


class Config:
    GPG_HOME = "gpg_home"
    GPG_BINARY_PATH = "gpg_binary_path"
    STORE_HOME = "store_home"
    MAX_RECENT_ITEMS = "max_recent_items"

    def __init__(self, path: Path) -> None:
        self._settings_path = path
        self._settings = self.reload_settings()

    def reload_settings(self) -> dict:
        """Return current settings content if it exists"""
        if not self._settings_path.exists():
            log.info("No custom settings found at %s", self._settings_path)
            return {}

        with open(self._settings_path) as fin:
            log.info("Loading custom settings from %s", self._settings_path)
            return json.load(fin)

    @property
    def store_home(self) -> str:
        return self._settings.get(self.STORE_HOME, _DEFAULT_STORE_HOME)

    @store_home.setter
    def store_home(self, value: str) -> None:
        self._store_setting(self.STORE_HOME, value)

    @property
    def max_recent_items(self) -> int:
        return self._settings.get("max_recent_items", _DEFAULT_MAX_RECENT_ITEMS)

    @max_recent_items.setter
    def max_recent_items(self, value: int) -> None:
        self._store_setting(self.MAX_RECENT_ITEMS, value)

    @property
    def gpg_home(self) -> str:
        return self._settings.get(self.GPG_HOME, _DEFAULT_GPG_HOME)

    @gpg_home.setter
    def gpg_home(self, value: str) -> None:
        self._store_setting(self.GPG_HOME, value)

    @property
    def gpg_binary_path(self) -> str:
        return self._settings.get(self.GPG_BINARY_PATH, _DEFAULT_GPG_BINARY_PATH)

    @gpg_binary_path.setter
    def gpg_binary_path(self, value: str) -> None:
        self._store_setting(self.GPG_BINARY_PATH, value)

    def _store_setting(self, name: str, value: Any) -> None:
        """Store a setting and commit it to the backend"""
        self._settings[name] = value
        log.info("Updated %s to %s", name, value)
        self._save_settings()

    def _save_settings(self) -> None:
        """Write current settings to storage"""
        with open(self._settings_path, "w") as fout:
            json.dump(self._settings, fout)
        log.info("Wrote settings to %s", self._settings_path)
