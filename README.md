# Book Manager - Grupo 03

## Sprint 3

### Objetivo

Obtener información de precios de Cúspide para comparar los libros del
catálogo de Book Manager con los precios publicados en la web.

### Introducción y contexto

Los sprints anteriores permitieron administrar el catálogo mediante una
consola, persistirlo en una base de datos y consultar cotizaciones externas.

En este sprint se incorporará un scraper con Scrapy para consultar los libros
del catálogo, comparar precios internos y externos, generar alertas en CSV y
un reporte en Excel. También se registrarán las operaciones del sistema en
un historial de auditoría consultable desde la consola.

## Sprint 2

### Objetivo

Ampliar Book Manager para persistir sus datos en una base de datos
relacional mediante SQLAlchemy y consultar cotizaciones externas.

### Introducción y contexto

El Sprint 1 permitió administrar libros, precios, stock y cotizaciones
mediante una aplicación de consola con persistencia en archivos CSV.

En este sprint se migrarán esos datos a tablas relacionadas. El sistema
continuará ofreciendo operaciones CRUD y agregará la consulta de
cotizaciones del dólar por API, la visualización de precios en dos
monedas y la exportación de precios a CSV.

## Sprint 1

### Objetivo

Aplicar programación orientada a objetos y persistencia de datos en
archivos mediante el desarrollo de un sistema de gestión de libros.

### Introducción y contexto

Una librería con venta al público necesita modernizar la gestión de su
inventario. La fluctuación de los costos de importación requiere manejar
precios en diferentes monedas y registrar las cotizaciones del dólar.

El sprint contempla una aplicación de consola en Python para gestionar
libros, géneros, editoriales, monedas, tipos de cotización, precios,
stock y cotizaciones del dólar, con operaciones CRUD para cada entidad.

El contexto del proyecto también plantea cotizar libros según el valor
del dólar y comparar precios con la competencia web, tomando a Cúspide
como referencia.
