""" Instaluje pliki konfiguracyjne w Dokumentach użytkownika."""

import importlib.resources as pkg_resources
import os
import shutil
from pathlib import Path

from platformdirs import user_documents_dir

from . import templates

# Tworzy nazwę podfolderu, który zostanie utworzony w 'Dokumentach'
CONFIG_SUBDIR = "stooqpy"

# Znajduje ścieżkę do systemowego folderu 'Dokumenty'/'Documents'
docs_dir = Path(user_documents_dir())

# Tworzy pełną ścieżkę do folderu konfiguracyjnego użytkownika
CONFIG_DIR = docs_dir / CONFIG_SUBDIR

# Definiuje ścieżkę docelową dla pliku konfiguracyjnego
USER_CONFIG_PATH = CONFIG_DIR / 'settings.py'
USER_SETUP_PATH = CONFIG_DIR / 'setup.yaml'


def initialize_config():
    """
    Tworzy pliki konfiguracyjne na podstawie szablonów,
    jeśli jeszcze nie istnieją.
    """
    # Akceptuje istnienie folderu (FileExistsError nie jest podnoszony).
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # Nie nadpisuje plików, tworzy tylko wtedy, gdy jeszcze nie istnieją.
    if not USER_CONFIG_PATH.exists():
        print(f"Tworzenie pliku konfiguracyjnego w: {USER_CONFIG_PATH}")
        with pkg_resources.path(templates, 'settings.py') as template_path:
            shutil.copy2(template_path, USER_CONFIG_PATH)

    if not USER_SETUP_PATH.exists():
        print(f"Tworzenie pliku konfiguracyjnego w: {USER_SETUP_PATH}")
        with pkg_resources.path(templates, 'setup.yaml') as template_path:
            shutil.copy2(template_path, USER_SETUP_PATH)


if __name__ == '__main__':  # pragma: no cover
    print(CONFIG_DIR)
    print(USER_CONFIG_PATH)
    print(USER_SETUP_PATH)
