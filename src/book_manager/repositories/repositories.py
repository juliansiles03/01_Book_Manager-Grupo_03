import abc
import csv
import datetime
from pathlib import Path
from typing import Generic, List, Optional, TypeVar

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    EntidadBase,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)


T = TypeVar("T", bound=EntidadBase)


class IRepositorio(abc.ABC, Generic[T]):
    """Interfaz para repositorios con operaciones CRUD básicas."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        """Crea una entidad y falla si su ID ya existe."""
        pass

    @abc.abstractmethod
    def leer_por_id(self, id: int) -> Optional[T]:
        """Devuelve la entidad del ID indicado o None."""
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[T]:
        """Devuelve todas las entidades."""
        pass

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente."""
        pass

    @abc.abstractmethod
    def eliminar(self, id: int) -> bool:
        """Elimina una entidad por ID e informa si existía."""
        pass


class IRepositorioStock(abc.ABC):
    """Interfaz para repositorios del tipo Stock."""

    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        """Crea un stock y falla si el libro ya posee uno."""
        pass

    @abc.abstractmethod
    def leer_por_libro(
        self,
        libro_id: int,
    ) -> Optional[Stock]:
        """Devuelve el stock del libro indicado o None."""
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[Stock]:
        """Devuelve todos los registros de stock."""
        pass

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza un stock existente."""
        pass

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock de un libro e informa si existía."""
        pass


class IRepositorioCotizacionDolar(abc.ABC):
    """Interfaz para repositorios de CotizacionDolar."""

    @abc.abstractmethod
    def crear(
        self,
        cotizacion: CotizacionDolar,
    ) -> CotizacionDolar:
        """Crea una cotización para un tipo y una fecha."""
        pass

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: datetime.date,
    ) -> Optional[CotizacionDolar]:
        """Devuelve una cotización por tipo y fecha o None."""
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[CotizacionDolar]:
        """Devuelve todas las cotizaciones."""
        pass

    @abc.abstractmethod
    def leer_historico_por_tipo(
        self,
        tipo_id: int,
    ) -> List[CotizacionDolar]:
        """Devuelve el histórico de un tipo de cotización."""
        pass

    @abc.abstractmethod
    def actualizar(
        self,
        cotizacion: CotizacionDolar,
    ) -> CotizacionDolar:
        """Actualiza una cotización existente."""
        pass

    @abc.abstractmethod
    def eliminar(
        self,
        tipo_id: int,
        fecha: datetime.date,
    ) -> bool:
        """Elimina una cotización e informa si existía."""
        pass


class Repositorio(IRepositorio[T], Generic[T]):
    """Implementa el CRUD de entidades identificadas por ID."""

    def __init__(self) -> None:
        self._entidades: dict[int, T] = {}

    def crear(self, entidad: T) -> T:
        if entidad.id in self._entidades:
            raise ValueError(
                f"Ya existe una entidad con el ID {entidad.id}."
            )

        self._entidades[entidad.id] = entidad
        return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        return self._entidades.get(id)

    def leer_todos(self) -> List[T]:
        return list(self._entidades.values())

    def actualizar(self, entidad: T) -> T:
        if entidad.id not in self._entidades:
            raise ValueError(
                f"No existe una entidad con el ID {entidad.id}."
            )

        self._entidades[entidad.id] = entidad
        return entidad

    def eliminar(self, id: int) -> bool:
        if id not in self._entidades:
            return False

        del self._entidades[id]
        return True


class RepositorioLibro(Repositorio[Libro]):
    """Repositorio CRUD de libros."""


class RepositorioGenero(Repositorio[Genero]):
    """Repositorio CRUD de géneros."""


class RepositorioEditorial(Repositorio[Editorial]):
    """Repositorio CRUD de editoriales."""


class RepositorioMoneda(Repositorio[Moneda]):
    """Repositorio CRUD de monedas."""


class RepositorioTipoCotizacion(Repositorio[TipoCotizacion]):
    """Repositorio CRUD de tipos de cotización."""


class RepositorioPrecio(Repositorio[Precio]):
    """Repositorio CRUD de precios."""


