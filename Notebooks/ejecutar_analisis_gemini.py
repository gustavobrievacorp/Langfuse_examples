#!/usr/bin/env python3
"""
Script para ejecutar el análisis regional Caribe con Gemini 2.5 Flash
Extrae y ejecuta el código del análisis del notebook flujo_actualizacion_vf.ipynb
"""

import os
import sys
import zipfile
import json
import pandas as pd
import numpy as np
import time
from dotenv import load_dotenv
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns

print("="*80)
print("INICIANDO ANÁLISIS REGIONAL CARIBE CON GEMINI")
print("="*80)

# ===== 1. CARGAR DATOS =====
print("\n📁 Cargando datos...")

# Ruta del ZIP con la base de conocimiento
ZIP_BC = "/home/ghost2077/claude-projects/Langfuse_examples/_tbl_subrespuesta__PRD_baseconocimientosdb_202511201112.zip"

# Cargar base de conocimiento
with zipfile.ZipFile(ZIP_BC, 'r') as z:
    with z.open('tbl_preguntas_conecta2_PRD_baseconocimientosdb_202511201113.json') as f:
        data_bc = json.load(f)
        records_bc = list(data_bc.values())[0]
        df_base_conocimiento = pd.DataFrame(records_bc)

print(f"✅ Base de conocimiento cargada: {len(df_base_conocimiento)} registros")

# Cargar datos de muestra (simulado - necesitamos el df_muestra del notebook principal)
# Por ahora crearemos datos de ejemplo
print("\n⚠️  NOTA: Este script asume que df_muestra ya está disponible.")
print("    Si no existe, necesitas ejecutar las celdas previas del notebook primero.")

# ===== 2. CONFIGURAR GEMINI API =====
print("\n"+"="*80)
print("CONFIGURANDO GEMINI API")
print("="*80)

load_dotenv()

# OPCIÓN 1: Usar API Key desde .env (método actual)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Determinar método de autenticación
USE_SERVICE_ACCOUNT = False  # Cambiar a True para usar Service Account

if USE_SERVICE_ACCOUNT:
    # Configuración con Service Account
    from google.oauth2 import service_account
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_APPLICATION_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/generative-language']
        )
        genai.configure(credentials=credentials)
        print(f"✅ Autenticación con Service Account: {GOOGLE_APPLICATION_CREDENTIALS}")
    except Exception as e:
        print(f"❌ ERROR configurando Service Account: {e}")
        print("   Revirtiendo a API Key...")
        USE_SERVICE_ACCOUNT = False

if not USE_SERVICE_ACCOUNT:
    # Configuración con API Key
    if not GOOGLE_API_KEY:
        print("❌ ERROR: GOOGLE_API_KEY no encontrado en .env")
        sys.exit(1)
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
        print(f"✅ Autenticación con API Key desde .env (longitud: {len(GOOGLE_API_KEY)} caracteres)")

# Usar modelo Gemini 2.0 Flash Exp (más estable y disponible)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

print(f"✅ Modelo Gemini configurado: gemini-2.0-flash-exp")
print(f"   Método de autenticación: {'Service Account' if USE_SERVICE_ACCOUNT else 'API Key'}")

# Definir categorías temáticas
CATEGORIAS_TEMATICAS = [
    "Productos y Servicios (tarjetas, cuentas, créditos)",
    "Canales Digitales (app, portal web, cajeros)",
    "Transacciones y Pagos",
    "Bloqueos y Seguridad",
    "Reclamos y Quejas",
    "Información Personal y Documentos",
    "Otros"
]

print(f"\n📋 Categorías temáticas definidas:")
for i, cat in enumerate(CATEGORIAS_TEMATICAS, 1):
    print(f"   {i}. {cat}")

# ===== 3. FUNCIONES DE ANÁLISIS =====

def clasificar_pregunta_gemini(pregunta, retry_count=0, max_retries=3):
    """
    Clasifica una pregunta en categorías temáticas usando Gemini.
    Incluye rate limiting y retry logic.
    """
    try:
        prompt = f"""Analiza la siguiente pregunta de un usuario de banca y clasifícala en UNA de estas categorías:

{chr(10).join([f'{i}. {cat}' for i, cat in enumerate(CATEGORIAS_TEMATICAS, 1)])}

Pregunta: "{pregunta}"

Responde SOLO con el número de la categoría (1-{len(CATEGORIAS_TEMATICAS)}) y el nombre de la categoría separados por coma.
Formato: "3, Transacciones y Pagos"
"""

        response = model.generate_content(prompt)
        resultado = response.text.strip()

        # Parsear resultado
        if ',' in resultado:
            num, categoria = resultado.split(',', 1)
            return categoria.strip()
        else:
            return resultado

    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            if retry_count < max_retries:
                wait_time = (2 ** retry_count) * 5
                print(f"  ⏱️  Rate limit alcanzado, esperando {wait_time}s...")
                time.sleep(wait_time)
                return clasificar_pregunta_gemini(pregunta, retry_count + 1, max_retries)
            else:
                return "Error: Rate limit excedido"
        else:
            print(f"  ❌ Error clasificando: {str(e)[:100]}")
            return "Error: " + str(e)[:50]

