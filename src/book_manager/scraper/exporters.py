import csv
import json

from pathlib import Path
from typing import TextIO

from book_manager.scraper.items import LibroCuspideItem


COLUMNAS_EXTRACCION: tuple[str, ...] = (
    "libro_id",
    "isbn",
    "titulo",
    "precio_web",
    "imagen_url",
    "formas_pago",
    "descripcion",
    "url_producto",
    "fecha_extraccion",
)


class GuardarExtraccionPipeline:
    """Guarda en CSV los productos validados por el primer pipeline."""

    def __init__(self) -> None:
        self._archivo: TextIO | None = None
        self._escritor: csv.DictWriter | None = None

    def open_spider(self, spider: object) -> None:
        """Crea un archivo nuevo para cada ejecución."""
        ruta_configurada = spider.crawler.settings.get(
            "RESULTADOS_CUSPIDE"
        )

        if not ruta_configurada:
            raise ValueError(
                "Falta configurar RESULTADOS_CUSPIDE."
            )

        ruta = Path(ruta_configurada)
        ruta.parent.mkdir(parents=True, exist_ok=True)

        self._archivo = ruta.open(
            "w",
            encoding="utf-8",
            newline="",
        )
        self._escritor = csv.DictWriter(
            self._archivo,
            fieldnames=COLUMNAS_EXTRACCION,
        )
        self._escritor.writeheader()

    def process_item(
        self,
        item: LibroCuspideItem,
        spider: object,
    ) -> LibroCuspideItem:
        """Escribe los datos de un libro ya validado."""
        if self._escritor is None:
            raise RuntimeError(
                "El archivo de extracción no está abierto."
            )

        fila = {
            columna: item.get(columna, "")
            for columna in COLUMNAS_EXTRACCION
        }
        fila["precio_web"] = str(
            fila["precio_web"]
        )
        fila["formas_pago"] = json.dumps(
            fila["formas_pago"],
            ensure_ascii=False,
        )

        self._escritor.writerow(fila)
        return item

    def close_spider(self, spider: object) -> None:
        """Cierra el archivo al terminar la extracción."""
        if self._archivo is not None:
            self._archivo.close()
            self._archivo = None
            self._escritor = None
