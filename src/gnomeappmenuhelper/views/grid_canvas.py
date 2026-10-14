"""
GridCanvas component replicating the GNOME Shell App Grid layout.
Features side arrow navigation buttons, responsive FlowBox icon canvas,
and bottom pagination dots.
"""

from typing import Callable, Optional, List, Tuple
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GObject

from gnomeappmenuhelper.backend import AppMenuBackend
from gnomeappmenuhelper.views.app_widget import AppWidget
from gnomeappmenuhelper.views.folder_widget import FolderWidget
from gnomeappmenuhelper.i18n import tr


class GridCanvas(Gtk.Box):
    def __init__(
        self,
        backend: AppMenuBackend,
        on_open_folder: Callable[[str], None],
        on_create_folder_prompt: Callable[[str, str], None],
        on_delete_folder: Callable[[str], None],
        on_toast: Callable[[str], None],
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.backend = backend
        self.on_open_folder = on_open_folder
        self.on_create_folder_prompt = on_create_folder_prompt
        self.on_delete_folder = on_delete_folder
        self.on_toast = on_toast

        self.current_page_idx = 0
        self.search_filter = ""

        self.add_css_class("gnome-app-canvas")
        self.set_vexpand(True)
        self.set_hexpand(True)

        # Top area with Left Arrow, Center Grid Canvas, and Right Arrow
        main_stage = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        main_stage.set_vexpand(True)
        main_stage.set_hexpand(True)
        main_stage.set_margin_start(16)
        main_stage.set_margin_end(16)
        main_stage.set_margin_top(16)
        main_stage.set_margin_bottom(12)

        # Left Nav Arrow Button
        self.btn_prev = Gtk.Button(label="‹")
        self.btn_prev.add_css_class("nav-arrow-btn")
        self.btn_prev.set_valign(Gtk.Align.CENTER)
        self.btn_prev.set_tooltip_text(tr("prev_page_tip"))
        self.btn_prev.connect("clicked", self._on_prev_page)
        main_stage.append(self.btn_prev)

        # Center: Scrolled Window + FlowBox
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)
        self.scrolled.set_hexpand(True)
        self.scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.CENTER)
        self.flowbox.set_halign(Gtk.Align.CENTER)
        self.flowbox.set_row_spacing(18)
        self.flowbox.set_column_spacing(18)
        self.flowbox.set_max_children_per_line(8)
        self.flowbox.set_min_children_per_line(4)
        self.flowbox.set_homogeneous(True)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        self.scrolled.set_child(self.flowbox)
        main_stage.append(self.scrolled)

        # Right Nav Arrow Button
        self.btn_next = Gtk.Button(label="›")
        self.btn_next.add_css_class("nav-arrow-btn")
        self.btn_next.set_valign(Gtk.Align.CENTER)
        self.btn_next.set_tooltip_text(tr("next_page_tip"))
        self.btn_next.connect("clicked", self._on_next_page)
        main_stage.append(self.btn_next)

        self.append(main_stage)

        # Bottom Bar: Page Info, Dots, Page Controls
        self.bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.bottom_bar.add_css_class("gnome-bottom-bar")
        self.bottom_bar.set_valign(Gtk.Align.END)

        # Page Info Label
        self.page_info_label = Gtk.Label()
        self.page_info_label.add_css_class("dim-label")
        self.bottom_bar.append(self.page_info_label)

        # Spacer
        spacer1 = Gtk.Box()
        spacer1.set_hexpand(True)
        self.bottom_bar.append(spacer1)

        # Pagination Dots Box
        self.dots_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.dots_box.set_halign(Gtk.Align.CENTER)
        self.bottom_bar.append(self.dots_box)

        # Spacer
        spacer2 = Gtk.Box()
        spacer2.set_hexpand(True)
        self.bottom_bar.append(spacer2)

        # Page Action Buttons
        page_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.btn_add_page = Gtk.Button(label=f"+ {tr('btn_add_page')}")
        self.btn_add_page.add_css_class("flat")
        self.btn_add_page.connect("clicked", self._on_add_page_clicked)
        page_actions.append(self.btn_add_page)

        self.btn_del_page = Gtk.Button(label=f"🗑️ {tr('btn_del_page')}")
        self.btn_del_page.add_css_class("flat")
        self.btn_del_page.connect("clicked", self._on_del_page_clicked)
        page_actions.append(self.btn_del_page)

        self.bottom_bar.append(page_actions)
        self.append(self.bottom_bar)

        self.refresh()

    def set_search_filter(self, query: str):
        self.search_filter = query.lower().strip()
        self.refresh()

    def set_page(self, page_idx: int):
        total_pages = len(self.backend.pages)
        if total_pages > 0:
            self.current_page_idx = max(0, min(page_idx, total_pages - 1))
            self.refresh()

    def _on_prev_page(self, _btn):
        if self.current_page_idx > 0:
            self.set_page(self.current_page_idx - 1)

    def _on_next_page(self, _btn):
        if self.current_page_idx < len(self.backend.pages) - 1:
            self.set_page(self.current_page_idx + 1)

    def _on_add_page_clicked(self, _btn):
        new_idx = self.backend.add_page()
        self.set_page(new_idx)
        self.on_toast(tr("toast_page_added", num=new_idx + 1))

    def _on_del_page_clicked(self, _btn):
        if len(self.backend.pages) <= 1:
            self.on_toast(tr("toast_cannot_del_last_page"))
            return

        del_idx = self.current_page_idx
        if self.backend.delete_page(del_idx):
            self.set_page(max(0, del_idx - 1))
            self.on_toast(tr("toast_page_deleted"))

    def refresh(self):
        """Re-renders grid canvas for the active page and updates dots and arrows."""
        total_pages = len(self.backend.pages)
        if total_pages == 0:
            self.backend.pages = [[]]
            total_pages = 1

        self.current_page_idx = max(0, min(self.current_page_idx, total_pages - 1))

        # Update Arrow buttons
        self.btn_prev.set_sensitive(self.current_page_idx > 0)
        self.btn_next.set_sensitive(self.current_page_idx < total_pages - 1)

        # Update Page Info
        item_count = len(self.backend.pages[self.current_page_idx])
        info_str = tr("page_info", current=self.current_page_idx + 1, total=total_pages)
        info_str += f" ({item_count} items)"
        self.page_info_label.set_text(info_str)

        # Update Del Page Button Sensitivity
        self.btn_del_page.set_sensitive(total_pages > 1)

        # Rebuild Dots
        child = self.dots_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.dots_box.remove(child)
            child = next_child

        for p in range(total_pages):
            dot_btn = Gtk.Button()
            dot_btn.add_css_class("page-dot-btn")
            if p == self.current_page_idx:
                dot_btn.add_css_class("active")

            def make_dot_cb(page_num):
                return lambda _b: self.set_page(page_num)

            dot_btn.connect("clicked", make_dot_cb(p))
            self.dots_box.append(dot_btn)

        # Clear FlowBox
        child = self.flowbox.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.flowbox.remove(child)
            child = next_child

        # Populate Items
        current_items = self.backend.pages[self.current_page_idx]

        for pos, item_id in enumerate(current_items):
            # Check if filtered by search
            display_name = self.backend.get_item_name(item_id)
            if self.search_filter and self.search_filter not in display_name.lower():
                continue

            if item_id in self.backend.folders:
                folder = self.backend.folders[item_id]
                preview_icons = self.backend.get_folder_preview_icons(folder.id)
                f_widget = FolderWidget(
                    folder=folder,
                    preview_icons=preview_icons,
                    page_idx=self.current_page_idx,
                    pos_idx=pos,
                    on_open_folder=self.on_open_folder,
                    on_move_left=self._move_item_left,
                    on_move_right=self._move_item_right,
                    on_move_to_page=self._move_item_to_page,
                    on_delete_folder=self._delete_folder,
                    on_app_dropped_in_folder=self._on_app_dropped_in_folder,
                    get_page_count=lambda: len(self.backend.pages)
                )
                self.flowbox.append(f_widget)

            elif item_id in self.backend.apps:
                app = self.backend.apps[item_id]
                a_widget = AppWidget(
                    app=app,
                    page_idx=self.current_page_idx,
                    pos_idx=pos,
                    on_move_left=self._move_item_left,
                    on_move_right=self._move_item_right,
                    on_move_to_page=self._move_item_to_page,
                    on_add_to_folder=self._on_add_to_folder,
                    on_create_folder_prompt=self.on_create_folder_prompt,
                    on_remove_from_page=self._on_remove_from_page,
                    on_toggle_hide=self._on_toggle_hide,
                    on_drop_on_app=self._on_drop_on_app,
                    get_page_count=lambda: len(self.backend.pages),
                    get_folders=lambda: [(f.id, f.name) for f in self.backend.folders.values()]
                )
                self.flowbox.append(a_widget)

    # Actions
    def _move_item_left(self, item_id: str, page_idx: int):
        page = self.backend.pages[page_idx]
        if item_id in page:
            idx = page.index(item_id)
            if idx > 0:
                self.backend.move_item_within_page(page_idx, idx, idx - 1)
                self.refresh()

    def _move_item_right(self, item_id: str, page_idx: int):
        page = self.backend.pages[page_idx]
        if item_id in page:
            idx = page.index(item_id)
            if idx < len(page) - 1:
                self.backend.move_item_within_page(page_idx, idx, idx + 1)
                self.refresh()

    def _move_item_to_page(self, item_id: str, source_page: int, target_page: int):
        if self.backend.move_item_to_page(item_id, source_page, target_page):
            self.refresh()
            self.on_toast(tr("page_info", current=target_page + 1, total=len(self.backend.pages)))

    def _on_remove_from_page(self, item_id: str, page_idx: int):
        self.backend.remove_item_from_grid(item_id)
        self.refresh()

    def _on_toggle_hide(self, app_id: str):
        is_hidden = self.backend.toggle_hide_app(app_id)
        self.refresh()
        msg = tr("toast_app_hidden") if is_hidden else tr("toast_app_unhidden")
        self.on_toast(msg)

    def _on_add_to_folder(self, app_id: str, folder_id: str):
        if self.backend.add_app_to_folder(folder_id, app_id):
            self.refresh()
            f_name = self.backend.get_item_name(folder_id)
            self.on_toast(f"Добавлено в «{f_name}»")

    def _delete_folder(self, folder_id: str):
        self.backend.unpack_folder(folder_id, self.current_page_idx)
        self.refresh()
        self.on_toast(tr("toast_folder_deleted"))

    def _on_app_dropped_in_folder(self, source_app_id: str, folder_id: str):
        self._on_add_to_folder(source_app_id, folder_id)

    def _on_drop_on_app(self, source_id: str, target_id: str):
        """When an app is dropped onto another app, offer folder creation or swap."""
        # Check if source is app
        if source_id in self.backend.apps and target_id in self.backend.apps:
            # Prompt folder creation with these two apps
            self.on_create_folder_prompt(source_id, target_id)
        else:
            # Swap positions
            page = self.backend.pages[self.current_page_idx]
            if source_id in page and target_id in page:
                idx1 = page.index(source_id)
                idx2 = page.index(target_id)
                page[idx1], page[idx2] = page[idx2], page[idx1]
                self.refresh()
