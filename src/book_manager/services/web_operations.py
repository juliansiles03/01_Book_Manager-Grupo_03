import csv
import os
import subprocess
import sys

from decimal import Decimal
from pathlib import Path

from book_manager.repositories.audit_repository import (
    RepositorioAuditoria,
)
from book_manager.repositories.database_repositories import (
    AlmacenDB,
)
from book_manager.reportes.reporte_precios import (
    generar_reporte_precios,
)
from book_manager.services.audit import auditar


class ServicioOperacionesWeb:
    """Coordina la extracción y el reporte desde la consola."""

    def __init__(self, almacen: AlmacenDB) -> None:
        self._almacen = almacen

    @property
    def _carpeta_reportes(self) -> Path:
        """Ubica los reportes dentro del proyecto."""
        return (
            Path(__file__).resolve().parents[1]
            / "reportes"
        )

    @auditar
    def ejecutar_scraping(
        self,
        umbral_porcentual: Decimal,
    ) -> tuple[Path, Path, int]:
        """Ejecuta el scraper y genera alertas con el umbral dado."""
        if (
            not umbral_porcentual.is_finite()
            or umbral_porcentual < 0
        ):
            raise ValueError(
                "El porcentaje debe ser mayor o igual a cero."
            )

        ruta_src = Path(
            __file__
        ).resolve().parents[2]

        resultado = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "book_manager.scraper.runner",
            ],
            cwd=ruta_src,
            env={
                **os.environ,
                "PYTHONPATH": str(ruta_src),
            },
            input=f"{umbral_porcentual}\n",
            capture_output=True,
            text=True,
            timeout=600,
        )

        if resultado.returncode != 0:
            raise RuntimeError(
                "Falló la extracción de Cúspide: "
                + resultado.stderr[-1500:]
            )

        ruta_extraccion = (
            self._carpeta_reportes
            / "extraccion_cuspide.csv"
        )
        ruta_alertas = (
            self._carpeta_reportes
            / "alertas_precios.csv"
        )

        if (
            not ruta_extraccion.is_file()
            or not ruta_alertas.is_file()
        ):
            raise RuntimeError(
                "Faltan los archivos generados "
                "por el scraper."
            )

        with ruta_extraccion.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as archivo:
            cantidad = sum(
                1 for _ in csv.DictReader(archivo)
            )

        return (
            ruta_extraccion,
            ruta_alertas,
            cantidad,
        )

    @auditar
    def generar_reporte(self) -> tuple[Path, int]:
        """Genera el Excel desde la última extracción."""
        ruta_extraccion = (
            self._carpeta_reportes
            / "extraccion_cuspide.csv"
        )
        ruta_excel = (
            self._carpeta_reportes
            / "comparacion_precios.xlsx"
        )

        cantidad = generar_reporte_precios(
            ruta_extraccion,
            ruta_excel,
        )

        return ruta_excel, cantidad


class ServicioAuditoria:
    """Permite consultar el historial de operaciones."""

    def __init__(self, almacen: AlmacenDB) -> None:
        self._almacen = almacen
        self._repositorio = RepositorioAuditoria(
            almacen._conexion
        )

    @auditar
    def leer_todos(self) -> list[dict[str, object]]:
        """Devuelve el historial del sistema."""
        return self._repositorio.leer_todos()
