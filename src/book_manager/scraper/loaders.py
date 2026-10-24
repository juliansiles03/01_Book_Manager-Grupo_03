import re

from decimal import Decimal, InvalidOperation

from itemloaders.processors import Identity, MapCompose, TakeFirst
from scrapy.loader import ItemLoader

from book_manager.scraper.items import LibroCuspideItem


def limpiar_texto(valor: object) -> str:
    """Elimina espacios repetidos del texto extraído."""
    return " ".join(str(valor).split())


def convertir_precio_argentino(
    valor: object,
) -> Decimal | None:
    """Convierte un precio en pesos con coma decimal a Decimal."""
    texto = limpiar_texto(valor)
    coincidencia = re.search(
        r"\d[\d.\s]*(?:,\d{1,2})?",
        texto,
    )

    if coincidencia is None:
        return None

    numero = (
        coincidencia.group()
        .replace(" ", "")
        .replace(".", "")
        .replace(",", ".")
    )

    try:
        return Decimal(numero)
    except InvalidOperation:
        return None


class LibroCuspideLoader(ItemLoader):
    """Normaliza los campos obtenidos por CuspideSpider."""

    default_item_class = LibroCuspideItem
    default_output_processor = TakeFirst()

    titulo_in = MapCompose(limpiar_texto)
    descripcion_in = MapCompose(limpiar_texto)
    isbn_in = MapCompose(limpiar_texto)
    precio_web_in = MapCompose(
        convertir_precio_argentino
    )

    formas_pago_in = Identity()
    formas_pago_out = Identity()
