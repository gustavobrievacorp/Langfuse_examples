#!/usr/bin/env python3
"""
Script para adaptar el notebook a la estructura real de muestra_langfuse.csv
"""

import json
import re
from datetime import datetime

notebook_path = "Notebooks/analisis_cubos_tokens_latencias_v3 (1).ipynb"
backup_path = notebook_path.replace(".ipynb", f"_before_adapt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb")

print("="*80)
print("ADAPTANDO NOTEBOOK A ESTRUCTURA REAL DE DATOS")
print("="*80)

# Crear backup
import shutil
shutil.copy(notebook_path, backup_path)
print(f"\n✅ Backup creado: {backup_path}")

# Cargar notebook
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"\n📊 Total de celdas: {len(nb['cells'])}")

# Función para adaptar el código de una celda
def adapt_cell_code(source_lines):
    """Adapta el código de una celda a la nueva estructura"""
    adapted = []

    for line in source_lines:
        # Reemplazar startTime por timestamp
        line = line.replace("df['startTime']", "df['timestamp']")
        line = line.replace('df["startTime"]', 'df["timestamp"]')
        line = line.replace("'startTime'", "'timestamp'")
        line = line.replace('"startTime"', '"timestamp"')

        # Reemplazar endTime por timestamp (usamos el mismo)
        line = line.replace("df['endTime']", "df['timestamp']")
        line = line.replace('df["endTime"]', 'df["timestamp"]')

        adapted.append(line)

    return adapted

# Contar celdas modificadas
modified_count = 0

# Adaptar cada celda de código
for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = cell['source'] if isinstance(cell['source'], list) else [cell['source']]
        original_source = ''.join(source)

        # Solo adaptar si contiene las palabras clave
        if 'startTime' in original_source or 'endTime' in original_source:
            adapted_source = adapt_cell_code(source)
            cell['source'] = adapted_source
            modified_count += 1
            print(f"  ✓ Celda {idx} adaptada")

print(f"\n✅ Total de celdas modificadas: {modified_count}")

# Modificaciones específicas

# CELDA 5: Cambiar ruta del CSV
for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'CSV_FILE_PATH' in source and 'langfuse_generations_CONSOLIDADO' in source:
            new_source = source.replace(
                "CSV_FILE_PATH = 'data/langfuse_generations_CONSOLIDADO_20251113_125037.csv'",
                "CSV_FILE_PATH = 'muestra_langfuse.csv'"
            )
            cell['source'] = new_source.split('\n')
            print(f"\n✅ Celda {idx}: Ruta CSV actualizada a 'muestra_langfuse.csv'")
            break

# CELDA 6: Agregar extracción de modelo
for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'Clasificando tipos de nodos' in source:
            # Agregar código para extraer modelo
            new_code = """# Aplicar clasificación de nodos
print("🔍 Clasificando tipos de nodos...")
df['node_type'] = df.apply(classify_node_type, axis=1)

# Convertir timestamps a datetime
print("📅 Procesando timestamps...")
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df['createdAt'] = pd.to_datetime(df['createdAt'], errors='coerce')

# Crear columnas de fecha para agregaciones temporales
df['date'] = df['timestamp'].dt.date
df['week'] = df['timestamp'].dt.to_period('W').astype(str)
df['hour'] = df['timestamp'].dt.hour

# Extraer modelo desde el campo 'output'
print("🔍 Extrayendo información de modelos...")

def extract_model_from_output(output_str):
    \"\"\"Extrae el nombre del modelo desde el campo output\"\"\"
    if pd.isna(output_str):
        return 'UNKNOWN'
    try:
        import re
        match = re.search(r"'model_name':\\s*'([^']+)'", str(output_str))
        if match:
            return match.group(1)
    except:
        pass
    return 'UNKNOWN'

df['model'] = df['output'].apply(extract_model_from_output)

print(f"✅ Procesamiento completado")
print(f"   Tipos de nodo únicos: {df['node_type'].nunique()}")
print(f"   Modelos únicos: {df['model'].nunique()}")
print(f"\\nDistribución de modelos:")
print(df['model'].value_counts())
"""
            cell['source'] = new_code.split('\n')
            print(f"✅ Celda {idx}: Agregada extracción de modelo")
            break

# Guardar notebook adaptado
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"\n✅ Notebook adaptado guardado: {notebook_path}")
print("\n" + "="*80)
print("RESUMEN DE CAMBIOS")
print("="*80)
print("\n✓ Todas las referencias a 'startTime' → 'timestamp'")
print("✓ Todas las referencias a 'endTime' → 'timestamp'")
print("✓ Ruta CSV → 'muestra_langfuse.csv'")
print("✓ Agregada extracción de modelo desde 'output'")
print(f"✓ Total de celdas modificadas: {modified_count + 2}")

print("\n" + "="*80)
print("✅ ADAPTACIÓN COMPLETADA")
print("="*80)
