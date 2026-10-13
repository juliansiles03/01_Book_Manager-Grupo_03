"""Repositorios SQLAlchemy compatibles con los servicios del Sprint 1."""

from datetime import date
from decimal import Decimal
from typing import Generic, TypeVar

from sqlalchemy import select

from book_manager.database.connection import ConexionDB
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
from book_manager.models.models import (
    CotizacionDolarModelo,
    EditorialModelo,
    GeneroModelo,
    LibroModelo,
    MonedaModelo,
    PrecioModelo,
    StockModelo,
    TipoCotizacionModelo,
)


T = TypeVar("T", bound=EntidadBase)


def _valores(entidad: object) -> dict[str, object]:
    """Obtiene las columnas SQL de una entidad."""
    if isinstance(entidad, Moneda):
        return {
            "id": entidad.id,
            "nombre": entidad.nombre,
            "codigo": entidad.codigo,
        }

    if isinstance(entidad, Libro):
        return {
            "id": entidad.id,
            "isbn": entidad.isbn,
            "titulo": entidad.titulo,
            "autor": entidad.autor,
            "editorial_id": entidad.editorial.id,
            "genero_id": entidad.genero.id,
        }

    if isinstance(entidad, Precio):
        return {
            "id": entidad.id,
            "libro_id": entidad.libro.id,
            "moneda_id": entidad.moneda.id,
            "valor": Decimal(str(entidad.valor)),
        }

    if isinstance(entidad, Stock):
        return {
            "libro_id": entidad.libro_id,
            "cantidad": entidad.cantidad,
        }

    if isinstance(entidad, CotizacionDolar):
        return {
            "tipo_id": entidad.tipo_id,
            "fecha": entidad.fecha,
            "compra": Decimal(str(entidad.compra)),
            "venta": Decimal(str(entidad.venta)),
        }

    if isinstance(entidad, (Genero, Editorial, TipoCotizacion)):
        return {
            "id": entidad.id,
            "nombre": entidad.nombre,
        }

    raise TypeError("Entidad no admitida por el repositorio.")


def _entidad(modelo: object) -> object:
    """Reconstruye una entidad mientras la sesión sigue abierta."""
    if isinstance(modelo, GeneroModelo):
        return Genero(modelo.id, modelo.nombre)

    if isinstance(modelo, EditorialModelo):
        return Editorial(modelo.id, modelo.nombre)

    if isinstance(modelo, MonedaModelo):
        return Moneda(modelo.id, modelo.nombre, modelo.codigo)

    if isinstance(modelo, TipoCotizacionModelo):
        return TipoCotizacion(modelo.id, modelo.nombre)

    if isinstance(modelo, LibroModelo):
        return Libro(
            modelo.id,
            modelo.isbn,
            modelo.titulo,
            modelo.autor,
            _entidad(modelo.editorial),
            _entidad(modelo.genero),
        )

    if isinstance(modelo, PrecioModelo):
        return Precio(
            modelo.id,
            _entidad(modelo.libro),
            _entidad(modelo.moneda),
            float(modelo.valor),
        )

    if isinstance(modelo, StockModelo):
        return Stock(
            _entidad(modelo.libro),
            modelo.cantidad,
        )

    if isinstance(modelo, CotizacionDolarModelo):
        return CotizacionDolar(
            _entidad(modelo.tipo),
            modelo.fecha,
            float(modelo.compra),
            float(modelo.venta),
        )

    raise TypeError("Modelo SQL desconocido.")


class RepositorioDB(Generic[T]):
    """CRUD persistente de entidades con un ID simple."""

    def __init__(self, conexion: ConexionDB, modelo: type) -> None:
        self._conexion = conexion
        self._modelo = modelo

    def crear(self, entidad: T) -> T:
        with self._conexion.transaccion() as sesion:
            if sesion.get(self._modelo, entidad.id) is not None:
                raise ValueError(
                    f"Ya existe una entidad con el ID {entidad.id}."
                )
            sesion.add(self._modelo(**_valores(entidad)))
        return entidad

    def leer_por_id(self, id: int) -> T | None:
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(self._modelo, id)
            return (
                _entidad(registro)
                if registro is not None
                else None
            )

    def leer_todos(self) -> list[T]:
        with self._conexion.transaccion() as sesion:
            registros = sesion.scalars(
                select(self._modelo).order_by(self._modelo.id)
            ).all()
            return [
                _entidad(registro)
                for registro in registros
            ]

    def actualizar(self, entidad: T) -> T:
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(self._modelo, entidad.id)

            if registro is None:
                raise ValueError(
                    f"No existe una entidad con el ID {entidad.id}."
                )

            for columna, valor in _valores(entidad).items():
                if columna != "id":
                    setattr(registro, columna, valor)

        return entidad

    def eliminar(self, id: int) -> bool:
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(self._modelo, id)

            if registro is None:
                return False

            sesion.delete(registro)

        return True


