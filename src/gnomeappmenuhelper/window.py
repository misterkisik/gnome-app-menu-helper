"""
GnomeAppMenuHelper MainWindow
Libadwaita Application Window hosting the GNOME App Grid canvas, header bar controls,
and integrated folder/catalog management dialogs.
"""

import os
from typing import Optional, List
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib

from gnomeappmenuhelper.backend import AppMenuBackend
from gnomeappmenuhelper.views.grid_canvas import GridCanvas
from gnomeappmenuhelper.views.folder_dialog import FolderDialog
from gnomeappmenuhelper.views.new_folder_dialog import NewFolderDialog
from gnomeappmenuhelper.views.catalog_dialog import CatalogDialog
from gnomeappmenuhelper.views.language_dialog import FirstRunLanguageDialog
from gnomeappmenuhelper.i18n import tr, add_language_change_listener, is_first_run


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(tr("app_title"))
        self.set_default_size(1080, 720)

        # Backend instance
        self.backend = AppMenuBackend()

        # Toast overlay
        self.toast_overlay = Adw.ToastOverlay()

        # Toolbar View
        self.toolbar_view = Adw.ToolbarView()
        self.toast_overlay.set_child(self.toolbar_view)
        self.set_content(self.toast_overlay)

        # Header Bar
        self.header_bar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header_bar)

        self._build_header_bar()

        # Grid Canvas
        self.grid_canvas = GridCanvas(
            backend=self.backend,
            on_open_folder=self._on_open_folder,
            on_create_folder_prompt=self._on_create_folder_prompt,
            on_delete_folder=self._on_delete_folder,
            on_toast=self.show_toast
        )
        self.toolbar_view.set_content(self.grid_canvas)

        # Listen for runtime language switches
        add_language_change_listener(self._update_ui_strings)

        # Check if first run to present language selection
        GLib.idle_add(self._check_first_run)

    def _check_first_run(self):
        if is_first_run():
            dlg = FirstRunLanguageDialog(self, on_completed=lambda _l: self._update_ui_strings())
            dlg.present()

    def _build_header_bar(self):
        # 1. Apply to GNOME Button (Accent / Suggested Action)
        self.btn_apply = Gtk.Button()
        apply_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        apply_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
        self.apply_label = Gtk.Label(label=tr("btn_apply"))
        apply_box.append(apply_icon)
        apply_box.append(self.apply_label)
        self.btn_apply.set_child(apply_box)
        self.btn_apply.add_css_class("suggested-action")
        self.btn_apply.set_tooltip_text(tr("btn_apply_tooltip"))
        self.btn_apply.connect("clicked", self._on_apply_clicked)
        self.header_bar.pack_start(self.btn_apply)

        # 2. Sort A-Z Button
        self.btn_sort = Gtk.Button()
        sort_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        sort_icon = Gtk.Image.new_from_icon_name("view-sort-ascending-symbolic")
        self.sort_label = Gtk.Label(label=tr("btn_sort_az"))
        sort_box.append(sort_icon)
        sort_box.append(self.sort_label)
        self.btn_sort.set_child(sort_box)
        self.btn_sort.connect("clicked", self._on_sort_clicked)
        self.header_bar.pack_start(self.btn_sort)

        # 3. Search Entry in Title Area
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(tr("search_placeholder"))
        self.search_entry.set_size_request(240, -1)
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.header_bar.set_title_widget(self.search_entry)

        # 4. New Folder Button
        self.btn_new_folder = Gtk.Button()
        folder_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        folder_icon = Gtk.Image.new_from_icon_name("folder-new-symbolic")
        self.new_folder_label = Gtk.Label(label=tr("btn_new_folder"))
        folder_box.append(folder_icon)
        folder_box.append(self.new_folder_label)
        self.btn_new_folder.set_child(folder_box)
        self.btn_new_folder.connect("clicked", self._on_new_folder_clicked)
        self.header_bar.pack_end(self.btn_new_folder)

        # 5. Catalog of All Apps Button
        self.btn_catalog = Gtk.Button()
        cat_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        cat_icon = Gtk.Image.new_from_icon_name("view-app-grid-symbolic")
        self.catalog_label = Gtk.Label(label=tr("btn_unassigned"))
        cat_box.append(cat_icon)
        cat_box.append(self.catalog_label)
        self.btn_catalog.set_child(cat_box)
        self.btn_catalog.connect("clicked", self._on_catalog_clicked)
        self.header_bar.pack_end(self.btn_catalog)

        # 6. Options Menu Button
        self.menu_btn = Gtk.MenuButton()
        self.menu_btn.set_icon_name("open-menu-symbolic")
        self.menu_btn.set_tooltip_text(tr("menu_options_tip"))
        self._build_menu_popover()
        self.header_bar.pack_end(self.menu_btn)

    def _build_menu_popover(self):
        popover = Gtk.Popover()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        # Language
        btn_lang = Gtk.Button(label=f"🌐  {tr('menu_language')}")
        btn_lang.add_css_class("flat")
        btn_lang.connect("clicked", lambda _b: (popover.popdown(), self._open_language_dialog()))
        box.append(btn_lang)

        # Backup
        btn_backup = Gtk.Button(label=f"💾  {tr('menu_backup')}")
        btn_backup.add_css_class("flat")
        btn_backup.connect("clicked", lambda _b: (popover.popdown(), self._create_backup()))
        box.append(btn_backup)

        # Restore
        btn_restore = Gtk.Button(label=f"🔄  {tr('menu_restore')}")
        btn_restore.add_css_class("flat")
        btn_restore.connect("clicked", lambda _b: (popover.popdown(), self._restore_backup()))
        box.append(btn_restore)

        box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # Reset
        btn_reset = Gtk.Button(label=f"⚠️  {tr('menu_reset_default')}")
        btn_reset.add_css_class("flat")
        btn_reset.connect("clicked", lambda _b: (popover.popdown(), self._reset_defaults()))
        box.append(btn_reset)

        box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # About
        btn_about = Gtk.Button(label=f"ℹ️  {tr('menu_about')}")
        btn_about.add_css_class("flat")
        btn_about.connect("clicked", lambda _b: (popover.popdown(), self._show_about()))
        box.append(btn_about)

        popover.set_child(box)
        self.menu_btn.set_popover(popover)

    def show_toast(self, message: str):
        toast = Adw.Toast.new(message)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)

    def _on_apply_clicked(self, _btn):
        if self.backend.save_to_gnome():
            self.show_toast(tr("toast_applied"))
        else:
            self.show_toast("Ошибка сохранения в GNOME Shell")

    def _on_sort_clicked(self, _btn):
        self.backend.sort_alphabetically(self.grid_canvas.current_page_idx)
        self.grid_canvas.refresh()
        self.show_toast(tr("toast_sorted"))

    def _on_search_changed(self, entry):
        self.grid_canvas.set_search_filter(entry.get_text())

    def _on_new_folder_clicked(self, _btn):
        dlg = NewFolderDialog(
            parent_window=self,
            all_apps=self.backend.apps,
            initial_selected_apps=[],
            target_page_idx=self.grid_canvas.current_page_idx,
            on_created=self._on_folder_created
        )
        dlg.present()

    def _on_create_folder_prompt(self, app_id1: str, app_id2: str):
        initial = [app_id1]
        if app_id2 and app_id2 != app_id1:
            initial.append(app_id2)
        dlg = NewFolderDialog(
            parent_window=self,
            all_apps=self.backend.apps,
            initial_selected_apps=initial,
            target_page_idx=self.grid_canvas.current_page_idx,
            on_created=self._on_folder_created
        )
        dlg.present()

    def _on_folder_created(self, name: str, app_ids: List[str], page_idx: int):
        folder = self.backend.create_folder(name, app_ids, page_idx)
        self.grid_canvas.refresh()
        self.show_toast(tr("toast_folder_created", name=folder.name))

    def _on_open_folder(self, folder_id: str):
        folder = self.backend.folders.get(folder_id)
        if not folder:
            return

        dlg = FolderDialog(
            parent_window=self,
            folder=folder,
            all_apps=self.backend.apps,
            on_rename=self._on_rename_folder,
            on_remove_app=self._on_remove_app_from_folder,
            on_add_apps=self._on_add_apps_to_folder,
            on_delete_folder=self._on_delete_folder
        )
        dlg.present()

    def _on_rename_folder(self, folder_id: str, new_name: str):
        self.backend.rename_folder(folder_id, new_name)
        self.grid_canvas.refresh()

    def _on_remove_app_from_folder(self, folder_id: str, app_id: str):
        self.backend.remove_app_from_folder(folder_id, app_id, self.grid_canvas.current_page_idx)
        self.grid_canvas.refresh()

    def _on_add_apps_to_folder(self, folder_id: str, app_ids: List[str]):
        for aid in app_ids:
            self.backend.add_app_to_folder(folder_id, aid)
        self.grid_canvas.refresh()

    def _on_delete_folder(self, folder_id: str):
        self.backend.unpack_folder(folder_id, self.grid_canvas.current_page_idx)
        self.grid_canvas.refresh()
        self.show_toast(tr("toast_folder_deleted"))

    def _on_catalog_clicked(self, _btn):
        dlg = CatalogDialog(
            parent_window=self,
            backend=self.backend,
            current_page_idx=self.grid_canvas.current_page_idx,
            on_app_added_to_page=self._on_app_added_to_page,
            on_toggle_hide=self._on_toggle_hide_app
        )
        dlg.present()

    def _on_app_added_to_page(self, app_id: str, page_idx: int):
        self.backend.add_item_to_page(app_id, page_idx)
        self.grid_canvas.refresh()
        self.show_toast(f"Добавлено на страницу {page_idx + 1}")

    def _on_toggle_hide_app(self, app_id: str):
        is_hidden = self.backend.toggle_hide_app(app_id)
        self.grid_canvas.refresh()
        msg = tr("toast_app_hidden") if is_hidden else tr("toast_app_unhidden")
        self.show_toast(msg)

    def _open_language_dialog(self):
        dlg = FirstRunLanguageDialog(self, on_completed=lambda _l: self._update_ui_strings())
        dlg.present()

    def _create_backup(self):
        path = self.backend.create_backup()
        self.show_toast(tr("toast_backed_up", path=os.path.basename(path)))

    def _restore_backup(self):
        # Check if backup files exist in backup dir
        backup_dir = os.path.expanduser("~/.config/gnomeappmenuhelper/backups")
        if not os.path.exists(backup_dir):
            self.show_toast("Нет сохранённых резервных копий")
            return

        files = sorted(
            [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith(".json")],
            key=os.path.getmtime,
            reverse=True
        )
        if not files:
            self.show_toast("Нет сохранённых резервных копий")
            return

        # Restore latest backup
        latest = files[0]
        if self.backend.restore_backup(latest):
            self.grid_canvas.refresh()
            self.show_toast(tr("toast_restored"))

    def _reset_defaults(self):
        if self.backend.reset_to_gnome_default():
            self.grid_canvas.refresh()
            self.show_toast("Сброшено к стандартам GNOME")

    def _show_about(self):
        about = Adw.AboutDialog()
        about.set_application_name("GnomeAppMenuHelper")
        about.set_developer_name("MisterKisik")
        about.set_version("1.0.0")
        about.set_copyright("© 2026 MisterKisik")
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_comments(GLib.markup_escape_text(tr("about_comments")))
        about.set_application_icon("org.cleanarch.GnomeAppMenuHelper")
        about.set_website("https://github.com/misterkisik/gnome-app-menu-helper")
        about.present(self)

    def _update_ui_strings(self):
        self.set_title(tr("app_title"))
        self.apply_label.set_text(tr("btn_apply"))
        self.btn_apply.set_tooltip_text(tr("btn_apply_tooltip"))
        self.sort_label.set_text(tr("btn_sort_az"))
        self.search_entry.set_placeholder_text(tr("search_placeholder"))
        self.new_folder_label.set_text(tr("btn_new_folder"))
        self.catalog_label.set_text(tr("btn_unassigned"))
        self._build_menu_popover()
        self.grid_canvas.refresh()
