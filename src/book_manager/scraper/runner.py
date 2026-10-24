import csv

from pathlib import Path

from scrapy.crawler import CrawlerProcess

from book_manager.repositories.database_repositories import (
    AlmacenDB,
)
from book_manager.scraper.spider import CuspideSpider


def ejecutar_scraper() -> Path:
    """Busca en Cúspide los libros registrados en Supabase."""
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

    ruta_resultados = (
        Path(__file__).resolve().parents[1]
        / "reportes"
        / "extraccion_cuspide.csv"
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
                ruta_resultados
            ),
            "FEED_EXPORT_ENCODING": "utf-8",
        }
    )

    proceso.crawl(
        CuspideSpider,
        libros_catalogo=catalogo,
    )
    proceso.start()

    with ruta_resultados.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as archivo:
        cantidad = sum(
            1 for _ in csv.DictReader(archivo)
        )

    print(
        f"Productos de nuestro catálogo encontrados: {cantidad}."
    )
    print("Extracción guardada en:", ruta_resultados)

    return ruta_resultados


if __name__ == "__main__":
    ejecutar_scraper()
