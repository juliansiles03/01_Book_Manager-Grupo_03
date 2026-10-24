# Sprint 3

## [Ejercicio 6]

- Creación de la tabla auditoria con acción, fecha y detalles en Supabase.
- Implementación del repositorio CRUD de registros de auditoría.
- Creación de un decorador para registrar operaciones correctas y errores.
- Aplicación del decorador a las operaciones públicas de los servicios.
- Comprobación en una base temporal y persistencia de una operación en Supabase.

## [Ejercicio 5]

- Generación de un reporte Excel con Libro, Precio interno, Precio web, Diferencia y Fecha de extracción.
- Comparación de los precios web con los precios internos en ARS.
- Almacenamiento de la diferencia como valor numérico visible en lectores de Excel.
- Comprobación de las cinco columnas, los importes y las fechas de extracción.

## [Ejercicio 4]

- Comparación del precio web con el precio interno en pesos argentinos.
- Solicitud del umbral porcentual antes de cada ejecución del scraper.
- Generación de un CSV descargable de alertas en cada ejecución.
- Comprobación de alertas con un umbral del 10 %.

## [Ejercicio 3]

- Implementación de CuspideSpider con búsquedas limitadas a títulos del catálogo.
- Revisión de los primeros diez resultados de cada título y confirmación mediante ISBN.
- Extracción de precio, imagen, medios de pago y descripción mediante un Item Loader.
- Validación y deduplicación con pipelines de Scrapy.
- Ejecución desde el proyecto y almacenamiento de los resultados para los reportes.
- Comprobación local y extracción real de productos del catálogo.

## [Ejercicio 2]

- Implementación de una función para cargar datos desde los archivos SQL generados en el TP2.
- Ejecución de los ocho archivos en el orden de dependencias de las tablas.
- Carga mediante una transacción y comprobación de los registros en Supabase.

## [Ejercicio 1]

- Creación de Sprint_3 a partir de Sprint_2 corregido.
- Preparación de las carpetas del scraper y los reportes.
- Registro de Scrapy y OpenPyXL en requirements.txt.
- Actualización del objetivo y contexto en README.md.

# Sprint 2
## [Ejercicio 6]

- Implementación de los ocho repositorios CRUD con SQLAlchemy.
- Integración de servicios y consola con PostgreSQL de Supabase.
- Adaptación de main.py para iniciar con los datos migrados.
- Comprobación del CRUD, la persistencia y el menú principal.
- Corrección: extracción de las interfaces a un módulo compartido sin importaciones circulares.
- Corrección: los repositorios de base implementan IRepositorio, IRepositorioStock e IRepositorioCotizacionDolar.
- Corrección: traducción de IntegrityError a ValueError después de revertir la transacción.
- Verificación de duplicados, borrados con dependencias y continuidad de las operaciones después de un error.

## [Ejercicio 4]

- Definición de las ocho tablas con SQLAlchemy ORM.
- Configuración de claves primarias, relaciones y restricciones.
- Comprobación de tablas y relaciones en una base temporal.
- Creación y comprobación de las ocho tablas en Supabase.
- Corrección: relaciones bidireccionales con back_populates entre los ocho modelos.
- Corrección: navegación desde Libro hacia sus precios y su stock individual.
- Conservación de las restricciones de borrado para registros con dependencias.

## [Ejercicio 8]

- Incorporación de la consulta de cotizaciones por API al menú.
- Visualización de precios en ARS y otra moneda seleccionada.
- Conversión a USD con la última cotización Oficial disponible.
- Carga de precios de demostración para las demás monedas.
- Exportación de precios a CSV para las monedas registradas.
- Comprobación de los menús y del archivo exportado.
- Registro de DATABASE_URL y API_URL en el archivo .env.
- Carga automática del .env desde ConexionDB.
- Verificación de Supabase sin una DATABASE_URL heredada.

## [Ejercicio 7]

- Lectura de API_URL desde .env mediante dotenv.
- Descarga y validación de cotizaciones desde DolarAPI.
- Asociación de las casas de la API con los tipos registrados.
- Alta y actualización de cotizaciones en Supabase.
- Comprobación de persistencia y actualización con una API simulada.

## [Ejercicio 5]

- Lectura de los ocho archivos CSV del Sprint 1.
- Migración de sus registros a las tablas de Supabase.
- Generación de ocho archivos SQL con sentencias de inserción.
- Comprobación de los datos cargados y de los archivos generados.

## [Ejercicio 3]

- Incorporación del context manager transaccion() a ConexionDB.
- Confirmación de cambios al finalizar correctamente.
- Reversión ante errores y cierre de sesiones.
- Comprobación de commit y rollback en una base temporal.

## [Ejercicio 2]

- Implementación de ConexionDB con SQLAlchemy.
- Configuración de PostgreSQL de Supabase y del controlador psycopg.
- Creación de sesiones y liberación de conexiones.
- Prueba aislada con SQLite y consulta real a Supabase.

## [Ejercicio 1]

- Configuración de la rama Sprint_2 a partir del Sprint_1.
- Preparación de los directorios y archivos del nuevo sprint.
- Registro de las dependencias y de API_URL en .env.
- Actualización del objetivo y contexto en README.md.

# Sprint 1

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
