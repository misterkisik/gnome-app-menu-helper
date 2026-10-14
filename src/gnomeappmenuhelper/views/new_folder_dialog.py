"""
NewFolderDialog for creating a brand new application folder in GNOME app grid.
"""

from typing import Callable, Optional, List
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

from gnomeappmenuhelper.models import AppItem
from gnomeappmenuhelper.i18n import tr


class NewFolderDialog(Adw.Window):
    def __init__(
        self,
        parent_window: Gtk.Window,
        all_apps: dict,
        initial_selected_apps: Optional[List[str]],
        target_page_idx: int,
        on_created: Callable[[str, List[str], int], None]
    ):
        super().__init__(transient_for=parent_window, modal=True)
        self.all_apps = all_apps
        self.target_page_idx = target_page_idx
        self.on_created = on_created
        self.selected_apps = set(initial_selected_apps or [])

        self.set_title(tr("new_folder_modal_title"))
        self.set_default_size(480, 560)
        self.set_destroy_with_parent(True)

        toolbar_view = Adw.ToolbarView()
        self.set_content(toolbar_view)

        header_bar = Adw.HeaderBar()
        toolbar_view.add_top_bar(header_bar)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        content.set_margin_start(20)
        content.set_margin_end(20)
        content.set_margin_top(16)
        content.set_margin_bottom(20)

        # 1. Folder Name Entry
        name_group = Adw.PreferencesGroup()
        name_group.set_title(tr("new_folder_prompt"))

        name_row = Adw.ActionRow()
        self.name_entry = Gtk.Entry()
        self.name_entry.set_placeholder_text(tr("new_folder_placeholder"))
        self.name_entry.set_hexpand(True)
        name_row.add_suffix(self.name_entry)
        name_group.add(name_row)
        content.append(name_group)

        # 2. Select Apps
        apps_group = Adw.PreferencesGroup()
        apps_group.set_title("Приложения для включения в папку / Apps to include")

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(tr("search_placeholder"))
        self.search_entry.connect("search-changed", self._on_search_changed)
        apps_group.add(self.search_entry)

        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_child(self.list_box)
        apps_group.add(scroll)

        content.append(apps_group)

        # Bottom Bar
        bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        bottom.set_margin_start(20)
        bottom.set_margin_end(20)
        bottom.set_margin_top(12)
        bottom.set_margin_bottom(16)

        btn_cancel = Gtk.Button(label=tr("btn_cancel"))
        btn_cancel.connect("clicked", lambda _b: self.close())
        bottom.append(btn_cancel)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        bottom.append(spacer)

        btn_create = Gtk.Button(label=f"✨ {tr('btn_new_folder')}")
        btn_create.add_css_class("suggested-action")
        btn_create.connect("clicked", self._on_create_clicked)
        bottom.append(btn_create)

        toolbar_view.add_bottom_bar(bottom)
        toolbar_view.set_content(content)

        self._populate_list()

    def _populate_list(self, filter_text: str = ""):
        child = self.list_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.list_box.remove(child)
            child = next_child

        query = filter_text.lower().strip()
        for app_id, app in sorted(self.all_apps.items(), key=lambda x: x[1].name.lower()):
            if query and query not in app.name.lower() and query not in app.description.lower():
                continue

            row = Adw.ActionRow()
            row.set_title(app.name)
            if app.description:
                row.set_subtitle(app.description)

            if app.gicon:
                img = Gtk.Image.new_from_gicon(app.gicon)
            elif app.icon_name:
                img = Gtk.Image.new_from_icon_name(app.icon_name)
            else:
                img = Gtk.Image.new_from_icon_name("application-x-executable")
            img.set_pixel_size(28)
            row.add_prefix(img)

            check = Gtk.CheckButton()
            check.set_active(app_id in self.selected_apps)

            def make_toggle(aid):
                return lambda ch: self._on_toggle(aid, ch.get_active())

            check.connect("toggled", make_toggle(app_id))
            row.add_suffix(check)
            row.set_activatable_widget(check)

            self.list_box.append(row)

    def _on_toggle(self, app_id: str, is_active: bool):
        if is_active:
            self.selected_apps.add(app_id)
        else:
            self.selected_apps.discard(app_id)

    def _on_search_changed(self, entry):
        self._populate_list(entry.get_text())

    def _on_create_clicked(self, _btn):
        name = self.name_entry.get_text().strip() or tr("folder_untitled")
        self.close()
        self.on_created(name, list(self.selected_apps), self.target_page_idx)
