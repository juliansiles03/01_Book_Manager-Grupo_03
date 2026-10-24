from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Base común de las tablas del sistema."""


class GeneroModelo(Base):
    """Género literario registrado en la base de datos."""

    __tablename__ = "generos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    libros: Mapped[list["LibroModelo"]] = relationship(
        back_populates="genero", passive_deletes="all"
    )


class EditorialModelo(Base):
    """Editorial registrada en la base de datos."""

    __tablename__ = "editoriales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    libros: Mapped[list["LibroModelo"]] = relationship(
        back_populates="editorial", passive_deletes="all"
    )


class MonedaModelo(Base):
    """Moneda utilizada para expresar los precios."""

    __tablename__ = "monedas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        unique=True,
    )

    precios: Mapped[list["PrecioModelo"]] = relationship(
        back_populates="moneda", passive_deletes="all"
    )


class TipoCotizacionModelo(Base):
    """Tipo de cotización del dólar."""

    __tablename__ = "tipos_cotizacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    cotizaciones: Mapped[list["CotizacionDolarModelo"]] = relationship(
        back_populates="tipo", passive_deletes="all"
    )


class LibroModelo(Base):
    """Libro vinculado con una editorial y un género."""

    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    isbn: Mapped[str] = mapped_column(
        String(13),
        nullable=False,
        unique=True,
    )
    titulo: Mapped[str] = mapped_column(String(250), nullable=False)
    autor: Mapped[str] = mapped_column(String(200), nullable=False)

    editorial_id: Mapped[int] = mapped_column(
        ForeignKey("editoriales.id"),
        nullable=False,
    )
    genero_id: Mapped[int] = mapped_column(
        ForeignKey("generos.id"),
        nullable=False,
    )

    editorial: Mapped[EditorialModelo] = relationship(
        back_populates="libros"
    )
    genero: Mapped[GeneroModelo] = relationship(
        back_populates="libros"
    )
    precios: Mapped[list["PrecioModelo"]] = relationship(
        back_populates="libro", passive_deletes="all"
    )
    stock: Mapped[Optional["StockModelo"]] = relationship(
        back_populates="libro", uselist=False,
        passive_deletes="all",
    )


class PrecioModelo(Base):
    """Precio de un libro expresado en una moneda."""

    __tablename__ = "precios"
    __table_args__ = (
        UniqueConstraint(
            "libro_id",
            "moneda_id",
            name="uq_precio_libro_moneda",
        ),
        CheckConstraint(
            "valor >= 0",
            name="ck_precio_valor",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    libro_id: Mapped[int] = mapped_column(
        ForeignKey("libros.id"),
        nullable=False,
    )
    moneda_id: Mapped[int] = mapped_column(
        ForeignKey("monedas.id"),
        nullable=False,
    )
    valor: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    libro: Mapped[LibroModelo] = relationship(
        back_populates="precios"
    )
    moneda: Mapped[MonedaModelo] = relationship(
        back_populates="precios"
    )


class StockModelo(Base):
    """Existencias identificadas por el libro."""

    __tablename__ = "stock"
    __table_args__ = (
        CheckConstraint(
            "cantidad >= 0",
            name="ck_stock_cantidad",
        ),
    )

    libro_id: Mapped[int] = mapped_column(
        ForeignKey("libros.id"),
        primary_key=True,
    )
    cantidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    libro: Mapped[LibroModelo] = relationship(
        back_populates="stock"
    )


class CotizacionDolarModelo(Base):
    """Cotización identificada por tipo y fecha."""

    __tablename__ = "cotizaciones"
    __table_args__ = (
        CheckConstraint(
            "compra >= 0",
            name="ck_cotizacion_compra",
        ),
        CheckConstraint(
            "venta >= 0",
            name="ck_cotizacion_venta",
        ),
    )

    tipo_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_cotizacion.id"),
        primary_key=True,
    )
    fecha: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
    )
    compra: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    venta: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    tipo: Mapped[TipoCotizacionModelo] = relationship(
        back_populates="cotizaciones"
    )
