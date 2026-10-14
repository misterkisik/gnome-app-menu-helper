# GnomeAppMenuHelper 🚀
> **Визуальный редактор сетки приложений и папок GNOME**  
> *Visual GNOME App Grid, Folder and Page Organizer (GTK 4 / Libadwaita)*

<p align="center">
  <img src="data/gnomeappmenuhelper.png" width="160" alt="GnomeAppMenuHelper Logo" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/GTK-4.0-blue?logo=gtk" alt="GTK 4" />
  <img src="https://img.shields.io/badge/Libadwaita-1.0-purple?logo=gnome" alt="Libadwaita" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-green.svg" alt="GPL-3.0 License" />
  <img src="https://img.shields.io/badge/Author-MisterKisik-orange.svg" alt="Author MisterKisik" />
  <img src="https://img.shields.io/badge/Python-3.9+-yellow?logo=python" alt="Python 3.9+" />
</p>

---

## 🌟 Возможности / Features

### 🇷🇺 Русский
- **Нативный внешний вид GNOME Shell**: полупрозрачный тёмный фон, скругленные иконки приложений (squircle), центрированные подписи, круговые стрелки перехода между страницами.
- **Управление страницами**: создание новых страниц, удаление страниц, навигация стрелками `‹` и `›`, индикаторные точки пагинации внизу с прямым переключением.
- **Интуитивная организация (Drag & Drop и контекстное меню)**:
  - Перетаскивание приложений для изменения порядка.
  - Перетаскивание приложения на приложение для создания новой папки.
  - Перетаскивание в папку для быстрого добавления.
  - Контекстное меню (ПКМ): *Сдвинуть влево*, *Сдвинуть вправо*, *Переместить на страницу…*, *Поместить в папку…*, *Убрать со страницы*, *Скрыть из меню GNOME*, *Запустить приложение*.
- **Управление папками**:
  - Предпросмотр 2x2 мини-иконок внутри плитки папки.
  - Переименование папок.
  - Добавление и удаление приложений из папки.
  - Расформирование (распаковка) папки обратно на страницу.
- **Каталог всех приложений**: просмотр всех установленных приложений, поиск по названию/описанию, фильтрация скрытых приложений, добавление приложений на сетку в один клик.
- **Скрытие / отображение приложений**: скрытие ненужных или системных ярлыков из меню GNOME Shell (`NoDisplay=true`).
- **Сортировка по алфавиту**: быстрая сортировка приложений на странице или всей сетке (А-Я / A-Z).
- **Резервное копирование и восстановление**: мгновенное сохранение снимка сетки в JSON и восстановление в любой момент, а также сброс к стандарту GNOME.
- **Мгновенное применение**: кнопка «Применить в GNOME» синхронизирует настройки напрямую в `org.gnome.shell app-picker-layout` и `org.gnome.desktop.app-folders`.
- **4 языка интерфейса**: Русский (RU), Английский (EN), Испанский (ES), Французский (FR) с диалогом выбора языка при первом запуске и переключением на лету.

---

### 🇬🇧 English
- **Native GNOME Shell Aesthetic**: dark translucent canvas, squircle app icons, centered two-line labels, circular navigation arrows.
- **Full Page Management**: create and delete pages, navigate with `‹` and `›`, interactive bottom pagination dots.
- **Drag & Drop & Rich Context Menus**:
  - Reorder apps and folders visually.
  - Drag an app onto another to create a folder.
  - Drop apps directly into existing folders.
  - Right-click menu: *Move Left*, *Move Right*, *Move to Page…*, *Add to Folder…*, *Remove from Page*, *Hide from Menu*, *Launch Application*.
- **App Folders Management**:
  - 2x2 mini-icon folder preview.
  - In-place folder editor: rename, add apps from catalog, remove individual apps, or unpack folder.
- **Installed Apps Catalog**: browse all installed apps, search, filter hidden/unassigned, place on active page.
- **App Visibility Control**: toggle `NoDisplay` for any desktop entry.
- **Alphabetical Sorting**: 1-click A-Z layout sorting.
- **Backup & Restore**: save layout snapshots to JSON, restore or reset to GNOME defaults.
- **Instant GNOME Sync**: direct live synchronization with GNOME Shell GSettings without restarting the session.
- **Multi-language Support**: English, Russian, Spanish, and French with first-run welcome selector.

---

### 🇪🇸 Español
- **Estilo visual de GNOME Shell**: lienzo oscuro translúcido, iconos squircle, navegación de páginas con flechas y puntos inferiores.
- **Gestión completa de carpetas y páginas**: crear, eliminar, desempaquetar carpetas con vista previa 2x2.
- **Arrastrar y soltar + Menú contextual**: mover aplicaciones, crear carpetas al soltar, ordenar alfabéticamente.
- **Catálogo y visibilidad**: ocultar aplicaciones del menú, buscar y restaurar copias de seguridad.
- **4 idiomas**: ruso, inglés, español y francés.

---

