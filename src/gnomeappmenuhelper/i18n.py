"""
GnomeAppMenuHelper Internationalization (i18n) Module
Supported languages: ru (Русский), en (English), es (Español), fr (Français).
"""

import os
import json
from typing import Dict, Any, Callable, List

CONFIG_DIR = os.path.expanduser("~/.config/gnomeappmenuhelper")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

SUPPORTED_LANGUAGES: Dict[str, str] = {
    "ru": "Русский",
    "en": "English",
    "es": "Español",
    "fr": "Français"
}

_current_lang = "ru"
_listeners: List[Callable[[], None]] = []

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Application & Header
    'app_title': {
        'ru': 'GnomeAppMenuHelper',
        'en': 'GnomeAppMenuHelper',
        'es': 'GnomeAppMenuHelper',
        'fr': 'GnomeAppMenuHelper'
    },
    'app_subtitle': {
        'ru': 'Визуальный редактор сетки приложений и папок GNOME',
        'en': 'Visual GNOME App Grid &amp; Folder Organizer',
        'es': 'Organizador visual de cuadrícula de aplicaciones y carpetas de GNOME',
        'fr': "Organisateur visuel de grille d'applications et dossiers GNOME"
    },

    # Welcome / First Run
    'welcome_title': {
        'ru': 'Добро пожаловать в GnomeAppMenuHelper!',
        'en': 'Welcome to GnomeAppMenuHelper!',
        'es': '¡Bienvenido a GnomeAppMenuHelper!',
        'fr': 'Bienvenue dans GnomeAppMenuHelper !'
    },
    'welcome_subtitle': {
        'ru': 'Выберите удобный язык интерфейса для организации меню приложений GNOME:',
        'en': 'Select your preferred interface language to organize your GNOME app grid:',
        'es': 'Seleccione su idioma preferido para organizar sus aplicaciones en GNOME:',
        'fr': "Sélectionnez votre langue d'interface préférée pour organiser vos applications GNOME :"
    },
    'welcome_continue': {
        'ru': 'Продолжить',
        'en': 'Continue',
        'es': 'Continuar',
        'fr': 'Continuer'
    },

    # Toolbar actions
    'btn_apply': {
        'ru': 'Применить в GNOME',
        'en': 'Apply to GNOME',
        'es': 'Aplicar a GNOME',
        'fr': 'Appliquer à GNOME'
    },
    'btn_apply_tooltip': {
        'ru': 'Сохранить изменения и мгновенно обновить сетку приложений GNOME Shell',
        'en': 'Save changes and immediately refresh GNOME Shell app grid',
        'es': 'Guardar cambios y actualizar la cuadrícula de GNOME Shell',
        'fr': "Enregistrer et rafraîchir immédiatement la grille d'applications GNOME Shell"
    },
    'btn_add_page': {
        'ru': 'Новая страница',
        'en': 'Add Page',
        'es': 'Añadir página',
        'fr': 'Ajouter une page'
    },
    'btn_del_page': {
        'ru': 'Удалить страницу',
        'en': 'Delete Page',
        'es': 'Eliminar página',
        'fr': 'Supprimer la page'
    },
    'btn_new_folder': {
        'ru': 'Создать папку',
        'en': 'New Folder',
        'es': 'Nueva carpeta',
        'fr': 'Nouveau dossier'
    },
    'btn_sort_az': {
        'ru': 'Сортировать А-Я',
        'en': 'Sort A-Z',
        'es': 'Ordenar A-Z',
        'fr': 'Trier A-Z'
    },
    'btn_unassigned': {
        'ru': 'Все приложения',
        'en': 'App Catalog',
        'es': 'Catálogo de aplicaciones',
        'fr': 'Catalogue des applications'
    },
    'search_placeholder': {
        'ru': 'Поиск приложений...',
        'en': 'Search applications...',
        'es': 'Buscar aplicaciones...',
        'fr': 'Rechercher des applications...'
    },

    # Multi-selection
    'btn_select_mode': {
        'ru': 'Выбор',
        'en': 'Select',
        'es': 'Selección',
        'fr': 'Sélection'
    },
    'btn_select_mode_tooltip': {
        'ru': 'Режим выделения нескольких приложений (или Ctrl+Клик)',
        'en': 'Multi-selection mode (or Ctrl+Click)',
        'es': 'Modo de selección múltiple (o Ctrl+Clic)',
        'fr': 'Mode de sélection multiple (ou Ctrl+Clic)'
    },
    'btn_select_all': {
        'ru': 'Выбрать все',
        'en': 'Select All',
        'es': 'Seleccionar todo',
        'fr': 'Tout sélectionner'
    },
    'btn_deselect_all': {
        'ru': 'Снять выбор',
        'en': 'Deselect',
        'es': 'Deseleccionar',
        'fr': 'Désélectionner'
    },
    'selected_count': {
        'ru': 'Выбрано: {count}',
        'en': 'Selected: {count}',
        'es': 'Seleccionados: {count}',
        'fr': 'Sélectionnés : {count}'
    },
    'btn_move_selected_to_page': {
        'ru': 'Переместить на страницу…',
        'en': 'Move to Page…',
        'es': 'Mover a la página…',
        'fr': 'Déplacer vers la page…'
    },
    'btn_move_selected_to_folder': {
        'ru': 'Поместить в папку…',
        'en': 'Add to Folder…',
        'es': 'Añadir a carpeta…',
        'fr': 'Ajouter au dossier…'
    },
    'btn_create_folder_from_selected': {
        'ru': 'Создать папку с выбранными',
        'en': 'Create Folder with Selected',
        'es': 'Crear carpeta con seleccionados',
        'fr': 'Créer un dossier avec les sélectionnés'
    },
    'toast_moved_to_page': {
        'ru': 'Перемещено {count} элементов на страницу {page}',
        'en': 'Moved {count} items to page {page}',
        'es': 'Se movieron {count} elementos a la página {page}',
        'fr': '{count} éléments déplacés vers la page {page}'
    },
    'toast_added_to_folder': {
        'ru': 'Добавлено {count} приложений в папку «{name}»',
        'en': 'Added {count} apps to folder \'{name}\'',
        'es': 'Se añadieron {count} aplicaciones a la carpeta \'{name}\'',
        'fr': '{count} applications ajoutées au dossier « {name} »'
    },

    # Pagination
    'page_info': {
        'ru': 'Страница {current} из {total}',
        'en': 'Page {current} of {total}',
        'es': 'Página {current} de {total}',
        'fr': 'Page {current} sur {total}'
    },
    'prev_page_tip': {
        'ru': 'Предыдущая страница',
        'en': 'Previous Page',
        'es': 'Página anterior',
        'fr': 'Page précédente'
    },
    'next_page_tip': {
        'ru': 'Следующая страница',
        'en': 'Next Page',
        'es': 'Página siguiente',
        'fr': 'Page suivante'
    },

    # Context menu on App
    'ctx_move_left': {
        'ru': 'Сдвинуть влево',
        'en': 'Move Left',
        'es': 'Mover a la izquierda',
        'fr': 'Déplacer à gauche'
    },
    'ctx_move_right': {
        'ru': 'Сдвинуть вправо',
        'en': 'Move Right',
        'es': 'Mover a la derecha',
        'fr': 'Déplacer à droite'
    },
    'ctx_move_to_page': {
        'ru': 'Переместить на страницу…',
        'en': 'Move to Page…',
        'es': 'Mover a la página…',
        'fr': 'Déplacer vers la page…'
    },
    'ctx_add_to_folder': {
        'ru': 'Поместить в папку…',
        'en': 'Add to Folder…',
        'es': 'Añadir a carpeta…',
        'fr': 'Ajouter au dossier…'
    },
    'ctx_remove_from_page': {
        'ru': 'Убрать со страницы',
        'en': 'Remove from Page',
        'es': 'Quitar de la página',
        'fr': 'Retirer de la page'
    },
    'ctx_hide_app': {
        'ru': 'Скрыть из меню GNOME',
        'en': 'Hide from GNOME Menu',
        'es': 'Ocultar del menú de GNOME',
        'fr': 'Masquer du menu GNOME'
    },
    'ctx_unhide_app': {
        'ru': 'Показать в меню GNOME',
        'en': 'Show in GNOME Menu',
        'es': 'Mostrar en el menú de GNOME',
        'fr': 'Afficher dans le menu GNOME'
    },
    'ctx_launch': {
        'ru': 'Запустить приложение',
        'en': 'Launch Application',
        'es': 'Iniciar aplicación',
        'fr': "Lancer l'application"
    },

    # Folders
    'folder_untitled': {
        'ru': 'Папка без названия',
        'en': 'Unnamed Folder',
        'es': 'Carpeta sin nombre',
        'fr': 'Dossier sans titre'
    },
    'folder_edit_dialog_title': {
        'ru': 'Управление папкой',
        'en': 'Manage Folder',
        'es': 'Administrar carpeta',
        'fr': 'Gérer le dossier'
    },
    'folder_name_label': {
        'ru': 'Название папки',
        'en': 'Folder Name',
        'es': 'Nombre de la carpeta',
        'fr': 'Nom du dossier'
    },
    'folder_apps_in_folder': {
        'ru': 'Приложения в папке ({count})',
        'en': 'Apps in Folder ({count})',
        'es': 'Aplicaciones en carpeta ({count})',
        'fr': 'Applications dans le dossier ({count})'
    },
    'folder_add_apps_btn': {
        'ru': 'Добавить приложения в эту папку',
        'en': 'Add Apps to this Folder',
        'es': 'Añadir aplicaciones a esta carpeta',
        'fr': 'Ajouter des applications à ce dossier'
    },
    'folder_delete_btn': {
        'ru': 'Расформировать папку',
        'en': 'Unpack / Delete Folder',
        'es': 'Desempaquetar / Eliminar carpeta',
        'fr': 'Dissoudre / Supprimer le dossier'
    },
    'folder_delete_confirm': {
        'ru': 'Все приложения из этой папки вернутся на текущую страницу.',
        'en': 'All apps in this folder will return to the active page.',
        'es': 'Todas las aplicaciones regresarán a la página activa.',
        'fr': 'Toutes les applications retourneront sur la page active.'
    },

    # New Folder Modal
    'new_folder_modal_title': {
        'ru': 'Создание новой папки',
        'en': 'Create New Folder',
        'es': 'Crear nueva carpeta',
        'fr': 'Créer un nouveau dossier'
    },
    'new_folder_prompt': {
        'ru': 'Введите название папки:',
        'en': 'Enter folder name:',
        'es': 'Ingrese el nombre de la carpeta:',
        'fr': 'Entrez le nom du dossier :'
    },
    'new_folder_placeholder': {
        'ru': 'Например: Утилиты, Игры, Разработка...',
        'en': 'e.g. Utilities, Games, Development...',
        'es': 'p. ej. Utilidades, Juegos, Desarrollo...',
        'fr': 'ex. Utilitaires, Jeux, Développement...'
    },

    # Unassigned Pool Modal
    'pool_title': {
        'ru': 'Каталог всех установленных приложений',
        'en': 'Installed Applications Catalog',
        'es': 'Catálogo de aplicaciones instaladas',
        'fr': 'Catalogue des applications installées'
    },
    'pool_desc': {
        'ru': 'Выберите приложение для размещения на текущей странице сетки:',
        'en': 'Select an application to place onto the current page:',
        'es': 'Seleccione una aplicación para añadir a la página actual:',
        'fr': 'Sélectionnez une application à placer sur la page active :'
    },
    'pool_add_btn': {
        'ru': 'Добавить на страницу',
        'en': 'Add to Page',
        'es': 'Añadir a la página',
        'fr': 'Ajouter à la page'
    },
    'pool_hidden_filter': {
        'ru': 'Показать скрытые приложения',
        'en': 'Show Hidden Applications',
        'es': 'Mostrar aplicaciones ocultas',
        'fr': 'Afficher les applications masquées'
    },

    # Move to Page Dialog
    'move_to_page_title': {
        'ru': 'Выберите целевую страницу',
        'en': 'Choose Target Page',
        'es': 'Elegir página de destino',
        'fr': 'Choisir la page cible'
    },

    # Menu items
    'menu_language': {
        'ru': 'Язык (Language)',
        'en': 'Language',
        'es': 'Idioma',
        'fr': 'Langue'
    },
    'menu_backup': {
        'ru': 'Сохранить резервную копию',
        'en': 'Create Layout Backup',
        'es': 'Crear copia de seguridad',
        'fr': 'Créer une sauvegarde'
    },
    'menu_restore': {
        'ru': 'Восстановить из резервной копии',
        'en': 'Restore from Backup',
        'es': 'Restaurar desde copia',
        'fr': 'Restaurer depuis la sauvegarde'
    },
    'menu_reset_default': {
        'ru': 'Сбросить к стандарту GNOME',
        'en': 'Reset to GNOME Default',
        'es': 'Restablecer a valores predeterminados',
        'fr': 'Réinitialiser aux paramètres GNOME'
    },
    'menu_about': {
        'ru': 'О программе',
        'en': 'About GnomeAppMenuHelper',
        'es': 'Acerca de GnomeAppMenuHelper',
        'fr': 'À propos de GnomeAppMenuHelper'
    },
    'menu_options_tip': {
        'ru': 'Меню и параметры',
        'en': 'Options &amp; Settings',
        'es': 'Opciones y ajustes',
        'fr': 'Options et paramètres'
    },

    # About
    'about_comments': {
        'ru': 'Удобный визуальный конфигуратор сетки приложений и папок для рабочего стола GNOME.',
        'en': 'Intuitive visual app grid and folder manager for the GNOME desktop environment.',
        'es': 'Cómodo configurador visual de cuadrícula y carpetas para el escritorio GNOME.',
        'fr': "Configurateur visuel intuitif de grille d'applications et de dossiers pour GNOME."
    },

    # Common buttons
    'btn_cancel': {
        'ru': 'Отмена',
        'en': 'Cancel',
        'es': 'Cancelar',
        'fr': 'Annuler'
    },
    'btn_save': {
        'ru': 'Сохранить',
        'en': 'Save',
        'es': 'Guardar',
        'fr': 'Enregistrer'
    },
    'btn_close': {
        'ru': 'Закрыть',
        'en': 'Close',
        'es': 'Cerrar',
        'fr': 'Fermer'
    },

    # Toasts
    'toast_applied': {
        'ru': 'Сетка приложений успешно обновлена в GNOME Shell! 🚀',
        'en': 'GNOME Shell app grid updated successfully! 🚀',
        'es': '¡Cuadrícula de GNOME Shell actualizada con éxito! 🚀',
        'fr': 'Grille des applications GNOME Shell mise à jour ! 🚀'
    },
    'toast_page_added': {
        'ru': 'Создана страница {num}',
        'en': 'Page {num} created',
        'es': 'Página {num} creada',
        'fr': 'Page {num} créée'
    },
    'toast_page_deleted': {
        'ru': 'Страница удалена',
        'en': 'Page deleted',
        'es': 'Página eliminada',
        'fr': 'Page supprimée'
    },
    'toast_folder_created': {
        'ru': 'Папка «{name}» успешно создана!',
        'en': "Folder '{name}' created successfully!",
        'es': "¡Carpeta '{name}' creada con éxito!",
        'fr': "Dossier « {name} » créé avec succès !"
    },
    'toast_folder_deleted': {
        'ru': 'Папка расформирована, приложения возвращены на страницу',
        'en': 'Folder unpacked, apps returned to page',
        'es': 'Carpeta desempaquetada, aplicaciones devueltas a la página',
        'fr': 'Dossier dissous, applications remises sur la page'
    },
    'toast_app_hidden': {
        'ru': 'Приложение скрыто из меню GNOME',
        'en': 'Application hidden from GNOME menu',
        'es': 'Aplicación oculta del menú de GNOME',
        'fr': 'Application masquée du menu GNOME'
    },
    'toast_app_unhidden': {
        'ru': 'Приложение снова видно в меню GNOME',
        'en': 'Application unhidden in GNOME menu',
        'es': 'Aplicación visible de nuevo en GNOME',
        'fr': 'Application de nouveau visible dans GNOME'
    },
    'toast_sorted': {
        'ru': 'Сетка отсортирована по алфавиту (A-Z) ✨',
        'en': 'Apps sorted alphabetically (A-Z) ✨',
        'es': 'Aplicaciones ordenadas alfabéticamente (A-Z) ✨',
        'fr': 'Applications triées par ordre alphabétique (A-Z) ✨'
    },
    'toast_backed_up': {
        'ru': 'Резервная копия сохранена в {path}',
        'en': 'Backup saved to {path}',
        'es': 'Copia de seguridad guardada en {path}',
        'fr': 'Sauvegarde enregistrée dans {path}'
    },
    'toast_restored': {
        'ru': 'Сетка приложений восстановлена из резервной копии!',
        'en': 'App grid restored from backup!',
        'es': '¡Cuadrícula restaurada desde la copia de seguridad!',
        'fr': 'Grille restaurée depuis la sauvegarde !'
    },
    'toast_lang_changed': {
        'ru': 'Язык интерфейса изменён',
        'en': 'Interface language updated',
        'es': 'Idioma de interfaz actualizado',
        'fr': "Langue de l'interface mise à jour"
    },
    'toast_cannot_del_last_page': {
        'ru': 'Нельзя удалить единственную страницу сетки.',
        'en': 'Cannot delete the only remaining page.',
        'es': 'No se puede eliminar la única página restante.',
        'fr': 'Impossible de supprimer la seule page restante.'
    }
}

