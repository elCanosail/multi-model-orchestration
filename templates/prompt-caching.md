# Plantilla práctica para prompt caching con NaN Builders

> **Propósito:** maximizar el uso del caching por prefijos en NaN Builders, reduciendo latencia y coste.  
> **Aplicación principal:** flujos con muchos sub-agentes paralelos que comparten instrucciones, convenciones o contexto base.

---

## 1. Cómo funciona el caching por prefijos

NaN Builders detecta automáticamente cuando varias peticiones comparten el mismo prefijo de tokens. Si el inicio del prompt es idéntico, la plataforma reutiliza la representación interna de ese prefijo en lugar de reprocesarlo.

Esto es especialmente poderoso con modelos como **DeepSeek V4 Flash**, que ofrece un descuento estimado del **~98 % en cached tokens**.

### 1.1. Condición fundamental

El prefijo debe ser **bit a bit idéntico**. Un espacio de más, una coma cambiada, una fecha dinámica o un identificador único al inicio rompen la caché.

### 1.2. Estructura óptima del prompt

Divide el prompt en dos bloques bien delimitados:

1. **Prefijo constante:** todo lo que no cambia entre peticiones.
2. **Sufijo variable:** la tarea concreta, los datos, la pregunta.

```text
[PREFIJO_CONSTANTE]
Eres un asistente especializado en análisis numérico.
Reglas:
- Usa notación LaTeX para fórmulas.
- No inventes datos.
- Responde en español con secciones numeradas.

[SUFIJO_VARIABLE]
Analiza la siguiente serie:
{datos}

Pregunta: {pregunta}
```

---

## 2. Plantilla de prompt

Usa esta plantilla como base para cualquier flujo masivamente paralelo.

```text
[PREFIJO_CONSTANTE]
Rol: {rol_del_sub_agente}
Instrucciones permanentes:
{lista_de_instrucciones}

Formato de salida:
{formato_esperado}

Convenciones:
{convenciones}

Ejemplos (si aplica):
{ejemplos}

[SUFIJO_VARIABLE]
Tarea concreta: {tarea}

Entradas:
{entradas}

Pregunta o instrucción final:
{instruccion_final}
```

### 2.1. Reglas para el prefijo constante

- No incluir datos de la petición actual.
- No incluir timestamps, IDs únicos ni metadatos variables.
- Mantener el orden exacto en todas las peticiones.
- Usar el mismo sistema de marcadores (`[PREFIJO_CONSTANTE]`, `[SUFIJO_VARIABLE]`).

### 2.2. Reglas para el sufijo variable

- Colocar todo lo que cambia aquí.
- No repetir instrucciones del prefijo.
- Ser lo más compacto posible; el caching ahorra en el prefijo, no en el sufijo.

---

## 3. El truco de calentamiento de caché

Si vas a lanzar múltiples sub-agentes en paralelo con el mismo prefijo, calienta la caché primero.

### 3.1. Pseudocódigo

```python
# Definir el prefijo compartido
PREFIJO = """
[PREFIJO_CONSTANTE]
Eres un asistente matemático especializado en análisis numérico.
Reglas:
- Usa notación LaTeX.
- No inventes datos.
- Responde en español.
"""

# 1. Lanzar una petición de calentamiento
warmup = llamar_modelo(
    prompt=PREFIJO + "\n[SUFIJO_VARIABLE]\nTarea de calentamiento.",
    modelo="deepseek-v4-flash"
)

# 2. Esperar a que termine (cold start ~3.29s en NaN Builders)
esperar(warmup)

# 3. Lanzar el resto en paralelo; el prefijo ya está en caché
resultados = ejecutar_en_paralelo([
    llamar_modelo(
        prompt=PREFIJO + f"\n[SUFIJO_VARIABLE]\n{tarea}",
        modelo="deepseek-v4-flash"
    )
    for tarea in lista_de_tareas
])
```

### 3.2. ¿Por qué funciona?

La primera petición paga el coste del cold start y del procesamiento del prefijo. Las siguientes peticiones reutilizan el prefijo, reduciendo drásticamente el tiempo de respuesta.

### 3.3. Métricas esperadas

| Estado | Latencia aproximada (estimaciones operativas) |
|---|---|
| Cold start | ~3,29 s |
| Sin caché, petición individual | ~0,76 s mediana |
| Con prefijo cacheado | ~0,57–0,78 s, muy estable |

---

## 4. Lista de verificación: ¿tu prompt está optimizado para caching?

- [ ] El prefijo es **idéntico** en todas las peticiones del lote.
- [ ] He separado claramente `[PREFIJO_CONSTANTE]` y `[SUFIJO_VARIABLE]`.
- [ ] No incluyo datos variables, timestamps ni IDs en el prefijo.
- [ ] El prefijo contiene instrucciones, convenciones, formato de salida y ejemplos.
- [ ] El sufijo contiene solo la tarea concreta y las entradas necesarias.
- [ ] He calentado la caché con una petición inicial antes del lanzamiento masivo.
- [ ] He medido latencia con y sin caché para confirmar el ahorro.
- [ ] Uso modelos que ofrecen descuento por cached tokens (ej. DeepSeek V4 Flash en NaN Builders, ~98 % estimado).

---

## 5. Ejemplo completo: verificación masiva de hipótesis

```text
[PREFIJO_CONSTANTE]
Eres un verificador matemático. Tu trabajo es examinar un argumento corto y decidir si es correcto, incorrecto o no demostrado.

Reglas:
- Responde solo con una de estas tres etiquetas: CORRECTO, INCORRECTO, NO_DEMOSTRADO.
- Añade una justificación de una sola línea.
- No corrijas el argumento; solo evalúalo.

Formato de salida:
ETIQUETA: <CORRECTO|INCORRECTO|NO_DEMOSTRADO>
JUSTIFICACION: <una línea>

[SUFIJO_VARIABLE]
Argumento a evaluar:
{argumento}

Entradas:
{datos_de_entrada}
```

En este ejemplo, el prefijo es común para cientos o miles de argumentos. El sufijo cambia solo en `{argumento}` y `{datos_de_entrada}`. Ideal para lanzar verificaciones masivas en paralelo tras calentar caché.

---

## 6. Anti-patrones de caching

| Anti-patrón | Por qué falla | Solución |
|---|---|---|
| Incluir un timestamp al inicio del prompt | Rompe la coincidencia de prefijos | Mover timestamps al sufijo o eliminarlos |
| Ordenar las instrucciones de forma diferente en cada petición | El caching es literal | Fijar el orden en una plantilla |
| Incluir resultados previos en el prefijo | El prefijo cambia en cada paso | Mantener el historial en el sufijo |
| No calentar caché antes de lanzar 50 peticiones en paralelo | Todas pagan el cold start | Calentar con una petición secuencial primero |
| Usar prompts dinámicos con concatenación inestable | Un espacio extra rompe la caché | Usar una plantilla concreta y revisarla |

---

## 7. Conclusión

El caching por prefijos no es magia: es una optimización mecánica que depende de la disciplina al estructurar los prompts. Con una plantilla clara, prefijos estables y un paso de calentamiento, puedes reducir drásticamente la latencia y el coste de flujos multi-agente en NaN Builders.
