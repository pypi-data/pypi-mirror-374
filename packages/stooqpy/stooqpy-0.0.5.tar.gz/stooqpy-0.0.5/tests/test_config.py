import shutil
from contextlib import contextmanager
from textwrap import dedent
from types import SimpleNamespace

import pytest

from src.stooqpy import config

# ## FIXTURES

@pytest.fixture
def fake_docs_n_dir(tmp_path, monkeypatch):
    """
    Przekierowuje globalne ścieżki do katalogu tymczasowego.
    """
    print('\n***\nrunning fake_docs_dirs\n***')

    # tworzy fejkowy subfolder, bazę dla tego setupu/fixture.
    config_subdir = tmp_path / config.CONFIG_SUBDIR

    # tworzy fake'owe ściezki obowiązujące w czasie testów.
    paths = SimpleNamespace(
        config_dir=config_subdir,  # dir od directory czyli folderu
        settings_path=config_subdir / 'settings.py',
        setup_yaml_path=config_subdir / 'setup.yaml',
    )

    # Wstrzykuje fake'owe ściezki do config na czas testów.
    monkeypatch.setattr(config, 'CONFIG_DIR', paths.config_dir)
    monkeypatch.setattr(config, 'USER_CONFIG_PATH', paths.settings_path)
    monkeypatch.setattr(config, 'USER_SETUP_PATH', paths.setup_yaml_path)

    yield paths

    # teardown: usuwa katalog po teście
    shutil.rmtree(config_subdir, ignore_errors=True)


@pytest.fixture
def tmpl_files_body():
    body = SimpleNamespace()
    body.settings = dedent("""\
    # Settings.py template
    # PATH_BASE = 'https://stooq.com/q/d/l/'
    """)
    body.yaml = dedent("""\
    # Setup.yaml template
    - number: 2
      ticker: WIG20
      name: WIG20
    """)
    return body


@pytest.fixture
def fake_templates(tmp_path, monkeypatch, tmpl_files_body):
    """
    Tworzy testowe pliki szablonów i podmienia pkg_resources.path,
    aby wskazywało na nie, zamiast prawdziwych zasobów.
    """
    print('\n+++\nrunning fake_templates\n+++')

    # tworzy fake'owy folder
    tmpl_dir = tmp_path / 'templates'
    tmpl_dir.mkdir()

    # generuje fake'owy plik i treść dla settings.py
    (tmpl_dir / 'settings.py').write_text(
        tmpl_files_body.settings, encoding='utf-8'
    )

    # generuje fake'owy plik i treść dla setup.yaml
    (tmpl_dir / 'setup.yaml').write_text(
        tmpl_files_body.yaml, encoding='utf-8'
    )

    @contextmanager
    def fake_path(_pkg, resource_name):
        yield tmpl_dir / resource_name

    # Fake funkcji path, używany w kodzie produkcyjnym do tworzenia plików.
    monkeypatch.setattr(config.pkg_resources, 'path', fake_path)

    # Udostępnia tmp_dir do testów, czy pliki istnieją i jaką treść mają.
    yield tmpl_dir

    # teardown: usuń katalog szablonów po teście
    shutil.rmtree(tmpl_dir, ignore_errors=True)


# ## INTEGRATION TESTS

def test_create_config_dir_n_files(fake_docs_n_dir, fake_templates):
    """
    Testuje proces inicjacji i tworzenia folderu z plikami konfiguracyjnymi.
    """
    # Given (kontekst początkowy, założenia („w jakim świecie startujemy”).
    # Brak katalogu konfiguracyjnego.
    assert not config.CONFIG_DIR.exists()

    # When (akcja, którą wykonujemy).
    config.initialize_config()

    # Then (oczekiwany rezultat).

    # folder i pliki istnieją
    assert config.CONFIG_DIR.is_dir()
    assert config.USER_CONFIG_PATH.is_file()
    assert config.USER_SETUP_PATH.is_file()

    # ...a zawartość pochodzi z szablonów.
    cfg_text = config.USER_CONFIG_PATH.read_text(encoding="utf-8")
    setup_text = config.USER_SETUP_PATH.read_text(encoding="utf-8")

    assert "PATH_BASE = 'https://stooq.com/q/d/l/'" in cfg_text
    assert "ticker: WIG20" in setup_text


# ## UNIT TESTS

def test_initialize_is_idempotent_does_not_overwrite(
        fake_docs_n_dir, fake_templates, tmpl_files_body):
    """
    Sprawdza sytuację, w której mam katalog i pliki konfiguracyjne.
    Proces inicjacji nie nadpisze ich, pozostaną nietknięte.
    """
    # Given - pliki istnieją na dysku usera
    config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config.USER_CONFIG_PATH.write_text(
        tmpl_files_body.settings, encoding='utf-8'
    )
    config.USER_SETUP_PATH.write_text(
        tmpl_files_body.yaml, encoding='utf-8'
    )

    # folder i pliki istnieją
    assert config.CONFIG_DIR.is_dir()
    assert config.USER_CONFIG_PATH.is_file()
    assert config.USER_SETUP_PATH.is_file()

    # When – wywołanie initialize_config
    config.initialize_config()

    # Then – pliki pozostały nietknięte
    cfg_text = config.USER_CONFIG_PATH.read_text(encoding="utf-8")
    setup_text = config.USER_SETUP_PATH.read_text(encoding="utf-8")

    assert cfg_text == tmpl_files_body.settings
    assert setup_text == tmpl_files_body.yaml


# ## NEGATIVE, obsługa błędów.

def test_init_raises_when_temlate_missing(
        fake_templates, fake_docs_n_dir, monkeypatch):
    """
    Sprawdza scenariusz negatywny, w którym pkg_resources.path zwraca ścieżkę
    do nieistniejącego pliku.
    shutil.copy2 powinno wyrzucić FileNotFoundError.
    """
    @contextmanager
    def missing_path(_pkg, resource_name):
        yield fake_templates / 'no_such_dir' / resource_name

    # Podmienia ścieżkę do zasobów na brakującą
    monkeypatch.setattr(config.pkg_resources, 'path', missing_path)

    # Podejmuje próbę zainicjowania konfiguracji
    with pytest.raises(FileNotFoundError):
        config.initialize_config()


# # ## Performance tests

# def test_perf_initialize(benchmark, fake_docs_n_dir, fake_templates):
#     def run():
#         # usuń pliki, żeby initialize_config musiał je znów tworzyć
#         for p in (config.USER_CONFIG_PATH, config.USER_SETUP_PATH):
#             if Path(p).exists():
#                 Path(p).unlink()
#         config.initialize_config()

#     benchmark(run)
