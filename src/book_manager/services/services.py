import abc
from datetime import date
from typing import Generic, List, Optional, TypeVar

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    EntidadBase,
    EntidadConNombre,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)
from book_manager.repositories.repositories import (
    AlmacenCSV,
    IRepositorio,
)


T = TypeVar("T", bound=EntidadBase)
N = TypeVar("N", bound=EntidadConNombre)


def validar_id(id: int) -> None:
    """Exige un identificador entero positivo."""
    if type(id) is not int or id <= 0:
        raise ValueError("El ID debe ser un entero positivo.")


def validar_texto(valor: str, campo: str) -> None:
    """Exige un texto no vacío."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} no puede estar vacío.")


def validar_importe(valor: float) -> None:
    """Exige un importe finito y no negativo."""
    if type(valor) not in (int, float) or not 0 <= valor < float("inf"):
        raise ValueError(
            "El importe debe ser un número finito no negativo."
        )


class ServicioBase(abc.ABC, Generic[T]):
    """Coordina el CRUD, las validaciones y el guardado en CSV."""

    def __init__(
        self,
        almacen: AlmacenCSV,
        repositorio: IRepositorio[T],
    ) -> None:
        self._almacen: AlmacenCSV = almacen
        self._repositorio: IRepositorio[T] = repositorio

    @abc.abstractmethod
    def _validar(self, entidad: T) -> None:
        """Valida los datos específicos de la entidad."""
        pass

    @abc.abstractmethod
    def _copiar_datos(self, destino: T, origen: T) -> None:
        """Actualiza el objeto existente sin romper sus referencias."""
        pass

    def _en_uso(self, id: int) -> bool:
        """Indica si otras entidades utilizan este registro."""
        return False

    def crear(self, entidad: T) -> T:
        """Valida, crea y guarda una entidad."""
        validar_id(entidad.id)
        self._validar(entidad)
        resultado: T = self._repositorio.crear(entidad)
        self._almacen.guardar()
        return resultado

    def leer_por_id(self, id: int) -> Optional[T]:
        """Busca una entidad por un ID válido."""
        validar_id(id)
        return self._repositorio.leer_por_id(id)

    def leer_todos(self) -> List[T]:
        """Devuelve todas las entidades del repositorio."""
        return self._repositorio.leer_todos()

    def actualizar(self, entidad: T) -> T:
        """Valida los cambios y modifica una entidad existente."""
        validar_id(entidad.id)
        existente: Optional[T] = self._repositorio.leer_por_id(
            entidad.id
        )

        if existente is None:
            raise ValueError(
                "La entidad que se desea modificar no existe."
            )

        self._validar(entidad)
        self._copiar_datos(existente, entidad)
        self._repositorio.actualizar(existente)
        self._almacen.guardar()
        return existente

    def eliminar(self, id: int) -> bool:
        """Elimina una entidad si ninguna otra la utiliza."""
        validar_id(id)

        if self._repositorio.leer_por_id(id) is None:
            return False

        if self._en_uso(id):
            raise ValueError(
                "No se puede eliminar: existen datos asociados."
            )

        resultado: bool = self._repositorio.eliminar(id)
        self._almacen.guardar()
        return resultado


class ServicioNombre(ServicioBase[N], Generic[N]):
    """Comparte las reglas de las entidades que poseen nombre."""

    def _validar(self, entidad: N) -> None:
        validar_texto(entidad.nombre, "El nombre")

        for existente in self.leer_todos():
            mismo_nombre: bool = (
                existente.nombre.strip().casefold()
                == entidad.nombre.strip().casefold()
            )
            if existente.id != entidad.id and mismo_nombre:
                raise ValueError(
                    "Ya existe una entidad con ese nombre."
                )

    def _copiar_datos(self, destino: N, origen: N) -> None:
        destino.nombre = origen.nombre


class ServicioGenero(ServicioNombre[Genero]):
    """Gestiona géneros y evita borrar los utilizados por libros."""

    def __init__(self, almacen: AlmacenCSV) -> None:
        super().__init__(almacen, almacen.generos)

    def _en_uso(self, id: int) -> bool:
        return any(
            libro.genero.id == id
            for libro in self._almacen.libros.leer_todos()
        )


class ServicioEditorial(ServicioNombre[Editorial]):
    """Gestiona editoriales y sus referencias desde libros."""

    def __init__(self, almacen: AlmacenCSV) -> None:
        super().__init__(almacen, almacen.editoriales)

    def _en_uso(self, id: int) -> bool:
        return any(
            libro.editorial.id == id
            for libro in self._almacen.libros.leer_todos()
        )


class ServicioMoneda(ServicioNombre[Moneda]):
    """Gestiona monedas con códigos únicos de tres letras."""

    def __init__(self, almacen: AlmacenCSV) -> None:
        super().__init__(almacen, almacen.monedas)

    def _validar(self, entidad: Moneda) -> None:
        super()._validar(entidad)
        validar_texto(entidad.codigo, "El código")
        codigo: str = entidad.codigo

        if (
            len(codigo) != 3
            or not codigo.isascii()
            or not codigo.isalpha()
        ):
            raise ValueError(
                "El código debe tener tres letras, como ARS."
            )

        if any(
            moneda.id != entidad.id
            and moneda.codigo.upper() == codigo.upper()
            for moneda in self.leer_todos()
        ):
            raise ValueError(
                "Ya existe una moneda con ese código."
            )

    def _copiar_datos(
        self, destino: Moneda, origen: Moneda
    ) -> None:
        super()._copiar_datos(destino, origen)
        destino.codigo = origen.codigo

    def _en_uso(self, id: int) -> bool:
        return any(
            precio.moneda.id == id
            for precio in self._almacen.precios.leer_todos()
        )


class ServicioTipoCotizacion(ServicioNombre[TipoCotizacion]):
    """Gestiona tipos de cotización y protege su histórico."""

    def __init__(self, almacen: AlmacenCSV) -> None:
        super().__init__(almacen, almacen.tipos)

    def _en_uso(self, id: int) -> bool:
        return bool(
            self._almacen.cotizaciones.leer_historico_por_tipo(id)
        )


class ServicioLibro(ServicioBase[Libro]):
    """Valida los datos bibliográficos y las relaciones del libro."""

    def __init__(self, almacen: AlmacenCSV) -> None:
        super().__init__(almacen, almacen.libros)

    def _validar(self, entidad: Libro) -> None:
        validar_texto(entidad.isbn, "El ISBN")
        validar_texto(entidad.titulo, "El título")
        validar_texto(entidad.autor, "El autor")

        if not isinstance(entidad.genero, Genero):
            raise ValueError(
                "El género debe ser un objeto Genero."
            )

        if not isinstance(entidad.editorial, Editorial):
            raise ValueError(
                "La editorial debe ser un objeto Editorial."
            )

        genero = self._almacen.generos.leer_por_id(
            entidad.genero.id
        )
        editorial = self._almacen.editoriales.leer_por_id(
            entidad.editorial.id
        )

        if genero is None or editorial is None:
            raise ValueError(
                "El género y la editorial deben estar registrados."
            )

        if any(
            libro.id != entidad.id and libro.isbn == entidad.isbn
            for libro in self.leer_todos()
        ):
            raise ValueError("Ya existe un libro con ese ISBN.")

        entidad.genero = genero
        entidad.editorial = editorial

    def _copiar_datos(self, destino: Libro, origen: Libro) -> None:
        destino.isbn = origen.isbn
        destino.titulo = origen.titulo
        destino.autor = origen.autor
        destino.editorial = origen.editorial
        destino.genero = origen.genero

    def _en_uso(self, id: int) -> bool:
        tiene_stock: bool = (
            self._almacen.stocks.leer_por_libro(id) is not None
        )
        tiene_precios: bool = any(
            precio.libro.id == id
            for precio in self._almacen.precios.leer_todos()
        )
        return tiene_stock or tiene_precios


class ServicioPrecio(ServicioBase[Precio]):
    """Valida importes y las relaciones con libros y monedas."""

    def __init__(self, almacen: AlmacenCSV) -> None:
        super().__init__(almacen, almacen.precios)

    def _validar(self, entidad: Precio) -> None:
        validar_importe(entidad.valor)

        if not isinstance(entidad.libro, Libro):
            raise ValueError("El libro debe ser un objeto Libro.")

        if not isinstance(entidad.moneda, Moneda):
            raise ValueError(
                "La moneda debe ser un objeto Moneda."
            )

        libro = self._almacen.libros.leer_por_id(
            entidad.libro.id
        )
        moneda = self._almacen.monedas.leer_por_id(
            entidad.moneda.id
        )

        if libro is None or moneda is None:
            raise ValueError(
                "El libro y la moneda deben estar registrados."
            )

        if any(
            precio.id != entidad.id
            and precio.libro.id == libro.id
            and precio.moneda.id == moneda.id
            for precio in self.leer_todos()
        ):
            raise ValueError(
                "Ya existe un precio para ese libro y moneda."
            )

        entidad.libro = libro
        entidad.moneda = moneda

    def _copiar_datos(
        self, destino: Precio, origen: Precio
    ) -> None:
        destino.libro = origen.libro
        destino.moneda = origen.moneda
        destino.valor = origen.valor


class ServicioStock:
    """Gestiona cantidades enteras no negativas para libros existentes."""

    def __init__(self, almacen: AlmacenCSV) -> None:
        self._almacen: AlmacenCSV = almacen

    def _validar(self, stock: Stock) -> Stock:
        """Valida el stock y lo vincula con el libro registrado."""
        if not isinstance(stock.libro, Libro):
            raise ValueError("El libro debe ser un objeto Libro.")

        validar_id(stock.libro_id)

        if type(stock.cantidad) is not int or stock.cantidad < 0:
            raise ValueError(
                "La cantidad debe ser un entero no negativo."
            )

        libro = self._almacen.libros.leer_por_id(stock.libro_id)
        if libro is None:
            raise ValueError("El libro no está registrado.")

        return Stock(libro, stock.cantidad)

    def crear(self, stock: Stock) -> Stock:
        """Valida y crea el stock de un libro."""
        resultado = self._almacen.stocks.crear(
            self._validar(stock)
        )
        self._almacen.guardar()
        return resultado

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Devuelve el stock del libro solicitado."""
        validar_id(libro_id)
        return self._almacen.stocks.leer_por_libro(libro_id)

    def leer_todos(self) -> List[Stock]:
        """Lista los stocks registrados."""
        return self._almacen.stocks.leer_todos()

    def actualizar(self, stock: Stock) -> Stock:
        """Valida y modifica un stock existente."""
        resultado = self._almacen.stocks.actualizar(
            self._validar(stock)
        )
        self._almacen.guardar()
        return resultado

    def eliminar(self, libro_id: int) -> bool:
        """Elimina el registro de stock del libro solicitado."""
        validar_id(libro_id)
        resultado: bool = self._almacen.stocks.eliminar(libro_id)
        if resultado:
            self._almacen.guardar()
        return resultado


