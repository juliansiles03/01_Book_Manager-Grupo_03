import csv

from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as insertar_postgres
from sqlalchemy.dialects import postgresql

from book_manager.database.connection import ConexionDB
from book_manager.models.models import (
    Base,
    CotizacionDolarModelo,
    EditorialModelo,
    GeneroModelo,
    LibroModelo,
    MonedaModelo,
    PrecioModelo,
    StockModelo,
    TipoCotizacionModelo,
)


TABLAS_EN_ORDEN = (
    ("generos", GeneroModelo),
    ("editoriales", EditorialModelo),
    ("monedas", MonedaModelo),
    ("tipos_cotizacion", TipoCotizacionModelo),
    ("libros", LibroModelo),
    ("precios", PrecioModelo),
    ("stock", StockModelo),
    ("cotizaciones", CotizacionDolarModelo),
)

COLUMNAS_ENTERAS = {
    "id", "editorial_id", "genero_id", "libro_id",
    "moneda_id", "tipo_id", "cantidad",
}
COLUMNAS_DECIMALES = {"valor", "compra", "venta"}


def convertir_valor(columna: str, valor: str | None):
    """Convierte los campos del CSV al tipo requerido por la tabla."""
    if valor is None or valor == "":
        raise ValueError(f"Falta un valor obligatorio: {columna}")

    if columna in COLUMNAS_ENTERAS:
        return int(valor)
    if columna in COLUMNAS_DECIMALES:
        return Decimal(valor)
    if columna == "fecha":
        return date.fromisoformat(valor)

    return valor


def migrar_datos(
    carpeta_csvs: str,
    carpeta_sqls: str,
) -> dict[str, int]:
    """Carga los CSV en PostgreSQL y genera sus INSERT en archivos SQL."""
    origen = Path(carpeta_csvs)
    destino = Path(carpeta_sqls)

    if not origen.is_dir():
        raise FileNotFoundError(f"No existe la carpeta de CSV: {origen}")

    conexion = ConexionDB()
    cantidades: dict[str, int] = {}
    archivos_sql: dict[str, str] = {}

    try:
        if conexion.motor.dialect.name != "postgresql":
            raise ValueError("La migración requiere PostgreSQL de Supabase.")

        Base.metadata.create_all(conexion.motor)

        with conexion.transaccion() as sesion:
            for numero, (nombre, modelo) in enumerate(
                TABLAS_EN_ORDEN, start=1
            ):
                ruta_csv = origen / f"{nombre}.csv"

                if not ruta_csv.is_file():
                    raise FileNotFoundError(
                        f"Falta el archivo {ruta_csv}"
                    )

                tabla = modelo.__table__
                columnas_esperadas = set(tabla.columns.keys())
                lineas_sql = ["BEGIN;"]
                cantidad = 0

                with ruta_csv.open(
                    "r", encoding="utf-8-sig", newline=""
                ) as archivo:
                    lector = csv.DictReader(archivo)

                    if (
                        lector.fieldnames is None
                        or set(lector.fieldnames) != columnas_esperadas
                    ):
                        raise ValueError(
                            f"Columnas inesperadas en {ruta_csv.name}: "
                            f"{lector.fieldnames}"
                        )

                    for fila in lector:
                        valores = {
                            columna: convertir_valor(
                                columna, fila[columna]
                            )
                            for columna in tabla.columns.keys()
                        }

                        sentencia = (
                            insertar_postgres(tabla)
                            .values(**valores)
                            .on_conflict_do_nothing()
                        )

                        sesion.execute(sentencia)

                        sql_insert = str(
                            sentencia.compile(
                                dialect=postgresql.dialect(),
                                compile_kwargs={
                                    "literal_binds": True
                                },
                            )
                        )
                        lineas_sql.append(sql_insert + ";")
                        cantidad += 1

                # Los CSV incluyen identificadores explícitos. Se ajusta
                # la secuencia para permitir futuras altas sin colisiones.
                if "id" in columnas_esperadas and cantidad:
                    sql_secuencia = (
                        "SELECT setval("
                        f"pg_get_serial_sequence('{nombre}', 'id'), "
                        f"(SELECT MAX(id) FROM {nombre}), true)"
                    )
                    sesion.execute(text(sql_secuencia))
                    lineas_sql.append(sql_secuencia + ";")

                lineas_sql.append("COMMIT;")
                cantidades[nombre] = cantidad
                archivos_sql[f"{numero:02d}_{nombre}.sql"] = (
                    "\n".join(lineas_sql) + "\n"
                )

        destino.mkdir(parents=True, exist_ok=True)

        for nombre_archivo, contenido in archivos_sql.items():
            (destino / nombre_archivo).write_text(
                contenido, encoding="utf-8"
            )

        return cantidades
    finally:
        conexion.cerrar()
