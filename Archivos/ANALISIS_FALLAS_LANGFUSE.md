# Análisis de Fallas Atribuibles a la IA - Trazas Langfuse

**Período analizado**: 11 de octubre - 5 de noviembre 2025
**Total trazas analizadas**: 17,000
**Conversaciones únicas**: 6,119

---

## Resumen Ejecutivo

De las **6,119 conversaciones** analizadas en las trazas de Langfuse:

✅ **314 conversaciones (5.1%)** presentan AL MENOS UNA falla atribuible a la IA
✅ **5,805 conversaciones (94.9%)** NO presentan fallas detectadas

### Tasa de Fallo: **5.1%**

---

## Tipos de Fallas Identificadas

### 1. **Rate Limit Exceeded** (Cuota Excedida) 🔴
- **Impacto**: 288 conversaciones afectadas (91.7% de los errores)
- **Descripción**: El sistema alcanza el límite de cuota del LLM de Azure
- **Latencia promedio**: 15.3 segundos
- **Patrón temporal**:
  - **Horas pico**: 14:00-15:00, 13:00-14:00, 20:00-21:00
  - **Días críticos**:
    - 14 de octubre: 76 errores
    - 4 de noviembre: 63 errores
    - 5 de noviembre: 60 errores

**Causa raíz**: Límites de cuota del servicio Azure OpenAI durante horas de alto tráfico

---

### 2. **Content Policy Violation (Error 400)** ⚠️
- **Impacto**: 19 conversaciones afectadas (6.0% de los errores)
- **Descripción**: Preguntas bloqueadas por el filtro de contenido de Azure OpenAI
- **Latencia promedio**: 1.8 segundos
- **Mensaje típico**: "The response was filtered due to the prompt triggering Azure OpenAI's content management policy"

**Causa raíz**: Políticas de contenido de Azure OpenAI triggereadas por ciertas preguntas

---

### 3. **Internal Server Error (Error 500)** 🔴
- **Impacto**: 12 trazas afectadas (3.7% de los errores)
- **Descripción**: Fallo de autenticación con servicios upstream
- **Latencia promedio**: 2.0 segundos
- **Concentración**: 100% ocurrieron el 5 de noviembre
- **Mensaje típico**: "Gateway cannot authenticate upstream services. Please contact Microsoft for help"

**Causa raíz**: Problema temporal de autenticación con Azure Gateway

---

### 4. **Timeout** ⏱️
- **Impacto**: 7 conversaciones afectadas (2.2% de los errores)
- **Descripción**: Tiempo de espera excedido
- **Latencia promedio**: 15.2 segundos

**Causa raíz**: Respuestas que tardan demasiado en generarse

---

## Distribución Temporal de Fallas

### Por Hora del Día (Rate Limit - Principal)
```
14:00-15:00: 50 errores ████████████████████
15:00-16:00: 39 errores ███████████████
13:00-14:00: 34 errores █████████████
21:00-22:00: 28 errores ███████████
20:00-21:00: 26 errores ██████████
```

### Por Día (Rate Limit)
```
14 Oct 2025: 76 errores █████████████████████████
04 Nov 2025: 63 errores ████████████████████
05 Nov 2025: 60 errores ███████████████████
11 Oct 2025: 30 errores █████████
15 Oct 2025: 15 errores ████
```

---

## Análisis de Severidad

**Clasificación por impacto en la conversación:**

| Severidad | Conversaciones | Porcentaje | Descripción |
|-----------|---------------|------------|-------------|
| **Crítico** | 314 | 5.1% | ≥50% de las trazas con error |
| **Alto** | 0 | 0.0% | 25-50% de las trazas con error |
| **Bajo** | 0 | 0.0% | <25% de las trazas con error |
| **Sin error** | 5,805 | 94.9% | Sin fallas detectadas |

**Nota**: Todas las conversaciones con error tienen 100% de sus trazas afectadas, lo que indica que cuando falla, falla completamente.

---

## Impacto en Latencia

| Tipo de Error | Latencia Promedio | vs Normal |
|---------------|-------------------|-----------|
| Rate Limit | 15.3s | +272% |
| Timeout | 15.2s | +271% |
| Error 500 | 2.0s | -51% (falla rápida) |
| Error 400 | 1.8s | -56% (falla rápida) |
| **Sin error** | **4.1s** | **baseline** |

---

## Correlación con Tasa NULL en Conversaciones

**Hallazgo clave**: Los días con más Rate Limit errors NO coinciden directamente con los días de mayor tasa NULL identificados anteriormente (28 de octubre, 3 de septiembre).

Esto sugiere que:
1. Los Rate Limit errors son un problema **diferente** al de las respuestas NULL
2. Las respuestas NULL pueden deberse a otros factores (calidad de retrieval, falta de información)
3. Los errores de Langfuse representan **fallas técnicas** mientras que los NULLs pueden ser **fallas de conocimiento**

---

## Recomendaciones

### 1. **Aumentar Cuota de Azure OpenAI** (Prioridad Alta)
- Negociar aumento de límites de rate para horas 13:00-15:00
- Considerar implementar caching para queries repetitivas
- Establecer sistema de cola con retry para rate limit errors

### 2. **Revisar Content Policy Filters** (Prioridad Media)
- Analizar las 19 preguntas bloqueadas
- Evaluar si el filtro es demasiado restrictivo para contexto bancario
- Implementar mensajes de error más informativos para usuarios

### 3. **Monitoreo de Gateway Authentication** (Prioridad Alta)
- Establecer alertas para errores 500
- Implementar redundancia en autenticación
- Plan de contingencia para fallos de Azure Gateway

### 4. **Optimización de Latencia** (Prioridad Media)
- Implementar timeouts más agresivos (<10s)
- Estrategia de fallback para respuestas que tardan mucho
- Caching de respuestas comunes

---

## Datos Generados

Los siguientes archivos fueron creados:

1. **`langfuse_sessions_with_errors.csv`**: Análisis detallado por sessionId
   - Campos: sessionId, num_traces, has_error, avg_latency, error_count, error_rate, severity

---

## Metodología

**Patrones de error detectados:**
```python
- Error Code 400: Content policy violations
- Error Code 500: Internal server errors
- Error Code 502: Bad gateway
- Error Code 503: Service unavailable
- Error Code 504: Gateway timeout
- Rate Limit: Rate limit/quota exceeded/429
- Timeout: timeout/timed out
- Authentication: auth failures
```

**Agrupación**: Por `sessionId` para identificar conversaciones completas afectadas

**Periodo**: 25 días de trazas (11 Oct - 5 Nov 2025)
