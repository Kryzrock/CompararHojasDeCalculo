# Comparar Hojas de Calculo
Este proyecto está diseñado para comparar dos archivos Excel ubicados en el directorio raíz del proyecto. Los scripts incluidos en este proyecto realizan las siguientes comparaciones entre las hojas de cálculo:

- La cantidad de hojas en cada archivo.
- La cantidad de columnas en cada hoja.
- El tipo de datos de cada columna.

Para utilizar los scripts, especifica los archivos a comparar en las variables `file1` y `file2` dentro de los scripts correspondientes.

Este proceso de comparación facilita la identificación de inconsistencias entre los archivos Excel, asegurando que los datos se mantengan coherentes y estructurados correctamente.

## Requisitos Previos

Antes de poder ejecutar los scripts, asegúrate de tener los siguientes requisitos instalados y configurados:

1. Instalar la última versión de Python desde [python.org](https://www.python.org/downloads/).
2. Verificar que Python esté instalado y corriendo correctamente usando el siguiente comando en la consola:
   ```bash
   py --version
   ```
3. Instalar los siguientes módulos de Python utilizando pip:
   ```bash
   py -m pip install pandas 
   py -m pip install xlrd
   py -m pip install openpyxl
   ```

## Scripts Disponibles

### 1. `comparar_excel.py`

Este script compara dos archivos Excel y genera un archivo `.txt` con el resultado de la comparación.

**Resultado de ejemplo en el archivo `.txt`:**
```
Diferencias en los tipos de datos de la hoja 'NombreHoja':
Archivo 1: [dtype('<M8[ns]'), dtype('O'), dtype('<M8[ns]'), dtype('<M8[ns]'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O')]
Archivo 2: [dtype('<M8[ns]'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O'), dtype('O')]
```

### 2. `comparar_excel2.py`

Este script también compara dos archivos Excel, pero está configurado para trabajar con archivos donde la fila 1 de cada hoja contiene los nombres de las columnas. 

**Resultado de ejemplo en el archivo `.txt`:**
```
Diferencias en los tipos de datos de la hoja 'Nombre de hoja':
Columna 'Nombre de columna': Tipo de dato en Archivo 1: datetime64[ns], Tipo de dato en Archivo 2: object
```

## Ejecución de los Scripts

Para ejecutar los scripts, utiliza la consola de la siguiente manera:

**Comparar Excel**
```bash
PS C:\DGA\CompararArchivos> py comparar_excel.py
>> 
Reporte de comparación generado: 'reporte_comparacion.txt'
El script se ejecutó correctamente.
```

**Comparar Excel 2**
```bash
PS C:\DGA\CompararArchivos> py comparar_excel2.py
>> 
Reporte de comparación generado: 'reporte_comparacion.txt'
El script se ejecutó correctamente.
```

Cada script generará un archivo `.txt` con el resultado de la comparación de los archivos especificados.

---

