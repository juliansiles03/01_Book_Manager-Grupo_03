import scrapy


class LibroCuspideItem(scrapy.Item):
    """Datos de Cúspide vinculados con un libro del catálogo."""
    
    libro_id = scrapy.Field()
    isbn = scrapy.Field()
    titulo = scrapy.Field()
    precio_web = scrapy.Field()
    imagen_url = scrapy.Field()
    formas_pago = scrapy.Field()
    descripcion = scrapy.Field()
    url_producto = scrapy.Field()
    fecha_extraccion = scrapy.Field()