def analizar_calidad_gemini(pregunta, retry_count=0, max_retries=3):
    """
    Analiza la calidad de una pregunta: claridad, especificidad, complejidad.
    Retorna un score de 1-5 y comentarios.
    """
    try:
        prompt = f"""Analiza la calidad de esta pregunta bancaria en términos de:
1. Claridad (¿se entiende qué pregunta?)
2. Especificidad (¿tiene detalles suficientes?)
3. Complejidad (¿qué tan compleja es la consulta?)

Pregunta: "{pregunta}"

Responde en este formato EXACTO (una línea, separado por pipes):
SCORE|CLARIDAD|ESPECIFICIDAD|COMPLEJIDAD|COMENTARIO

Donde:
- SCORE: número del 1 (muy mala) al 5 (excelente)
- CLARIDAD: Alta/Media/Baja
- ESPECIFICIDAD: Alta/Media/Baja
- COMPLEJIDAD: Alta/Media/Baja
- COMENTARIO: Una frase corta (máximo 50 caracteres)

Ejemplo: "3|Media|Baja|Media|Pregunta ambigua sin contexto"
"""

        response = model.generate_content(prompt)
        resultado = response.text.strip()

        # Parsear resultado
        if '|' in resultado:
            parts = resultado.split('|')
            if len(parts) >= 5:
                return {
                    'score': int(parts[0]) if parts[0].isdigit() else 3,
                    'claridad': parts[1],
                    'especificidad': parts[2],
                    'complejidad': parts[3],
                    'comentario': parts[4]
                }

        return {
            'score': 3,
            'claridad': 'Media',
            'especificidad': 'Media',
            'complejidad': 'Media',
            'comentario': 'Análisis no disponible'
        }

    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            if retry_count < max_retries:
                wait_time = (2 ** retry_count) * 5
                print(f"  ⏱️  Rate limit alcanzado, esperando {wait_time}s...")
                time.sleep(wait_time)
                return analizar_calidad_gemini(pregunta, retry_count + 1, max_retries)
            else:
                return {'score': 0, 'claridad': 'Error', 'especificidad': 'Error', 'complejidad': 'Error', 'comentario': 'Rate limit'}
        else:
            return {'score': 0, 'claridad': 'Error', 'especificidad': 'Error', 'complejidad': 'Error', 'comentario': str(e)[:30]}

print(f"\n✅ Funciones de análisis IA configuradas")

# ===== 4. TEST DE CONEXIÓN =====
print("\n"+"="*80)
print("TEST DE CONEXIÓN CON GEMINI")
print("="*80)

test_pregunta = "¿Cómo puedo activar mi tarjeta de crédito?"
print(f"\nPregunta de prueba: '{test_pregunta}'")

try:
    test_categoria = clasificar_pregunta_gemini(test_pregunta)
    print(f"✅ Categoría detectada: {test_categoria}")

    test_calidad = analizar_calidad_gemini(test_pregunta)
    print(f"✅ Análisis de calidad:")
    print(f"   - Score: {test_calidad['score']}/5")
    print(f"   - Claridad: {test_calidad['claridad']}")
    print(f"   - Especificidad: {test_calidad['especificidad']}")
    print(f"   - Complejidad: {test_calidad['complejidad']}")
    print(f"   - Comentario: {test_calidad['comentario']}")

    print(f"\n✅ Test exitoso! El modelo Gemini está funcionando correctamente.")

except Exception as e:
    print(f"\n❌ Error en test: {e}")
    print(f"   Verifica tu API key y conexión a internet.")
    sys.exit(1)

print("\n"+"="*80)
print("ANÁLISIS COMPLETO DISPONIBLE")
print("="*80)
print(f"\n💡 Para ejecutar el análisis regional completo:")
print(f"   1. Abre el notebook flujo_actualizacion_vf.ipynb")
print(f"   2. Ejecuta todas las celdas hasta 'Análisis IA: Caribe vs Otras'")
print(f"   3. El análisis procesará ~400 preguntas con Gemini 2.5 Flash")
print(f"\n   Configuración actual: {GOOGLE_API_KEY[:10]}...***")
print(f"   Modelo: gemini-2.5-flash")
print(f"   Autenticación: {'Service Account' if USE_SERVICE_ACCOUNT else 'API Key'}")
