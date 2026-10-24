from functools import wraps
from typing import Any, Callable, TypeVar

from book_manager.repositories.audit_repository import (
    RepositorioAuditoria,
)


F = TypeVar("F", bound=Callable[..., Any])


def auditar(funcion: F) -> F:
    """Registra el resultado de una operación de un servicio."""
    @wraps(funcion)
    def envoltura(
        self: object,
        *args: object,
        **kwargs: object,
    ) -> Any:
        nombre_accion = (
            f"{type(self).__name__}.{funcion.__name__}"
        )

        if args:
            primer_argumento = args[0]
        elif kwargs:
            primer_argumento = next(iter(kwargs.values()))
        else:
            primer_argumento = None

        referencia = getattr(
            primer_argumento,
            "id",
            getattr(
                primer_argumento,
                "libro_id",
                getattr(
                    primer_argumento,
                    "tipo_id",
                    primer_argumento
                    if isinstance(
                        primer_argumento,
                        (int, str),
                    )
                    else "sin identificador",
                ),
            ),
        )

        repositorio = RepositorioAuditoria(
            self._almacen._conexion
        )

        try:
            resultado = funcion(
                self,
                *args,
                **kwargs,
            )
        except Exception as error:
            detalles = (
                f"Referencia: {referencia}; "
                f"resultado: error "
                f"({type(error).__name__})."
            )

            try:
                repositorio.crear(
                    nombre_accion,
                    detalles,
                )
            except Exception:
                pass

            raise

        estado = (
            "sin registro"
            if resultado is False or resultado is None
            else "correcto"
        )

        repositorio.crear(
            nombre_accion,
            (
                f"Referencia: {referencia}; "
                f"resultado: {estado}."
            ),
        )

        return resultado

    return envoltura
