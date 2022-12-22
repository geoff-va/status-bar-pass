from pathlib import Path

import gnupg


class Gpg:
    def __init__(self, gpg_home_path: str, binary_path: str, use_agent=True) -> None:
        self._use_agent = use_agent
        self._gpg_home_path = gpg_home_path
        self._gpg_binary_path = binary_path
        self._gpg = None
        self._create_gpg()

    def decrypt_key(self, path: Path, passphase=None) -> str:
        """Decrypt gpg file using optional passphrase"""
        kwargs = {"fileobj_or_path": path}
        if passphase:
            kwargs["passphrase"] = passphase
        return str(self._gpg.decrypt_file(**kwargs))

    def set_gpg_home_path(self, path: str) -> None:
        """Recreate GPG interface with the new homedir"""
        self._gpg_home_path = path
        self._create_gpg()

    def set_gpg_binary_path(self, path: str) -> None:
        """Set the gpg binary path and recreate the gpg client"""
        self._gpg_binary_path = path
        self._create_gpg()

    def _create_gpg(self) -> None:
        """Create the GPG client using stored_settings"""
        self._gpg = gnupg.GPG(
            gnupghome=self._gpg_home_path,
            use_agent=self._use_agent,
            gpgbinary=self._gpg_binary_path,
        )
