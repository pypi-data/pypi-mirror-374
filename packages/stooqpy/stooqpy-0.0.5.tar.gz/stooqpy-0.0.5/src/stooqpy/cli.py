"""Console script for stooqpy."""
import typer
from rich.console import Console

from . import config

app = typer.Typer(help="CLI dla pakietu stooqpy", no_args_is_help=True)

out = Console()
err = Console(stderr=True)


@app.command(
        "init-config",
        help="Inicjuje pliki konfiguracyjne w folderze Dokumenty")
def init_config():
    """
    Inicjuje pliki konfiguracyjne (jeśli ich brakuje).
    """
    try:
        config.initialize_config()
        out.print(
            "[green]Pliki konfiguracyjne zostały utworzone "
            "(jeśli brakowało).[/green]"
        )
    except Exception as ex:
        err.print(f"[red]Błąd podczas inicjalizacji: {ex}[/red]")
        raise typer.Exit(code=1) from None


@app.command("noop", help="Nic nie robi, przykład dodatkowej komendy")
def noop():
    """Pusta komenda dla testów wielokomendowego CLI."""
    pass


def main():
    """Punkt wejścia dla CLI."""
    app()


if __name__ == "__main__":
    main()
