## [Ejercicio 3]

- Sprint 2: incorporación de un context manager para transacciones.
- Confirmación de cambios cuando la operación termina correctamente.
- Reversión de cambios y cierre de la sesión cuando ocurre un error.
- Comprobación de commit y rollback con una base de prueba temporal.

## [Ejercicio 2]

- Sprint 2: creación de ConexionDB con SQLAlchemy.
- Configuración del motor para la base de datos SQLite.
- Creación de sesiones y liberación de conexiones.
- Comprobación de la conexión mediante una consulta de prueba.

## [Ejercicio 1]

- Sprint 2: creación de la rama desde Sprint_1.
- Incorporación de la estructura para conexión, modelos y migraciones.
- Incorporación de dependencias y configuración inicial de la API.
- Actualización del objetivo y contexto en README.md.

## [Ejercicio 7]

- Creación de main.py como punto de entrada del sistema.
- Integración de la precarga, la persistencia CSV y la consola.
- Verificación de la ejecución con y sin precarga.

## [Ejercicio 6]

- Implementación del menú principal de consola.
- Incorporación de listados para las ocho entidades.
- Incorporación de alta, modificación y baja para cada modelo.
- Conexión de los menús con los servicios y sus validaciones.
- Presentación de mensajes para operaciones correctas y errores de datos.

## [Ejercicio 5]

- Implementación de la precarga en preload_data.py.
- Creación de ocho archivos CSV con diez registros por entidad.
- Vinculación de libros, precios, stock y cotizaciones mediante IDs.
- Comprobación de la carga de archivos y de las relaciones entre objetos.
- Conservación de los CSV que ya contienen datos al repetir la precarga.

## [Ejercicio 4]

- Implementación de servicios para las ocho entidades.
- Validación de identificadores, textos, importes y cantidades.
- Control de duplicados y de relaciones con entidades registradas.
- Protección del borrado de registros utilizados por otras entidades.
- Guardado en CSV después de las operaciones de modificación.
- Comprobación del CRUD y de la recuperación de datos desde archivos.

## [Ejercicio 3]

- Definición de las interfaces de repositorios.
- Implementación del CRUD de las ocho entidades.
- Persistencia en CSV y reconstrucción de relaciones entre objetos.
- Incorporación del listado completo de stock y cotizaciones.
- Incorporación de type hints en parámetros y retornos.

## [Ejercicio 2]

- Definición de las ocho entidades del sistema.
- Incorporación de clases base para compartir atributos y comportamiento.
- Encapsulación de atributos mediante propiedades.
- Implementación de relaciones entre entidades mediante objetos.
- Incorporación de type hints en atributos, parámetros y retornos.

## [Ejercicio 1]

- Configuración del repositorio y de la rama Sprint_1.
- Creación de la estructura de directorios y archivos del proyecto.
- Incorporación del objetivo y contexto del sprint en README.md.
- Creación de requirements.txt y del registro de cambios.

