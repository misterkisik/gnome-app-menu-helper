"""
GnomeAppMenuHelper Backend Engine
Manages GNOME Shell app-picker-layout (aa{sv}) and org.gnome.desktop.app-folders.
"""

import os
import re
import json
import uuid
import time
from typing import Dict, List, Optional, Tuple, Any

import gi
gi.require_version("Gio", "2.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gio, GLib

try:
    gi.require_version("GioUnix", "2.0")
    from gi.repository import GioUnix
    HAVE_GIO_UNIX = True
except Exception:
    HAVE_GIO_UNIX = False

from gnomeappmenuhelper.models import AppItem, FolderItem

BACKUP_DIR = os.path.expanduser("~/.config/gnomeappmenuhelper/backups")
LOCAL_APPS_DIR = os.path.expanduser("~/.local/share/applications")


class AppMenuBackend:
    def __init__(self):
        self.schema_source = Gio.SettingsSchemaSource.get_default()
        self.has_shell_schema = self.schema_source.lookup("org.gnome.shell", True) is not None
        self.has_folders_schema = self.schema_source.lookup("org.gnome.desktop.app-folders", True) is not None

        if self.has_shell_schema:
            self.shell_settings = Gio.Settings.new("org.gnome.shell")
        else:
            self.shell_settings = None

        if self.has_folders_schema:
            self.folder_settings = Gio.Settings.new("org.gnome.desktop.app-folders")
        else:
            self.folder_settings = None

        self.apps: Dict[str, AppItem] = {}
        self.folders: Dict[str, FolderItem] = {}
        self.pages: List[List[str]] = [[]]

        self.load()

    def load(self):
        """Loads all installed apps, folders, and grid pages from GNOME Shell."""
        self._load_apps()
        self._load_folders()
        self._load_pages()

    def _load_apps(self):
        """Scans all installed applications via Gio.AppInfo."""
        self.apps.clear()
        all_app_infos = Gio.AppInfo.get_all()

        for info in all_app_infos:
            app_id = info.get_id()
            if not app_id:
                continue

            name = info.get_display_name() or info.get_name() or app_id
            gicon = info.get_icon()
            icon_name = gicon.to_string() if gicon else None
            desc = info.get_description() or ""
            should_show = info.should_show()

            nodisplay = False
            desktop_info = None
            if HAVE_GIO_UNIX:
                try:
                    desktop_info = GioUnix.DesktopAppInfo.new(app_id)
                except Exception:
                    pass
            if not desktop_info and hasattr(Gio, "DesktopAppInfo"):
                try:
                    desktop_info = Gio.DesktopAppInfo.new(app_id)
                except Exception:
                    pass

            if desktop_info:
                nodisplay = desktop_info.get_nodisplay() or not should_show

            self.apps[app_id] = AppItem(
                id=app_id,
                name=name,
                icon_name=icon_name,
                gicon=gicon,
                description=desc,
                nodisplay=nodisplay,
                is_folder=False
            )

    def _load_folders(self):
        """Loads app folders configured in org.gnome.desktop.app-folders."""
        self.folders.clear()
        if not self.folder_settings:
            return

        try:
            folder_ids = self.folder_settings.get_strv("folder-children") or []
            for f_id in folder_ids:
                path = f"/org/gnome/desktop/app-folders/folders/{f_id}/"
                try:
                    f_setting = Gio.Settings.new_with_path("org.gnome.desktop.app-folders.folder", path)
                    name = f_setting.get_string("name") or f_id
                    apps = list(f_setting.get_strv("apps") or [])
                    self.folders[f_id] = FolderItem(
                        id=f_id,
                        name=name,
                        apps=apps,
                        is_folder=True
                    )
                except Exception as e:
                    print(f"[GnomeAppMenuHelper] Error loading folder {f_id}: {e}")
        except Exception as e:
            print(f"[GnomeAppMenuHelper] Error loading folder-children: {e}")

    def _load_pages(self):
        """Loads app-picker-layout aa{sv} into pages list."""
        self.pages = []
        if self.shell_settings:
            try:
                layout_val = self.shell_settings.get_value("app-picker-layout")
                if layout_val and layout_val.get_type_string() == "aa{sv}":
                    unpacked = layout_val.unpack()
                    for page_dict in unpacked:
                        sorted_items = sorted(
                            page_dict.keys(),
                            key=lambda k: page_dict[k].get("position", 0) if isinstance(page_dict[k], dict) else 0
                        )
                        self.pages.append(sorted_items)
            except Exception as e:
                print(f"[GnomeAppMenuHelper] Error reading app-picker-layout: {e}")

        # If layout is empty, construct initial pages from visible apps
        if not self.pages or all(len(p) == 0 for p in self.pages):
            self.pages = []
            current_page: List[str] = []

            # First add existing folders
            for f_id in self.folders.keys():
                current_page.append(f_id)

            # Collect folder apps so we don't repeat them
            in_folders = set()
            for f in self.folders.values():
                in_folders.update(f.apps)

            # Add visible apps in chunks of 24
            PAGE_CAPACITY = 24
            for app_id, app in self.apps.items():
                if not app.nodisplay and app_id not in in_folders:
                    current_page.append(app_id)
                    if len(current_page) >= PAGE_CAPACITY:
                        self.pages.append(current_page)
                        current_page = []

            if current_page or not self.pages:
                self.pages.append(current_page)

        # Guarantee at least 1 page
        if not self.pages:
            self.pages = [[]]

    def get_item_name(self, item_id: str) -> str:
        """Returns the display name of an app or folder."""
        if item_id in self.folders:
            return self.folders[item_id].name
        if item_id in self.apps:
            return self.apps[item_id].name
        return item_id

    def get_unassigned_apps(self) -> List[AppItem]:
        """Returns list of installed apps not placed on any page or folder."""
        assigned = set()
        for p in self.pages:
            for item in p:
                if item in self.apps:
                    assigned.add(item)
        for f in self.folders.values():
            for app in f.apps:
                assigned.add(app)

        result = []
        for app_id, app in sorted(self.apps.items(), key=lambda x: x[1].name.lower()):
            if app_id not in assigned:
                result.append(app)
        return result

    def get_folder_preview_icons(self, folder_id: str, max_icons: int = 4) -> List[Optional[Gio.Icon]]:
        """Returns up to 4 GIcons for a folder preview."""
        icons: List[Optional[Gio.Icon]] = []
        folder = self.folders.get(folder_id)
        if not folder:
            return icons

        for app_id in folder.apps[:max_icons]:
            app = self.apps.get(app_id)
            if app and app.gicon:
                icons.append(app.gicon)
            elif HAVE_GIO_UNIX:
                try:
                    info = GioUnix.DesktopAppInfo.new(app_id)
                    icons.append(info.get_icon() if info else None)
                except Exception:
                    icons.append(None)
            else:
                icons.append(None)
        return icons

    # Page actions
    def add_page(self) -> int:
        """Creates a new empty page and returns its index."""
        self.pages.append([])
        return len(self.pages) - 1

    def delete_page(self, page_idx: int) -> bool:
        """Deletes page at index and moves its items to adjacent page."""
        if len(self.pages) <= 1:
            return False

        items_to_move = self.pages[page_idx]
        target_idx = page_idx - 1 if page_idx > 0 else 0
        self.pages.pop(page_idx)

        # Place remaining items on target page
        self.pages[target_idx].extend(items_to_move)
        return True

    # Item reordering & movement
    def move_item_within_page(self, page_idx: int, old_pos: int, new_pos: int) -> bool:
        """Moves an item within the same page."""
        if page_idx < 0 or page_idx >= len(self.pages):
            return False
        page = self.pages[page_idx]
        if old_pos < 0 or old_pos >= len(page):
            return False

        new_pos = max(0, min(new_pos, len(page) - 1))
        item = page.pop(old_pos)
        page.insert(new_pos, item)
        return True

    def move_item_to_page(self, item_id: str, source_page: int, target_page: int, target_pos: Optional[int] = None) -> bool:
        """Moves an item from source_page to target_page."""
        if source_page < 0 or source_page >= len(self.pages):
            return False
        if target_page < 0 or target_page >= len(self.pages):
            return False

        if item_id in self.pages[source_page]:
            self.pages[source_page].remove(item_id)
            if target_pos is not None:
                target_pos = max(0, min(target_pos, len(self.pages[target_page])))
                self.pages[target_page].insert(target_pos, item_id)
            else:
                self.pages[target_page].append(item_id)
            return True
        return False

    def remove_item_from_grid(self, item_id: str) -> bool:
        """Removes an item from whichever page it is currently on."""
        removed = False
        for p in self.pages:
            if item_id in p:
                p.remove(item_id)
                removed = True
        return removed

    def add_item_to_page(self, item_id: str, page_idx: int, pos: Optional[int] = None):
        """Adds an item to a specific page."""
        self.remove_item_from_grid(item_id)
        if 0 <= page_idx < len(self.pages):
            if pos is not None:
                pos = max(0, min(pos, len(self.pages[page_idx])))
                self.pages[page_idx].insert(pos, item_id)
            else:
                self.pages[page_idx].append(item_id)

    def move_multiple_items_to_page(self, item_ids: List[str], source_page: int, target_page: int) -> int:
        """Moves multiple items from source_page to target_page preserving order."""
        if target_page < 0 or target_page >= len(self.pages):
            return 0
        moved = 0
        for item_id in item_ids:
            if 0 <= source_page < len(self.pages) and item_id in self.pages[source_page]:
                self.pages[source_page].remove(item_id)
                self.pages[target_page].append(item_id)
                moved += 1
        return moved

    def add_multiple_apps_to_folder(self, folder_id: str, item_ids: List[str]) -> int:
        """Adds multiple apps into a folder, removing them from pages."""
        folder = self.folders.get(folder_id)
        if not folder:
            return 0
        added = 0
        for item_id in item_ids:
            # Cannot put folder inside folder
            if item_id in self.apps:
                self.remove_item_from_grid(item_id)
                if item_id not in folder.apps:
                    folder.apps.append(item_id)
                    added += 1
        return added

    def remove_multiple_items_from_grid(self, item_ids: List[str]) -> int:
        """Removes multiple items from the grid (to unassigned catalog)."""
        removed = 0
        for item_id in item_ids:
            if self.remove_item_from_grid(item_id):
                removed += 1
        return removed

    # Folder operations
    def create_folder(self, name: str, app_ids: List[str], page_idx: int, pos: Optional[int] = None) -> FolderItem:
        """Creates a new folder with apps and places it on page_idx."""
        clean_name = name.strip() or "Folder"
        slug = re.sub(r"[^a-zA-Z0-9_-]", "", clean_name.lower()) or "folder"
        folder_id = f"{slug}-{uuid.uuid4().hex[:6]}"

        folder = FolderItem(
            id=folder_id,
            name=clean_name,
            apps=list(app_ids),
            is_folder=True
        )
        self.folders[folder_id] = folder

        # Remove apps from any page grid
        for app_id in app_ids:
            self.remove_item_from_grid(app_id)

        # Place folder on page
        self.add_item_to_page(folder_id, page_idx, pos)
        return folder

    def unpack_folder(self, folder_id: str, target_page: Optional[int] = None) -> List[str]:
        """Disbands folder and unpacks all apps onto the page."""
        folder = self.folders.pop(folder_id, None)
        if not folder:
            return []

        # Find page where folder was located
        found_page = target_page if target_page is not None else 0
        folder_pos = None

        for p_idx, page in enumerate(self.pages):
            if folder_id in page:
                found_page = p_idx
                folder_pos = page.index(folder_id)
                page.remove(folder_id)
                break

        # Insert apps back
        if 0 <= found_page < len(self.pages):
            if folder_pos is not None:
                for idx, app in enumerate(folder.apps):
                    self.pages[found_page].insert(folder_pos + idx, app)
            else:
                self.pages[found_page].extend(folder.apps)

        return folder.apps

    def rename_folder(self, folder_id: str, new_name: str) -> bool:
        """Renames a folder."""
        folder = self.folders.get(folder_id)
        if folder:
            folder.name = new_name.strip() or folder.name
            return True
        return False

    def add_app_to_folder(self, folder_id: str, app_id: str) -> bool:
        """Adds an app into a folder."""
        folder = self.folders.get(folder_id)
        if not folder:
            return False

        self.remove_item_from_grid(app_id)
        if app_id not in folder.apps:
            folder.apps.append(app_id)
        return True

    def remove_app_from_folder(self, folder_id: str, app_id: str, target_page: Optional[int] = None) -> bool:
        """Removes an app from a folder and places it onto target_page."""
        folder = self.folders.get(folder_id)
        if not folder or app_id not in folder.apps:
            return False

        folder.apps.remove(app_id)
        p_idx = target_page if target_page is not None else 0
        self.add_item_to_page(app_id, p_idx)
        return True

    # Sorting
    def sort_alphabetically(self, page_idx: Optional[int] = None):
        """Sorts apps and folders alphabetically by display name."""
        def item_sort_key(item_id: str):
            name = self.get_item_name(item_id)
            return (0 if item_id in self.folders else 1, name.lower())

        if page_idx is not None:
            if 0 <= page_idx < len(self.pages):
                self.pages[page_idx].sort(key=item_sort_key)
        else:
            for page in self.pages:
                page.sort(key=item_sort_key)

    # Hide / Unhide apps
    def toggle_hide_app(self, app_id: str) -> bool:
        """Toggles NoDisplay for an app in ~/.local/share/applications."""
        os.makedirs(LOCAL_APPS_DIR, exist_ok=True)
        local_path = os.path.join(LOCAL_APPS_DIR, app_id)

        app = self.apps.get(app_id)
        current_nodisplay = app.nodisplay if app else False
        new_nodisplay = not current_nodisplay

        keyfile = GLib.KeyFile.new()
        if os.path.exists(local_path):
            try:
                keyfile.load_from_file(local_path, GLib.KeyFileFlags.NONE)
            except Exception:
                pass

        # If it was a system desktop file not yet in ~/.local/share/applications:
        if not keyfile.has_group(GLib.KEY_FILE_DESKTOP_GROUP):
            # Try to load original system file
            sys_paths = [
                os.path.join("/usr/share/applications", app_id),
                os.path.join("/var/lib/flatpak/exports/share/applications", app_id),
                os.path.expanduser(f"~/.local/share/flatpak/exports/share/applications/{app_id}")
            ]
            loaded = False
            for p in sys_paths:
                if os.path.exists(p):
                    try:
                        keyfile.load_from_file(p, GLib.KeyFileFlags.NONE)
                        loaded = True
                        break
                    except Exception:
                        pass
            if not loaded:
                keyfile.set_string(GLib.KEY_FILE_DESKTOP_GROUP, "Type", "Application")
                keyfile.set_string(GLib.KEY_FILE_DESKTOP_GROUP, "Name", app.name if app else app_id)

        keyfile.set_boolean(GLib.KEY_FILE_DESKTOP_GROUP, "NoDisplay", new_nodisplay)
        keyfile.save_to_file(local_path)

        if app:
            app.nodisplay = new_nodisplay

        return new_nodisplay

    # Save to GNOME Shell
    def save_to_gnome(self) -> bool:
        """Writes current pages and folders to GNOME Shell GSettings."""
        try:
            # 1. Update app-folders
            if self.folder_settings:
                folder_ids = list(self.folders.keys())
                self.folder_settings.set_strv("folder-children", folder_ids)

                for f_id, folder in self.folders.items():
                    path = f"/org/gnome/desktop/app-folders/folders/{f_id}/"
                    f_setting = Gio.Settings.new_with_path("org.gnome.desktop.app-folders.folder", path)
                    f_setting.set_string("name", folder.name)
                    f_setting.set_strv("apps", folder.apps)
                    f_setting.set_boolean("translate", True)

            # 2. Update app-picker-layout aa{sv}
            if self.shell_settings:
                pages_v = []
                for p in self.pages:
                    page_dict = {}
                    for pos, item_id in enumerate(p):
                        sub_dict = {"position": GLib.Variant("i", pos)}
                        page_dict[item_id] = GLib.Variant("a{sv}", sub_dict)
                    pages_v.append(page_dict)

                val = GLib.Variant("aa{sv}", pages_v)
                self.shell_settings.set_value("app-picker-layout", val)

            Gio.Settings.sync()
            return True
        except Exception as e:
            print(f"[GnomeAppMenuHelper] Error saving to GNOME Shell: {e}")
            return False

    # Backup & Restore
    def create_backup(self, custom_name: Optional[str] = None) -> str:
        """Creates a JSON backup of the current grid configuration."""
        os.makedirs(BACKUP_DIR, exist_ok=True)
        ts_str = time.strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{ts_str}.json" if not custom_name else custom_name
        filepath = os.path.join(BACKUP_DIR, filename)

        data = {
            "version": 1,
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pages": self.pages,
            "folders": {
                k: {"id": v.id, "name": v.name, "apps": v.apps}
                for k, v in self.folders.items()
            }
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    def restore_backup(self, filepath: str) -> bool:
        """Restores grid layout from a backup file."""
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "pages" in data and "folders" in data:
                self.pages = data["pages"]
                self.folders = {
                    k: FolderItem(id=v["id"], name=v["name"], apps=v.get("apps", []))
                    for k, v in data["folders"].items()
                }
                return True
        except Exception as e:
            print(f"[GnomeAppMenuHelper] Error restoring backup from {filepath}: {e}")
        return False

    def reset_to_gnome_default(self) -> bool:
        """Resets layout and folders to GNOME system defaults."""
        try:
            if self.shell_settings:
                self.shell_settings.reset("app-picker-layout")
            if self.folder_settings:
                self.folder_settings.reset("folder-children")
            Gio.Settings.sync()
            self.load()
            return True
        except Exception as e:
            print(f"[GnomeAppMenuHelper] Error resetting to defaults: {e}")
            return False
