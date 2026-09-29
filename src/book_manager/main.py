from pathlib import Path

from book_manager.preload_data.preload_data import crear_archivos_csv
from book_manager.repositories.repositories import AlmacenCSV
from book_manager.ui.console import Consola


def main(import_default_data: bool = True) -> None:
    """Prepara los datos y ejecuta la aplicación de consola."""
    directorio_csv: Path = (
        Path(__file__).resolve().parent / "migrations" / "csv"
    )

    if import_default_data:
        crear_archivos_csv(directorio_csv)

    almacen: AlmacenCSV = AlmacenCSV(directorio_csv)
    consola: Consola = Consola(almacen)
    consola.ejecutar()


if __name__ == "__main__":
    main()
