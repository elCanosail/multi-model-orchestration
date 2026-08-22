# Patrones de orquestación enjambre (swarm) con NaN Builders

> **Audiencia:** equipos que quieren pasar de "un orquestador + sub-agentes secuenciales" a sistemas donde **muchos modelos especializados trabajan en paralelo, compiten, se contradicen y convergen**.
> **Plataforma objetivo:** NaN Builders (`https://api.nan.builders/v1`) — modelos `gemma4`, `qwen3.6`, `deepseek-v4-flash`, `mimo-v2.5`; límites reales verificados: **60 rpm / 5 concurrentes por key / 1.5M tokens/min por modelo**.
> **Nota de honestidad:** estos son patrones de arquitectura de agentes, no algoritmos nuevos. El valor está en adaptarlos a un harness concreto (OpenClaw, Claude Code, OpenCode) con **contratos estrictos** y **sesgos de rol** explícitos.

---

## 0. Por qué enjambre y no "un agente con muchas tools"

Un agente secuencial encadena pasos: razona → tool → razona → tool. Un enjambre (swarm) **lanza N agentes a la vez sobre la misma pregunta**, cada uno con un rol, sesgo o restricción distinta, y combina los resultados con una **regla explícita** (voto, arbitraje, consenso ponderado, síntesis).

**Cuándo un enjambre gana:** tareas donde la verdad es verificable de múltiples maneras — análisis de datos, auditorías, código, investigación, redacción con varias voces, búsqueda de errores, generación de alternativas de diseño.

**Cuándo un enjambre pierde:** tareas secuenciales con dependencias duras (builds, deploys, pipelines con estado), tareas triviales (donde el fan-out es coste puro), o problemas con contexto compartido enorme (cada copia lo multiplica por N).

**Regla de coste:** con NaN, 5 agentes en paralelo ≈ 5× tokens. Con el prefijo cacheado (ver `templates/prompt-caching.md`), el coste marginal de cada agente extra cae drásticamente. Diseña el prefijo del contrato para maximizar cache hits.

---

## 1. Fan-out / Fan-in (divergir y converger)

El patrón base de cualquier enjambre.

### Cómo funciona

1. El orquestador divide el problema en **K perspectivas o subtareas** complementarias (no idénticas).
2. Lanza K sub-agentes en paralelo; cada uno recibe un **contrato propio** (objetivo, entradas, restricciones, criterio de éxito) y un **sesgo de rol** distinto.
3. Los resultados vuelven y el orquestador **reduce**: sumariza, vota, o cruza contradicciones.

### Ejemplo OpenClaw (pseudocódigo)

```python
roles = [
    ("gemma4",           "ejecutor: implementa el cambio mínimo",
     "no razones de más; tool-calls directas; JSON estricto"),
    ("deepseek-v4-flash","analista: busca fallos y efectos secundarios del cambio de gemma4",
     "revisión adversarial; señala archivos y líneas concretas"),
    ("qwen3.6",          "alternativo: propone un enfoque distinto si el de gemma4 huele mal",
     "sesgo contrario al mainstream; justifica brevemente"),
]

for model, tarea, restriccion in roles:
    spawn_subagent(model=model, contrato=CONTRATO_BASE + tarea + restriccion)
```

### Verificación

- Trata los outputs como **hipótesis**, no como respuestas definitivas.
- Si N≥2 convergen idénticas → confianza alta. Si divergen → hallazgo, no fallo.
- El orquestador sintetiza en <200 palabras: qué coincidió, qué no, qué decisión se necesita.

---

## 2. Jurado (voting swarm / panel de veredicto)

El patrón de **verificación independiente**: los verificadores no deben ser los mismos modelos que produjeron el resultado, ni tener su contexto de razonamiento.

### Cómo funciona

1. Un ejecutor produce el resultado.
2. Se lanzan **jueces sin contexto de producción**: solo el resultado final, el criterio de éxito y el mínimo contexto de evaluación.
3. Cada juez dictamina: **PASS / FAIL + una línea de causa**.
4. Regla simple: ≥2 jueces fallan → rechazado. 1 fallo con causa distinta y resultado crítico → revisar. Todos PASS → adelante.

### Por qué no basta el "auto-check"

Un modelo que acaba de generar una respuesta sufre *rubber-stamping*: tiende a validar lo propio. Un verificador externo, con otro sesgo (deepseek-v4-flash juzgando código de gemma4, qwen3.6 juzgando razonamiento de deepseek), no comparte el camino de error.

### Plantilla de veredicto

