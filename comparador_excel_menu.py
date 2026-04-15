import glob
import json
import os
import re
from datetime import datetime

import pandas as pd


DEFAULT_CATEGORIES = {
    "DGA_CPF_OFICIOS_JUDICIALES": ["DGA-CPF", "Oficios Judiciales"],
    "DGA_CPF_OPERATIVOS_PAGO": ["DGA-CPF", "Operativos de Pago"],
    "DGA_CPF_PROGRAMAS": ["DGA-CPF", "Programas"],
    "REGISTRO_": ["SECRETARIA", "Registro"],
    "DATOSMES": ["PRESUPUESTARIA", "Datos del Mes"],
    "PRESUPUESTO": ["PRESUPUESTARIA", "Presupuesto"],
}


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_supported_excel_files(folder, recursive=False):
    """Obtiene archivos .xls y .xlsx desde una carpeta."""
    pattern = "**/*" if recursive else "*"
    xls_files = glob.glob(os.path.join(folder, f"{pattern}.xls"), recursive=recursive)
    xlsx_files = glob.glob(os.path.join(folder, f"{pattern}.xlsx"), recursive=recursive)
    return sorted(xls_files + xlsx_files)


def get_engine(filepath):
    """Devuelve el engine correcto según la extensión del archivo."""
    ext = os.path.splitext(filepath)[1].lower()
    return "xlrd" if ext == ".xls" else "openpyxl"


def load_categories(config_path="categorias.json"):
    """Carga categorías desde JSON o usa defaults si no existe."""
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    return DEFAULT_CATEGORIES


def get_output_dir(base_dir):
    """Crea y retorna la carpeta de salida para reportes."""
    output_dir = os.path.join(base_dir, "reportes", datetime.now().strftime("%Y%m%d"))
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def save_report(report_text, report_name, metadata_lines, output_dir):
    """Guarda un reporte con encabezado común."""
    report_path = os.path.join(output_dir, report_name)
    with open(report_path, "w", encoding="utf-8", errors="replace") as f:
        f.write("REPORTE DE COMPARACION\n")
        f.write("=" * 71 + "\n\n")
        for line in metadata_lines:
            f.write(f"{line}\n")
        f.write("\n" + "=" * 71 + "\n\n")
        f.write(report_text)
    return report_path


def extract_file_info(filename):
    """Extrae información del nombre del archivo (prefijo, fecha, hora)."""
    basename = os.path.basename(filename)

    patterns = [
        r"(.+?)_(\d{8})_(\d{4})\.xlsx?$",
        r"(.+?)_(\d{8})\.xlsx?$",
    ]

    for pattern in patterns:
        match = re.match(pattern, basename, re.IGNORECASE)
        if match:
            groups = match.groups()
            prefix = groups[0]
            date_str = groups[1]
            time_str = groups[2] if len(groups) > 2 else "0000"

            try:
                dt = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M")
            except ValueError:
                continue

            return {
                "filename": basename,
                "fullpath": filename,
                "prefix": prefix,
                "date": date_str,
                "time": time_str,
                "datetime": dt,
            }

    return None


def group_files_by_prefix(files):
    """Agrupa archivos por su prefijo."""
    groups = {}

    for file in files:
        info = extract_file_info(file)
        if info:
            prefix = info["prefix"]
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(info)

    for prefix in groups:
        groups[prefix].sort(key=lambda item: item["datetime"], reverse=True)

    return groups


def detect_file_category(prefix, categories):
    """Detecta la categoría del archivo basándose en el prefijo."""
    prefix_upper = prefix.upper()
    prefix_compact = prefix_upper.replace("_", "")

    for pattern, category_info in categories.items():
        pattern_upper = pattern.upper()
        normalized_pattern = pattern_upper.replace("_", "")
        if pattern_upper in prefix_upper or normalized_pattern in prefix_compact:
            return tuple(category_info)

    return "OTROS", "Sin categoría"


