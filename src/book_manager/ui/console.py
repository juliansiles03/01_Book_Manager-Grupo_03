import csv
import subprocess
from decimal import Decimal, InvalidOperation
from datetime import date
from pathlib import Path

import requests
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


from book_manager.services.web_operations import (
    ServicioAuditoria,
    ServicioOperacionesWeb,
)


T = TypeVar("T", bound=EntidadBase)


class Consola:
    """Presenta menús CRUD para las ocho entidades de la librería."""

    def __init__(
        self,
        generos: ServicioGenero,
        editoriales: ServicioEditorial,
        monedas: ServicioMoneda,
        tipos: ServicioTipoCotizacion,
        libros: ServicioLibro,
        precios: ServicioPrecio,
        stocks: ServicioStock,
        cotizaciones: ServicioCotizacionDolar,
        operaciones_web: ServicioOperacionesWeb | None = None,
        auditoria: ServicioAuditoria | None = None,
    ) -> None:
        self.generos: ServicioGenero = generos
        self.editoriales: ServicioEditorial = editoriales
        self.monedas: ServicioMoneda = monedas
        self.tipos: ServicioTipoCotizacion = tipos
        self.libros: ServicioLibro = libros
        self.precios: ServicioPrecio = precios
        self.stocks: ServicioStock = stocks
        self.cotizaciones: ServicioCotizacionDolar = cotizaciones
        self.operaciones_web = operaciones_web
        self.auditoria = auditoria


    def ejecutar(self) -> None:
        """Abre el menú principal hasta que el usuario decida salir."""
        try:
            while True:
                print("\n=== BOOK MANAGER ===")
                print("1. Libros         2. Géneros")
                print("3. Editoriales    4. Monedas")
                print("5. Tipos dólar    6. Precios")
                print("7. Stock          8. Cotizaciones dólar")
                print("9. Obtener cotizaciones por API")
                print("10. Precios bimonetarios")
                print("11. Exportar precios a CSV")
                print("12. Ejecutar scraping")
                print("13. Generar reporte")
                print("14. Ver historial de auditoría")
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
                elif opcion == "9":
                    self._obtener_cotizaciones_api()
                elif opcion == "10":
                    self._mostrar_precios_bimonetarios()
                elif opcion == "11":
                    self._exportar_precios_csv()
                elif opcion == "12":
                    self._ejecutar_scraping()
                elif opcion == "13":
                    self._generar_reporte_excel()
                elif opcion == "14":
                    self._mostrar_auditoria()
                elif opcion == "0":
                    print("Sesión finalizada.")
                    return
                else:
                    print("Opción inválida.")

        except EOFError:
            print("\nSesión finalizada.")

    def _obtener_cotizaciones_api(self) -> None:
        """Descarga cotizaciones y muestra las registradas."""
        try:
            registradas = self.cotizaciones.obtener_cotizaciones()
        except (
            requests.RequestException,
            ValueError,
            KeyError,
            TypeError,
        ) as error:
            print(f"Error al consultar la API: {error}")
            return

        print(f"Cotizaciones registradas: {len(registradas)}.")
        self._listar(registradas)

    def _ultima_cotizacion_oficial(
        self,
    ) -> CotizacionDolar | None:
        """Obtiene la última cotización Oficial registrada."""
        tipo_oficial = next(
            (
                tipo
                for tipo in self.tipos.leer_todos()
                if tipo.nombre.casefold() == "oficial"
            ),
            None,
        )

        if tipo_oficial is None:
            return None

        historico = self.cotizaciones.leer_historico_por_tipo(
            tipo_oficial.id
        )
        validas = [
            cotizacion
            for cotizacion in historico
            if cotizacion.venta > 0
        ]

        return max(
            validas,
            key=lambda cotizacion: cotizacion.fecha,
            default=None,
        )

    def _mostrar_precios_bimonetarios(self) -> None:
        """Presenta ARS y la moneda seleccionada para cada libro."""
        monedas = self.monedas.leer_todos()

        for moneda in monedas:
            print(
                f"{moneda.id}. {moneda.nombre} "
                f"({moneda.codigo})"
            )

        try:
            moneda_id = int(
                input("ID de la segunda moneda: ")
            )
        except ValueError:
            print("El ID de moneda debe ser un número entero.")
            return

        seleccionada = self.monedas.leer_por_id(moneda_id)

        if seleccionada is None:
            print("No existe esa moneda.")
            return

        if seleccionada.codigo == "ARS":
            print("Elegí una moneda distinta de ARS.")
            return

        moneda_ars = next(
            (
                moneda
                for moneda in monedas
                if moneda.codigo == "ARS"
            ),
            None,
        )

        if moneda_ars is None:
            print("No está registrada la moneda ARS.")
            return

        precios = {
            (precio.libro.id, precio.moneda.id): precio.valor
            for precio in self.precios.leer_todos()
        }
        oficial = (
            self._ultima_cotizacion_oficial()
            if seleccionada.codigo == "USD"
            else None
        )

        print(
            f"=== PRECIOS EN ARS Y "
            f"{seleccionada.codigo} ==="
        )

        for libro in self.libros.leer_todos():
            importe_ars = precios.get(
                (libro.id, moneda_ars.id)
            )
            importe_seleccionado = precios.get(
                (libro.id, seleccionada.id)
            )

            if (
                importe_seleccionado is None
                and seleccionada.codigo == "USD"
                and importe_ars is not None
                and oficial is not None
            ):
                importe_seleccionado = (
                    importe_ars / oficial.venta
                )

            texto_ars = (
                f"{importe_ars:.2f} ARS"
                if importe_ars is not None
                else "Sin precio ARS"
            )
            texto_seleccionado = (
                f"{importe_seleccionado:.2f} "
                f"{seleccionada.codigo}"
                if importe_seleccionado is not None
                else f"Sin precio en {seleccionada.codigo}"
            )

            print(
                f"{libro.titulo} | "
                f"{texto_ars} | {texto_seleccionado}"
            )

        if oficial is not None:
            print(
                "Conversión a USD: dólar Oficial venta "
                f"{oficial.venta:.2f} del "
                f"{oficial.fecha.isoformat()}."
            )

    def _exportar_precios_csv(self) -> None:
        """Exporta cada libro en todas las monedas registradas."""
        libros = self.libros.leer_todos()
        monedas = self.monedas.leer_todos()

        if not libros or not monedas:
            print("No hay libros o monedas para exportar.")
            return

        precios = {
            (precio.libro.id, precio.moneda.id): precio.valor
            for precio in self.precios.leer_todos()
        }
        moneda_ars = next(
            (
                moneda
                for moneda in monedas
                if moneda.codigo == "ARS"
            ),
            None,
        )
        oficial = self._ultima_cotizacion_oficial()

        ruta_salida = Path("/content/precios_book_manager.csv")

        with ruta_salida.open(
            "w", encoding="utf-8", newline=""
        ) as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(
                [
                    "libro_id",
                    "isbn",
                    "titulo",
                    "moneda",
                    "valor",
                    "origen",
                ]
            )

            for libro in libros:
                for moneda in monedas:
                    importe = precios.get(
                        (libro.id, moneda.id)
                    )
                    origen = (
                        "Precio registrado"
                        if importe is not None
                        else "Sin precio registrado"
                    )

                    if (
                        importe is None
                        and moneda.codigo == "USD"
                        and moneda_ars is not None
                        and oficial is not None
                    ):
                        importe_ars = precios.get(
                            (libro.id, moneda_ars.id)
                        )

                        if importe_ars is not None:
                            importe = (
                                importe_ars / oficial.venta
                            )
                            origen = (
                                "Convertido con dólar Oficial "
                                f"del {oficial.fecha.isoformat()}"
                            )

                    escritor.writerow(
                        [
                            libro.id,
                            libro.isbn,
                            libro.titulo,
                            moneda.codigo,
                            (
                                f"{importe:.2f}"
                                if importe is not None
                                else ""
                            ),
                            origen,
                        ]
                    )

        print(f"Precios exportados a: {ruta_salida}")

    def _ejecutar_scraping(self) -> None:
        """Pide el umbral, ejecuta Scrapy y muestra sus archivos."""
        if self.operaciones_web is None:
            print("El servicio de scraping no está configurado.")
            return

        entrada = input(
            "Diferencia mínima para alertas (%): "
        ).strip()

        try:
            umbral = Decimal(
                entrada.replace(",", ".")
            )
        except InvalidOperation:
            print("Ingresá un porcentaje numérico.")
            return

        try:
            extraccion, alertas, cantidad = (
                self.operaciones_web.ejecutar_scraping(
                    umbral
                )
            )
        except (
            ValueError,
            RuntimeError,
            subprocess.TimeoutExpired,
        ) as error:
            print(f"Error en scraping: {error}")
            return

        print(f"Libros encontrados: {cantidad}.")
        print(f"Extracción: {extraccion}")
        print(f"Alertas descargables: {alertas}")

    def _generar_reporte_excel(self) -> None:
        """Genera y muestra la ruta del reporte solicitado."""
        if self.operaciones_web is None:
            print("El servicio de reporte no está configurado.")
            return

        try:
            ruta, cantidad = (
                self.operaciones_web.generar_reporte()
            )
        except (
            ValueError,
            RuntimeError,
            FileNotFoundError,
        ) as error:
            print(f"Error en reporte: {error}")
            return

        print(
            f"Reporte generado para {cantidad} libros."
        )
        print(f"Excel descargable: {ruta}")

    def _mostrar_auditoria(self) -> None:
        """Muestra el historial de auditoría registrado."""
        if self.auditoria is None:
            print("El servicio de auditoría no está configurado.")
            return

        try:
            registros = self.auditoria.leer_todos()
        except ValueError as error:
            print(f"Error en auditoría: {error}")
            return

        print("\n=== HISTORIAL DE AUDITORÍA ===")

        if not registros:
            print("No hay operaciones registradas.")
            return

        for registro in registros:
            fecha = registro["fecha"]
            texto_fecha = (
                fecha.strftime("%d/%m/%Y %H:%M:%S")
                if hasattr(fecha, "strftime")
                else str(fecha)
            )
            print(
                f'{registro["id"]} | {texto_fecha} | '
                f'{registro["accion"]} | '
                f'{registro["detalles"]}'
            )

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
