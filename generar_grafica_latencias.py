#!/usr/bin/env python3
"""
Script para generar gráfica de tendencia diaria de latencias
Usa el archivo muestra_langfuse.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

print("="*80)
print("GENERANDO GRÁFICA DE TENDENCIA DIARIA DE LATENCIAS")
print("="*80)

# Cargar datos
CSV_FILE = 'muestra_langfuse.csv'
print(f"\n📂 Cargando archivo: {CSV_FILE}")

df = pd.read_csv(CSV_FILE)
print(f"✅ Datos cargados: {len(df)} registros")

# Procesar timestamps
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date

# Filtrar registros con latencia válida
df_clean = df[df['latency'].notna()].copy()
print(f"📊 Registros con latencia válida: {len(df_clean)}")

# Calcular estadísticas diarias por node_type
daily_stats = df_clean.groupby(['date', 'node_type'])['latency'].agg([
    ('count', 'count'),
    ('mean', 'mean'),
    ('median', 'median'),
    ('p95', lambda x: x.quantile(0.95)),
    ('min', 'min'),
    ('max', 'max')
]).reset_index()

print(f"\n📅 Días con datos: {daily_stats['date'].nunique()}")
print(f"🏷️  Tipos de nodo: {daily_stats['node_type'].unique()}")

# ========================================
# GRÁFICA: Tendencia Diaria de Latencias
# ========================================

fig, axes = plt.subplots(3, 1, figsize=(16, 14))

# Convertir date a datetime para mejor visualización
daily_stats['date'] = pd.to_datetime(daily_stats['date'])

# ========================================
# GRÁFICA 1: Latencia Media por Node Type
# ========================================
ax1 = axes[0]

for node_type in daily_stats['node_type'].unique():
    data = daily_stats[daily_stats['node_type'] == node_type]
    ax1.plot(data['date'], data['mean'], marker='o', linewidth=2,
             label=node_type, markersize=8)

ax1.set_xlabel('Fecha', fontsize=12, fontweight='bold')
ax1.set_ylabel('Latencia Media (segundos)', fontsize=12, fontweight='bold')
ax1.set_title('Tendencia Diaria de Latencia Media por Tipo de Nodo',
              fontsize=14, fontweight='bold', pad=15)
ax1.legend(fontsize=10, loc='best')
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.tick_params(axis='x', rotation=45)

# ========================================
# GRÁFICA 2: Percentil 95 por Node Type
# ========================================
ax2 = axes[1]

for node_type in daily_stats['node_type'].unique():
    data = daily_stats[daily_stats['node_type'] == node_type]
    ax2.plot(data['date'], data['p95'], marker='s', linewidth=2,
             label=node_type, markersize=8, linestyle='--')

ax2.set_xlabel('Fecha', fontsize=12, fontweight='bold')
ax2.set_ylabel('Latencia P95 (segundos)', fontsize=12, fontweight='bold')
ax2.set_title('Tendencia Diaria de Latencia P95 por Tipo de Nodo',
              fontsize=14, fontweight='bold', pad=15)
ax2.legend(fontsize=10, loc='best')
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.tick_params(axis='x', rotation=45)

# Línea de referencia en 3 segundos (umbral típico de SLA)
ax2.axhline(y=3.0, color='red', linestyle=':', linewidth=2, alpha=0.7,
            label='Umbral SLA (3s)')

# ========================================
# GRÁFICA 3: Volumen de Llamadas Diarias
# ========================================
ax3 = axes[2]

# Agrupar por fecha y node_type
volume_data = df_clean.groupby(['date', 'node_type']).size().reset_index(name='count')
volume_data['date'] = pd.to_datetime(volume_data['date'])

# Crear gráfico de barras apiladas
pivot_volume = volume_data.pivot(index='date', columns='node_type', values='count').fillna(0)
pivot_volume.plot(kind='bar', stacked=True, ax=ax3, width=0.7, alpha=0.8)

ax3.set_xlabel('Fecha', fontsize=12, fontweight='bold')
ax3.set_ylabel('Número de Llamadas', fontsize=12, fontweight='bold')
ax3.set_title('Volumen Diario de Llamadas por Tipo de Nodo',
              fontsize=14, fontweight='bold', pad=15)
ax3.legend(fontsize=10, loc='best', title='Tipo de Nodo')
ax3.grid(True, alpha=0.3, linestyle='--', axis='y')
ax3.tick_params(axis='x', rotation=45)

# Ajustar formato de fechas en eje X
ax3.set_xticklabels([d.strftime('%Y-%m-%d') for d in pivot_volume.index])

plt.tight_layout()

# Guardar gráfica
output_file = 'tendencia_latencias_diaria.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✅ Gráfica guardada: {output_file}")

plt.show()

# ========================================
# RESUMEN EN CONSOLA
# ========================================
print("\n" + "="*80)
print("RESUMEN ESTADÍSTICO POR TIPO DE NODO")
print("="*80)

for node_type in df_clean['node_type'].unique():
    data = df_clean[df_clean['node_type'] == node_type]
    print(f"\n📌 {node_type}:")
    print(f"   Llamadas: {len(data):,}")
    print(f"   Latencia Media: {data['latency'].mean():.3f}s")
    print(f"   Latencia Mediana: {data['latency'].median():.3f}s")
    print(f"   Latencia P95: {data['latency'].quantile(0.95):.3f}s")
    print(f"   Rango: [{data['latency'].min():.3f}s - {data['latency'].max():.3f}s]")

print("\n" + "="*80)
print("✅ ANÁLISIS COMPLETADO")
print("="*80)