def values_equal(df1, df2):
    """Compara valores tratando NaN/NaT como equivalentes."""
    return df1.eq(df2) | (df1.isna() & df2.isna())


def summarize_data_differences(df1, df2, max_differences=10):
    """Resume diferencias de contenido entre dos dataframes equivalentes."""
    equal_mask = values_equal(df1, df2)
    diff_mask = ~equal_mask
    total_cells = int(diff_mask.to_numpy().sum())
    examples = []

    if total_cells == 0:
        return total_cells, examples

    changed_rows = diff_mask.any(axis=1)
    for row_idx in df1.index[changed_rows]:
        differing_columns = diff_mask.columns[diff_mask.loc[row_idx]]
        for col in differing_columns:
            val1 = df1.at[row_idx, col]
            val2 = df2.at[row_idx, col]
            examples.append((row_idx + 2, col, val1, val2))
            if len(examples) >= max_differences:
                return total_cells, examples

    return total_cells, examples


# ============================================================================
# FUNCIÓN DE COMPARACIÓN
# ============================================================================

def compare_excel_files(file1, file2, file1_label="Archivo Antiguo", file2_label="Archivo Nuevo"):
    """Compara dos archivos Excel y genera un reporte detallado."""
    try:
        excel1 = pd.ExcelFile(file1, engine=get_engine(file1))
        excel2 = pd.ExcelFile(file2, engine=get_engine(file2))
    except Exception as e:
        return f"Error al leer los archivos: {e}"

    sheets1 = excel1.sheet_names
    sheets2 = excel2.sheet_names

    report = ""
    structural_differences = 0
    data_differences = 0

    report += "COMPARACION DE HOJAS\n"
    report += "-" * 50 + "\n"

    if sheets1 != sheets2:
        structural_differences += 1
        report += "LAS HOJAS SON DIFERENTES\n\n"

        sheets_only_in_1 = set(sheets1) - set(sheets2)
        sheets_only_in_2 = set(sheets2) - set(sheets1)
        common_sheets = set(sheets1) & set(sheets2)

        if sheets_only_in_1:
            report += f"   Hojas solo en {file1_label}: {list(sheets_only_in_1)}\n"
        if sheets_only_in_2:
            report += f"   Hojas solo en {file2_label}: {list(sheets_only_in_2)}\n"
        if common_sheets:
            report += f"   Hojas comunes: {list(common_sheets)}\n"
        report += "\n"

        sheets_to_compare = list(common_sheets)
    else:
        report += f"AMBOS ARCHIVOS TIENEN LAS MISMAS HOJAS ({len(sheets1)} hojas)\n"
        report += f"   Hojas: {sheets1}\n\n"
        sheets_to_compare = sheets1

    if sheets_to_compare:
        report += "COMPARACION DETALLADA POR HOJA\n"
        report += "=" * 50 + "\n\n"

        for i, sheet in enumerate(sheets_to_compare, 1):
            report += f"HOJA {i}: '{sheet}'\n"
            report += "-" * 30 + "\n"

            try:
                df1 = pd.read_excel(file1, sheet_name=sheet, engine=get_engine(file1))
                df2 = pd.read_excel(file2, sheet_name=sheet, engine=get_engine(file2))

                report += "   Dimensiones:\n"
                report += f"      - {file1_label}: {df1.shape[0]} filas x {df1.shape[1]} columnas\n"
                report += f"      - {file2_label}: {df2.shape[0]} filas x {df2.shape[1]} columnas\n"

                if df1.shape != df2.shape:
                    structural_differences += 1
                    report += "      Las dimensiones son diferentes\n"
                    if df1.shape[0] != df2.shape[0]:
                        diff_rows = df2.shape[0] - df1.shape[0]
                        if diff_rows > 0:
                            report += f"      El archivo nuevo tiene {diff_rows} fila(s) mas\n"
                        else:
                            report += f"      El archivo nuevo tiene {abs(diff_rows)} fila(s) menos\n"
                else:
                    report += "      Las dimensiones son iguales\n"
                report += "\n"

                cols1 = df1.columns.tolist()
                cols2 = df2.columns.tolist()

                report += "   Columnas:\n"
                if cols1 != cols2:
                    structural_differences += 1
                    report += "      LAS COLUMNAS SON DIFERENTES\n"

                    cols_only_in_1 = [col for col in cols1 if col not in cols2]
                    cols_only_in_2 = [col for col in cols2 if col not in cols1]
                    common_cols = [col for col in cols1 if col in cols2]

                    if cols_only_in_1:
                        report += f"         - Solo en {file1_label}: {cols_only_in_1}\n"
                    if cols_only_in_2:
                        report += f"         - Solo en {file2_label}: {cols_only_in_2}\n"
                    if common_cols:
                        report += (
                            f"         - Columnas comunes: {len(common_cols)} "
                            f"de {max(len(cols1), len(cols2))}\n"
                        )
                else:
                    report += f"      COLUMNAS IDENTICAS ({len(cols1)} columnas)\n"

                    dtypes1 = df1.dtypes.tolist()
                    dtypes2 = df2.dtypes.tolist()

                    report += "\n   Tipos de datos:\n"
                    if dtypes1 != dtypes2:
                        structural_differences += 1
                        report += "      ALGUNOS TIPOS DE DATOS SON DIFERENTES\n"
                        for col, dtype1, dtype2 in zip(cols1, dtypes1, dtypes2):
                            if dtype1 != dtype2:
                                report += f"         - '{col}': {dtype1} -> {dtype2}\n"
                    else:
                        report += "      TODOS LOS TIPOS DE DATOS SON IGUALES\n"

                    report += "\n   Contenido:\n"
                    if df1.shape == df2.shape:
                        df1_reset = df1.reset_index(drop=True)
                        df2_reset = df2.reset_index(drop=True)
                        total_cells, examples = summarize_data_differences(df1_reset, df2_reset)

                        if total_cells > 0:
                            data_differences += total_cells
                            report += f"      DATOS DIFERENTES: {total_cells} celda(s) con cambios\n"
                            for row_number, column, value1, value2 in examples:
                                report += (
                                    f"         - Fila {row_number}, '{column}': "
                                    f"{value1!r} -> {value2!r}\n"
                                )
                            if total_cells > len(examples):
                                pending = total_cells - len(examples)
                                report += f"         - ... y {pending} diferencia(s) mas\n"
                        else:
                            report += "      CONTENIDO IDENTICO\n"
                    else:
                        report += "      No se comparo contenido por diferencias de dimensiones\n"

            except Exception as e:
                report += f"      Error al procesar la hoja: {e}\n"

            report += "\n"

    report += "RESUMEN FINAL\n"
    report += "=" * 50 + "\n"
    report += f"Diferencias estructurales: {structural_differences}\n"
    report += f"Diferencias de contenido:  {data_differences}\n\n"

    if structural_differences == 0 and data_differences == 0:
        report += "LOS ARCHIVOS SON IDENTICOS EN ESTRUCTURA Y CONTENIDO\n"
        report += "   - Mismas hojas\n"
        report += "   - Mismas columnas en cada hoja\n"
        report += "   - Mismos tipos de datos\n"
        report += "   - Mismo contenido\n"
    elif structural_differences == 0:
        report += "LA ESTRUCTURA ES COMPATIBLE, PERO HAY CAMBIOS EN LOS DATOS\n"
    else:
        report += "SE ENCONTRARON DIFERENCIAS ESTRUCTURALES Y/O DE CONTENIDO\n"
        report += "   Revisa el detalle para identificar impacto en la importacion.\n"

    return report


