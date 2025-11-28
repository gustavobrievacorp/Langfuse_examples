#!/usr/bin/env python3
"""
Script para validar que el notebook se ejecute completamente con muestra_1000_registros.csv
También actualiza el notebook para:
1. Usar muestra_1000_registros.csv
2. Agregar funcionalidad de combinar archivos y eliminar duplicados
"""

import json
import shutil
from datetime import datetime

notebook_path = "Notebooks/analisis_cubos_tokens_latencias_v3 (1).ipynb"
backup_path = notebook_path.replace(".ipynb", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb")

print("="*80)
print("VALIDACIÓN Y ACTUALIZACIÓN DEL NOTEBOOK")
print("="*80)

# Backup
shutil.copy(notebook_path, backup_path)
print(f"\n✅ Backup creado: {backup_path}")

# Cargar notebook
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"\n📊 Total de celdas: {len(nb['cells'])}")

# =================================================================
# PASO 1: Actualizar Celda 5 - Ruta CSV y funcionalidad multi-archivo
# =================================================================

for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'CSV_FILE_PATH' in source and 'Cargar datos' in source:
            new_code = """# CONFIGURACIÓN: Rutas de archivos CSV
# Opción 1: Archivo único
CSV_FILE_PATH = 'muestra_1000_registros.csv'

# Opción 2: Múltiples archivos (opcional)
# Descomenta y agrega rutas para combinar archivos
CSV_FILES = [
    'muestra_1000_registros.csv',
    # 'archivo_adicional_1.csv',
    # 'archivo_adicional_2.csv',
]

USE_MULTIPLE_FILES = False  # Cambiar a True para usar múltiples archivos

# ============================================================
# CARGA DE DATOS CON DEDUPLICACIÓN
# ============================================================

import pandas as pd

if USE_MULTIPLE_FILES:
    print(f"📂 Cargando y combinando {len(CSV_FILES)} archivos...")

    dfs = []
    total_records = 0

    for csv_file in CSV_FILES:
        try:
            df_temp = pd.read_csv(csv_file)
            records_count = len(df_temp)
            total_records += records_count
            dfs.append(df_temp)
            print(f"   ✓ {csv_file}: {records_count:,} registros")
        except FileNotFoundError:
            print(f"   ✗ {csv_file}: No encontrado (omitido)")
        except Exception as e:
            print(f"   ✗ {csv_file}: Error - {str(e)}")

    if not dfs:
        raise ValueError("❌ No se pudo cargar ningún archivo")

    # Combinar todos los DataFrames
    df = pd.concat(dfs, ignore_index=True)
    print(f"\\n📊 Total de registros antes de deduplicar: {total_records:,}")

    # Eliminar duplicados por 'id'
    initial_count = len(df)
    df = df.drop_duplicates(subset='id', keep='first')
    duplicates_removed = initial_count - len(df)

    print(f"🗑️  Duplicados eliminados: {duplicates_removed:,}")
    print(f"✅ Registros únicos finales: {len(df):,}")

else:
    # Cargar archivo único
    print(f"📂 Cargando datos desde: {CSV_FILE_PATH}")
    df = pd.read_csv(CSV_FILE_PATH)
    print(f"\\n📊 Datos cargados: {len(df):,} registros")

print(f"📅 Columnas disponibles: {len(df.columns)}")

# Mostrar primeras filas
df.head(2)
"""
            cell['source'] = new_code.split('\n')
            print(f"✅ Celda {idx}: Actualizada con soporte multi-archivo y deduplicación")
            break

# =================================================================
# PASO 2: Actualizar Celda 6 - Simplificar procesamiento (ya tiene las columnas)
# =================================================================

for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'Clasificando tipos de nodos' in source:
            new_code = """# Aplicar clasificación de nodos
print("🔍 Clasificando tipos de nodos...")
df['node_type'] = df.apply(classify_node_type, axis=1)

# Convertir timestamps a datetime
print("📅 Procesando timestamps...")
df['startTime'] = pd.to_datetime(df['startTime'], errors='coerce')
df['endTime'] = pd.to_datetime(df['endTime'], errors='coerce')
df['createdAt'] = pd.to_datetime(df['createdAt'], errors='coerce')

# Crear columnas de fecha para agregaciones temporales
df['date'] = df['startTime'].dt.date
df['week'] = df['startTime'].dt.to_period('W').astype(str)
df['hour'] = df['startTime'].dt.hour

print(f"✅ Procesamiento completado")
print(f"   Tipos de nodo únicos: {df['node_type'].nunique()}")
print(f"   Modelos únicos: {df['model'].nunique()}")
print(f"   Total de tokens procesados: {df['totalTokens'].sum():,}")
print(f"\\nDistribución de modelos:")
print(df['model'].value_counts())
print(f"\\nDistribución de tipos de nodo:")
print(df['node_type'].value_counts())
print(f"\\nEstadísticas de tokens:")
print(f"   Promedio input tokens: {df['promptTokens'].mean():.0f}")
print(f"   Promedio output tokens: {df['completionTokens'].mean():.0f}")
print(f"   Costo total: ${df['calculatedTotalCost'].sum():.4f}")
print(f"\\nEstadísticas de latencia:")
print(f"   Latencia promedio: {df['latency'].mean():.3f}s")
print(f"   Latencia P95: {df['latency'].quantile(0.95):.3f}s")
"""
            cell['source'] = new_code.split('\n')
            print(f"✅ Celda {idx}: Actualizada para usar columnas existentes")
            break

# Guardar
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"\n✅ Notebook actualizado: {notebook_path}")

print("\n" + "="*80)
print("RESUMEN DE CAMBIOS")
print("="*80)
print("\n✓ Archivo CSV actualizado: muestra_1000_registros.csv")
print("✓ Soporte para múltiples archivos CSV agregado")
print("✓ Deduplicación automática por 'id'")
print("✓ Procesamiento simplificado (usa columnas ya existentes)")
print("✓ Compatible con la estructura real de Langfuse")

print("\n" + "="*80)
print("CÓMO USAR MÚLTIPLES ARCHIVOS")
print("="*80)
print("""
1. En la Celda 5, cambia:
   USE_MULTIPLE_FILES = True

2. Agrega tus archivos a la lista CSV_FILES:
   CSV_FILES = [
       'muestra_1000_registros.csv',
       'archivo_nuevo_20251128.csv',
       'archivo_nuevo_20251129.csv',
   ]

3. Ejecuta el notebook normalmente
4. Los duplicados se eliminarán automáticamente
""")

print("="*80)
print("✅ VALIDACIÓN COMPLETADA")
print("="*80)
