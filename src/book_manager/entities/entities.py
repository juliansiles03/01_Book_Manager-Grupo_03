from datetime import date


class EntidadBase:
    """Entidad identificada por un ID de solo lectura."""

    def __init__(self, id: int) -> None:
        self._id: int = id

    @property
    def id(self) -> int:
        return self._id


class EntidadConNombre(EntidadBase):
    """Comparte el ID y el nombre de las entidades de catálogo."""

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self._nombre: str = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, nombre: str) -> None:
        self._nombre = nombre


class Genero(EntidadConNombre):
    """Categoría literaria de un libro."""


class Editorial(EntidadConNombre):
    """Editorial que provee libros a la librería."""


class TipoCotizacion(EntidadConNombre):
    """Tipo de cotización del dólar, como Oficial, Blue o MEP."""


class Moneda(EntidadConNombre):
    """Moneda identificada por su nombre y código."""

    def __init__(self, id: int, nombre: str, codigo: str) -> None:
        super().__init__(id, nombre)
        self._codigo: str = codigo

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, codigo: str) -> None:
        self._codigo = codigo


class Libro(EntidadBase):
    """Libro relacionado con objetos Editorial y Genero."""

    def __init__(
        self,
        id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial: Editorial,
        genero: Genero,
    ) -> None:
        super().__init__(id)
        self._isbn: str = isbn
        self._titulo: str = titulo
        self._autor: str = autor
        self._editorial: Editorial = editorial
        self._genero: Genero = genero

    @property
    def isbn(self) -> str:
        return self._isbn

    @isbn.setter
    def isbn(self, isbn: str) -> None:
        self._isbn = isbn

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, titulo: str) -> None:
        self._titulo = titulo

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, autor: str) -> None:
        self._autor = autor

    @property
    def editorial(self) -> Editorial:
        return self._editorial

    @editorial.setter
    def editorial(self, editorial: Editorial) -> None:
        self._editorial = editorial

    @property
    def genero(self) -> Genero:
        return self._genero

    @genero.setter
    def genero(self, genero: Genero) -> None:
        self._genero = genero


class Precio(EntidadBase):
    """Valor de un libro expresado en una moneda."""

    def __init__(
        self, id: int, libro: Libro, moneda: Moneda, valor: float
    ) -> None:
        super().__init__(id)
        self._libro: Libro = libro
        self._moneda: Moneda = moneda
        self._valor: float = valor

    @property
    def libro(self) -> Libro:
        return self._libro

    @libro.setter
    def libro(self, libro: Libro) -> None:
        self._libro = libro

    @property
    def moneda(self) -> Moneda:
        return self._moneda

    @moneda.setter
    def moneda(self, moneda: Moneda) -> None:
        self._moneda = moneda

    @property
    def valor(self) -> float:
        return self._valor

    @valor.setter
    def valor(self, valor: float) -> None:
        self._valor = valor


class Stock:
    """Existencias de un libro, identificadas por el ID del libro."""

    def __init__(self, libro: Libro, cantidad: int) -> None:
        self._libro: Libro = libro
        self._cantidad: int = cantidad

    @property
    def libro(self) -> Libro:
        return self._libro

    @property
    def libro_id(self) -> int:
        return self._libro.id

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, cantidad: int) -> None:
        self._cantidad = cantidad


class CotizacionDolar:
    """Cotización identificada por el tipo y la fecha."""

    def __init__(
        self,
        tipo: TipoCotizacion,
        fecha: date,
        compra: float,
        venta: float,
    ) -> None:
        self._tipo: TipoCotizacion = tipo
        self._fecha: date = fecha
        self._compra: float = compra
        self._venta: float = venta

    @property
    def tipo(self) -> TipoCotizacion:
        return self._tipo

    @property
    def tipo_id(self) -> int:
        return self._tipo.id

    @property
    def fecha(self) -> date:
        return self._fecha

    @property
    def compra(self) -> float:
        return self._compra

    @compra.setter
    def compra(self, compra: float) -> None:
        self._compra = compra

    @property
    def venta(self) -> float:
        return self._venta

    @venta.setter
    def venta(self, venta: float) -> None:
        self._venta = venta
