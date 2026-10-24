from decimal import Decimal

from scrapy.exceptions import DropItem

from book_manager.scraper.items import LibroCuspideItem


class ValidarLibroCuspidePipeline:
    """Conserva resultados válidos del catálogo, sin duplicados."""

    def __init__(self) -> None:
        self._isbn_vistos: set[str] = set()

    def open_spider(self, spider: object) -> None:
        """Reinicia el seguimiento al comenzar cada extracción."""
        self._isbn_vistos.clear()

    def process_item(
        self,
        item: LibroCuspideItem,
        spider: object,
    ) -> LibroCuspideItem:
        """Comprueba ISBN, precio y pertenencia al catálogo."""
        isbn = str(item.get("isbn", "")).strip()
        precio = item.get("precio_web")
        libro_id = item.get("libro_id")

        catalogo: dict[str, int] = getattr(
            spider, "isbn_del_catalogo", {}
        )

        if isbn not in catalogo:
            raise DropItem(
                f"ISBN ajeno al catálogo: {isbn!r}"
            )

        if libro_id != catalogo[isbn]:
            raise DropItem(
                f"El libro {libro_id!r} no corresponde "
                f"al ISBN {isbn}."
            )

        if not isinstance(precio, Decimal) or precio < 0:
            raise DropItem(
                f"Precio web inválido para ISBN {isbn}."
            )

        if isbn in self._isbn_vistos:
            raise DropItem(
                f"Resultado duplicado para ISBN {isbn}."
            )

        item["isbn"] = isbn
        item["titulo"] = str(
            item.get("titulo", "")
        ).strip()
        item["descripcion"] = str(
            item.get("descripcion", "")
        ).strip()
        item["imagen_url"] = str(
            item.get("imagen_url", "")
        ).strip()
        item["url_producto"] = str(
            item.get("url_producto", "")
        ).strip()
        item["formas_pago"] = list(
            item.get("formas_pago", [])
        )

        self._isbn_vistos.add(isbn)
        return item
