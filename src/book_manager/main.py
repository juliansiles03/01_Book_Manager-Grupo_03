from pathlib import Path

from book_manager.migrations.migrations import migrar_datos
from book_manager.repositories.repositories import AlmacenDB
from book_manager.services.services import (
    ServicioCotizacionDolar,
    ServicioEditorial,
    ServicioGenero,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioStock,
    ServicioTipoCotizacion,
)
from book_manager.ui.console import Consola


def main(import_default_data: bool = True) -> None:
    """Prepara los datos, crea los servicios y ejecuta la consola."""
    carpeta_migraciones: Path = (
        Path(__file__).resolve().parent / "migrations"
    )

    if import_default_data:
        migrar_datos(
            str(carpeta_migraciones / "csv"),
            str(carpeta_migraciones / "sql"),
        )

    almacen: AlmacenDB = AlmacenDB()

    try:
        consola: Consola = Consola(
            generos=ServicioGenero(almacen),
            editoriales=ServicioEditorial(almacen),
            monedas=ServicioMoneda(almacen),
            tipos=ServicioTipoCotizacion(almacen),
            libros=ServicioLibro(almacen),
            precios=ServicioPrecio(almacen),
            stocks=ServicioStock(almacen),
            cotizaciones=ServicioCotizacionDolar(almacen),
        )
        consola.ejecutar()
    finally:
        almacen.cerrar()


if __name__ == "__main__":
    main()
