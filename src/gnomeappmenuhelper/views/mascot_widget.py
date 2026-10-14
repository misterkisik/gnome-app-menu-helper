"""
MascotWidget component displaying the interactive anime fox-girl assistant (Senko-san)
with speech balloon, status updates, and interactive tips.
"""

import os
from typing import Optional
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk

from gnomeappmenuhelper.i18n import tr


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
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_size_request(240, -1)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.add_css_class("gnome-mascot-box")

        self._current_mood = "idle"
        self._current_kwargs = {}
        self._tip_index = 0

        # 1. Speech Balloon Card
        self.bubble = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.bubble.add_css_class("card")
        self.bubble.add_css_class("mascot-speech-card")
        self.bubble.set_margin_bottom(4)

        # Header with Name
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.set_margin_start(12)
        header.set_margin_end(12)
        header.set_margin_top(10)

        fox_icon = Gtk.Label(label="🦊")
        header.append(fox_icon)

        self.name_label = Gtk.Label(label=tr("mascot_name"))
        self.name_label.add_css_class("heading")
        header.append(self.name_label)
        self.bubble.append(header)

        # Speech Text
        self.speech_label = Gtk.Label()
        self.speech_label.set_wrap(True)
        self.speech_label.set_justify(Gtk.Justification.LEFT)
        self.speech_label.set_margin_start(12)
        self.speech_label.set_margin_end(12)
        self.speech_label.set_margin_bottom(8)
        self.speech_label.add_css_class("body")
        self.bubble.append(self.speech_label)

        # Subtitle caption
        self.sub_label = Gtk.Label(label="✨ Кликни по мне для совета!")
        self.sub_label.set_wrap(True)
        self.sub_label.set_margin_start(12)
        self.sub_label.set_margin_end(12)
        self.sub_label.set_margin_bottom(8)
        self.sub_label.add_css_class("caption")
        self.sub_label.add_css_class("dim-label")
        self.bubble.append(self.sub_label)

        self.append(self.bubble)

        # 2. Mascot Picture
        mascot_path = find_mascot_image_path()
        if mascot_path and os.path.exists(mascot_path):
            self.picture = Gtk.Picture.new_for_filename(mascot_path)
            self.picture.set_can_shrink(True)
            if hasattr(Gtk, "ContentFit"):
                self.picture.set_content_fit(Gtk.ContentFit.CONTAIN)
            self.picture.set_vexpand(True)
            self.picture.set_hexpand(True)
            self.picture.set_cursor(Gdk.Cursor.new_from_name("pointer", None))

            # Click gesture for interactive tip cycling
            click = Gtk.GestureClick.new()
            click.set_button(1)
            click.connect("pressed", self._on_picture_click)
            self.picture.add_controller(click)

            self.append(self.picture)
        else:
            fallback = Gtk.Label(label="🦊")
            fallback.set_vexpand(True)
            self.append(fallback)

        self.set_mood("idle")

    def _on_picture_click(self, _gesture, _n_press, _x, _y):
        tips = ["mascot_tip_1", "mascot_tip_2", "mascot_tip_3", "mascot_idle"]
        key = tips[self._tip_index % len(tips)]
        self._tip_index += 1
        self.set_speech(tr(key), "🦊 Сэнко-сан подсказывает:")

    def set_speech(self, text: str, subtitle: str = ""):
        self.speech_label.set_text(text)
        if subtitle:
            self.sub_label.set_text(subtitle)
            self.sub_label.set_visible(True)

    def set_mood(self, mood: str, **kwargs):
        self._current_mood = mood
        self._current_kwargs = kwargs

        if mood == "idle":
            self.set_speech(tr("mascot_idle"), "✨ Твой уютный помощник")
        elif mood == "applied":
            self.set_speech(tr("mascot_applied"), "🚀 Синхронизировано с GNOME Shell")
        elif mood == "selected":
            count = kwargs.get("count", 0)
            self.set_speech(tr("mascot_selected", count=count), f"🔧 Выбрано: {count}")
        elif mood == "folder_created":
            name = kwargs.get("name", "")
            self.set_speech(tr("mascot_folder_created", name=name), "📁 Папка организована")
        elif mood == "sorted":
            self.set_speech(tr("mascot_sorted"), "✨ Сортировка завершена")
        elif mood == "page_added":
            self.set_speech("Новая страница добавлена! Можно перетаскивать ярлыки! 📄", "📄 Новая страница")
        elif mood == "folder_deleted":
            self.set_speech("Папка расформирована, все приложения снова на странице! 📦", "📦 Распаковано")

    def retranslate(self):
        self.name_label.set_text(tr("mascot_name"))
        self.set_mood(self._current_mood, **self._current_kwargs)
