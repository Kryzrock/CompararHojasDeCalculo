import pandas as pd

def compare_excel_files(file1, file2):
    try:
        # Leer ambos archivos Excel usando xlrd
        excel1 = pd.ExcelFile(file1, engine='xlrd')
        excel2 = pd.ExcelFile(file2, engine='xlrd')
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
            df1 = pd.read_excel(file1, sheet_name=sheet, engine='xlrd')
            df2 = pd.read_excel(file2, sheet_name=sheet, engine='xlrd')

            # Comparar columnas
            cols1 = df1.columns.tolist()
            cols2 = df2.columns.tolist()
            dtypes1 = df1.dtypes.tolist()
            dtypes2 = df2.dtypes.tolist()

            if cols1 != cols2:
                report += f"Diferencias en las columnas de la hoja '{sheet}':\nArchivo 1: {cols1}\nArchivo 2: {cols2}\n"
            else:
                report += f"Las columnas en la hoja '{sheet}' son iguales.\n"

                # Comparar tipos de datos
                if dtypes1 != dtypes2:
                    report += f"Diferencias en los tipos de datos de la hoja '{sheet}':\n"
                    for col, dtype1, dtype2 in zip(cols1, dtypes1, dtypes2):
                        if dtype1 != dtype2:
                            report += f"Columna '{col}': Tipo de dato en Archivo 1: {dtype1}, Tipo de dato en Archivo 2: {dtype2}\n"
                else:
                    report += f"Los tipos de datos en la hoja '{sheet}' son iguales.\n"

    return report

# Usar la función
file1 = 'REGISTRO_Gsandoval_20240208_1341.xls'
file2 = 'REGISTRO_Gsandoval_20240805_1251.xls'

resultado = compare_excel_files(file1, file2)

# Guardar el reporte en un archivo de texto
with open('reporte_comparacion.txt', 'w') as f:
    f.write(resultado)

# Imprimir mensaje de confirmación en la terminal
print("Reporte de comparación generado: 'reporte_comparacion.txt'")
print("El script se ejecutó correctamente.")