def run_comparison(file_old, file_new, output_dir, report_prefix, metadata_lines):
    """Ejecuta la comparación y guarda el reporte."""
    result = compare_excel_files(file_old, file_new, "Archivo VIEJO", "Archivo NUEVO")
    filename = f"{report_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = save_report(result, filename, metadata_lines, output_dir)
    return result, path


# ============================================================================
# SISTEMA DE MENÚ
# ============================================================================

def show_menu():
    """Muestra el menú principal."""
    print("\n" + "=" * 70)
    print("SISTEMA DE COMPARACION DE ARCHIVOS EXCEL - DATA WAREHOUSE")
    print("=" * 70)
    print("\nMODOS DE OPERACION:\n")
    print("   1. Comparacion por Carpetas (archivos_nuevos vs archivos_viejos)")
    print("   2. Comparacion Automatica (2 archivos en carpeta actual)")
    print("   3. Comparacion Manual (seleccionar archivos especificos)")
    print("   4. Ver Inventario de Archivos")
    print("   0. Salir")
    print("\n" + "-" * 70)

    choice = input("Selecciona una opcion: ").strip()
    return choice


def modo_carpetas(categories):
    """Modo de comparación por carpetas."""
    print("\n" + "=" * 70)
    print("MODO: COMPARACION POR CARPETAS")
    print("=" * 70)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    carpeta_nuevos = os.path.join(current_dir, "archivos_nuevos")
    carpeta_viejos = os.path.join(current_dir, "archivos_viejos")
    output_dir = get_output_dir(current_dir)

    if not os.path.exists(carpeta_nuevos):
        print("\nNo existe la carpeta: archivos_nuevos")
        print("Creando carpeta...")
        os.makedirs(carpeta_nuevos)
        print(f"Carpeta creada: {carpeta_nuevos}")

    if not os.path.exists(carpeta_viejos):
        print("\nNo existe la carpeta: archivos_viejos")
        print("Creando carpeta...")
        os.makedirs(carpeta_viejos)
        print(f"Carpeta creada: {carpeta_viejos}")

    archivos_nuevos = get_supported_excel_files(carpeta_nuevos)
    archivos_viejos = get_supported_excel_files(carpeta_viejos)

    if not archivos_nuevos:
        print("\nNo hay archivos .xls/.xlsx en: archivos_nuevos")
        print("Coloca los archivos nuevos en esa carpeta")
        return

    if not archivos_viejos:
        print("\nNo hay archivos .xls/.xlsx en: archivos_viejos")
        print("Coloca los archivos viejos en esa carpeta")
        return

    grupos_nuevos = group_files_by_prefix(archivos_nuevos)
    grupos_viejos = group_files_by_prefix(archivos_viejos)

    print("\nARCHIVOS ENCONTRADOS:")
    print(f"   Archivos nuevos: {len(archivos_nuevos)}")
    print(f"   Archivos viejos: {len(archivos_viejos)}")

    prefijos_comunes = set(grupos_nuevos.keys()) & set(grupos_viejos.keys())

    if not prefijos_comunes:
        print("\nNo se encontraron archivos con prefijos coincidentes")
        print("\nVerifica que los nombres de archivo tengan el mismo prefijo:")
        print("   Ejemplo: DGA_CPF_PROGRAMAS_20251216_1201.xlsx (nuevo)")
        print("            DGA_CPF_PROGRAMAS_20251210_0830.xls (viejo)")
        return

    print(f"\nCOINCIDENCIAS ENCONTRADAS: {len(prefijos_comunes)} tipo(s) de archivo\n")

    comparaciones_realizadas = 0

    for prefix in sorted(prefijos_comunes):
        archivo_nuevo = grupos_nuevos[prefix][0]
        archivo_viejo = grupos_viejos[prefix][0]

        category, subcategory = detect_file_category(prefix, categories)

        print("-" * 70)
        print(f"Tipo: {category} - {subcategory}")
        print(f"   Nuevo: {archivo_nuevo['filename']}")
        print(f"   Viejo: {archivo_viejo['filename']}")
        print("-" * 70)

        metadata_lines = [
            f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Categoria: {category} - {subcategory}",
            f"Archivo Viejo: {archivo_viejo['filename']}",
            f"Archivo Nuevo: {archivo_nuevo['filename']}",
        ]
        resultado, reporte_path = run_comparison(
            archivo_viejo["fullpath"],
            archivo_nuevo["fullpath"],
            output_dir,
            f"reporte_{prefix}",
            metadata_lines,
        )

        print(resultado)
        print(f"\nReporte guardado: {reporte_path}\n")
        comparaciones_realizadas += 1

    print("=" * 70)
    print(f"Comparaciones realizadas: {comparaciones_realizadas}")
    print("=" * 70)


