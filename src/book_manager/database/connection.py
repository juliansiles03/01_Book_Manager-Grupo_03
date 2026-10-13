import os

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class ConexionDB:
    """Configura la conexión y administra sesiones de base de datos."""

    def __init__(self, url: str | None = None) -> None:
        if url is None:
            url = os.getenv("DATABASE_URL")

        if not url:
            ruta_db: Path = (
                Path(__file__).resolve().parent.parent
                / "migrations"
                / "sql"
                / "book_manager.db"
            )
            ruta_db.parent.mkdir(parents=True, exist_ok=True)
            url = f"sqlite:///{ruta_db.as_posix()}"

        self._motor: Engine = create_engine(url, echo=False)
        self._fabrica_sesiones: sessionmaker[Session] = sessionmaker(
            bind=self._motor,
            expire_on_commit=False,
        )

    @property
    def motor(self) -> Engine:
        """Devuelve el motor de SQLAlchemy."""
        return self._motor

    def crear_sesion(self) -> Session:
        """Crea una sesión que debe cerrarse después de usarla."""
        return self._fabrica_sesiones()

    @contextmanager
    def transaccion(self) -> Iterator[Session]:
        """Confirma los cambios o los revierte si ocurre un error."""
        sesion: Session = self.crear_sesion()

        try:
            yield sesion
            sesion.commit()
        except Exception:
            sesion.rollback()
            raise
        finally:
            sesion.close()

    def cerrar(self) -> None:
        """Libera las conexiones mantenidas por el motor."""
        self._motor.dispose()
