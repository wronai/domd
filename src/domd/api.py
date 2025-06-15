#!/usr/bin/env python3
"""
Punkt wejściowy dla REST API aplikacji DoMD.
"""

import argparse
import logging
import sys
from pathlib import Path

from .adapters.api.flask_api import DomdFlaskApi


def create_parser() -> argparse.ArgumentParser:
    """Tworzy parser argumentów wiersza poleceń."""
    parser = argparse.ArgumentParser(
        prog="domd-api",
        description="DoMD REST API Server",
        epilog="""
Examples:
  domd-api                         # Uruchom serwer API na domyślnym porcie 5000
  domd-api --port 8080             # Uruchom serwer API na porcie 8080
  domd-api --path /path/to/project # Uruchom serwer API dla określonego projektu
  domd-api --debug                 # Uruchom serwer API w trybie debug
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--path",
        "-p",
        default=".",
        help="Ścieżka do katalogu projektu (domyślnie: bieżący katalog)",
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host, na którym ma być uruchomiony serwer (domyślnie: 0.0.0.0)",
    )

    parser.add_argument(
        "--port",
        "-P",
        type=int,
        default=5000,
        help="Port, na którym ma być uruchomiony serwer (domyślnie: 5000)",
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Uruchom serwer w trybie debug",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Włącz szczegółowe logowanie",
    )

    return parser


def setup_logging(verbose: bool) -> None:
    """
    Konfiguruje logowanie.

    Args:
        verbose: Czy włączyć szczegółowe logowanie
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> int:
    """
    Główny punkt wejściowy dla REST API.

    Returns:
        Kod wyjścia
    """
    parser = create_parser()
    args = parser.parse_args()

    # Konfiguracja logowania
    setup_logging(args.verbose)

    try:
        # Inicjalizacja ścieżki projektu
        project_path = Path(args.path).resolve()
        if not project_path.exists():
            print(
                f"Błąd: Ścieżka projektu nie istnieje: {project_path}", file=sys.stderr
            )
            return 1

        if not project_path.is_dir():
            print(
                f"Błąd: Ścieżka projektu nie jest katalogiem: {project_path}",
                file=sys.stderr,
            )
            return 1

        # Inicjalizacja API
        api = DomdFlaskApi(project_path=project_path)

        # Wyświetl informacje o serwerze
        print("DoMD REST API Server")
        print(f"Projekt: {project_path}")
        print(f"Uruchamianie serwera na http://{args.host}:{args.port}")
        print("Dostępne endpointy:")
        print("  GET  /health                  - Sprawdź stan serwera")
        print("  GET  /api/commands            - Pobierz listę komend")
        print("  POST /api/commands/scan       - Skanuj projekt w poszukiwaniu komend")
        print("  POST /api/commands/test       - Testuj komendy")
        print("  GET  /api/reports             - Pobierz informacje o raportach")
        print("  POST /api/reports/generate    - Generuj raporty")
        print("  GET  /api/stats               - Pobierz statystyki")
        print("Naciśnij CTRL+C, aby zatrzymać serwer")

        # Uruchom serwer
        api.run(host=args.host, port=args.port, debug=args.debug)
        return 0

    except KeyboardInterrupt:
        print("\nSerwer zatrzymany przez użytkownika")
        return 0
    except Exception as e:
        print(f"Błąd: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
