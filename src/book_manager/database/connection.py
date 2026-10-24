import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class ConexionDB:
    """Configura la conexión y crea sesiones de base de datos."""

    def __init__(self, url: str | None = None) -> None:
        if url is None:
            ruta_env: Path = (
                Path(__file__).resolve().parents[3] / ".env"
            )
            load_dotenv(ruta_env, interpolate=False)
            url = os.getenv("DATABASE_URL")

        if not url:
            raise ValueError(
                "Falta DATABASE_URL en el archivo .env."
            )

        if url.startswith("postgresql://"):
            url = url.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1,
            )

        if url.startswith("postgresql+psycopg://"):
            self._motor: Engine = create_engine(
                url,
                pool_pre_ping=True,
                connect_args={"sslmode": "require"},
            )
        elif url.startswith("sqlite://"):
            self._motor = create_engine(url)
        else:
            raise ValueError(
                "DATABASE_URL debe ser una URI PostgreSQL."
            )

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

    def cerrar(self) -> None:
        """Libera las conexiones mantenidas por el motor."""
        self._motor.dispose()