```markdown
## Jurado — Veredicto
Modelo juez: {model}
Tarea: {id}
Veredicto: PASS | FAIL
Causa (una línea):
Evidencia (archivo:línea o fragmento):
Riesgo si PASS (opcional):
```

**Regla de oro:** el juez nunca recibe el prompt completo del ejecutor — solo el resultado y los criterios.

---

## 3. Especialistas cruzados (cross-examination)

Interrogatorio contradictorio entre dos modelos con sesgo ortogonal, con el orquestador de árbitro.

### Cómo funciona

- Modelo A: "busca los errores en el resultado de B" (sesgo: atacar)
- Modelo B: "responde punto por punto a las críticas de A, admitiendo dónde se equivoca" (sesgo: defender con rigor)
- Árbitro (orquestador o un tercer modelo): dictamina si las defensas cierran los vectores (máximo 2 rondas para no disparar coste).

### Cuándo usarlo

- Resultado crítico y bond de verificar barato: código de cobros, cálculos, SQL sobre datos sensibles, configs.
- Cuando los modelos tienen sesgos ortogonales reales. En nuestro plan: **gemma4** (ejecución directa) como defensor, **deepseek-v4-flash** (escepticismo) como atacante, y **qwen3.6** (alternativo) como árbitro o segundón.

---

## 4. Red-team (adversario deliberado)

Uno de los agentes intenta **romper** deliberadamente lo que el sistema produce. Ideal para seguridad, prompts adversariales y prueba de robustez.

- **Atacante** (`deepseek-v4-flash`): "encuentra 3 formas de romper este SQL/plan/prompt".
- **Defensor** (`gemma4`): "parchea el resultado para cerrar los 3 vectores sin cambiar la intención".
- **Árbitro** (orquestador): acepta o descarta los parches.

Es la forma barata de montar un bucle de red-teaming sin operador humano.

---

## 5. Enjambre de rutas múltiples (multiverse)

Para problemas donde **no sabemos cuál es la mejor ruta**: lanza 3-5 sub-agentes con **metodologías distintas** sobre el mismo objetivo.

- Caso real: la búsqueda de Riemann (ver `examples/riemann-case-study.md`) corrió 6 ángulos (numérico, funcional, algebraico, etc.), cada uno con un modelo de sesgo distinto, sobre la misma barrera del 2/3. El resultado negativo pero preciso se logró porque **los ángulos convergían en los mismos puntos críticos** aunque ninguno solo tenía la imagen completa.
- Regla: contrato idéntico para todas las rutas excepto el **rol/metodología**. Mide confianza unitaria y busca ultrajes.

---

## 6. Colapso de consenso y cómo evitarlo

**Advertencia de higiene:** la calidad del enjambre depende de la **diversidad real de sesgos**, no del número de agentes.

- Tres modelos de la misma plataforma entrenados con datos solapados pueden **compartir el mismo ciego** → consenso falso.
- Mitigación: mezclar especializaciones (código / rápidos / lógicos / alternativos), incluir un modelo con **sesgo contrario deliberado**, y nunca tratar el consenso como prueba de verdad — solo como señal de ausencia de outliers obvios.

---

## 7. Costes y límites reales (NaN, verificado 2026-08-22)

| Recurso | Límite | Implicación para swarm |
|---|---|---|
| Request / min | **60 rpm** por key | Fan-out de 5-8 es cómodo; un bucle cerrado de jurado puede tocar el techo |
| Concurrent | **5** | Nunca lanzar N>5 a NaN; serializa en olas de 5 |
| Tokens / min | **1.5M tpm** por modelo | El fan-out multiplica rápido; monitoriza en dashboard |
| Cuota mensual | deepseek-v4-flash **2B** · mimo-v2.5 **1B** | Con cuotas amplias, el jurado barato es viable; mimo/v2.5 no es herramienta de swarm (JSON débil) |

**Modelo de coste:** 1 agente × 10 veces ≈ 10×; 10 agentes en paralelo ≈ mismo total de tokens inmediato. Con precaching del prefijo común, el coste marginal de cada réplica baja mucho — por eso el fan-out bien diseñado es viable en NaN.

---

## 8. Resumen rápido

- **Fan-out / fan-in** → generar alternativas y converger.
- **Jurado** → verificar resultados críticos con jueces independientes.
- **Especialistas cruzados** → arbitrar bajo contradicción controlada.
- **Red-team** → imponer un adversario a lo generado.
- **Multiverse** → rutas múltiples cuando no se sabe cuál es la mejor.
- **Consenso** — solo como señal, recordando el sesgo común compartido.

---

*Documento vivo — Elcano Research Program · 2026-08-22*