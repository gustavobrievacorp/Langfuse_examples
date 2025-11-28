#!/usr/bin/env python3
"""
Análisis detallado de GPT-4.1 Mini - Última Semana
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from datetime import datetime, timedelta

print("="*80)
print("ANÁLISIS DETALLADO: GPT-4.1 MINI - ÚLTIMA SEMANA")
print("="*80)

# Cargar datos
CSV_FILE = 'muestra_langfuse.csv'
df = pd.read_csv(CSV_FILE)

# Procesar timestamps
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date
df['datetime'] = df['timestamp']
df['hour'] = df['timestamp'].dt.hour

# Extraer modelo desde output
def extract_model_from_output(output_str):
    if pd.isna(output_str):
        return None
    try:
        match = re.search(r"'model_name':\s*'([^']+)'", str(output_str))
        if match:
            return match.group(1)
    except:
        pass
    return None

df['model'] = df['output'].apply(extract_model_from_output)

# Filtrar GPT-4.1 Mini
mini_filter = df['model'].notna() & df['model'].str.contains('mini', case=False, na=False)
df_mini = df[mini_filter].copy()

print(f"\n📊 Total de llamadas GPT-4.1 Mini: {len(df_mini)}")
print(f"📅 Período analizado:")
print(f"   Desde: {df_mini['timestamp'].min()}")
print(f"   Hasta: {df_mini['timestamp'].max()}")

# Estadísticas de latencia
print("\n" + "="*80)
print("📈 ESTADÍSTICAS DE LATENCIA")
print("="*80)
print(f"\n   Latencia Mínima:  {df_mini['latency'].min():.3f}s")
print(f"   Latencia Máxima:  {df_mini['latency'].max():.3f}s")
print(f"   Latencia Media:   {df_mini['latency'].mean():.3f}s")
print(f"   Latencia Mediana: {df_mini['latency'].median():.3f}s")
print(f"   Percentil 75:     {df_mini['latency'].quantile(0.75):.3f}s")
print(f"   Percentil 90:     {df_mini['latency'].quantile(0.90):.3f}s")
print(f"   Percentil 95:     {df_mini['latency'].quantile(0.95):.3f}s")
print(f"   Percentil 99:     {df_mini['latency'].quantile(0.99):.3f}s")
print(f"   Desviación Std:   {df_mini['latency'].std():.3f}s")

# Agregación por día
daily_stats = df_mini.groupby('date')['latency'].agg([
    ('count', 'count'),
    ('mean', 'mean'),
    ('median', 'median'),
    ('p95', lambda x: x.quantile(0.95)),
    ('min', 'min'),
    ('max', 'max')
]).reset_index()

print("\n" + "="*80)
print("📅 ESTADÍSTICAS DIARIAS")
print("="*80)
for _, row in daily_stats.iterrows():
    print(f"\n{row['date']}:")
    print(f"   Llamadas: {int(row['count']):,}")
    print(f"   Media:    {row['mean']:.3f}s")
    print(f"   Mediana:  {row['median']:.3f}s")
    print(f"   P95:      {row['p95']:.3f}s")
    print(f"   Rango:    [{row['min']:.3f}s - {row['max']:.3f}s]")

# Agregación por hora del día
hourly_stats = df_mini.groupby('hour')['latency'].agg([
    ('count', 'count'),
    ('mean', 'mean'),
    ('p95', lambda x: x.quantile(0.95))
]).reset_index()

print("\n" + "="*80)
print("⏰ ESTADÍSTICAS POR HORA DEL DÍA")
print("="*80)
for _, row in hourly_stats.iterrows():
    print(f"{int(row['hour']):02d}:00 | Llamadas: {int(row['count']):3} | "
          f"Media: {row['mean']:.3f}s | P95: {row['p95']:.3f}s")

# ========================================
# GRÁFICAS
# ========================================

fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# ========================================
# GRÁFICA 1: Serie Temporal Completa
# ========================================
ax1 = fig.add_subplot(gs[0, :])

ax1.scatter(df_mini['datetime'], df_mini['latency'], alpha=0.6, s=50, c='#3498db')
ax1.plot(df_mini['datetime'], df_mini['latency'].rolling(window=5).mean(),
         color='red', linewidth=2, label='Media Móvil (5 llamadas)')

# Línea de P95
p95_value = df_mini['latency'].quantile(0.95)
ax1.axhline(y=p95_value, color='orange', linestyle='--', linewidth=2,
            label=f'P95: {p95_value:.3f}s')

ax1.set_xlabel('Timestamp', fontsize=12, fontweight='bold')
ax1.set_ylabel('Latencia (segundos)', fontsize=12, fontweight='bold')
ax1.set_title('GPT-4.1 Mini: Serie Temporal de Latencias\n(Última Semana)',
              fontsize=14, fontweight='bold', pad=15)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# ========================================
# GRÁFICA 2: Distribución (Histograma)
# ========================================
ax2 = fig.add_subplot(gs[1, 0])

ax2.hist(df_mini['latency'], bins=20, color='#2ecc71', alpha=0.7, edgecolor='black')
ax2.axvline(df_mini['latency'].mean(), color='red', linestyle='--', linewidth=2,
            label=f"Media: {df_mini['latency'].mean():.3f}s")
ax2.axvline(df_mini['latency'].median(), color='blue', linestyle='--', linewidth=2,
            label=f"Mediana: {df_mini['latency'].median():.3f}s")
ax2.axvline(p95_value, color='orange', linestyle='--', linewidth=2,
            label=f"P95: {p95_value:.3f}s")

ax2.set_xlabel('Latencia (segundos)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Frecuencia', fontsize=11, fontweight='bold')
ax2.set_title('Distribución de Latencias', fontsize=12, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3, axis='y')

# ========================================
# GRÁFICA 3: Box Plot
# ========================================
ax3 = fig.add_subplot(gs[1, 1])

box_data = [df_mini['latency']]
bp = ax3.boxplot(box_data, vert=True, patch_artist=True, widths=0.5)
bp['boxes'][0].set_facecolor('#3498db')
bp['boxes'][0].set_alpha(0.7)

# Agregar puntos individuales
y = df_mini['latency']
x = [1] * len(y)
ax3.scatter(x, y, alpha=0.3, s=30, c='red')

ax3.set_ylabel('Latencia (segundos)', fontsize=11, fontweight='bold')
ax3.set_title('Diagrama de Caja (Box Plot)', fontsize=12, fontweight='bold')
ax3.set_xticklabels(['GPT-4.1 Mini'])
ax3.grid(True, alpha=0.3, axis='y')

# ========================================
# GRÁFICA 4: Latencia por Día
# ========================================
ax4 = fig.add_subplot(gs[2, 0])

daily_stats['date'] = pd.to_datetime(daily_stats['date'])
x_pos = range(len(daily_stats))

ax4.bar(x_pos, daily_stats['mean'], alpha=0.7, color='#2ecc71', label='Media')
ax4.plot(x_pos, daily_stats['p95'], marker='o', color='red', linewidth=2,
         markersize=8, label='P95')

ax4.set_xlabel('Fecha', fontsize=11, fontweight='bold')
ax4.set_ylabel('Latencia (segundos)', fontsize=11, fontweight='bold')
ax4.set_title('Latencia Media y P95 por Día', fontsize=12, fontweight='bold')
ax4.set_xticks(x_pos)
ax4.set_xticklabels([d.strftime('%Y-%m-%d') for d in daily_stats['date']], rotation=45)
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3, axis='y')

# ========================================
# GRÁFICA 5: Latencia por Hora del Día
# ========================================
ax5 = fig.add_subplot(gs[2, 1])

ax5.bar(hourly_stats['hour'], hourly_stats['mean'], alpha=0.7, color='#9b59b6')
ax5.plot(hourly_stats['hour'], hourly_stats['p95'], marker='s', color='red',
         linewidth=2, markersize=6, label='P95')

ax5.set_xlabel('Hora del Día', fontsize=11, fontweight='bold')
ax5.set_ylabel('Latencia (segundos)', fontsize=11, fontweight='bold')
ax5.set_title('Latencia por Hora del Día', fontsize=12, fontweight='bold')
ax5.set_xticks(hourly_stats['hour'])
ax5.legend(fontsize=9)
ax5.grid(True, alpha=0.3, axis='y')

# Guardar
output_file = 'analisis_gpt41_mini_detallado.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✅ Gráfica guardada: {output_file}")

plt.show()

print("\n" + "="*80)
print("✅ ANÁLISIS COMPLETADO")
print("="*80)
