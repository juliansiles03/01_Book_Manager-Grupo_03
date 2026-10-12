#@title Entidades con validaciones en constructores y setters

from datetime import date


def _validar_texto(valor: str, campo: str) -> str:
    """Valida un texto obligatorio y quita espacios externos."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} debe ser un texto no vacío.")
    return valor.strip()


def _validar_importe(valor: float) -> float:
    """Acepta importes numéricos, finitos y no negativos."""
    if type(valor) not in (int, float) or not 0 <= valor < float("inf"):
        raise ValueError("El importe debe ser finito y no negativo.")
    return valor


def _validar_isbn(isbn: str) -> str:
    """Valida el formato y el dígito verificador de ISBN-10 o ISBN-13."""
    isbn = _validar_texto(isbn, "El ISBN")
    isbn = isbn.replace("-", "").replace(" ", "").upper()

    if not isbn.isascii():
        raise ValueError("El ISBN contiene caracteres inválidos.")

    if len(isbn) == 13 and isbn.isdigit() and isbn[:3] in ("978", "979"):
        suma = sum(
            int(digito) * (1 if indice % 2 == 0 else 3)
            for indice, digito in enumerate(isbn)
        )
        if suma % 10 == 0:
            return isbn

    if (
        len(isbn) == 10
        and isbn[:9].isdigit()
        and (isbn[-1].isdigit() or isbn[-1] == "X")
    ):
        suma = sum(
            (10 if digito == "X" else int(digito)) * (10 - indice)
            for indice, digito in enumerate(isbn)
        )
        if suma % 11 == 0:
            return isbn

    raise ValueError("El ISBN debe ser un ISBN-10 o ISBN-13 válido.")


class EntidadBase:
    """Entidad identificada por un ID de solo lectura."""

    def __init__(self, id: int) -> None:
        if type(id) is not int or id <= 0:
            raise ValueError("El ID debe ser un entero positivo.")
        self._id: int = id

    @property
    def id(self) -> int:
        return self._id


class EntidadConNombre(EntidadBase):
    """Comparte el ID y el nombre de las entidades de catálogo."""

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, nombre: str) -> None:
        self._nombre = _validar_texto(nombre, "El nombre")


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
        self.codigo = codigo

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, codigo: str) -> None:
        codigo = _validar_texto(codigo, "El código").upper()

        if len(codigo) != 3 or not codigo.isascii() or not codigo.isalpha():
            raise ValueError("El código debe tener tres letras, como ARS.")

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
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial = editorial
        self.genero = genero

    @property
    def isbn(self) -> str:
        return self._isbn

    @isbn.setter
    def isbn(self, isbn: str) -> None:
        self._isbn = _validar_isbn(isbn)

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, titulo: str) -> None:
        self._titulo = _validar_texto(titulo, "El título")

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, autor: str) -> None:
        self._autor = _validar_texto(autor, "El autor")

    @property
    def editorial(self) -> Editorial:
        return self._editorial

    @editorial.setter
    def editorial(self, editorial: Editorial) -> None:
        if not isinstance(editorial, Editorial):
            raise ValueError("La editorial debe ser un objeto Editorial.")
        self._editorial = editorial

    @property
    def genero(self) -> Genero:
        return self._genero

    @genero.setter
    def genero(self, genero: Genero) -> None:
        if not isinstance(genero, Genero):
            raise ValueError("El género debe ser un objeto Genero.")
        self._genero = genero


class Precio(EntidadBase):
    """Valor de un libro expresado en una moneda."""

    def __init__(
        self, id: int, libro: Libro, moneda: Moneda, valor: float
    ) -> None:
        super().__init__(id)
        self.libro = libro
        self.moneda = moneda
        self.valor = valor

    @property
    def libro(self) -> Libro:
        return self._libro

    @libro.setter
    def libro(self, libro: Libro) -> None:
        if not isinstance(libro, Libro):
            raise ValueError("El libro debe ser un objeto Libro.")
        self._libro = libro

    @property
    def moneda(self) -> Moneda:
        return self._moneda

    @moneda.setter
    def moneda(self, moneda: Moneda) -> None:
        if not isinstance(moneda, Moneda):
            raise ValueError("La moneda debe ser un objeto Moneda.")
        self._moneda = moneda

    @property
    def valor(self) -> float:
        return self._valor

    @valor.setter
    def valor(self, valor: float) -> None:
        self._valor = _validar_importe(valor)


class Stock:
    """Existencias de un libro, identificadas por el ID del libro."""

    def __init__(self, libro: Libro, cantidad: int) -> None:
        if not isinstance(libro, Libro):
            raise ValueError("El libro debe ser un objeto Libro.")
        self._libro: Libro = libro
        self.cantidad = cantidad

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
        if type(cantidad) is not int or cantidad < 0:
            raise ValueError("La cantidad debe ser un entero no negativo.")
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
        if not isinstance(tipo, TipoCotizacion):
            raise ValueError("El tipo debe ser un objeto TipoCotizacion.")
        if type(fecha) is not date:
            raise ValueError("La fecha debe ser un objeto date.")

        self._tipo: TipoCotizacion = tipo
        self._fecha: date = fecha
        self.compra = compra
        self.venta = venta

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
        self._compra = _validar_importe(compra)

    @property
    def venta(self) -> float:
        return self._venta

    @venta.setter
    def venta(self, venta: float) -> None:
        self._venta = _validar_importe(venta)