### 🇫🇷 Français
- **Esthétique native GNOME Shell** : toile sombre translucide, icônes squircle, flèches de navigation et points de pagination.
- **Gestion complète des dossiers et pages** : créer, supprimer, dissoudre des dossiers avec aperçu 2x2.
- **Glisser-déposer et menu contextuel** : réorganiser, créer des dossiers, trier de A à Z.
- **Catalogue et masquage** : masquer des applications du menu, sauvegarder et restaurer.
- **4 langues** : français, anglais, russe et espagnol.

---

## 🛠 Системные требования / Requirements

Для работы необходимы **Python 3.10+**, **GTK 4** и **Libadwaita**:

| Дистрибутив / Distro | Команда установки зависимостей / Dependencies command |
| :--- | :--- |
| **Arch Linux / Manjaro** | `sudo pacman -S python python-gobject gtk4 libadwaita` |
| **Fedora** | `sudo dnf install python3 python3-gobject gtk4 libadwaita` |
| **Ubuntu / Debian** | `sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1` |
| **openSUSE** | `sudo zypper install python3 python3-gobject typelib-Gtk-4_0 typelib-Adw-1` |

---

## 🚀 Подробное руководство по установке / Installation Guide

### 🇷🇺 Русский

#### Способ 1: Сборка и установка через makepkg в Arch Linux (Рекомендуется)
Если вы используете Arch Linux, Manjaro, CachyOS или EndeavourOS:
```bash
# 1. Склонируйте репозиторий
git clone https://github.com/misterkisik/gnome-app-menu-helper.git
cd gnome-app-menu-helper

# 2. Соберите и установите пакет одной командой
makepkg -p PKGBUILD.local -si
```
Команда `makepkg -si` автоматически соберёт `.pkg.tar.zst`, установит бинарник `/usr/bin/gnome-app-menu-helper`, зарегистрирует `.desktop`-файл, все размеры иконок от 16x16 до 512x512 + SVG и арт маскота.

#### Способ 2: Установка из AUR (yay / paru)
```bash
yay -S gnome-app-menu-helper
# или
paru -S gnome-app-menu-helper
```

#### Способ 3: Установка через Python pip / pipx (Любой Linux)
Подходит для Ubuntu, Debian, Fedora, openSUSE и других дистрибутивов:
```bash
git clone https://github.com/misterkisik/gnome-app-menu-helper.git
cd gnome-app-menu-helper

# Установка в домашний каталог пользователя
pip install --user .
```
*(Если в вашем дистрибутиве действует политика PEP 668, используйте `pipx install .` или добавьте `--break-system-packages`)*.

##### 📌 Регистрация ярлыка и иконки в меню GNOME при установке через pip:
```bash
# Ярлык приложения
mkdir -p ~/.local/share/applications
cp data/org.cleanarch.GnomeAppMenuHelper.desktop ~/.local/share/applications/

# Иконки приложения
mkdir -p ~/.local/share/icons/hicolor
cp -r data/icons/hicolor/* ~/.local/share/icons/hicolor/
gtk-update-icon-cache -q ~/.local/share/icons/hicolor

# Ассеты маскота
mkdir -p ~/.local/share/gnome-app-menu-helper
cp data/mascot.png ~/.local/share/gnome-app-menu-helper/
```

#### Способ 4: Портативный запуск без установки
Вы можете запустить приложение сразу из папки без инсталляции в систему:
```bash
git clone https://github.com/misterkisik/gnome-app-menu-helper.git
cd gnome-app-menu-helper
./bin/gnome-app-menu-helper
```

---

### 🇬🇧 English

#### Method 1: Arch Linux Native Build (makepkg)
```bash
git clone https://github.com/misterkisik/gnome-app-menu-helper.git
cd gnome-app-menu-helper
makepkg -p PKGBUILD.local -si
```

#### Method 2: AUR Package
```bash
yay -S gnome-app-menu-helper
```

#### Method 3: Python pip / pipx (Universal)
```bash
git clone https://github.com/misterkisik/gnome-app-menu-helper.git
cd gnome-app-menu-helper
pip install --user .
```

#### Method 4: Run Directly (Portable)
```bash
git clone https://github.com/misterkisik/gnome-app-menu-helper.git
cd gnome-app-menu-helper
./bin/gnome-app-menu-helper
```

---

## 🎮 Запуск и использование / Usage

- **Из системного меню GNOME**: Нажмите клавишу `Super` (Windows) и введите в поиск `GnomeAppMenuHelper`.
- **Из любого терминала**:
  ```bash
  gnome-app-menu-helper
  ```

---

## 🗑 Удаление / Uninstall

- **Arch Linux (pacman)**:
  ```bash
  sudo pacman -R gnome-app-menu-helper
  ```
- **Pip**:
  ```bash
  pip uninstall gnome-app-menu-helper
  rm -f ~/.local/share/applications/org.cleanarch.GnomeAppMenuHelper.desktop
  rm -rf ~/.local/share/gnome-app-menu-helper
  ```

---

## 👤 Автор и копирайт / Author & Copyright
- **Автор**: MisterKisik
- **Copyright**: © 2026 MisterKisik
- **Лицензия**: [GNU General Public License v3.0](LICENSE)
