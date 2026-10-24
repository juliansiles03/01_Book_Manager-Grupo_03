import csv

from decimal import Decimal, InvalidOperation
from pathlib import Path

from scrapy.crawler import CrawlerProcess

from book_manager.repositories.database_repositories import (
    AlmacenDB,
)
from book_manager.scraper.alerts import generar_alertas
from book_manager.scraper.spider import CuspideSpider


def pedir_umbral() -> Decimal:
    """Solicita la diferencia porcentual antes de consultar la web."""
    entrada = input(
        "Diferencia mínima para alertas (%): "
    ).strip()

    try:
        umbral = Decimal(
            entrada.replace(",", ".")
        )
    except InvalidOperation as error:
        raise ValueError(
            "Ingresá un porcentaje numérico."
        ) from error

    if not umbral.is_finite() or umbral < 0:
        raise ValueError(
            "El porcentaje debe ser mayor o igual a cero."
        )

    return umbral


def ejecutar_scraper(
    umbral_porcentual: Decimal | None = None,
) -> tuple[Path, Path]:
    """Extrae precios y genera las alertas de esa ejecución."""
    if umbral_porcentual is None:
        umbral_porcentual = pedir_umbral()

    if (
        not umbral_porcentual.is_finite()
        or umbral_porcentual < 0
    ):
        raise ValueError(
            "El porcentaje debe ser mayor o igual a cero."
        )

    almacen = AlmacenDB()

    try:
        libros = almacen.libros.leer_todos()
        catalogo: list[dict[str, object]] = [
            {
                "id": libro.id,
                "isbn": libro.isbn,
                "titulo": libro.titulo,
            }
            for libro in libros
        ]
    finally:
        almacen.cerrar()

    if not catalogo:
        raise ValueError(
            "No hay libros en el catálogo para buscar."
        )

    carpeta_reportes = (
        Path(__file__).resolve().parents[1]
        / "reportes"
    )
    ruta_extraccion = (
        carpeta_reportes
        / "extraccion_cuspide.csv"
    )
    ruta_alertas = (
        carpeta_reportes
        / "alertas_precios.csv"
    )

    proceso = CrawlerProcess(
        settings={
            "ITEM_PIPELINES": {
                (
                    "book_manager.scraper.pipelines."
                    "ValidarLibroCuspidePipeline"
                ): 100,
                (
                    "book_manager.scraper.exporters."
                    "GuardarExtraccionPipeline"
                ): 200,
            },
            "RESULTADOS_CUSPIDE": str(
                ruta_extraccion
            ),
            "FEED_EXPORT_ENCODING": "utf-8",
        }
    )

    proceso.crawl(
        CuspideSpider,
        libros_catalogo=catalogo,
    )
    proceso.start()

    with ruta_extraccion.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as archivo:
        cantidad = sum(
            1 for _ in csv.DictReader(archivo)
        )

    resultado_alertas = generar_alertas(
        ruta_extraccion,
        ruta_alertas,
        umbral_porcentual,
    )

    print(
        f"Productos del catálogo encontrados: {cantidad}."
    )
    print(
        f"Umbral elegido: {umbral_porcentual}%."
    )
    print(
        f"Alertas generadas: "
        f"{resultado_alertas['alertas']}."
    )
    print(
        "Productos sin precio interno ARS:",
        resultado_alertas["sin_precio_ars"],
    )
    print("Extracción:", ruta_extraccion)
    print("Alertas:", ruta_alertas)

    return ruta_extraccion, ruta_alertas


if __name__ == "__main__":
    ejecutar_scraper()
