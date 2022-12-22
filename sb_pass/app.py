import logging
import sys
from pathlib import Path

import gui
import pyperclip
import rumps
from config import Config
from gpg import Gpg

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

APP_NAME = "sb_pass"
MAX_ATTEMPTS = 3
MAX_RECENTS = 10


class Status(rumps.App):
    def __init__(self, name, title=None, icon=None, template=None, menu=None):
        super().__init__(name, title, icon, template, menu, quit_button=None)
        config_path = Path(rumps.application_support(APP_NAME)) / "config.json"
        self._config = Config(config_path)
        self._recents = gui.RecentMenuItem("Recents", max_recents=MAX_RECENTS)
        self.create_menu(Path(self._config.store_home))
        self._gpg: Gpg | None = None

    def _configure_gpg(self) -> None:
        """Configure GPG class"""
        binary_path = self._config.gpg_binary_path
        gpg_home_path = self._config.gpg_home

        while not Path(binary_path).is_file():
            binary_path = self._get_gpg_binary_path_from_user()
            if binary_path is None:
                self._show_no_binary_quitting_window()
            self._config.gpg_binary_path = binary_path

        while not Path(gpg_home_path).is_dir():
            gpg_home_path = self._get_gpg_home_path_from_user()
            self._config.gpg_home = gpg_home_path

        self._gpg = Gpg(gpg_home_path=gpg_home_path, binary_path=binary_path)

    def create_menu(self, root: Path) -> list[gui.PathMenuItem]:
        """Create the main menu"""
        _quit = rumps.MenuItem("Quit", rumps.quit_application)
        self.menu.clear()
        self._recents.reset()
        options = self._create_options_entries()
        gpg_keys = self._create_gpg_key_entries(root)
        self.menu = [
            self._recents,
            {"Options": options},
            None,
            {"Passwords": gpg_keys},
            None,
            _quit,
        ]

    def _create_options_entries(self) -> list[rumps.MenuItem]:
        """Return the menu options"""
        return [
            rumps.MenuItem(
                "Set GPG Binary Path", callback=self._set_gpg_binary_path_callback
            ),
            rumps.MenuItem(
                "Set GPG Home Directory", callback=self._set_gpg_home_path_callback
            ),
            rumps.MenuItem(
                "Set Pass Store Directory",
                callback=self._set_pass_store_dir_callback,
            ),
        ]

    def _create_gpg_key_entries(self, root: Path) -> list[gui.PathMenuItem]:
        """Recursively create the menus and submenus from .gpg and directories"""
        entries = self._get_gpg_key_paths(root)
        menu = []
        for path in entries:
            if path.is_file():
                menu.append(
                    gui.PathMenuItem(path.stem, path, self._gpg_key_clicked_callback)
                )
            elif path.is_dir():
                submenu = self._create_gpg_key_entries(path)
                menu.append([path.name, submenu])
        return menu

    def _get_gpg_key_paths(self, root: Path) -> list[Path]:
        """Return list of GPG paths within root"""
        entries = [x for x in root.glob("*") if self._menu_filter(x)]
        return sorted(entries, key=lambda x: (x.is_dir(), x))

    def _menu_filter(self, path: Path) -> bool:
        """Return True if we want to keep the path"""
        if path.is_dir() and not path.name.startswith("."):
            return True
        if path.is_file() and path.suffix == ".gpg":
            return True
        return False

    def _set_gpg_home_path_callback(self, _) -> None:
        """Set the gpg home path from user input"""
        path = self._get_gpg_home_path_from_user()
        if path is None or path == self._config.gpg_home:
            return

        self._config.gpg_home = path
        self._gpg.set_gpg_home_path(gpg_home_path=self._config.gpg_home)

    def _get_gpg_home_path_from_user(self) -> str:
        """Show prompt to get the gpg home path"""
        return gui.show_get_path(
            msg="Please enter the path to your GPG Home directory.\n\nWe try to use a "
            "sensible default here, but you can check yours by typing `gpg --version` "
            "from the command line and checking the `Home:`  value.",
            title="Set GPG Home Directory",
            default_text=self._config.gpg_home,
            obj_type="dir",
        )

    def _set_gpg_binary_path_callback(self, _) -> None:
        """Set the gpg binary path from user input"""
        path = self._get_gpg_binary_path_from_user()
        if path is None or path == self._config.gpg_binary_path:
            return

        self._config.gpg_binary_path = path
        if self._gpg:
            self._gpg.set_gpg_binary_path(path=self._config.gpg_binary_path)

    def _get_gpg_binary_path_from_user(self) -> str:
        """Show prompt to get the GPG Binary path"""
        result = gui.show_get_path(
            msg=(
                "Please enter path to the gpg binary.\n\nYou can open a terminal and use "
                "`which gpg` to determine this."
            ),
            title="Enter GPG Binary Path",
            default_text=self._config.gpg_binary_path,
            obj_type="file",
        )
        return result

    def _show_no_binary_quitting_window(self) -> None:
        """Show user a window indicating application will quit b/c of no gpg binary"""
        gui.show_message_with_ok_button(
            "The GPG Binary is required for use and since none was entered, the "
            "application will now exit.",
            title="No GPG Binary entered",
        )
        rumps.quit_application()

    def _set_pass_store_dir_callback(self, _) -> None:
        """Get password store dir from user and store it"""
        path = self._get_pass_store_dir_from_user_input()
        if path is None or path == self._config.store_home:
            return

        self._config.store_home = path
        log.info("Set pass dir to %s", self._config.store_home)
        self.create_menu(Path(self._config.store_home))

    def _get_pass_store_dir_from_user_input(self) -> str:
        """Show prommpt to get the password store directory"""
        return gui.show_get_path(
            msg="Please enter the path to your pass directory",
            title="Set Password Store Directory",
            default_text=self._config.store_home,
            obj_type="dir",
        )

    def _gpg_key_clicked_callback(self, sender: gui.PathMenuItem):
        """Callback when gpg key entry is clicked"""
        # Prefer user get to choose GPG/Create dir if it doesn't exist b/c otherwise
        # GPG will create it automatically w/ a bunch of GPG stuff
        if not self._gpg:
            self._configure_gpg()

        for attempt_num in range(MAX_ATTEMPTS):
            resp = gui.get_user_passphrase(sender.path, attempt_num + 1, MAX_ATTEMPTS)
            if resp.clicked == gui.CANCEL:
                return

            password = self._gpg.decrypt_key(sender.path, resp.text)
            if not password:
                log.warning("Invalid Passphrase for %s", sender.path)
                continue

            if resp.clicked == gui.SHOW:
                gui.show_full_pass_contents(sender.title, password)
                return

            pyperclip.copy(password.split()[0])
            self._recents.add_recent(sender)
            # NOTE: Seems to show notification in notification center, but doesn't
            # pop up
            rumps.notification(
                title="Password Copied",
                subtitle="COPIED SUB",
                message=f"Copied {sender.path.name} to Clipboard",
            )
            return


def main():
    app = Status("🔐")
    app.run()


if __name__ == "__main__":
    main()
