import pandas as pd
import os
import glob

def compare_excel_files(file1, file2):
    try:
        # Leer ambos archivos Excel usando xlrd
        excel1 = pd.ExcelFile(file1, engine='xlrd')
        excel2 = pd.ExcelFile(file2, engine='xlrd')
    except FileNotFoundError as e:
        return f"❌ Error: {e}"

    # Comparar las hojas (sheets)
    sheets1 = excel1.sheet_names
    sheets2 = excel2.sheet_names

    report = ""
    total_differences = 0

    # 1. COMPARACIÓN DE HOJAS
    report += "📋 COMPARACIÓN DE HOJAS\n"
    report += "─" * 50 + "\n"
    
    if sheets1 != sheets2:
        total_differences += 1
        report += "❌ LAS HOJAS SON DIFERENTES\n\n"
        
        # Hojas únicas en cada archivo
        sheets_only_in_1 = set(sheets1) - set(sheets2)
        sheets_only_in_2 = set(sheets2) - set(sheets1)
        common_sheets = set(sheets1) & set(sheets2)
        
        if sheets_only_in_1:
            report += f"   📄 Hojas solo en Archivo 1: {list(sheets_only_in_1)}\n"
        if sheets_only_in_2:
            report += f"   📄 Hojas solo en Archivo 2: {list(sheets_only_in_2)}\n"
        if common_sheets:
            report += f"   📄 Hojas comunes: {list(common_sheets)}\n"
        report += "\n"
        
        # Solo comparar hojas comunes
        sheets_to_compare = list(common_sheets)
    else:
        report += f"✅ AMBOS ARCHIVOS TIENEN LAS MISMAS HOJAS ({len(sheets1)} hojas)\n"
        report += f"   📄 Hojas: {sheets1}\n\n"
        sheets_to_compare = sheets1

    # 2. COMPARACIÓN DETALLADA DE CADA HOJA
    if sheets_to_compare:
        report += "📊 COMPARACIÓN DETALLADA POR HOJA\n"
        report += "═" * 50 + "\n\n"
        
        for i, sheet in enumerate(sheets_to_compare, 1):
            report += f"🔍 HOJA {i}: '{sheet}'\n"
            report += "─" * 30 + "\n"
            
            try:
                df1 = pd.read_excel(file1, sheet_name=sheet, engine='xlrd')
                df2 = pd.read_excel(file2, sheet_name=sheet, engine='xlrd')
                
                # Información básica
                report += f"   📏 Dimensiones:\n"
                report += f"      • Archivo 1: {df1.shape[0]} filas × {df1.shape[1]} columnas\n"
                report += f"      • Archivo 2: {df2.shape[0]} filas × {df2.shape[1]} columnas\n"
                
                if df1.shape != df2.shape:
                    report += "      ⚠️  Las dimensiones son diferentes\n"
                else:
                    report += "      ✅ Las dimensiones son iguales\n"
                report += "\n"
                
                # Comparar columnas
                cols1 = df1.columns.tolist()
                cols2 = df2.columns.tolist()
                
                report += f"   📋 Columnas:\n"
                if cols1 != cols2:
                    total_differences += 1
                    report += "      ❌ LAS COLUMNAS SON DIFERENTES\n"
                    
                    cols_only_in_1 = [col for col in cols1 if col not in cols2]
                    cols_only_in_2 = [col for col in cols2 if col not in cols1]
                    common_cols = [col for col in cols1 if col in cols2]
                    
                    if cols_only_in_1:
                        report += f"         • Solo en Archivo 1: {cols_only_in_1}\n"
                    if cols_only_in_2:
                        report += f"         • Solo en Archivo 2: {cols_only_in_2}\n"
                    if common_cols:
                        report += f"         • Columnas comunes: {len(common_cols)} de {max(len(cols1), len(cols2))}\n"
                else:
                    report += f"      ✅ COLUMNAS IDÉNTICAS ({len(cols1)} columnas)\n"
                    report += f"         {cols1}\n"
                    
                    # Solo comparar tipos de datos si las columnas son iguales
                    dtypes1 = df1.dtypes.tolist()
                    dtypes2 = df2.dtypes.tolist()
                    
                    report += "\n   🔧 Tipos de datos:\n"
                    if dtypes1 != dtypes2:
                        total_differences += 1
                        report += "      ❌ ALGUNOS TIPOS DE DATOS SON DIFERENTES\n"
                        different_types = []
                        for col, dtype1, dtype2 in zip(cols1, dtypes1, dtypes2):
                            if dtype1 != dtype2:
                                different_types.append(f"'{col}': {dtype1} → {dtype2}")
                        
                        if different_types:
                            report += "         Diferencias encontradas:\n"
                            for diff in different_types:
                                report += f"         • {diff}\n"
                    else:
                        report += "      ✅ TODOS LOS TIPOS DE DATOS SON IGUALES\n"
                
            except Exception as e:
                report += f"      ❌ Error al procesar la hoja: {e}\n"
            
            report += "\n"
    
    # 3. RESUMEN FINAL
    report += "📋 RESUMEN FINAL\n"
    report += "═" * 50 + "\n"
    if total_differences == 0:
        report += "🎉 LOS ARCHIVOS SON ESTRUCTURALMENTE IDÉNTICOS\n"
        report += "   ✅ Mismas hojas\n"
        report += "   ✅ Mismas columnas en cada hoja\n"
        report += "   ✅ Mismos tipos de datos\n"
    else:
        report += f"⚠️  SE ENCONTRARON {total_differences} DIFERENCIA(S) ESTRUCTURAL(ES)\n"
        report += "   ℹ️  Los archivos tienen estructuras diferentes\n"
    
    report += "\n💡 NOTA: Esta comparación analiza solo la estructura (hojas, columnas, tipos de datos).\n"
    report += "   Para comparar el contenido de los datos, se requiere un análisis adicional.\n"

    return report

