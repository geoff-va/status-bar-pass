from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import mock

import pytest

from sb_pass import gpg as _gpg

_GPG_HOME = TemporaryDirectory(prefix="gpg_home_")
_BINARY_PATH = NamedTemporaryFile(prefix="gpg_binary_")


@pytest.fixture
def mock_gpg():
    mock_gpg = mock.patch("sb_pass.gpg.gnupg.GPG")
    yield mock_gpg.start()
    mock_gpg.stop()


def test_gpg_created_with_proper_args(mock_gpg):
    _gpg.Gpg(_GPG_HOME, _BINARY_PATH)

    mock_gpg.assert_called_with(
        gnupghome=_GPG_HOME,
        use_agent=True,
        gpgbinary=_BINARY_PATH,
    )


def test_set_gpg_binary_path_creates_gpg_with_new_path(mock_gpg):
    new_path = "/some/new/binary/path"
    gpg = _gpg.Gpg(_GPG_HOME, _BINARY_PATH)
    mock_gpg.reset_mock()

    gpg.set_gpg_binary_path(new_path)

    assert gpg._gpg_binary_path == new_path
    mock_gpg.assert_called_with(
        gnupghome=_GPG_HOME,
        use_agent=True,
        gpgbinary=new_path,
    )


def test_set_gpg_home_path_creates_gpg_with_new_path(mock_gpg):
    new_path = "/some/new/home/path/"
    gpg = _gpg.Gpg(_GPG_HOME, _BINARY_PATH)
    mock_gpg.reset_mock()

    gpg.set_gpg_home_path(new_path)

    assert gpg._gpg_home_path == new_path
    mock_gpg.assert_called_with(
        gnupghome=new_path,
        use_agent=True,
        gpgbinary=_BINARY_PATH,
    )


def test_decrypt_key_no_passphrase_excludes_from_kwargs(mock_gpg):
    gpg = _gpg.Gpg(_GPG_HOME, _BINARY_PATH)
    tmp_file = NamedTemporaryFile(prefix="gpg_key", suffix=".gpg")
    expected = {"fileobj_or_path": tmp_file.name}

    gpg.decrypt_key(tmp_file.name)

    gpg._gpg.decrypt_file.assert_called_with(**expected)


def test_decrypt_key_with_passphrase_includes_in_kwargs(mock_gpg):
    gpg = _gpg.Gpg(_GPG_HOME, _BINARY_PATH)
    tmp_file = NamedTemporaryFile(prefix="gpg_key", suffix=".gpg")
    expected = {"fileobj_or_path": tmp_file.name, "passphrase": "test"}

    gpg.decrypt_key(tmp_file.name, passphase="test")

    gpg._gpg.decrypt_file.assert_called_with(**expected)
