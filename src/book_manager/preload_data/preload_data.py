import csv
from pathlib import Path


def generar_isbn13(numero: int) -> str:
    """Genera un ISBN-13 de ejemplo con dígito verificador válido."""
    base: str = f"978000000{numero:03d}"

    suma: int = sum(
        int(digito) * (1 if posicion % 2 == 0 else 3)
        for posicion, digito in enumerate(base)
    )

    verificador: int = (10 - suma % 10) % 10
    return f"{base}{verificador}"


def crear_archivos_csv(directorio: Path) -> None:
    """Crea la precarga sin reemplazar CSV que ya contienen datos."""
    generos: list[str] = [
        "Novela",
        "Ensayo",
        "Infantil",
        "Ciencia ficción",
        "Fantasía",
        "Historia",
        "Biografía",
        "Poesía",
        "Tecnología",
        "Cocina",
    ]

    editoriales: list[str] = [
        "Editorial del Sur",
        "Editorial del Norte",
        "Editorial Central",
        "Editorial Río",
        "Editorial Horizonte",
        "Editorial Prisma",
        "Editorial Bosque",
        "Editorial Faro",
        "Editorial Luna",
        "Editorial Puente",
    ]

    monedas: list[tuple[str, str]] = [
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

    tipos: list[str] = [
        "Oficial",
        "Blue",
        "MEP",
        "CCL",
        "Mayorista",
        "Tarjeta",
        "Cripto",
        "Turista",
        "Ahorro",
        "Bancario",
    ]

    titulos: list[str] = [
        "La casa del viento",
        "Ideas para pensar",
        "Viaje al bosque",
        "El planeta distante",
        "El reino escondido",
        "Crónicas del puerto",
        "Vida en movimiento",
        "Versos de otoño",
        "Python paso a paso",
        "Recetas cotidianas",
    ]

    datos: dict[
        str,
        tuple[list[str], list[list[str]]],
    ] = {
        "generos.csv": (
            ["id", "nombre"],
            [
                [str(i), nombre]
                for i, nombre in enumerate(generos, 1)
            ],
        ),
        "editoriales.csv": (
            ["id", "nombre"],
            [
                [str(i), nombre]
                for i, nombre in enumerate(editoriales, 1)
            ],
        ),
        "monedas.csv": (
            ["id", "nombre", "codigo"],
            [
                [str(i), nombre, codigo]
                for i, (codigo, nombre) in enumerate(monedas, 1)
            ],
        ),
        "tipos_cotizacion.csv": (
            ["id", "nombre"],
            [
                [str(i), nombre]
                for i, nombre in enumerate(tipos, 1)
            ],
        ),
        "libros.csv": (
            [
                "id",
                "isbn",
                "titulo",
                "autor",
                "editorial_id",
                "genero_id",
            ],
            [
                [
                    str(i),
                    generar_isbn13(i),
                    titulo,
                    f"Autor de ejemplo {i}",
                    str(i),
                    str(i),
                ]
                for i, titulo in enumerate(titulos, 1)
            ],
        ),
        "precios.csv": (
            ["id", "libro_id", "moneda_id", "valor"],
            [
                [
                    str(i),
                    str(i),
                    "1",
                    str(15000 + i * 3000),
                ]
                for i in range(1, 11)
            ],
        ),
        "stock.csv": (
            ["libro_id", "cantidad"],
            [
                [str(i), str(4 + i)]
                for i in range(1, 11)
            ],
        ),
        "cotizaciones.csv": (
            ["tipo_id", "fecha", "compra", "venta"],
            [
                [
                    str(i),
                    "2026-01-15",
                    str(900 + 20 * i),
                    str(950 + 20 * i),
                ]
                for i in range(1, 11)
            ],
        ),
    }

    directorio.mkdir(parents=True, exist_ok=True)

    for nombre, (columnas, filas) in datos.items():
        ruta: Path = directorio / nombre

        if ruta.exists():
            with ruta.open(
                encoding="utf-8", newline=""
            ) as archivo:
                if any(csv.DictReader(archivo)):
                    continue

        with ruta.open(
            "w", encoding="utf-8", newline=""
        ) as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(columnas)
            escritor.writerows(filas)