# Obtener la ruta actual del script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Buscar todos los archivos .xls en la carpeta actual
xls_files = glob.glob(os.path.join(current_directory, "*.xls"))

# Verificar que hay exactamente 2 archivos .xls
if len(xls_files) < 2:
    print("❌ ERROR: No se encontraron suficientes archivos")
    print("="*50)
    print(f"📊 Archivos .xls encontrados: {len(xls_files)}")
    print("🎯 Se necesitan exactamente 2 archivos .xls para comparar")
    print()
    
    if len(xls_files) == 1:
        print(f"📄 Archivo encontrado: {os.path.basename(xls_files[0])}")
        print("💡 Agrega otro archivo .xls a la carpeta")
    elif len(xls_files) == 0:
        print("📁 No se encontraron archivos .xls en la carpeta actual")
        print("💡 Coloca 2 archivos .xls en la misma carpeta que este script")
    
    print("\n⚠️  Verifica que:")
    print("   • Los archivos tengan extensión .xls (no .xlsx)")
    print("   • Estén en la misma carpeta que el script")
    print("   • No estén dañados o protegidos")
    exit()

elif len(xls_files) > 2:
    print("❌ ERROR: Demasiados archivos .xls")
    print("="*50)
    print(f"📊 Se encontraron {len(xls_files)} archivos .xls:")
    for i, file in enumerate(xls_files, 1):
        print(f"   {i}. {os.path.basename(file)}")
    print()
    print("🎯 Se necesitan exactamente 2 archivos .xls para comparar")
    print("💡 Mueve los archivos extra a otra carpeta, dejando solo 2")
    exit()

# Si hay exactamente 2 archivos, proceder con la comparación
file1 = xls_files[0]
file2 = xls_files[1]

print("\n" + "="*70)
print("🔍 COMPARADOR DE ARCHIVOS EXCEL")
print("="*70)
print(f"📁 Comparando archivos:")
print(f"   📄 Archivo 1: {os.path.basename(file1)}")
print(f"   📄 Archivo 2: {os.path.basename(file2)}")
print("="*70)

# Realizar la comparación
print("\n🔄 Analizando archivos...")
resultado = compare_excel_files(file1, file2)

# Mostrar el reporte por pantalla
print("\n" + "="*70)
print("📊 RESULTADO DE LA COMPARACIÓN")
print("="*70)
print(resultado)

# Guardar el reporte en un archivo de texto
reporte_filename = 'reporte_comparacion.txt'
print("="*70)
print("💾 GUARDANDO REPORTE...")

# Crear encabezado más detallado para el archivo
header = f"""🔍 REPORTE DE COMPARACIÓN DE ARCHIVOS EXCEL
═══════════════════════════════════════════════════════════════════════

📅 Fecha del análisis: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
📁 Directorio: {current_directory}
📄 Archivo 1: {os.path.basename(file1)}
📄 Archivo 2: {os.path.basename(file2)}

═══════════════════════════════════════════════════════════════════════

"""

with open(reporte_filename, 'w', encoding='utf-8') as f:
    f.write(header)
    f.write(resultado)

print(f"✅ Reporte guardado exitosamente en: '{reporte_filename}'")
print(f"📍 Ubicación: {os.path.join(current_directory, reporte_filename)}")
print("\n🎯 ¡Análisis completado!")
print("="*70)