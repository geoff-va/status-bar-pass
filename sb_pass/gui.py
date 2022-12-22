from pathlib import Path

import rumps
from rumps.rumps import Response

CANCEL = 0
OK = 1
SHOW = 2


class PathMenuItem(rumps.MenuItem):
    """A MenuItem that stores a Path"""

    def __init__(
        self,
        title,
        path: Path,
        callback=None,
        key=None,
        icon=None,
        dimensions=None,
        template=None,
    ):
        super().__init__(title, callback, key, icon, dimensions, template)
        self.path = path


class RecentMenuItem(rumps.MenuItem):
    """A Menu to hold the last N most recently accessed items"""

    def __init__(
        self,
        title,
        max_recents,
        callback=None,
        key=None,
        icon=None,
        dimensions=None,
        template=None,
    ):
        super().__init__(title, callback, key, icon, dimensions, template)
        self._none_item = rumps.MenuItem("None")
        self.add(self._none_item)
        self._max_items = max_recents

    def reset(self) -> None:
        """Reset the recents menu"""
        self.clear()
        self.add(self._none_item)

    def add_recent(self, item: PathMenuItem) -> None:
        """Add entry to the most recently used items"""
        if self._none_item.title in self:
            self._replace_empty(item)
            return

        if item.title in self:
            self._move_to_top(item)
        else:
            self._add_to_top(item)

    def _replace_empty(self, item: PathMenuItem) -> None:
        """Replaces the default None item with the incoming item"""
        self.clear()
        self.add(PathMenuItem(item.title, item.path, item.callback))

    def _move_to_top(self, item: PathMenuItem) -> None:
        """Moves existing item to the top of the menu"""
        existing = self.pop(item.title)
        if len(self.keys()) == 0:
            self.add(existing)
            return

        front = self.values()[0]
        self.insert_before(front.title, existing)

    def _add_to_top(self, item: PathMenuItem) -> None:
        """Add a new entry to the top of the menu"""
        front = self.values()[0]
        self.insert_before(
            front.title, PathMenuItem(item.title, item.path, item.callback)
        )
        if len(self) > self._max_items:
            self.pop(self.values()[-1].title)


def get_user_passphrase(path: Path, attempt_num: int, max_attempts: int) -> Response:
    win = rumps.Window(
        f"Please enter passphrase (Attempt {attempt_num}/{max_attempts})",
        title="Enter Passphrase",
        cancel=True,
        secure=True,
        dimensions=(300, 25),
        ok="Copy",
    )
    win.add_button("Show")
    resp = win.run()
    return resp


def show_get_path(msg: str, title: str, default_text: str, obj_type: str) -> str:
    """Show a gui to get a path based on obj_type"""
    msg_txt = msg
    while True:
        win = rumps.Window(
            msg_txt,
            title=title,
            cancel=True,
            dimensions=(300, 25),
            default_text=default_text,
        )
        resp = win.run()

        if not resp.clicked:
            return

        path = Path(resp.text)

        if obj_type == "dir":
            if not path.is_dir():
                msg_txt = f"Directory does not exist.\n{msg}"
                continue

        elif obj_type == "file":
            if not path.is_file():
                msg_txt = f"File does not exist.\n{msg}"
                continue

        else:
            raise ValueError(f"Unsupport obj_type: {obj_type}. Must be 'dir' or 'file'")

        return resp.text


def show_full_pass_contents(key_name: str, password: str) -> None:
    """Show the full password contents"""
    win = rumps.Window(
        f"Password",
        title=key_name,
        cancel=False,
        default_text=password,
    )
    win.run()


def show_message_with_ok_button(msg: str, title: str) -> None:
    """Shows an alert window with message, title and OK button"""
    win = rumps.Window(msg, title=title, cancel=False, dimensions=(0, 0))
    win.run()
