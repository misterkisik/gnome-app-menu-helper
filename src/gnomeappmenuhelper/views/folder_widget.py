"""
FolderWidget component representing an application folder tile in the GNOME app grid.
Displays a 2x2 preview of up to 4 mini-icons inside a squircle container.
Supports drag-to-add, click-to-edit, multi-selection, and right-click context menu.
"""

from typing import Callable, Optional, List, Tuple
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GObject, Pango

from gnomeappmenuhelper.models import FolderItem
from gnomeappmenuhelper.i18n import tr


class FolderWidget(Gtk.Box):
    def __init__(
        self,
        folder: FolderItem,
        preview_icons: List[Optional[Gio.Icon]],
        page_idx: int,
        pos_idx: int,
        is_selected: bool = False,
        is_selection_mode: bool = False,
        on_toggle_select: Optional[Callable[[str], None]] = None,
        get_selected_items: Optional[Callable[[], List[str]]] = None,
        on_open_folder: Optional[Callable[[str], None]] = None,
        on_move_left: Optional[Callable[[str, int], None]] = None,
        on_move_right: Optional[Callable[[str, int], None]] = None,
        on_move_to_page: Optional[Callable[[str, int, int], None]] = None,
        on_move_selected_to_page: Optional[Callable[[List[str], int], None]] = None,
        on_delete_folder: Optional[Callable[[str], None]] = None,
        on_app_dropped_in_folder: Optional[Callable[[str, str], None]] = None,
        on_deselect_all: Optional[Callable[[], None]] = None,
        get_page_count: Optional[Callable[[], int]] = None,
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.folder = folder
        self.preview_icons = preview_icons
        self.page_idx = page_idx
        self.pos_idx = pos_idx
        self.is_selected = is_selected
        self.is_selection_mode = is_selection_mode

        self.on_toggle_select = on_toggle_select
        self.get_selected_items = get_selected_items
        self.on_open_folder = on_open_folder
        self.on_move_left = on_move_left
        self.on_move_right = on_move_right
        self.on_move_to_page = on_move_to_page
        self.on_move_selected_to_page = on_move_selected_to_page
        self.on_delete_folder = on_delete_folder
        self.on_app_dropped_in_folder = on_app_dropped_in_folder
        self.on_deselect_all = on_deselect_all
        self.get_page_count = get_page_count

        self.set_size_request(108, 116)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.add_css_class("gnome-folder-tile")
        self.set_cursor(Gdk.Cursor.new_from_name("pointer", None))

        if self.is_selected:
            self.add_css_class("selected-item")

        # Preview Container Box inside Overlay
        overlay = Gtk.Overlay()
        overlay.set_halign(Gtk.Align.CENTER)
        overlay.set_valign(Gtk.Align.CENTER)
        overlay.set_size_request(66, 66)

        self.preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.preview_box.set_size_request(66, 66)
        self.preview_box.set_halign(Gtk.Align.CENTER)
        self.preview_box.set_valign(Gtk.Align.CENTER)
        self.preview_box.add_css_class("gnome-folder-preview-box")

        # 2x2 Mini-Grid
        if self.preview_icons:
            grid = Gtk.Grid()
            grid.set_row_spacing(3)
            grid.set_column_spacing(3)
            grid.set_halign(Gtk.Align.CENTER)
            grid.set_valign(Gtk.Align.CENTER)

            for idx, icon in enumerate(self.preview_icons[:4]):
                if icon:
                    img = Gtk.Image.new_from_gicon(icon)
                else:
                    img = Gtk.Image.new_from_icon_name("application-x-executable")
                img.set_pixel_size(24)
                grid.attach(img, idx % 2, idx // 2, 1, 1)

            self.preview_box.append(grid)
        else:
            folder_icon = Gtk.Image.new_from_icon_name("folder-symbolic")
            folder_icon.set_pixel_size(36)
            folder_icon.set_halign(Gtk.Align.CENTER)
            folder_icon.set_valign(Gtk.Align.CENTER)
            self.preview_box.append(folder_icon)

        overlay.set_child(self.preview_box)

        if self.is_selected:
            badge = Gtk.Label(label="✓")
            badge.add_css_class("selection-badge")
            badge.set_halign(Gtk.Align.END)
            badge.set_valign(Gtk.Align.START)
            overlay.add_overlay(badge)

        self.append(overlay)

        # Label widget
        self.label = Gtk.Label(label=self.folder.name)
        self.label.set_wrap(True)
        self.label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label.set_lines(2)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_max_width_chars(13)
        self.label.add_css_class("gnome-app-label")
        self.append(self.label)

        # Tooltip
        app_count = len(self.folder.apps)
        self.set_tooltip_text(f"{self.folder.name} ({app_count} apps)")

        # Setup Drag and Drop
        self._setup_dnd()

        # Setup Clicks & Context Menu
        self._setup_gestures()

    def _setup_dnd(self):
        # Drag Source (moves folder itself)
        drag_source = Gtk.DragSource.new()
        drag_source.set_actions(Gdk.DragAction.MOVE)

        def on_prepare(_source, _x, _y):
            val = GObject.Value()
            val.init(GObject.TYPE_STRING)
            val.set_string(self.folder.id)
            return Gdk.ContentProvider.new_for_value(val)

        drag_source.connect("prepare", on_prepare)
        self.add_controller(drag_source)

        # Drop Target (dropping an app into folder)
        drop_target = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.MOVE)

        def on_drop(_target, value, _x, _y):
            source_id = value
            if source_id and source_id != self.folder.id:
                if self.on_app_dropped_in_folder:
                    self.on_app_dropped_in_folder(source_id, self.folder.id)
                return True
            return False

        drop_target.connect("drop", on_drop)
        self.add_controller(drop_target)

    def _setup_gestures(self):
        # Left Click: Toggle select or Open Folder Dialog
        left_click = Gtk.GestureClick.new()
        left_click.set_button(1)
        left_click.connect("pressed", self._on_left_click)
        self.add_controller(left_click)

        # Right Click: Context Menu
        right_click = Gtk.GestureClick.new()
        right_click.set_button(3)
        right_click.connect("pressed", self._on_right_click)
        self.add_controller(right_click)

    def _on_left_click(self, gesture, _n_press, _x, _y):
        current_event = gesture.get_current_event()
        state = current_event.get_modifier_state() if current_event else 0
        is_modifier = bool(state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK))

        if self.is_selection_mode or is_modifier:
            if self.on_toggle_select:
                self.on_toggle_select(self.folder.id)
        else:
            if self.on_open_folder:
                self.on_open_folder(self.folder.id)

    def _on_right_click(self, _gesture, _n_press, x, y):
        self._show_context_menu(x, y)

    def _show_context_menu(self, x: float, y: float):
        popover = Gtk.Popover()
        popover.set_parent(self)
        popover.set_has_arrow(True)
        rect = Gdk.Rectangle()
        rect.x = int(x)
        rect.y = int(y)
        rect.width = 1
        rect.height = 1
        popover.set_pointing_to(rect)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_start(6)
        box.set_margin_end(6)
        box.set_margin_top(6)
        box.set_margin_bottom(6)

        selected_items = self.get_selected_items() if self.get_selected_items else []
        is_in_bulk = self.is_selected and len(selected_items) > 1

        if is_in_bulk:
            count = len(selected_items)
            hdr = Gtk.Label(label=f"Выбрано: {count} элементов")
            hdr.add_css_class("heading")
            hdr.add_css_class("accent")
            box.append(hdr)

            btn_bulk_page = Gtk.Button(label=f"📄  {tr('btn_move_selected_to_page')}")
            btn_bulk_page.add_css_class("flat")
            def on_bulk_page_clicked(_b):
                popover.popdown()
                self._show_bulk_page_picker(selected_items)
            btn_bulk_page.connect("clicked", on_bulk_page_clicked)
            box.append(btn_bulk_page)

            btn_desel = Gtk.Button(label=f"✕  {tr('btn_deselect_all')}")
            btn_desel.add_css_class("flat")
            def on_desel_clicked(_b):
                popover.popdown()
                if self.on_deselect_all:
                    self.on_deselect_all()
            btn_desel.connect("clicked", on_desel_clicked)
            box.append(btn_desel)

            box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # 1. Edit Folder
        btn_edit = Gtk.Button(label=f"✏️  {tr('folder_edit_dialog_title')}")
        btn_edit.add_css_class("flat")
        def on_edit_clicked(_b):
            popover.popdown()
            if self.on_open_folder:
                self.on_open_folder(self.folder.id)
        btn_edit.connect("clicked", on_edit_clicked)
        box.append(btn_edit)

        # 2. Move Left
        btn_left = Gtk.Button(label=f"⬅️  {tr('ctx_move_left')}")
        btn_left.add_css_class("flat")
        def on_left_clicked(_b):
            popover.popdown()
            if self.on_move_left:
                self.on_move_left(self.folder.id, self.page_idx)
        btn_left.connect("clicked", on_left_clicked)
        box.append(btn_left)

        # 3. Move Right
        btn_right = Gtk.Button(label=f"➡️  {tr('ctx_move_right')}")
        btn_right.add_css_class("flat")
        def on_right_clicked(_b):
            popover.popdown()
            if self.on_move_right:
                self.on_move_right(self.folder.id, self.page_idx)
        btn_right.connect("clicked", on_right_clicked)
        box.append(btn_right)

        # 4. Move to Page
        total_pages = self.get_page_count() if self.get_page_count else 1
        if total_pages > 1:
            btn_page = Gtk.Button(label=f"📄  {tr('ctx_move_to_page')}")
            btn_page.add_css_class("flat")
            def on_page_clicked(_b):
                popover.popdown()
                self._show_page_picker()
            btn_page.connect("clicked", on_page_clicked)
            box.append(btn_page)

        box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # 5. Delete / Unpack Folder
        btn_del = Gtk.Button(label=f"🗑️  {tr('folder_delete_btn')}")
        btn_del.add_css_class("destructive-action")
        def on_del_clicked(_b):
            popover.popdown()
            if self.on_delete_folder:
                self.on_delete_folder(self.folder.id)
        btn_del.connect("clicked", on_del_clicked)
        box.append(btn_del)

        popover.set_child(box)
        popover.popup()

    def _show_bulk_page_picker(self, items: List[str]):
        popover = Gtk.Popover()
        popover.set_parent(self)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        lbl = Gtk.Label(label=tr("move_to_page_title"))
        lbl.add_css_class("heading")
        box.append(lbl)

        total_pages = self.get_page_count() if self.get_page_count else 1
        for p in range(total_pages):
            if p == self.page_idx:
                continue
            btn = Gtk.Button(label=tr("page_info", current=p + 1, total=total_pages))
            btn.add_css_class("flat")
            def make_page_cb(target_p):
                return lambda _b: (popover.popdown(), self.on_move_selected_to_page(items, target_p) if self.on_move_selected_to_page else None)
            btn.connect("clicked", make_page_cb(p))
            box.append(btn)

        popover.set_child(box)
        popover.popup()

    def _show_page_picker(self):
        popover = Gtk.Popover()
        popover.set_parent(self)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        lbl = Gtk.Label(label=tr("move_to_page_title"))
        lbl.add_css_class("heading")
        box.append(lbl)

        total_pages = self.get_page_count() if self.get_page_count else 1
        for p in range(total_pages):
            if p == self.page_idx:
                continue
            btn = Gtk.Button(label=tr("page_info", current=p + 1, total=total_pages))
            btn.add_css_class("flat")
            def make_page_cb(target_p):
                return lambda _b: (popover.popdown(), self.on_move_to_page(self.folder.id, self.page_idx, target_p) if self.on_move_to_page else None)
            btn.connect("clicked", make_page_cb(p))
            box.append(btn)

        popover.set_child(box)
        popover.popup()