class RepositorioStock(IRepositorioStock):
    """Implementa el CRUD de stock usando el libro como clave."""

    def __init__(self) -> None:
        self._stocks: dict[int, Stock] = {}

    def crear(self, stock: Stock) -> Stock:
        if stock.libro_id in self._stocks:
            raise ValueError(
                f"El libro {stock.libro_id} ya posee un stock."
            )

        self._stocks[stock.libro_id] = stock
        return stock

    def leer_por_libro(
        self,
        libro_id: int,
    ) -> Optional[Stock]:
        return self._stocks.get(libro_id)

    def leer_todos(self) -> List[Stock]:
        return list(self._stocks.values())

    def actualizar(self, stock: Stock) -> Stock:
        if stock.libro_id not in self._stocks:
            raise ValueError(
                f"No existe stock para el libro {stock.libro_id}."
            )

        self._stocks[stock.libro_id] = stock
        return stock

    def eliminar(self, libro_id: int) -> bool:
        if libro_id not in self._stocks:
            return False

        del self._stocks[libro_id]
        return True


class RepositorioCotizacionDolar(
    IRepositorioCotizacionDolar
):
    """Implementa el CRUD usando tipo y fecha como clave."""

    def __init__(self) -> None:
        self._cotizaciones: dict[
            tuple[int, datetime.date],
            CotizacionDolar,
        ] = {}

    def crear(
        self,
        cotizacion: CotizacionDolar,
    ) -> CotizacionDolar:
        clave: tuple[int, datetime.date] = (
            cotizacion.tipo_id,
            cotizacion.fecha,
        )

        if clave in self._cotizaciones:
            raise ValueError(
                "Ya existe una cotización para ese tipo y fecha."
            )

        self._cotizaciones[clave] = cotizacion
        return cotizacion

    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: datetime.date,
    ) -> Optional[CotizacionDolar]:
        return self._cotizaciones.get((tipo_id, fecha))

    def leer_todos(self) -> List[CotizacionDolar]:
        return list(self._cotizaciones.values())

    def leer_historico_por_tipo(
        self,
        tipo_id: int,
    ) -> List[CotizacionDolar]:
        historico: List[CotizacionDolar] = [
            cotizacion
            for cotizacion in self._cotizaciones.values()
            if cotizacion.tipo_id == tipo_id
        ]

        return sorted(
            historico,
            key=lambda cotizacion: cotizacion.fecha,
        )

    def actualizar(
        self,
        cotizacion: CotizacionDolar,
    ) -> CotizacionDolar:
        clave: tuple[int, datetime.date] = (
            cotizacion.tipo_id,
            cotizacion.fecha,
        )

        if clave not in self._cotizaciones:
            raise ValueError(
                "No existe una cotización para ese tipo y fecha."
            )

        self._cotizaciones[clave] = cotizacion
        return cotizacion

    def eliminar(
        self,
        tipo_id: int,
        fecha: datetime.date,
    ) -> bool:
        clave: tuple[int, datetime.date] = (
            tipo_id,
            fecha,
        )

        if clave not in self._cotizaciones:
            return False

        del self._cotizaciones[clave]
        return True


