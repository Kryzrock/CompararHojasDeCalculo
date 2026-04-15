# Comparar Hojas de Calculo

Este proyecto compara archivos Excel `.xls` y `.xlsx` para detectar diferencias entre versiones de planillas usadas en procesos de carga o importacion.

La herramienta principal actual es `comparador_excel_menu.py`, que permite ejecutar comparaciones desde un menu interactivo y generar reportes `.txt`.

## Que compara

El comparador revisa:

- Hojas presentes en cada archivo.
- Dimensiones de cada hoja.
- Columnas por hoja.
- Tipos de datos por columna.
- Contenido de las celdas cuando la estructura coincide.

El reporte final separa:

- Diferencias estructurales.
- Diferencias de contenido.

## Requisitos

1. Instalar Python desde [python.org](https://www.python.org/downloads/).
2. Verificar la instalacion:

```bash
py --version
```

3. Instalar dependencias:

```bash
py -m pip install pandas
py -m pip install xlrd
py -m pip install openpyxl
```

## Archivos principales

- `comparador_excel_menu.py`: interfaz principal con menu.
- `comparar_excel.py`: script simple legado.
- `comparar_excel2.py`: variante legacy para hojas con encabezados en la primera fila.
- `categorias.json`: configuracion de categorias detectadas por prefijo.
- `comparar_excel.bat`: lanzador rapido en Windows para abrir el menu.

## Uso

### Opcion recomendada

Ejecutar el menu principal:

```bash
py comparador_excel_menu.py
```

O en Windows:

```bat
comparar_excel.bat
```

### Modos del menu

1. `Comparacion por Carpetas`
   Compara automaticamente archivos de `archivos_viejos/` contra `archivos_nuevos/` usando el prefijo del nombre.

2. `Comparacion Automatica`
   Usa exactamente 2 archivos `.xls` o `.xlsx` ubicados en la carpeta actual.

3. `Comparacion Manual`
   Busca archivos de forma recursiva y permite elegir manualmente cual es el archivo viejo y cual es el nuevo.

4. `Ver Inventario de Archivos`
   Lista los archivos detectados agrupados por categoria y subcategoria.

## Convencion de nombres

Para detectar version y agrupar archivos, el menu reconoce nombres como:

```text
NOMBRE_YYYYMMDD_HHMM.xls
NOMBRE_YYYYMMDD_HHMM.xlsx
NOMBRE_YYYYMMDD.xls
NOMBRE_YYYYMMDD.xlsx
```

Ejemplos:

```text
DGA_CPF_PROGRAMAS_20251216_1201.xls
DGA_CPF_OFICIOS_JUDICIALES_20251216_1202.xlsx
```

## Categorias configurables

La deteccion de categorias ya no esta fija en el codigo. Se toma desde `categorias.json`.

Ejemplo:

```json
{
  "DGA_CPF_PROGRAMAS": ["DGA-CPF", "Programas"],
  "REGISTRO_": ["SECRETARIA", "Registro"]
}
```

Si necesitas agregar una categoria nueva, alcanza con sumar una entrada en ese archivo.

## Salida de reportes

Los reportes se guardan automaticamente en:

```text
reportes/YYYYMMDD/
```

Cada reporte incluye:

- Fecha y hora de ejecucion.
- Archivos comparados.
- Categoria detectada cuando aplica.
- Detalle de diferencias estructurales y de contenido.

## Estructura esperada

Ejemplo de carpetas:

```text
CompararArchivos/
├─ archivos_nuevos/
├─ archivos_viejos/
├─ historial/
├─ reportes/
├─ categorias.json
├─ comparar_excel.bat
└─ comparador_excel_menu.py
```

## Ejemplo de ejecucion

```bash
PS C:\DirectorioProyecto> py comparador_excel_menu.py
```

El programa abrira el menu y guiara la comparacion segun el modo elegido.

## Notas

- Para archivos `.xls` se usa `xlrd`.
- Para archivos `.xlsx` se usa `openpyxl`.
- Los reportes se escriben en UTF-8.
- Si dos archivos tienen la misma estructura pero distinto contenido, el reporte ahora lo informa explicitamente.
