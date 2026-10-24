import csv

from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from book_manager.database.connection import ConexionDB
from book_manager.models.models import (
    MonedaModelo,
    PrecioModelo,
)


COLUMNAS_ALERTAS: tuple[str, ...] = (
    "libro",
    "isbn",
    "precio_interno",
    "precio_web",
    "diferencia",
    "diferencia_porcentual",
    "fecha_extraccion",
    "url_producto",
)


def generar_alertas(
    ruta_extraccion: str | Path,
    ruta_alertas: str | Path,
    umbral_porcentual: Decimal,
) -> dict[str, int]:
    """Compara precios ARS y genera alertas desde el umbral elegido."""
    if (
        not umbral_porcentual.is_finite()
        or umbral_porcentual < 0
    ):
        raise ValueError(
            "La diferencia porcentual debe ser un número "
            "mayor o igual a cero."
        )

    origen = Path(ruta_extraccion)
    destino = Path(ruta_alertas)

    if not origen.is_file():
        raise FileNotFoundError(
            f"No existe la extracción: {origen}"
        )

    conexion = ConexionDB()

    try:
        with conexion.transaccion() as sesion:
            registros = sesion.execute(
                select(
                    PrecioModelo.libro_id,
                    PrecioModelo.valor,
                )
                .join(
                    MonedaModelo,
                    PrecioModelo.moneda_id
                    == MonedaModelo.id,
                )
                .where(
                    MonedaModelo.codigo == "ARS"
                )
            ).all()

        precios_internos: dict[int, Decimal] = {
            int(libro_id): Decimal(str(valor))
            for libro_id, valor in registros
        }
    finally:
        conexion.cerrar()

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    examinados = 0
    alertas = 0
    sin_precio_ars = 0

    with origen.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as archivo_origen, destino.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as archivo_destino:
        lector = csv.DictReader(archivo_origen)
        escritor = csv.DictWriter(
            archivo_destino,
            fieldnames=COLUMNAS_ALERTAS,
        )
        escritor.writeheader()

        for fila in lector:
            examinados += 1
            libro_id = int(fila["libro_id"])
            precio_interno = precios_internos.get(
                libro_id
            )

            if precio_interno is None or precio_interno <= 0:
                sin_precio_ars += 1
                continue

            precio_web = Decimal(
                fila["precio_web"]
            )
            diferencia = (
                precio_web - precio_interno
            )
            porcentaje = (
                abs(diferencia)
                / precio_interno
                * Decimal("100")
            )

            if (
                diferencia == 0
                or porcentaje < umbral_porcentual
            ):
                continue

            escritor.writerow(
                {
                    "libro": fila["titulo"],
                    "isbn": fila["isbn"],
                    "precio_interno": str(
                        precio_interno
                    ),
                    "precio_web": str(
                        precio_web
                    ),
                    "diferencia": str(
                        diferencia
                    ),
                    "diferencia_porcentual": str(
                        porcentaje.quantize(
                            Decimal("0.01")
                        )
                    ),
                    "fecha_extraccion": fila[
                        "fecha_extraccion"
                    ],
                    "url_producto": fila[
                        "url_producto"
                    ],
                }
            )
            alertas += 1

    return {
        "examinados": examinados,
        "alertas": alertas,
        "sin_precio_ars": sin_precio_ars,
    }
