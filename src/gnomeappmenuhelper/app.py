"""
GnomeAppMenuHelper Application Entry
Initializes Libadwaita application, loads theme CSS and presents the main window.
"""

import sys
import os
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, Gio

from gnomeappmenuhelper.window import MainWindow

APP_CSS = """
.gnome-app-canvas {
    background: #18181d;
}

.gnome-app-tile {
    border-radius: 20px;
    padding: 10px;
    transition: background-color 150ms ease-out;
}

.gnome-app-tile:hover {
    background-color: rgba(255, 255, 255, 0.12);
}

.gnome-app-tile:active {
    background-color: rgba(255, 255, 255, 0.20);
}

.gnome-app-tile.hidden-app {
    opacity: 0.5;
}

.gnome-app-label {
    color: #ffffff;
    font-size: 13px;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
}

.gnome-folder-tile {
    border-radius: 20px;
    padding: 10px;
    transition: background-color 150ms ease-out;
}

.gnome-folder-tile:hover {
    background-color: rgba(255, 255, 255, 0.12);
}

.gnome-folder-preview-box {
    background-color: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 20px;
    min-width: 68px;
    min-height: 68px;
}

.nav-arrow-btn {
    min-width: 48px;
    min-height: 48px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #ffffff;
    font-size: 24px;
    font-weight: bold;
    transition: all 150ms ease-out;
}

.nav-arrow-btn:hover {
    background: rgba(255, 255, 255, 0.22);
    border-color: rgba(255, 255, 255, 0.35);
}

.nav-arrow-btn:disabled {
    opacity: 0.18;
    background: rgba(255, 255, 255, 0.02);
}

.page-dot-btn {
    min-width: 8px;
    min-height: 8px;
    padding: 0;
    margin: 4px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.35);
    border: none;
    transition: all 200ms ease;
}

.page-dot-btn.active {
    min-width: 28px;
    background: #3584e4;
}

.page-dot-btn:hover:not(.active) {
    background: rgba(255, 255, 255, 0.65);
}

.gnome-bottom-bar {
    background-color: rgba(0, 0, 0, 0.28);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding: 10px 20px;
}
"""


class GnomeAppMenuHelperApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="org.cleanarch.GnomeAppMenuHelper",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )

    def do_startup(self):
        Adw.Application.do_startup(self)
        self._load_css()

    def _load_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(APP_CSS.encode("utf-8"))
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def do_activate(self):
        win = self.get_active_window()
        if not win:
            win = MainWindow(application=self)
        win.present()


def main():
    app = GnomeAppMenuHelperApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
