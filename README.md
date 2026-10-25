# CSV Data Cleaning Pipeline

Proceso de limpieza y validación de ventas en archivos CSV,
desarrollado con Python y pandas.

## Objetivo

Transformar datos desordenados en un conjunto de datos utilizable,
conservando los registros rechazados y sus motivos para revisión.

## Funcionalidades

- Normalización de espacios y correos.
- Eliminación de duplicados exactos.
- Validación de columnas obligatorias.
- Validación de identificadores, fechas, cantidades y precios.
- Detección de identificadores repetidos.
- Separación de registros válidos y rechazados.
- Generación de un reporte de calidad en JSON.

## Tecnologías

- Python
- pandas
- pathlib
- logging

## Ejecución

1. Crear y activar un entorno virtual.
2. Instalar dependencias:

   python -m pip install -r requirements.txt

3. Ejecutar:

   python src/clean_data.py

## Resultados del ejemplo

- 10 filas de entrada.
- 1 duplicado eliminado.
- 3 registros válidos.
- 6 registros rechazados.

## Reglas de negocio

- El identificador debe ser un entero positivo y único.
- El cliente es obligatorio.
- El correo debe tener una estructura válida.
- La fecha debe usar el formato YYYY-MM-DD.
- La cantidad debe ser un entero positivo.
- El precio unitario debe ser mayor que cero.

## Datos

Todos los datos utilizados son ficticios.

## Limitaciones

- El archivo se procesa completo en memoria.
- La validación del correo no verifica su existencia.
- Para simplificar el ejemplo, los precios usan números de pandas;
  un sistema financiero requeriría una estrategia explícita de precisión.