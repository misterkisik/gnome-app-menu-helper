"""
CatalogDialog displaying all installed applications and unplaced apps pool.
Allows searching, placing apps onto active page, and toggling hidden state.
"""

from typing import Callable, Optional, List
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

from gnomeappmenuhelper.models import AppItem
from gnomeappmenuhelper.i18n import tr


class CatalogDialog(Adw.Window):
    def __init__(
        self,
        parent_window: Gtk.Window,
        backend,
        current_page_idx: int,
        on_app_added_to_page: Callable[[str, int], None],
        on_toggle_hide: Callable[[str], None],
    ):
        super().__init__(transient_for=parent_window, modal=True)
        self.backend = backend
        self.current_page_idx = current_page_idx
        self.on_app_added_to_page = on_app_added_to_page
        self.on_toggle_hide = on_toggle_hide

        self.set_title(tr("pool_title"))
        self.set_default_size(560, 640)
        self.set_destroy_with_parent(True)

        toolbar_view = Adw.ToolbarView()
        self.set_content(toolbar_view)

        header_bar = Adw.HeaderBar()
        toolbar_view.add_top_bar(header_bar)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_start(20)
        content.set_margin_end(20)
        content.set_margin_top(14)
        content.set_margin_bottom(16)

        # Search Bar
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(tr("search_placeholder"))
        self.search_entry.connect("search-changed", self._on_filter_changed)
        content.append(self.search_entry)

        # Filters Row
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)

        self.check_hidden = Gtk.CheckButton(label=tr("pool_hidden_filter"))
        self.check_hidden.set_active(False)
        self.check_hidden.connect("toggled", self._on_filter_changed)
        filter_box.append(self.check_hidden)

        self.check_unassigned = Gtk.CheckButton(label="Только неразмещённые / Only unplaced")
        self.check_unassigned.set_active(False)
        self.check_unassigned.connect("toggled", self._on_filter_changed)
        filter_box.append(self.check_unassigned)

        content.append(filter_box)

        # Applications List
        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_child(self.list_box)
        content.append(scroll)

        # Bottom Bar
        bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bottom.set_margin_start(20)
        bottom.set_margin_end(20)
        bottom.set_margin_top(10)
        bottom.set_margin_bottom(14)

        self.status_label = Gtk.Label()
        self.status_label.add_css_class("dim-label")
        bottom.append(self.status_label)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        bottom.append(spacer)

        btn_close = Gtk.Button(label=tr("btn_close"))
        btn_close.connect("clicked", lambda _b: self.close())
        bottom.append(btn_close)

        toolbar_view.add_bottom_bar(bottom)
        toolbar_view.set_content(content)

        self._populate()

    def _get_item_placement(self, app_id: str) -> str:
        for p_idx, page in enumerate(self.backend.pages):
            if app_id in page:
                return f"Стр. {p_idx + 1}"
        for folder in self.backend.folders.values():
            if app_id in folder.apps:
                return f"📁 {folder.name}"
        return "Не размещено"

    def _populate(self):
        child = self.list_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.list_box.remove(child)
            child = next_child

        query = self.search_entry.get_text().lower().strip()
        show_hidden_only = self.check_hidden.get_active()
        show_unassigned_only = self.check_unassigned.get_active()

        count = 0
        for app_id, app in sorted(self.backend.apps.items(), key=lambda x: x[1].name.lower()):
            if show_hidden_only and not app.nodisplay:
                continue

            placement = self._get_item_placement(app_id)
            if show_unassigned_only and placement != "Не размещено":
                continue

            if query:
                match = (query in app.name.lower()) or (query in app.description.lower()) or (query in app_id.lower())
                if not match:
                    continue

            count += 1
            row = Adw.ActionRow()
            row.set_title(app.name)

            sub = f"{app_id} • {placement}"
            if app.nodisplay:
                sub += " • [Скрыто]"
            row.set_subtitle(sub)

            # Icon
            if app.gicon:
                img = Gtk.Image.new_from_gicon(app.gicon)
            elif app.icon_name:
                img = Gtk.Image.new_from_icon_name(app.icon_name)
            else:
                img = Gtk.Image.new_from_icon_name("application-x-executable")
            img.set_pixel_size(32)
            row.add_prefix(img)

            # Action Buttons: Add to current page & Hide/Unhide
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

            btn_add = Gtk.Button(label=f"+ {tr('pool_add_btn')}")
            btn_add.add_css_class("flat")
            def make_add_cb(aid):
                return lambda _b: self._on_add(aid)
            btn_add.connect("clicked", make_add_cb(app_id))
            btn_box.append(btn_add)

            btn_hide = Gtk.Button(label="👁️")
            btn_hide.add_css_class("flat")
            btn_hide.set_tooltip_text(tr("ctx_unhide_app") if app.nodisplay else tr("ctx_hide_app"))
            def make_hide_cb(aid):
                return lambda _b: self._on_hide(aid)
            btn_hide.connect("clicked", make_hide_cb(app_id))
            btn_box.append(btn_hide)

            row.add_suffix(btn_box)
            self.list_box.append(row)

        self.status_label.set_text(f"Всего приложений: {count}")

    def _on_filter_changed(self, _w):
        self._populate()

    def _on_add(self, app_id: str):
        self.on_app_added_to_page(app_id, self.current_page_idx)
        self._populate()

    def _on_hide(self, app_id: str):
        self.on_toggle_hide(app_id)
        self._populate()
