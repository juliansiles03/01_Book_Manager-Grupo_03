from datetime import datetime, timezone

from sqlalchemy import select

from book_manager.database.connection import ConexionDB
from book_manager.models.models import AuditoriaModelo


class RepositorioAuditoria:
    """Administra los registros persistentes de auditoría."""

    def __init__(self, conexion: ConexionDB) -> None:
        self._conexion = conexion

    @staticmethod
    def _datos(
        registro: AuditoriaModelo,
    ) -> dict[str, object]:
        """Devuelve una representación independiente de la sesión."""
        return {
            "id": registro.id,
            "accion": registro.accion,
            "fecha": registro.fecha,
            "detalles": registro.detalles,
        }

    def crear(
        self,
        accion: str,
        detalles: str,
        fecha: datetime | None = None,
    ) -> dict[str, object]:
        """Registra una operación con fecha y detalles."""
        if not accion.strip() or not detalles.strip():
            raise ValueError(
                "Acción y detalles son obligatorios."
            )

        if len(accion) > 100:
            raise ValueError(
                "La acción no puede superar 100 caracteres."
            )

        registro = AuditoriaModelo(
            accion=accion,
            detalles=detalles,
            fecha=fecha or datetime.now(timezone.utc),
        )

        with self._conexion.transaccion() as sesion:
            sesion.add(registro)
            sesion.flush()
            datos = self._datos(registro)

        return datos

    def leer_por_id(
        self,
        identificador: int,
    ) -> dict[str, object] | None:
        """Consulta una operación por su identificador."""
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(
                AuditoriaModelo,
                identificador,
            )
            return (
                self._datos(registro)
                if registro is not None
                else None
            )

    def leer_todos(self) -> list[dict[str, object]]:
        """Consulta el historial, empezando por lo más reciente."""
        with self._conexion.transaccion() as sesion:
            registros = sesion.scalars(
                select(AuditoriaModelo).order_by(
                    AuditoriaModelo.fecha.desc(),
                    AuditoriaModelo.id.desc(),
                )
            ).all()
            return [
                self._datos(registro)
                for registro in registros
            ]

    def actualizar(
        self,
        identificador: int,
        accion: str,
        detalles: str,
    ) -> bool:
        """Modifica un registro de auditoría existente."""
        if not accion.strip() or not detalles.strip():
            raise ValueError(
                "Acción y detalles son obligatorios."
            )

        if len(accion) > 100:
            raise ValueError(
                "La acción no puede superar 100 caracteres."
            )

        with self._conexion.transaccion() as sesion:
            registro = sesion.get(
                AuditoriaModelo,
                identificador,
            )

            if registro is None:
                return False

            registro.accion = accion
            registro.detalles = detalles

        return True

    def eliminar(
        self,
        identificador: int,
    ) -> bool:
        """Elimina un registro por su identificador."""
        with self._conexion.transaccion() as sesion:
            registro = sesion.get(
                AuditoriaModelo,
                identificador,
            )

            if registro is None:
                return False

            sesion.delete(registro)

        return True
