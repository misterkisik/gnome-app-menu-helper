"""
MascotWidget component displaying the anime fox-girl (Senko-san) centered and scaled
in the side area of the GNOME application grid.
"""

import os
from typing import Optional
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def find_mascot_image_path() -> Optional[str]:
    """Locates the mascot image on the filesystem."""
    candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "mascot.png")),
        os.path.expanduser("~/.local/share/gnome-app-menu-helper/mascot.png"),
        "/usr/share/gnome-app-menu-helper/mascot.png",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


class MascotWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_size_request(320, -1)
        self.set_margin_start(4)
        self.set_margin_end(4)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.add_css_class("gnome-mascot-box")

        mascot_path = find_mascot_image_path()
        if mascot_path and os.path.exists(mascot_path):
            self.picture = Gtk.Picture.new_for_filename(mascot_path)
            self.picture.set_can_shrink(True)
            if hasattr(Gtk, "ContentFit"):
                self.picture.set_content_fit(Gtk.ContentFit.CONTAIN)
            self.picture.set_valign(Gtk.Align.CENTER)
            self.picture.set_halign(Gtk.Align.CENTER)
            self.picture.set_vexpand(True)
            self.picture.set_hexpand(True)
            self.append(self.picture)
        else:
            fallback = Gtk.Box()
            fallback.set_vexpand(True)
            self.append(fallback)

    def set_mood(self, mood: str, **kwargs):
        pass

    def retranslate(self):
        pass