def modo_automatico():
    """Modo de comparación automática con 2 archivos en carpeta actual."""
    print("\n" + "=" * 70)
    print("MODO: COMPARACION AUTOMATICA")
    print("=" * 70)

    current_directory = os.path.dirname(os.path.abspath(__file__))
    output_dir = get_output_dir(current_directory)
    excel_files = get_supported_excel_files(current_directory)

    if len(excel_files) != 2:
        print(f"\nERROR: Se encontraron {len(excel_files)} archivos .xls/.xlsx")
        print("Este modo requiere EXACTAMENTE 2 archivos en la carpeta actual")
        print("No busca archivos en subcarpetas; para eso usa el modo manual.")
        if excel_files:
            print("\nArchivos encontrados:")
            for file_path in excel_files:
                print(f"   - {os.path.basename(file_path)}")
        return

    info1 = extract_file_info(excel_files[0])
    info2 = extract_file_info(excel_files[1])

    if info1 and info2:
        if info1["datetime"] < info2["datetime"]:
            archivo_viejo, archivo_nuevo = excel_files[0], excel_files[1]
        else:
            archivo_viejo, archivo_nuevo = excel_files[1], excel_files[0]

        print("\nDeteccion automatica de versiones:")
        print(f"   Archivo VIEJO: {os.path.basename(archivo_viejo)}")
        print(f"   Archivo NUEVO: {os.path.basename(archivo_nuevo)}")
    else:
        archivo_viejo, archivo_nuevo = sorted(excel_files)
        print("\nNo se pudo detectar fechas, comparando en orden alfabetico")

    print("\nAnalizando archivos...")

    metadata_lines = [
        f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Archivo Viejo: {os.path.basename(archivo_viejo)}",
        f"Archivo Nuevo: {os.path.basename(archivo_nuevo)}",
    ]
    resultado, reporte_path = run_comparison(
        archivo_viejo,
        archivo_nuevo,
        output_dir,
        "reporte_comparacion",
        metadata_lines,
    )

    print("\n" + "=" * 70)
    print("RESULTADO DE LA COMPARACION")
    print("=" * 70)
    print(resultado)
    print("=" * 70)
    print(f"Reporte guardado: {reporte_path}")
    print("=" * 70)