class RepositorioStockDB:
    """CRUD persistente de stock por libro."""

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion

    def crear(self, stock: Stock) -> Stock:
        with self._conexion.transaccion() as sesion:
            if sesion.get(StockModelo, stock.libro_id) is not None:
                raise ValueError("El libro ya posee un stock.")
            sesion.add(StockModelo(**_valores(stock)))
        return stock

    def leer_por_libro(self, libro_id: int) -> Stock | None:
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(StockModelo, libro_id)
            return (
                _entidad(registro)
                if registro is not None
                else None
            )

    def leer_todos(self) -> list[Stock]:
        with self._conexion.transaccion() as sesion:
            registros = sesion.scalars(
                select(StockModelo).order_by(StockModelo.libro_id)
            ).all()
            return [
                _entidad(registro)
                for registro in registros
            ]

    def actualizar(self, stock: Stock) -> Stock:
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(StockModelo, stock.libro_id)

            if registro is None:
                raise ValueError("No existe stock para ese libro.")

            registro.cantidad = stock.cantidad

        return stock

    def eliminar(self, libro_id: int) -> bool:
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(StockModelo, libro_id)

            if registro is None:
                return False

            sesion.delete(registro)

        return True


class RepositorioCotizacionDB:
    """CRUD persistente de cotizaciones por tipo y fecha."""

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion

    def crear(
        self,
        cotizacion: CotizacionDolar,
    ) -> CotizacionDolar:
        clave = (cotizacion.tipo_id, cotizacion.fecha)

        with self._conexion.transaccion() as sesion:
            if sesion.get(CotizacionDolarModelo, clave) is not None:
                raise ValueError(
                    "Ya existe cotización para ese tipo y fecha."
                )
            sesion.add(
                CotizacionDolarModelo(**_valores(cotizacion))
            )

        return cotizacion

    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: date,
    ) -> CotizacionDolar | None:
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(
                CotizacionDolarModelo,
                (tipo_id, fecha),
            )
            return (
                _entidad(registro)
                if registro is not None
                else None
            )

    def leer_todos(self) -> list[CotizacionDolar]:
        with self._conexion.transaccion() as sesion:
            registros = sesion.scalars(
                select(CotizacionDolarModelo).order_by(
                    CotizacionDolarModelo.tipo_id,
                    CotizacionDolarModelo.fecha,
                )
            ).all()
            return [
                _entidad(registro)
                for registro in registros
            ]

    def leer_historico_por_tipo(
        self,
        tipo_id: int,
    ) -> list[CotizacionDolar]:
        with self._conexion.transaccion() as sesion:
            registros = sesion.scalars(
                select(CotizacionDolarModelo)
                .where(
                    CotizacionDolarModelo.tipo_id == tipo_id
                )
                .order_by(CotizacionDolarModelo.fecha)
            ).all()
            return [
                _entidad(registro)
                for registro in registros
            ]

    def actualizar(
        self,
        cotizacion: CotizacionDolar,
    ) -> CotizacionDolar:
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(
                CotizacionDolarModelo,
                (cotizacion.tipo_id, cotizacion.fecha),
            )

            if registro is None:
                raise ValueError("No existe esa cotización.")

            registro.compra = Decimal(
                str(cotizacion.compra)
            )
            registro.venta = Decimal(
                str(cotizacion.venta)
            )

        return cotizacion

    def eliminar(
        self,
        tipo_id: int,
        fecha: date,
    ) -> bool:
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(
                CotizacionDolarModelo,
                (tipo_id, fecha),
            )

            if registro is None:
                return False

            sesion.delete(registro)

        return True


class AlmacenDB:
    """Agrupa los ocho repositorios de PostgreSQL."""

    def __init__(
        self,
        conexion: ConexionDB | None = None,
    ) -> None:
        self._conexion = conexion or ConexionDB()
        self._conexion_propia = conexion is None

        self.generos = RepositorioDB[Genero](
            self._conexion, GeneroModelo
        )
        self.editoriales = RepositorioDB[Editorial](
            self._conexion, EditorialModelo
        )
        self.monedas = RepositorioDB[Moneda](
            self._conexion, MonedaModelo
        )
        self.tipos = RepositorioDB[TipoCotizacion](
            self._conexion, TipoCotizacionModelo
        )
        self.libros = RepositorioDB[Libro](
            self._conexion, LibroModelo
        )
        self.precios = RepositorioDB[Precio](
            self._conexion, PrecioModelo
        )
        self.stocks = RepositorioStockDB(self._conexion)
        self.cotizaciones = RepositorioCotizacionDB(
            self._conexion
        )

    def guardar(self) -> None:
        """Mantiene la API anterior; cada operación ya se confirmó."""

    def cerrar(self) -> None:
        """Libera las conexiones que abrió este almacén."""
        if self._conexion_propia:
            self._conexion.cerrar()