def load_saved_language() -> str:
    """Loads saved language from config or system locale."""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                lang = data.get("language")
                if lang in SUPPORTED_LANGUAGES:
                    return lang
    except Exception:
        pass

    sys_lang = os.environ.get("LANG", "").split(".")[0].split("_")[0].lower()
    if sys_lang in SUPPORTED_LANGUAGES:
        return sys_lang

    return "ru"

def save_language(lang: str, first_run_done: bool = True):
    """Saves language preference to config file."""
    global _current_lang
    if lang in SUPPORTED_LANGUAGES:
        _current_lang = lang
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            data = {}
            if os.path.exists(CONFIG_PATH):
                try:
                    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    pass
            data["language"] = lang
            if first_run_done:
                data["first_run_done"] = True
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[GnomeAppMenuHelper] Error saving language config: {e}")

def set_language(lang: str, first_run_done: bool = True):
    """Sets active language and notifies listeners."""
    global _current_lang
    if lang in SUPPORTED_LANGUAGES:
        _current_lang = lang
        save_language(lang, first_run_done=first_run_done)
        for listener in _listeners:
            try:
                listener()
            except Exception as e:
                print(f"[GnomeAppMenuHelper] Error in i18n listener: {e}")

def get_current_language() -> str:
    return _current_lang

def add_language_change_listener(callback: Callable[[], None]):
    _listeners.append(callback)

def is_first_run() -> bool:
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return not data.get("first_run_done", False)
    except Exception:
        pass
    return True

def tr(key: str, **kwargs) -> str:
    lang_dict = TRANSLATIONS.get(key)
    if not lang_dict:
        return key

    text = lang_dict.get(_current_lang) or lang_dict.get("en") or lang_dict.get("ru") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

# Initialize on import
_current_lang = load_saved_language()