def modo_manual(categories):
    """Modo de selección manual de archivos."""
    print("\n" + "=" * 70)
    print("MODO: COMPARACION MANUAL")
    print("=" * 70)

    current_directory = os.path.dirname(os.path.abspath(__file__))
    output_dir = get_output_dir(current_directory)
    excel_files = get_supported_excel_files(current_directory, recursive=True)

    if len(excel_files) < 2:
        print(f"\nSe encontraron solo {len(excel_files)} archivo(s) .xls/.xlsx")
        print("Se necesitan al menos 2 archivos para comparar")
        return

    print(f"\nArchivos .xls/.xlsx encontrados ({len(excel_files)}):\n")

    for i, file in enumerate(excel_files, 1):
        rel_path = os.path.relpath(file, current_directory)
        info = extract_file_info(file)
        if info:
            category, subcategory = detect_file_category(info["prefix"], categories)
            print(f"   {i:2d}. {rel_path}")
            print(f"       {category} - {subcategory} | {info['date']} {info['time']}")
        else:
            print(f"   {i:2d}. {rel_path}")

    print("\n" + "-" * 70)

    try:
        idx1 = int(input("Numero del archivo VIEJO: ").strip()) - 1
    except ValueError:
        print("Debes ingresar un numero para el archivo VIEJO")
        return

    try:
        idx2 = int(input("Numero del archivo NUEVO: ").strip()) - 1
    except ValueError:
        print("Debes ingresar un numero para el archivo NUEVO")
        return

    if idx1 < 0 or idx1 >= len(excel_files) or idx2 < 0 or idx2 >= len(excel_files):
        print("Numeros invalidos")
        return

    if idx1 == idx2:
        print("Debes seleccionar archivos diferentes")
        return

    archivo_viejo = excel_files[idx1]
    archivo_nuevo = excel_files[idx2]

    print("\nComparando:")
    print(f"   Viejo: {os.path.basename(archivo_viejo)}")
    print(f"   Nuevo: {os.path.basename(archivo_nuevo)}")

    metadata_lines = [
        f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Archivo Viejo: {os.path.basename(archivo_viejo)}",
        f"Archivo Nuevo: {os.path.basename(archivo_nuevo)}",
    ]
    resultado, reporte_path = run_comparison(
        archivo_viejo,
        archivo_nuevo,
        output_dir,
        "reporte_manual",
        metadata_lines,
    )

    print("\n" + "=" * 70)
    print("RESULTADO DE LA COMPARACION")
    print("=" * 70)
    print(resultado)
    print("=" * 70)
    print(f"Reporte guardado: {reporte_path}")
    print("=" * 70)


