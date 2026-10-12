#@title Día 5 - Definición de la precarga mediante repositorios

from datetime import date
from pathlib import Path

from book_manager.entities.entities import (
    CotizacionDolar, Editorial, Genero, Libro,
    Moneda, Precio, Stock, TipoCotizacion,
)
from book_manager.repositories.repositories import AlmacenCSV


LIBROS_REALES: list[tuple[str, str, str, int, int]] = [
    ("9789500755757", "Ficciones", "Jorge Luis Borges", 2, 9),
    ("9789877252538", "Rayuela", "Julio Cortázar", 1, 1),
    (
        "9789877256963", "Cien años de soledad",
        "Gabriel García Márquez", 1, 1,
    ),
    (
        "9789500758802", "El principito",
        "Antoine de Saint-Exupéry", 2, 3,
    ),
    (
        "9789878002316", "Harry Potter y la piedra filosofal",
        "J. K. Rowling", 3, 5,
    ),
    ("9789505472697", "El hobbit", "J. R. R. Tolkien", 4, 5),
    ("9789505472611", "El Silmarillion", "J. R. R. Tolkien", 4, 5),
    ("9788426400260", "1984", "George Orwell", 5, 4),
    ("9789877252941", "Bestiario", "Julio Cortázar", 1, 9),
    ("9789877382846", "Final del juego", "Julio Cortázar", 6, 9),
]


def crear_archivos_csv(directorio: Path) -> None:
    """Precarga un almacén vacío mediante objetos y repositorios.

    Conserva los almacenes que ya contienen registros.
    Los datos bibliográficos corresponden a ediciones reales de Cúspide.
    Precios, existencias e importes de cotización son datos de práctica.
    """
    almacen = AlmacenCSV(directorio)
    repositorios = (
        almacen.generos, almacen.editoriales, almacen.monedas,
        almacen.tipos, almacen.libros, almacen.precios,
        almacen.stocks, almacen.cotizaciones,
    )

    if any(repositorio.leer_todos() for repositorio in repositorios):
        return

    nombres_generos: list[str] = [
        "Novela", "Ensayo", "Infantil", "Ciencia ficción", "Fantasía",
        "Historia", "Biografía", "Poesía", "Cuento", "Teatro",
    ]
    nombres_editoriales: list[str] = [
        "Debolsillo", "Sudamericana", "Salamandra", "Minotauro", "Lumen",
        "Alfaguara", "Planeta", "Emecé", "Anagrama", "Seix Barral",
    ]
    datos_monedas: list[tuple[str, str]] = [
        ("ARS", "Peso argentino"),
        ("USD", "Dólar estadounidense"),
        ("EUR", "Euro"),
        ("BRL", "Real brasileño"),
        ("GBP", "Libra esterlina"),
        ("UYU", "Peso uruguayo"),
        ("CLP", "Peso chileno"),
        ("MXN", "Peso mexicano"),
        ("COP", "Peso colombiano"),
        ("CAD", "Dólar canadiense"),
    ]
    nombres_tipos: list[str] = [
        "Oficial", "Blue", "MEP", "CCL", "Mayorista",
        "Tarjeta", "Cripto", "Turista", "Ahorro", "Bancario",
    ]

    generos: dict[int, Genero] = {
        numero: almacen.generos.crear(Genero(numero, nombre))
        for numero, nombre in enumerate(nombres_generos, 1)
    }
    editoriales: dict[int, Editorial] = {
        numero: almacen.editoriales.crear(Editorial(numero, nombre))
        for numero, nombre in enumerate(nombres_editoriales, 1)
    }
    monedas: dict[int, Moneda] = {
        numero: almacen.monedas.crear(Moneda(numero, nombre, codigo))
        for numero, (codigo, nombre) in enumerate(datos_monedas, 1)
    }
    tipos: dict[int, TipoCotizacion] = {
        numero: almacen.tipos.crear(TipoCotizacion(numero, nombre))
        for numero, nombre in enumerate(nombres_tipos, 1)
    }

    for numero, datos in enumerate(LIBROS_REALES, 1):
        isbn, titulo, autor, editorial_id, genero_id = datos
        libro = almacen.libros.crear(
            Libro(
                numero, isbn, titulo, autor,
                editoriales[editorial_id], generos[genero_id],
            )
        )
        almacen.precios.crear(
            Precio(numero, libro, monedas[1], 15000.0 + numero * 3000)
        )
        almacen.stocks.crear(Stock(libro, 4 + numero))

    for numero, tipo in tipos.items():
        almacen.cotizaciones.crear(
            CotizacionDolar(
                tipo, date(2026, 1, 15),
                900.0 + 20 * numero, 950.0 + 20 * numero,
            )
        )

    almacen.guardar()
