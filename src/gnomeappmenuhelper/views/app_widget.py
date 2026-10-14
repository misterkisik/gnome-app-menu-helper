"""
AppWidget component representing a single application tile in the GNOME app grid.
Supports drag-and-drop, hover feedback, multi-selection, and right-click context menu.
"""

from typing import Callable, Optional, List, Tuple
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GObject, Pango

from gnomeappmenuhelper.models import AppItem
from gnomeappmenuhelper.i18n import tr


class AppWidget(Gtk.Box):
    def __init__(
        self,
        app: AppItem,
        page_idx: int,
        pos_idx: int,
        is_selected: bool = False,
        is_selection_mode: bool = False,
        on_toggle_select: Optional[Callable[[str], None]] = None,
        get_selected_items: Optional[Callable[[], List[str]]] = None,
        on_move_left: Optional[Callable[[str, int], None]] = None,
        on_move_right: Optional[Callable[[str, int], None]] = None,
        on_move_to_page: Optional[Callable[[str, int, int], None]] = None,
        on_move_selected_to_page: Optional[Callable[[List[str], int], None]] = None,
        on_add_to_folder: Optional[Callable[[str, str], None]] = None,
        on_add_selected_to_folder: Optional[Callable[[List[str], str], None]] = None,
        on_create_folder_prompt: Optional[Callable[[str, str], None]] = None,
        on_create_folder_from_selected: Optional[Callable[[List[str]], None]] = None,
        on_remove_from_page: Optional[Callable[[str, int], None]] = None,
        on_toggle_hide: Optional[Callable[[str], None]] = None,
        on_drop_on_app: Optional[Callable[[str, str], None]] = None,
        on_deselect_all: Optional[Callable[[], None]] = None,
        get_page_count: Optional[Callable[[], int]] = None,
        get_folders: Optional[Callable[[], List[Tuple[str, str]]]] = None,
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.app = app
        self.page_idx = page_idx
        self.pos_idx = pos_idx
        self.is_selected = is_selected
        self.is_selection_mode = is_selection_mode

        self.on_toggle_select = on_toggle_select
        self.get_selected_items = get_selected_items
        self.on_move_left = on_move_left
        self.on_move_right = on_move_right
        self.on_move_to_page = on_move_to_page
        self.on_move_selected_to_page = on_move_selected_to_page
        self.on_add_to_folder = on_add_to_folder
        self.on_add_selected_to_folder = on_add_selected_to_folder
        self.on_create_folder_prompt = on_create_folder_prompt
        self.on_create_folder_from_selected = on_create_folder_from_selected
        self.on_remove_from_page = on_remove_from_page
        self.on_toggle_hide = on_toggle_hide
        self.on_drop_on_app = on_drop_on_app
        self.on_deselect_all = on_deselect_all
        self.get_page_count = get_page_count
        self.get_folders = get_folders

        self.set_size_request(108, 116)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.add_css_class("gnome-app-tile")
        self.set_cursor(Gdk.Cursor.new_from_name("pointer", None))

        if self.app.nodisplay:
            self.add_css_class("hidden-app")

        if self.is_selected:
            self.add_css_class("selected-item")

        # Icon widget with overlay for selection badge
        overlay = Gtk.Overlay()
        overlay.set_halign(Gtk.Align.CENTER)
        overlay.set_valign(Gtk.Align.CENTER)
        overlay.set_size_request(64, 64)

        if self.app.gicon:
            self.icon_widget = Gtk.Image.new_from_gicon(self.app.gicon)
        elif self.app.icon_name:
            self.icon_widget = Gtk.Image.new_from_icon_name(self.app.icon_name)
        else:
            self.icon_widget = Gtk.Image.new_from_icon_name("application-x-executable")

        self.icon_widget.set_pixel_size(64)
        overlay.set_child(self.icon_widget)

        if self.is_selected:
            badge = Gtk.Label(label="✓")
            badge.add_css_class("selection-badge")
            badge.set_halign(Gtk.Align.END)
            badge.set_valign(Gtk.Align.START)
            overlay.add_overlay(badge)

        self.append(overlay)

        # Label widget
        self.label = Gtk.Label(label=self.app.name)
        self.label.set_wrap(True)
        self.label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label.set_lines(2)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_max_width_chars(13)
        self.label.add_css_class("gnome-app-label")
        self.append(self.label)

        # Tooltip
        tooltip_text = self.app.name
        if self.app.description:
            tooltip_text += f"\n{self.app.description}"
        if self.app.nodisplay:
            tooltip_text += " [Скрыто / Hidden]"
        self.set_tooltip_text(tooltip_text)

        # Setup Drag and Drop
        self._setup_dnd()

        # Setup Clicks & Context Menu
        self._setup_gestures()

    def _setup_dnd(self):
        # Drag Source
        drag_source = Gtk.DragSource.new()
        drag_source.set_actions(Gdk.DragAction.MOVE)

        def on_prepare(_source, _x, _y):
            val = GObject.Value()
            val.init(GObject.TYPE_STRING)
            val.set_string(self.app.id)
            return Gdk.ContentProvider.new_for_value(val)

        drag_source.connect("prepare", on_prepare)
        self.add_controller(drag_source)

        # Drop Target
        drop_target = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.MOVE)

        def on_drop(_target, value, _x, _y):
            source_id = value
            if source_id and source_id != self.app.id:
                if self.on_drop_on_app:
                    self.on_drop_on_app(source_id, self.app.id)
                return True
            return False

        drop_target.connect("drop", on_drop)
        self.add_controller(drop_target)

    def _setup_gestures(self):
        # Left Click Gesture (Select toggle or activation)
        left_click = Gtk.GestureClick.new()
        left_click.set_button(1)
        left_click.connect("pressed", self._on_left_click)
        self.add_controller(left_click)

        # Right Click Gesture (Context Menu)
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
                self.on_toggle_select(self.app.id)

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

        # Bulk Actions section if multiple items are selected
        if is_in_bulk:
            count = len(selected_items)
            hdr = Gtk.Label(label=f"Выбрано: {count} элементов")
            hdr.add_css_class("heading")
            hdr.add_css_class("accent")
            box.append(hdr)

            # Move all to page
            btn_bulk_page = Gtk.Button(label=f"📄  {tr('btn_move_selected_to_page')}")
            btn_bulk_page.add_css_class("flat")
            def on_bulk_page_clicked(_b):
                popover.popdown()
                self._show_bulk_page_picker(selected_items)
            btn_bulk_page.connect("clicked", on_bulk_page_clicked)
            box.append(btn_bulk_page)

            # Put all to folder
            btn_bulk_folder = Gtk.Button(label=f"📁  {tr('btn_move_selected_to_folder')}")
            btn_bulk_folder.add_css_class("flat")
            def on_bulk_folder_clicked(_b):
                popover.popdown()
                self._show_bulk_folder_picker(selected_items)
            btn_bulk_folder.connect("clicked", on_bulk_folder_clicked)
            box.append(btn_bulk_folder)

            # Deselect
            btn_desel = Gtk.Button(label=f"✕  {tr('btn_deselect_all')}")
            btn_desel.add_css_class("flat")
            def on_desel_clicked(_b):
                popover.popdown()
                if self.on_deselect_all:
                    self.on_deselect_all()
            btn_desel.connect("clicked", on_desel_clicked)
            box.append(btn_desel)

            box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # 1. Move Left
        btn_left = Gtk.Button(label=f"⬅️  {tr('ctx_move_left')}")
        btn_left.add_css_class("flat")
        btn_left.set_halign(Gtk.Align.FILL)
        def on_left_clicked(_b):
            popover.popdown()
            if self.on_move_left:
                self.on_move_left(self.app.id, self.page_idx)
        btn_left.connect("clicked", on_left_clicked)
        box.append(btn_left)

        # 2. Move Right
        btn_right = Gtk.Button(label=f"➡️  {tr('ctx_move_right')}")
        btn_right.add_css_class("flat")
        btn_right.set_halign(Gtk.Align.FILL)
        def on_right_clicked(_b):
            popover.popdown()
            if self.on_move_right:
                self.on_move_right(self.app.id, self.page_idx)
        btn_right.connect("clicked", on_right_clicked)
        box.append(btn_right)

        # 3. Move to Page
        total_pages = self.get_page_count() if self.get_page_count else 1
        if total_pages > 1:
            btn_page = Gtk.Button(label=f"📄  {tr('ctx_move_to_page')}")
            btn_page.add_css_class("flat")
            btn_page.set_halign(Gtk.Align.FILL)
            def on_page_clicked(_b):
                popover.popdown()
                self._show_page_picker()
            btn_page.connect("clicked", on_page_clicked)
            box.append(btn_page)

        # 4. Add to Folder
        btn_folder = Gtk.Button(label=f"📁  {tr('ctx_add_to_folder')}")
        btn_folder.add_css_class("flat")
        btn_folder.set_halign(Gtk.Align.FILL)
        def on_folder_clicked(_b):
            popover.popdown()
            self._show_folder_picker()
        btn_folder.connect("clicked", on_folder_clicked)
        box.append(btn_folder)

        box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # 5. Remove from page
        btn_remove = Gtk.Button(label=f"✕  {tr('ctx_remove_from_page')}")
        btn_remove.add_css_class("flat")
        def on_remove_clicked(_b):
            popover.popdown()
            if self.on_remove_from_page:
                self.on_remove_from_page(self.app.id, self.page_idx)
        btn_remove.connect("clicked", on_remove_clicked)
        box.append(btn_remove)

        # 6. Hide / Unhide
        hide_label = f"👁️  {tr('ctx_unhide_app') if self.app.nodisplay else tr('ctx_hide_app')}"
        btn_hide = Gtk.Button(label=hide_label)
        btn_hide.add_css_class("flat")
        def on_hide_clicked(_b):
            popover.popdown()
            if self.on_toggle_hide:
                self.on_toggle_hide(self.app.id)
        btn_hide.connect("clicked", on_hide_clicked)
        box.append(btn_hide)

        # 7. Launch
        btn_launch = Gtk.Button(label=f"🚀  {tr('ctx_launch')}")
        btn_launch.add_css_class("flat")
        def on_launch_clicked(_b):
            popover.popdown()
            self._launch_app()
        btn_launch.connect("clicked", on_launch_clicked)
        box.append(btn_launch)

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

    def _show_bulk_folder_picker(self, items: List[str]):
        popover = Gtk.Popover()
        popover.set_parent(self)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        lbl = Gtk.Label(label=tr("btn_move_selected_to_folder"))
        lbl.add_css_class("heading")
        box.append(lbl)

        folders = self.get_folders() if self.get_folders else []
        for f_id, f_name in folders:
            btn = Gtk.Button(label=f"📁 {f_name}")
            btn.add_css_class("flat")
            def make_cb(fid):
                return lambda _b: (popover.popdown(), self.on_add_selected_to_folder(items, fid) if self.on_add_selected_to_folder else None)
            btn.connect("clicked", make_cb(f_id))
            box.append(btn)

        box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        btn_new = Gtk.Button(label=f"+ {tr('btn_create_folder_from_selected')}")
        btn_new.add_css_class("suggested-action")
        def on_new_clicked(_b):
            popover.popdown()
            if self.on_create_folder_from_selected:
                self.on_create_folder_from_selected(items)
        btn_new.connect("clicked", on_new_clicked)
        box.append(btn_new)

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
                return lambda _b: (popover.popdown(), self.on_move_to_page(self.app.id, self.page_idx, target_p) if self.on_move_to_page else None)
            btn.connect("clicked", make_page_cb(p))
            box.append(btn)

        popover.set_child(box)
        popover.popup()

    def _show_folder_picker(self):
        popover = Gtk.Popover()
        popover.set_parent(self)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        lbl = Gtk.Label(label=tr("ctx_add_to_folder"))
        lbl.add_css_class("heading")
        box.append(lbl)

        folders = self.get_folders() if self.get_folders else []
        if folders:
            for f_id, f_name in folders:
                btn = Gtk.Button(label=f"📁 {f_name}")
                btn.add_css_class("flat")
                def make_folder_cb(fid):
                    return lambda _b: (popover.popdown(), self.on_add_to_folder(self.app.id, fid) if self.on_add_to_folder else None)
                btn.connect("clicked", make_folder_cb(f_id))
                box.append(btn)
        else:
            empty_lbl = Gtk.Label(label="Нет созданных папок")
            empty_lbl.add_css_class("dim-label")
            box.append(empty_lbl)

        box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        btn_new = Gtk.Button(label=f"+ {tr('btn_new_folder')}")
        btn_new.add_css_class("suggested-action")
        def on_new_clicked(_b):
            popover.popdown()
            if self.on_create_folder_prompt:
                self.on_create_folder_prompt(self.app.id, "")
        btn_new.connect("clicked", on_new_clicked)
        box.append(btn_new)

        popover.set_child(box)
        popover.popup()

    def _launch_app(self):
        try:
            info = Gio.DesktopAppInfo.new(self.app.id)
            if info:
                info.launch([], None)
        except Exception as e:
            print(f"[GnomeAppMenuHelper] Error launching {self.app.id}: {e}")
