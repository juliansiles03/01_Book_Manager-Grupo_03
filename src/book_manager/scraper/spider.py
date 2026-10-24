from datetime import datetime, timezone
from urllib.parse import urlencode

import scrapy

from book_manager.scraper.loaders import LibroCuspideLoader


class CuspideSpider(scrapy.Spider):
    """Busca títulos del catálogo y comprueba cada producto por ISBN."""

    name = "cuspide"
    allowed_domains = ["cuspide.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_TIMEOUT": 20,
        "RETRY_TIMES": 1,
        "ROBOTSTXT_OBEY": True,
        "LOG_LEVEL": "WARNING",
    }

    def __init__(
        self,
        libros_catalogo: list[dict[str, object]],
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)

        if not libros_catalogo:
            raise ValueError(
                "No hay libros en el catálogo para consultar."
            )

        self.libros_catalogo = libros_catalogo
        self.isbn_del_catalogo: dict[str, int] = {
            str(libro["isbn"]): int(libro["id"])
            for libro in libros_catalogo
        }

    async def start(self):
        """Inicia exclusivamente búsquedas por títulos del catálogo."""
        for libro in self.libros_catalogo:
            titulo = str(libro["titulo"]).strip()

            if not titulo:
                continue

            parametros = urlencode(
                {
                    "s": titulo,
                    "post_type": "product",
                }
            )
            url = f"https://cuspide.com/?{parametros}"

            yield scrapy.Request(
                url,
                callback=self.parse_busqueda,
                cb_kwargs={"libro": libro},
            )

    def parse_busqueda(
        self,
        response: scrapy.http.Response,
        libro: dict[str, object],
    ):
        """Visita los primeros diez productos de esa búsqueda."""
        enlaces = response.css(
            "div.product-small.box "
            "a[href*='/producto/']::attr(href)"
        ).getall()

        enlaces_unicos = list(dict.fromkeys(enlaces))

        for enlace in enlaces_unicos[:10]:
            yield response.follow(
                enlace,
                callback=self.parse_producto,
                cb_kwargs={"libro": libro},
            )

    def parse_producto(
        self,
        response: scrapy.http.Response,
        libro: dict[str, object],
    ):
        """Extrae la ficha únicamente si coincide el ISBN propio."""
        isbn_web = (
            response.css(
                ".product_meta .sku::text"
            ).get(default="")
        ).strip()

        if isbn_web != str(libro["isbn"]):
            return

        loader = LibroCuspideLoader(response=response)

        loader.add_value("libro_id", int(libro["id"]))
        loader.add_value("isbn", isbn_web)

        loader.add_css(
            "titulo",
            "h1.product_title::text",
        )
        loader.add_css(
            "precio_web",
            ".product-info .price-wrapper "
            "p.price bdi::text",
        )

        imagen = (
            response.css(
                "img.wp-post-image::attr(data-large_image)"
            ).get()
            or response.css(
                "img.wp-post-image::attr(src)"
            ).get()
            or ""
        )
        loader.add_value(
            "imagen_url",
            response.urljoin(imagen) if imagen else "",
        )

        descripcion = response.xpath(
            "//*[contains(@class, 'product-page-description') "
            "or @id='tab-description']//text()"
        ).getall()

        if not descripcion:
            descripcion = response.xpath(
                "//h3[contains(., 'Sinopsis')]"
                "/following-sibling::p[1]//text()"
            ).getall()

        loader.add_value(
            "descripcion",
            " ".join(descripcion),
        )
        loader.add_value("url_producto", response.url)
        loader.add_value(
            "fecha_extraccion",
            datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
        )

        item = loader.load_item()
        precio_publicado = str(
            item.get("precio_web", "")
        )

        medios_pago = response.css(
            "#contentPaymentsPopUpArg li"
        )

        item["formas_pago"] = [
            {
                "forma": medio.xpath(
                    "normalize-space(.)"
                ).get().lstrip("> ").strip(),
                "precio_publicado": precio_publicado,
            }
            for medio in medios_pago
            if medio.xpath(
                "normalize-space(.)"
            ).get()
        ]

        yield item
