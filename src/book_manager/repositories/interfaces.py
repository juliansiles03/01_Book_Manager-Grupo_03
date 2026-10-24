import abc
import datetime
from typing import Generic, List, Optional, TypeVar

from book_manager.entities.entities import (
    CotizacionDolar, EntidadBase, Stock,
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
