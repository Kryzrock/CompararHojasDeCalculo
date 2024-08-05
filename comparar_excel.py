import pandas as pd

def compare_excel_files(file1, file2):
    try:
        # Leer ambos archivos Excel
        excel1 = pd.ExcelFile(file1)
        excel2 = pd.ExcelFile(file2)
    except FileNotFoundError as e:
        return f"Error: {e}"

    # Comparar las hojas (sheets)
    sheets1 = excel1.sheet_names
    sheets2 = excel2.sheet_names

    report = ""

    if sheets1 != sheets2:
        report += f"Diferencias en las hojas:\nArchivo 1: {sheets1}\nArchivo 2: {sheets2}\n"
    else:
        report += "Ambos archivos tienen las mismas hojas.\n"

        # Comparar estructura de cada hoja
        for sheet in sheets1:
            df1 = pd.read_excel(excel1, sheet_name=sheet)
            df2 = pd.read_excel(excel2, sheet_name=sheet)

            if df1.columns.tolist() != df2.columns.tolist():
                report += f"Diferencias en las columnas de la hoja '{sheet}':\nArchivo 1: {df1.columns.tolist()}\nArchivo 2: {df2.columns.tolist()}\n"
            else:
                report += f"Las columnas en la hoja '{sheet}' son iguales.\n"

                # Comparar tipos de datos
                if df1.dtypes.tolist() != df2.dtypes.tolist():
                    report += f"Diferencias en los tipos de datos de la hoja '{sheet}':\nArchivo 1: {df1.dtypes.tolist()}\nArchivo 2: {df2.dtypes.tolist()}\n"
                else:
                    report += f"Los tipos de datos en la hoja '{sheet}' son iguales.\n"

    return report

# Usar la función
file1 = 'File1.xls'
file2 = 'File2.xls'

resultado = compare_excel_files(file1, file2)

# Guardar el reporte en un archivo de texto
with open('reporte_comparacion.txt', 'w') as f:
    f.write(resultado)

# Imprimir mensaje de confirmación en la terminal
print("Reporte de comparación generado: 'reporte_comparacion.txt'")
print("El script se ejecutó correctamente.")
