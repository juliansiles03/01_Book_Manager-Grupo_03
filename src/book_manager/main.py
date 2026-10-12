#@title Día 7 - Punto de entrada y creación de servicios

from pathlib import Path

from book_manager.preload_data.preload_data import crear_archivos_csv
from book_manager.repositories.repositories import AlmacenCSV
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
    directorio_csv: Path = (
        Path(__file__).resolve().parent / "migrations" / "csv"
    )

    if import_default_data:
        crear_archivos_csv(directorio_csv)

    almacen: AlmacenCSV = AlmacenCSV(directorio_csv)

    generos: ServicioGenero = ServicioGenero(almacen)
    editoriales: ServicioEditorial = ServicioEditorial(almacen)
    monedas: ServicioMoneda = ServicioMoneda(almacen)
    tipos: ServicioTipoCotizacion = ServicioTipoCotizacion(almacen)
    libros: ServicioLibro = ServicioLibro(almacen)
    precios: ServicioPrecio = ServicioPrecio(almacen)
    stocks: ServicioStock = ServicioStock(almacen)
    cotizaciones: ServicioCotizacionDolar = ServicioCotizacionDolar(
        almacen
    )

    consola: Consola = Consola(
        generos=generos,
        editoriales=editoriales,
        monedas=monedas,
        tipos=tipos,
        libros=libros,
        precios=precios,
        stocks=stocks,
        cotizaciones=cotizaciones,
    )
    consola.ejecutar()


if __name__ == "__main__":
    main()