class AlmacenCSV:
    """Carga y guarda los ocho repositorios en archivos CSV."""

    def __init__(self, directorio: Path) -> None:
        self._directorio: Path = directorio
        self.generos = RepositorioGenero()
        self.editoriales = RepositorioEditorial()
        self.monedas = RepositorioMoneda()
        self.tipos = RepositorioTipoCotizacion()
        self.libros = RepositorioLibro()
        self.precios = RepositorioPrecio()
        self.stocks = RepositorioStock()
        self.cotizaciones = RepositorioCotizacionDolar()
        self._cargar()

    def _leer(self, nombre: str) -> List[dict[str, str]]:
        """Lee un CSV o devuelve una lista vacía si todavía no existe."""
        ruta: Path = self._directorio / nombre
        if not ruta.exists():
            return []

        with ruta.open(encoding="utf-8", newline="") as archivo:
            return list(csv.DictReader(archivo))

    def _escribir(
        self,
        nombre: str,
        campos: List[str],
        filas: List[List[str]],
    ) -> None:
        """Escribe un CSV y reemplaza su versión anterior."""
        self._directorio.mkdir(parents=True, exist_ok=True)
        ruta: Path = self._directorio / nombre
        temporal: Path = ruta.with_suffix(".tmp")

        with temporal.open(
            "w", encoding="utf-8", newline=""
        ) as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(campos)
            escritor.writerows(filas)

        temporal.replace(ruta)

    def _obtener(
        self,
        repositorio: IRepositorio[T],
        id: str,
    ) -> T:
        """Resuelve una referencia durante la carga."""
        entidad: Optional[T] = repositorio.leer_por_id(int(id))
        if entidad is None:
            raise ValueError(
                f"El CSV referencia una entidad inexistente: {id}."
            )
        return entidad

    def _cargar(self) -> None:
        """Reconstruye las entidades y sus relaciones en orden."""
        for fila in self._leer("generos.csv"):
            self.generos.crear(
                Genero(int(fila["id"]), fila["nombre"])
            )

        for fila in self._leer("editoriales.csv"):
            self.editoriales.crear(
                Editorial(int(fila["id"]), fila["nombre"])
            )

        for fila in self._leer("monedas.csv"):
            self.monedas.crear(
                Moneda(
                    int(fila["id"]),
                    fila["nombre"],
                    fila["codigo"],
                )
            )

        for fila in self._leer("tipos_cotizacion.csv"):
            self.tipos.crear(
                TipoCotizacion(
                    int(fila["id"]),
                    fila["nombre"],
                )
            )

        for fila in self._leer("libros.csv"):
            self.libros.crear(
                Libro(
                    int(fila["id"]),
                    fila["isbn"],
                    fila["titulo"],
                    fila["autor"],
                    self._obtener(
                        self.editoriales,
                        fila["editorial_id"],
                    ),
                    self._obtener(
                        self.generos,
                        fila["genero_id"],
                    ),
                )
            )

        for fila in self._leer("precios.csv"):
            self.precios.crear(
                Precio(
                    int(fila["id"]),
                    self._obtener(
                        self.libros,
                        fila["libro_id"],
                    ),
                    self._obtener(
                        self.monedas,
                        fila["moneda_id"],
                    ),
                    float(fila["valor"]),
                )
            )

        for fila in self._leer("stock.csv"):
            self.stocks.crear(
                Stock(
                    self._obtener(
                        self.libros,
                        fila["libro_id"],
                    ),
                    int(fila["cantidad"]),
                )
            )

        for fila in self._leer("cotizaciones.csv"):
            self.cotizaciones.crear(
                CotizacionDolar(
                    self._obtener(
                        self.tipos,
                        fila["tipo_id"],
                    ),
                    datetime.date.fromisoformat(
                        fila["fecha"]
                    ),
                    float(fila["compra"]),
                    float(fila["venta"]),
                )
            )

    def guardar(self) -> None:
        """Guarda los datos actuales de todos los repositorios."""
        self._escribir(
            "generos.csv",
            ["id", "nombre"],
            [
                [str(entidad.id), entidad.nombre]
                for entidad in self.generos.leer_todos()
            ],
        )
        self._escribir(
            "editoriales.csv",
            ["id", "nombre"],
            [
                [str(entidad.id), entidad.nombre]
                for entidad in self.editoriales.leer_todos()
            ],
        )
        self._escribir(
            "monedas.csv",
            ["id", "nombre", "codigo"],
            [
                [
                    str(entidad.id),
                    entidad.nombre,
                    entidad.codigo,
                ]
                for entidad in self.monedas.leer_todos()
            ],
        )
        self._escribir(
            "tipos_cotizacion.csv",
            ["id", "nombre"],
            [
                [str(entidad.id), entidad.nombre]
                for entidad in self.tipos.leer_todos()
            ],
        )
        self._escribir(
            "libros.csv",
            [
                "id",
                "isbn",
                "titulo",
                "autor",
                "editorial_id",
                "genero_id",
            ],
            [
                [
                    str(entidad.id),
                    entidad.isbn,
                    entidad.titulo,
                    entidad.autor,
                    str(entidad.editorial.id),
                    str(entidad.genero.id),
                ]
                for entidad in self.libros.leer_todos()
            ],
        )
        self._escribir(
            "precios.csv",
            ["id", "libro_id", "moneda_id", "valor"],
            [
                [
                    str(entidad.id),
                    str(entidad.libro.id),
                    str(entidad.moneda.id),
                    str(entidad.valor),
                ]
                for entidad in self.precios.leer_todos()
            ],
        )
        self._escribir(
            "stock.csv",
            ["libro_id", "cantidad"],
            [
                [
                    str(entidad.libro_id),
                    str(entidad.cantidad),
                ]
                for entidad in self.stocks.leer_todos()
            ],
        )
        self._escribir(
            "cotizaciones.csv",
            ["tipo_id", "fecha", "compra", "venta"],
            [
                [
                    str(entidad.tipo_id),
                    entidad.fecha.isoformat(),
                    str(entidad.compra),
                    str(entidad.venta),
                ]
                for entidad in self.cotizaciones.leer_todos()
            ],
        )
