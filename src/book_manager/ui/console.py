from datetime import date
from typing import Callable, Iterable, TypeVar

from book_manager.entities.entities import (
    CotizacionDolar,
    Editorial,
    EntidadBase,
    EntidadConNombre,
    Genero,
    Libro,
    Moneda,
    Precio,
    Stock,
    TipoCotizacion,
)
from book_manager.repositories.repositories import AlmacenCSV
from book_manager.services.services import (
    ServicioBase,
    ServicioCotizacionDolar,
    ServicioEditorial,
    ServicioGenero,
    ServicioLibro,
    ServicioMoneda,
    ServicioPrecio,
    ServicioStock,
    ServicioTipoCotizacion,
)


T = TypeVar("T", bound=EntidadBase)


class Consola:
    """Presenta menús CRUD para las ocho entidades de la librería."""

    def __init__(self, almacen: AlmacenCSV) -> None:
        self.generos: ServicioGenero = ServicioGenero(almacen)
        self.editoriales: ServicioEditorial = ServicioEditorial(almacen)
        self.monedas: ServicioMoneda = ServicioMoneda(almacen)
        self.tipos: ServicioTipoCotizacion = (
            ServicioTipoCotizacion(almacen)
        )
        self.libros: ServicioLibro = ServicioLibro(almacen)
        self.precios: ServicioPrecio = ServicioPrecio(almacen)
        self.stocks: ServicioStock = ServicioStock(almacen)
        self.cotizaciones: ServicioCotizacionDolar = (
            ServicioCotizacionDolar(almacen)
        )

    def ejecutar(self) -> None:
        """Abre el menú principal hasta que el usuario decida salir."""
        try:
            while True:
                print("\n=== BOOK MANAGER ===")
                print("1. Libros         2. Géneros")
                print("3. Editoriales    4. Monedas")
                print("5. Tipos dólar    6. Precios")
                print("7. Stock          8. Cotizaciones dólar")
                print("0. Salir")

                opcion: str = input("Opción: ").strip()

                if opcion == "1":
                    self._menu_catalogo(
                        "Libros",
                        self.libros,
                        self._armar_libro,
                    )
                elif opcion == "2":
                    self._menu_catalogo(
                        "Géneros",
                        self.generos,
                        self._armar_genero,
                    )
                elif opcion == "3":
                    self._menu_catalogo(
                        "Editoriales",
                        self.editoriales,
                        self._armar_editorial,
                    )
                elif opcion == "4":
                    self._menu_catalogo(
                        "Monedas",
                        self.monedas,
                        self._armar_moneda,
                    )
                elif opcion == "5":
                    self._menu_catalogo(
                        "Tipos de cotización",
                        self.tipos,
                        self._armar_tipo,
                    )
                elif opcion == "6":
                    self._menu_catalogo(
                        "Precios",
                        self.precios,
                        self._armar_precio,
                    )
                elif opcion == "7":
                    self._menu_crud(
                        "Stock",
                        self.stocks.leer_todos,
                        self._crear_stock,
                        self._modificar_stock,
                        self._eliminar_stock,
                    )
                elif opcion == "8":
                    self._menu_crud(
                        "Cotizaciones dólar",
                        self.cotizaciones.leer_todos,
                        self._crear_cotizacion,
                        self._modificar_cotizacion,
                        self._eliminar_cotizacion,
                    )
                elif opcion == "0":
                    print("Sesión finalizada.")
                    return
                else:
                    print("Opción inválida.")

        except EOFError:
            print("\nSesión finalizada.")

    def _menu_crud(
        self,
        titulo: str,
        leer_todos: Callable[[], Iterable[object]],
        crear: Callable[[], None],
        modificar: Callable[[], None],
        eliminar: Callable[[], None],
    ) -> None:
        """Muestra las mismas opciones CRUD para todos los modelos."""
        acciones: dict[str, Callable[[], None]] = {
            "1": lambda: self._listar(leer_todos()),
            "2": crear,
            "3": modificar,
            "4": eliminar,
        }

        while True:
            print(f"\n=== {titulo.upper()} ===")
            print("1. Listar    2. Crear    3. Modificar")
            print("4. Eliminar  0. Volver")

            opcion: str = input("Opción: ").strip()

            if opcion == "0":
                return

            if opcion not in acciones:
                print("Opción inválida.")
                continue

            try:
                acciones[opcion]()
            except ValueError as error:
                print(f"Error: {error}")

    def _menu_catalogo(
        self,
        titulo: str,
        servicio: ServicioBase[T],
        construir: Callable[[int], T],
    ) -> None:
        """Vincula un menú CRUD con un servicio identificado por ID."""
        self._menu_crud(
            titulo,
            servicio.leer_todos,
            lambda: self._crear_por_id(servicio, construir),
            lambda: self._modificar_por_id(servicio, construir),
            lambda: self._eliminar_por_id(servicio),
        )

    def _listar(self, registros: Iterable[object]) -> None:
        """Presenta un listado descriptivo de las entidades."""
        elementos: list[object] = list(registros)

        if not elementos:
            print("No hay registros.")
            return

        for elemento in elementos:
            print(self._describir(elemento))

    def _describir(self, entidad: object) -> str:
        """Devuelve una línea legible para un registro."""
        if isinstance(entidad, Libro):
            return (
                f"{entidad.id} | {entidad.titulo} | "
                f"ISBN {entidad.isbn} | {entidad.autor} | "
                f"{entidad.editorial.nombre} | "
                f"{entidad.genero.nombre}"
            )

        if isinstance(entidad, Precio):
            return (
                f"{entidad.id} | {entidad.libro.titulo} | "
                f"{entidad.valor:.2f} {entidad.moneda.codigo}"
            )

        if isinstance(entidad, Stock):
            return (
                f"Libro {entidad.libro_id} "
                f"({entidad.libro.titulo}) | "
                f"Cantidad: {entidad.cantidad}"
            )

        if isinstance(entidad, CotizacionDolar):
            return (
                f"{entidad.tipo.nombre} | "
                f"{entidad.fecha.isoformat()} | "
                f"Compra: {entidad.compra:.2f} | "
                f"Venta: {entidad.venta:.2f}"
            )

        if isinstance(entidad, Moneda):
            return (
                f"{entidad.id} | {entidad.nombre} "
                f"({entidad.codigo})"
            )

        if isinstance(entidad, EntidadConNombre):
            return f"{entidad.id} | {entidad.nombre}"

        raise ValueError("Entidad desconocida.")

    def _crear_por_id(
        self,
        servicio: ServicioBase[T],
        construir: Callable[[int], T],
    ) -> None:
        """Pide los datos y crea una entidad identificada por ID."""
        id: int = int(input("Nuevo ID: "))
        entidad: T = construir(id)
        servicio.crear(entidad)
        print("Registro creado.")

    def _modificar_por_id(
        self,
        servicio: ServicioBase[T],
        construir: Callable[[int], T],
    ) -> None:
        """Pide los datos y modifica una entidad existente."""
        id: int = int(input("ID a modificar: "))

        if servicio.leer_por_id(id) is None:
            print("No existe ese registro.")
            return

        entidad: T = construir(id)
        servicio.actualizar(entidad)
        print("Registro modificado.")

    def _eliminar_por_id(
        self,
        servicio: ServicioBase[T],
    ) -> None:
        """Elimina un registro por ID cuando el servicio lo permite."""
        id: int = int(input("ID a eliminar: "))

        if servicio.eliminar(id):
            print("Registro eliminado.")
        else:
            print("No existe ese registro.")

    def _referencia(
        self,
        servicio: ServicioBase[T],
        nombre: str,
    ) -> T:
        """Obtiene un objeto relacionado previamente registrado."""
        id: int = int(input(f"ID de {nombre}: "))
        entidad: T | None = servicio.leer_por_id(id)

        if entidad is None:
            raise ValueError(
                f"No existe {nombre} con ID {id}."
            )

        return entidad

    def _armar_genero(self, id: int) -> Genero:
        """Pide los datos de un género."""
        return Genero(
            id,
            input("Nombre: ").strip(),
        )

    def _armar_editorial(self, id: int) -> Editorial:
        """Pide los datos de una editorial."""
        return Editorial(
            id,
            input("Nombre: ").strip(),
        )

    def _armar_moneda(self, id: int) -> Moneda:
        """Pide los datos de una moneda."""
        nombre: str = input("Nombre: ").strip()
        codigo: str = input(
            "Código (ARS, USD, etc.): "
        ).strip().upper()

        return Moneda(id, nombre, codigo)

    def _armar_tipo(self, id: int) -> TipoCotizacion:
        """Pide los datos de un tipo de cotización."""
        return TipoCotizacion(
            id,
            input("Nombre: ").strip(),
        )

    def _armar_libro(self, id: int) -> Libro:
        """Pide datos de un libro y sus objetos relacionados."""
        isbn: str = input("ISBN: ").strip()
        titulo: str = input("Título: ").strip()
        autor: str = input("Autor: ").strip()

        editorial: Editorial = self._referencia(
            self.editoriales,
            "editorial",
        )
        genero: Genero = self._referencia(
            self.generos,
            "género",
        )

        return Libro(
            id,
            isbn,
            titulo,
            autor,
            editorial,
            genero,
        )

    def _armar_precio(self, id: int) -> Precio:
        """Pide el libro, la moneda y el importe del precio."""
        libro: Libro = self._referencia(
            self.libros,
            "libro",
        )
        moneda: Moneda = self._referencia(
            self.monedas,
            "moneda",
        )
        valor: float = float(input("Valor: "))

        return Precio(id, libro, moneda, valor)

    def _armar_stock(self, libro_id: int) -> Stock:
        """Pide una cantidad para un libro existente."""
        libro: Libro | None = self.libros.leer_por_id(
            libro_id
        )

        if libro is None:
            raise ValueError(
                f"No existe el libro {libro_id}."
            )

        cantidad: int = int(input("Cantidad: "))
        return Stock(libro, cantidad)

    def _crear_stock(self) -> None:
        """Da de alta el stock de un libro."""
        libro_id: int = int(input("ID del libro: "))
        self.stocks.crear(
            self._armar_stock(libro_id)
        )
        print("Stock creado.")

    def _modificar_stock(self) -> None:
        """Modifica la cantidad del stock de un libro."""
        libro_id: int = int(input("ID del libro: "))

        if self.stocks.leer_por_libro(libro_id) is None:
            print("No existe stock para ese libro.")
            return

        self.stocks.actualizar(
            self._armar_stock(libro_id)
        )
        print("Stock modificado.")

    def _eliminar_stock(self) -> None:
        """Elimina el registro de stock de un libro."""
        libro_id: int = int(input("ID del libro: "))

        if self.stocks.eliminar(libro_id):
            print("Stock eliminado.")
        else:
            print("No existe stock para ese libro.")

    def _clave_cotizacion(self) -> tuple[int, date]:
        """Pide el tipo y la fecha que identifican una cotización."""
        tipo_id: int = int(
            input("ID del tipo de cotización: ")
        )
        fecha: date = date.fromisoformat(
            input("Fecha (AAAA-MM-DD): ").strip()
        )

        return tipo_id, fecha

    def _armar_cotizacion(
        self,
        tipo_id: int,
        fecha: date,
    ) -> CotizacionDolar:
        """Pide los importes de una cotización."""
        tipo: TipoCotizacion | None = (
            self.tipos.leer_por_id(tipo_id)
        )

        if tipo is None:
            raise ValueError(
                f"No existe el tipo {tipo_id}."
            )

        compra: float = float(
            input("Cotización de compra: ")
        )
        venta: float = float(
            input("Cotización de venta: ")
        )

        return CotizacionDolar(
            tipo,
            fecha,
            compra,
            venta,
        )

    def _crear_cotizacion(self) -> None:
        """Da de alta una cotización por tipo y fecha."""
        tipo_id, fecha = self._clave_cotizacion()

        self.cotizaciones.crear(
            self._armar_cotizacion(tipo_id, fecha)
        )
        print("Cotización creada.")

    def _modificar_cotizacion(self) -> None:
        """Modifica una cotización existente."""
        tipo_id, fecha = self._clave_cotizacion()

        existente = (
            self.cotizaciones.leer_por_tipo_y_fecha(
                tipo_id,
                fecha,
            )
        )

        if existente is None:
            print("No existe esa cotización.")
            return

        self.cotizaciones.actualizar(
            self._armar_cotizacion(tipo_id, fecha)
        )
        print("Cotización modificada.")

    def _eliminar_cotizacion(self) -> None:
        """Elimina una cotización por tipo y fecha."""
        tipo_id, fecha = self._clave_cotizacion()

        if self.cotizaciones.eliminar(tipo_id, fecha):
            print("Cotización eliminada.")
        else:
            print("No existe esa cotización.")
