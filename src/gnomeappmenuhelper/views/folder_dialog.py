"""
FolderDialog for managing apps within a folder, renaming, adding apps, or unpacking/deleting.
"""

from typing import Callable, Optional, List
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

from gnomeappmenuhelper.models import FolderItem, AppItem
from gnomeappmenuhelper.i18n import tr


class FolderDialog(Adw.Window):
    def __init__(
        self,
        parent_window: Gtk.Window,
        folder: FolderItem,
        all_apps: dict,
        on_rename: Callable[[str, str], None],
        on_remove_app: Callable[[str, str], None],
        on_add_apps: Callable[[str, List[str]], None],
        on_delete_folder: Callable[[str], None],
    ):
        super().__init__(transient_for=parent_window, modal=True)
        self.folder = folder
        self.all_apps = all_apps
        self.on_rename = on_rename
        self.on_remove_app = on_remove_app
        self.on_add_apps = on_add_apps
        self.on_delete_folder = on_delete_folder

        self.set_title(tr("folder_edit_dialog_title"))
        self.set_default_size(520, 580)
        self.set_destroy_with_parent(True)

        toolbar_view = Adw.ToolbarView()
        self.set_content(toolbar_view)

        # Header Bar
        header_bar = Adw.HeaderBar()
        toolbar_view.add_top_bar(header_bar)

        # Main Layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(20)

        # 1. Folder Name Group
        name_group = Adw.PreferencesGroup()
        name_group.set_title(tr("folder_name_label"))

        name_row = Adw.ActionRow()
        self.name_entry = Gtk.Entry()
        self.name_entry.set_text(self.folder.name)
        self.name_entry.set_hexpand(True)
        self.name_entry.connect("changed", self._on_name_changed)

        btn_save_name = Gtk.Button(label=tr("btn_save"))
        btn_save_name.add_css_class("suggested-action")
        btn_save_name.connect("clicked", lambda _b: self._save_name())

        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        name_box.append(self.name_entry)
        name_box.append(btn_save_name)
        name_row.add_suffix(name_box)
        name_group.add(name_row)
        main_box.append(name_group)

        # 2. Apps in Folder Group
        self.apps_group = Adw.PreferencesGroup()
        self._update_apps_group_title()

        # Add Apps Action Row
        add_row = Adw.ActionRow()
        add_row.set_title(tr("folder_add_apps_btn"))
        add_btn = Gtk.Button(label="+")
        add_btn.add_css_class("suggested-action")
        add_btn.add_css_class("circular")
        add_btn.connect("clicked", self._on_open_add_apps_picker)
        add_row.add_suffix(add_btn)
        add_row.set_activatable_widget(add_btn)
        self.apps_group.add(add_row)

        # Scrolled apps list
        self.rows_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self._populate_app_rows()
        self.apps_group.add(self.rows_box)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_child(main_box)
        toolbar_view.set_content(scroll)

        # Bottom Bar: Delete Folder Button
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        bottom_bar.set_margin_start(20)
        bottom_bar.set_margin_end(20)
        bottom_bar.set_margin_top(12)
        bottom_bar.set_margin_bottom(16)

        btn_del = Gtk.Button(label=f"🗑️ {tr('folder_delete_btn')}")
        btn_del.add_css_class("destructive-action")
        btn_del.connect("clicked", self._on_delete_clicked)
        bottom_bar.append(btn_del)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        bottom_bar.append(spacer)

        btn_close = Gtk.Button(label=tr("btn_close"))
        btn_close.connect("clicked", lambda _b: self.close())
        bottom_bar.append(btn_close)

        toolbar_view.add_bottom_bar(bottom_bar)

    def _update_apps_group_title(self):
        count = len(self.folder.apps)
        self.apps_group.set_title(tr("folder_apps_in_folder", count=count))

    def _on_name_changed(self, _entry):
        pass

    def _save_name(self):
        new_name = self.name_entry.get_text().strip()
        if new_name and new_name != self.folder.name:
            self.folder.name = new_name
            self.on_rename(self.folder.id, new_name)

    def _populate_app_rows(self):
        # Clear existing rows
        child = self.rows_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.rows_box.remove(child)
            child = next_child

        for app_id in self.folder.apps:
            app: Optional[AppItem] = self.all_apps.get(app_id)
            name = app.name if app else app_id
            desc = app.description if app else ""

            row = Adw.ActionRow()
            row.set_title(name)
            if desc:
                row.set_subtitle(desc)

            # Icon
            if app and app.gicon:
                img = Gtk.Image.new_from_gicon(app.gicon)
            elif app and app.icon_name:
                img = Gtk.Image.new_from_icon_name(app.icon_name)
            else:
                img = Gtk.Image.new_from_icon_name("application-x-executable")
            img.set_pixel_size(32)
            row.add_prefix(img)

            # Remove from folder button
            btn_remove = Gtk.Button(label="✕")
            btn_remove.add_css_class("flat")
            btn_remove.add_css_class("circular")
            btn_remove.set_tooltip_text("Убрать из папки / Remove from folder")

            def make_remove_cb(aid):
                return lambda _b: self._remove_app(aid)

            btn_remove.connect("clicked", make_remove_cb(app_id))
            row.add_suffix(btn_remove)

            self.rows_box.append(row)

    def _remove_app(self, app_id: str):
        self.on_remove_app(self.folder.id, app_id)
        self._update_apps_group_title()
        self._populate_app_rows()

    def _on_delete_clicked(self, _btn):
        self.close()
        self.on_delete_folder(self.folder.id)

    def _on_open_add_apps_picker(self, _btn):
        # Dialog to pick apps to add
        picker = AddAppsPickerWindow(self, self.all_apps, self.folder.apps, self._on_apps_picked)
        picker.present()

    def _on_apps_picked(self, picked_ids: List[str]):
        if picked_ids:
            self.on_add_apps(self.folder.id, picked_ids)
            self._update_apps_group_title()
            self._populate_app_rows()


