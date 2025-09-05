from typer.testing import CliRunner

import src.stooqpy.cli as cli

runner = CliRunner()


def test_help_lists_init_config():
    result = runner.invoke(cli.app, ["--help"])

    print(f'{result.exit_code=}')
    print(f'{result.stdout=}')
    print(f'{result.stderr=}')
    assert result.exit_code == 0
    # nazwa i opis komendy
    assert "init-config" in result.stdout
    assert "Inicjuje pliki konfiguracyjne" in result.stdout


def test_init_config_success(monkeypatch):
    called = {"ok": False}

    def fake_initialize_config():
        called["ok"] = True

    # podmieniamy funkcję wołaną przez CLI
    monkeypatch.setattr(
        cli.config, "initialize_config", fake_initialize_config)

    result = runner.invoke(cli.app, ["init-config"])

    print(f'{result.exit_code=}')
    print(f'{result.stdout=}')
    print(f'{result.stderr=}')

    assert result.exit_code == 0
    assert called["ok"] is True
    # komunikat powodzenia z Rich
    assert "Pliki konfiguracyjne zostały utworzone" in result.stdout


def test_init_config_failure_paths_to_exit_1(monkeypatch):
    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(cli.config, "initialize_config", boom)

    result = runner.invoke(cli.app, ["init-config"])

    print(f'{result.exit_code=}')
    print(f'{result.stdout=}')
    print(f'{result.stderr=}')

    # Typer powinien zakończyć proces kodem 1
    assert result.exit_code == 1
    # komunikat błędu z Rich
    assert "Błąd podczas inicjalizacji: boom" in result.stderr


if __name__ == '__main__':
    pass