def ver_inventario(categories):
    """Muestra un inventario de todos los archivos disponibles."""
    print("\n" + "=" * 70)
    print("INVENTARIO DE ARCHIVOS")
    print("=" * 70)

    current_directory = os.path.dirname(os.path.abspath(__file__))
    excel_files = get_supported_excel_files(current_directory, recursive=True)

    if not excel_files:
        print("\nNo se encontraron archivos .xls/.xlsx")
        return

    grupos = group_files_by_prefix(excel_files)

    categorias = {}
    for prefix, files in grupos.items():
        category, subcategory = detect_file_category(prefix, categories)
        categorias.setdefault(category, {})
        categorias[category].setdefault(subcategory, [])
        categorias[category][subcategory].extend(files)

    for category in sorted(categorias.keys()):
        print(f"\n{category}")
        print("-" * 70)

        for subcategory in sorted(categorias[category].keys()):
            files = categorias[category][subcategory]
            files.sort(key=lambda item: item["datetime"], reverse=True)

            print(f"\n   {subcategory} ({len(files)} archivo(s)):")
            for file_info in files:
                rel_path = os.path.relpath(file_info["fullpath"], current_directory)
                folder = os.path.dirname(rel_path) or "."
                print(f"      - {file_info['filename']}")
                print(f"        {file_info['date']} {file_info['time']} | {folder}")

    print("\n" + "=" * 70)
    print(f"Total de archivos: {len(excel_files)}")
    print("=" * 70)


# ============================================================================
# PROGRAMA PRINCIPAL
# ============================================================================

def main():
    """Función principal del programa."""
    current_directory = os.path.dirname(os.path.abspath(__file__))
    categories = load_categories(os.path.join(current_directory, "categorias.json"))

    while True:
        choice = show_menu()

        if choice == "1":
            modo_carpetas(categories)
        elif choice == "2":
            modo_automatico()
        elif choice == "3":
            modo_manual(categories)
        elif choice == "4":
            ver_inventario(categories)
        elif choice == "0":
            print("\nHasta luego")
            print("=" * 70)
            break
        else:
            print("\nOpcion invalida. Selecciona una opcion valida.")

        if choice in ["1", "2", "3", "4"]:
            input("\nPresiona ENTER para volver al menu...")


if __name__ == "__main__":
    main()