class AddAppsPickerWindow(Adw.Window):
    def __init__(
        self,
        parent: Gtk.Window,
        all_apps: dict,
        existing_apps: List[str],
        on_selected: Callable[[List[str]], None]
    ):
        super().__init__(transient_for=parent, modal=True)
        self.all_apps = all_apps
        self.existing_apps = set(existing_apps)
        self.on_selected = on_selected
        self.selected_apps = set()

        self.set_title(tr("folder_add_apps_btn"))
        self.set_default_size(440, 500)

        toolbar_view = Adw.ToolbarView()
        self.set_content(toolbar_view)

        header_bar = Adw.HeaderBar()
        toolbar_view.add_top_bar(header_bar)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(12)
        content.set_margin_bottom(16)

        # Search Entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(tr("search_placeholder"))
        self.search_entry.connect("search-changed", self._on_search_changed)
        content.append(self.search_entry)

        # List
        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_child(self.list_box)
        content.append(scroll)

        # Bottom Bar
        bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_cancel = Gtk.Button(label=tr("btn_cancel"))
        btn_cancel.connect("clicked", lambda _b: self.close())
        bottom.append(btn_cancel)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        bottom.append(spacer)

        self.btn_add = Gtk.Button(label=tr("folder_add_apps_btn"))
        self.btn_add.add_css_class("suggested-action")
        self.btn_add.connect("clicked", self._on_confirm)
        bottom.append(self.btn_add)
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
            if app_id in self.existing_apps:
                continue
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
            def make_toggle_cb(aid):
                return lambda ch: self._on_toggle(aid, ch.get_active())
            check.connect("toggled", make_toggle_cb(app_id))
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

    def _on_confirm(self, _btn):
        self.close()
        self.on_selected(list(self.selected_apps))
