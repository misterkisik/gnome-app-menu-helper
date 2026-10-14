"""
GnomeAppMenuHelper Data Models
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any
import gi
gi.require_version("Gio", "2.0")
from gi.repository import Gio

@dataclass
class AppItem:
    id: str
    name: str
    icon_name: Optional[str] = None
    gicon: Optional[Any] = None
    description: str = ""
    nodisplay: bool = False
    is_folder: bool = False

@dataclass
class FolderItem:
    id: str
    name: str
    apps: List[str] = field(default_factory=list)
    is_folder: bool = True