class ServicioCotizacionDolar:
    """Gestiona las cotizaciones por tipo y fecha."""

    def __init__(self, almacen: AlmacenCSV) -> None:
        self._almacen: AlmacenCSV = almacen

    def _validar(
        self, cotizacion: CotizacionDolar
    ) -> CotizacionDolar:
        """Valida fecha, importes y tipo registrado."""
        if not isinstance(cotizacion.tipo, TipoCotizacion):
            raise ValueError(
                "El tipo debe ser un objeto TipoCotizacion."
            )

        validar_id(cotizacion.tipo_id)

        if type(cotizacion.fecha) is not date:
            raise ValueError("La fecha debe ser un objeto date.")

        validar_importe(cotizacion.compra)
        validar_importe(cotizacion.venta)

        tipo = self._almacen.tipos.leer_por_id(
            cotizacion.tipo_id
        )
        if tipo is None:
            raise ValueError(
                "El tipo de cotización no está registrado."
            )

        return CotizacionDolar(
            tipo,
            cotizacion.fecha,
            cotizacion.compra,
            cotizacion.venta,
        )

    def crear(
        self, cotizacion: CotizacionDolar
    ) -> CotizacionDolar:
        """Valida y crea una cotización."""
        resultado = self._almacen.cotizaciones.crear(
            self._validar(cotizacion)
        )
        self._almacen.guardar()
        return resultado

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: date
    ) -> Optional[CotizacionDolar]:
        """Busca una cotización por su clave."""
        validar_id(tipo_id)
        if type(fecha) is not date:
            raise ValueError("La fecha debe ser un objeto date.")

        return self._almacen.cotizaciones.leer_por_tipo_y_fecha(
            tipo_id, fecha
        )

    def leer_todos(self) -> List[CotizacionDolar]:
        """Lista todas las cotizaciones."""
        return self._almacen.cotizaciones.leer_todos()

    def leer_historico_por_tipo(
        self, tipo_id: int
    ) -> List[CotizacionDolar]:
        """Lista el histórico de un tipo ordenado por fecha."""
        validar_id(tipo_id)
        return self._almacen.cotizaciones.leer_historico_por_tipo(
            tipo_id
        )

    def actualizar(
        self, cotizacion: CotizacionDolar
    ) -> CotizacionDolar:
        """Valida y modifica una cotización existente."""
        resultado = self._almacen.cotizaciones.actualizar(
            self._validar(cotizacion)
        )
        self._almacen.guardar()
        return resultado

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina una cotización por tipo y fecha."""
        validar_id(tipo_id)
        if type(fecha) is not date:
            raise ValueError("La fecha debe ser un objeto date.")

        resultado: bool = self._almacen.cotizaciones.eliminar(
            tipo_id, fecha
        )
        if resultado:
            self._almacen.guardar()
        return resultado
