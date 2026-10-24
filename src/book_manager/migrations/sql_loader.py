from pathlib import Path

from sqlalchemy import text

from book_manager.database.connection import ConexionDB


ARCHIVOS_SQL: tuple[str, ...] = (
    "01_generos.sql",
    "02_editoriales.sql",
    "03_monedas.sql",
    "04_tipos_cotizacion.sql",
    "05_libros.sql",
    "06_precios.sql",
    "07_stock.sql",
    "08_cotizaciones.sql",
)


def cargar_datos_desde_sql(
    carpeta_sqls: str | Path,
) -> dict[str, dict[str, int]]:
    """Ejecuta, en orden, los SQL de inserción generados en el TP2."""
    carpeta = Path(carpeta_sqls)

    if not carpeta.is_dir():
        raise FileNotFoundError(
            f"No existe la carpeta de SQL: {carpeta}"
        )

    instrucciones: dict[str, list[str]] = {}

    for nombre in ARCHIVOS_SQL:
        ruta = carpeta / nombre

        if not ruta.is_file():
            raise FileNotFoundError(
                f"Falta el archivo SQL del TP2: {ruta}"
            )

        lineas = [
            linea.strip()
            for linea in ruta.read_text(
                encoding="utf-8"
            ).splitlines()
            if linea.strip()
        ]

        if (
            len(lineas) < 3
            or lineas[0] != "BEGIN;"
            or lineas[-1] != "COMMIT;"
        ):
            raise ValueError(
                f"El archivo {nombre} no tiene el formato "
                "generado en el TP2."
            )

        sentencias = lineas[1:-1]

        for sentencia in sentencias:
            if not sentencia.endswith(";"):
                raise ValueError(
                    f"Falta el cierre de una sentencia en {nombre}."
                )

            if not (
                sentencia.startswith("INSERT INTO ")
                or sentencia.startswith("SELECT setval(")
            ):
                raise ValueError(
                    f"Sentencia inesperada en {nombre}."
                )

        instrucciones[nombre] = sentencias

    conexion = ConexionDB()
    resultado: dict[str, dict[str, int]] = {}

    try:
        if conexion.motor.dialect.name != "postgresql":
            raise ValueError(
                "Los SQL del TP2 requieren PostgreSQL de Supabase."
            )

        with conexion.transaccion() as sesion:
            for nombre in ARCHIVOS_SQL:
                procesadas = 0
                insertadas = 0

                for sentencia in instrucciones[nombre]:
                    ejecucion = sesion.execute(
                        text(sentencia[:-1])
                    )

                    if sentencia.startswith("INSERT INTO "):
                        procesadas += 1
                        insertadas += max(
                            ejecucion.rowcount, 0
                        )

                resultado[nombre] = {
                    "procesadas": procesadas,
                    "insertadas": insertadas,
                }

        return resultado
    finally:
        conexion.cerrar()
