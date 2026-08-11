# Orquestación Multi-Modelo con NaN Builders

**Una guía práctica, open-source y pedagógica para orquestar múltiples modelos de IA en paralelo.**

*Probada en un experimento real contra la Hipótesis de Riemann. Aplicable a tu día a día.*

---

## ¿Qué es esto?

La mayoría de gente usa un modelo de IA. Le da un prompt, recibe una respuesta. Si la respuesta no es buena, prueba otro prompt, o cambia de modelo.

Esto es sobre algo distinto: **orquestar varios modelos especializados en paralelo**, cada uno con un rol asignado, para atacar problemas que ningún modelo individual puede resolver bien.

No es teoría. Lo usamos para investigar la barrera del 2/3 en los ceros de la función zeta de Riemann — un problema de matemáticas abierto desde 1859. Cinco modelos, seis ángulos de ataque, ocho horas, resultado negativo pero preciso. [El repo de ese experimento está aquí](https://github.com/elCanosail/riemann-conjecture).

Esta guía extrae lo que aprendimos y lo hace reproducible.

---

## ¿Por qué multi-modelo?

Un solo modelo, por bueno que sea, tiene blind spots. Comparte sesgos across todas sus respuestas. Si se equivoca en un tipo de razonamiento, se equivoca igual en todos los intentos.

**Cinco modelos con biases distintos no comparten los mismos blind spots.** Si uno falla, los otros pueden cubrirlo. Si todos coinciden, la confianza sube. Si discrepan, has encontrado algo interesante.

La pregunta deja de ser "¿qué modelo uso?" y pasa a ser "¿qué responsabilidad tiene cada modelo?"

---

## Lo que vas a encontrar aquí

| Sección | Qué contiene |
|---------|-------------|
| [Guía completa](docs/guia-completa.md) | ~3500 palabras. Panel de modelos, contratos, caching, verificación, patrones, anti-patrones. Todo explicado pedagógicamente |
| [Caso de estudio: Riemann](examples/riemann-case-study.md) | El experimento real que validó esta arquitectura. 5 modelos, 6 ángulos, fallo real de Kimi K2.6 y recuperación |
| [Plantilla: Contrato de trabajo](templates/contrato-trabajo.md) | Template reutilizable para handoffs orquestador → sub-agente |
| [Plantilla: Prompt caching](templates/prompt-caching.md) | Cómo estructurar prompts para maximizar cache hits en NaN Builders (98% descuento) |

---

## Panel de modelos recomendado

| Rol | Modelo | Plataforma | Tamaño | Por qué |
|-----|--------|-----------|--------|---------|
| Orquestador | GLM-5.2 | Ollama Cloud | 1508 GB | 1M contexto, mantiene visión global, sintetiza |
| Ejecutor rápido | DeepSeek V4 Flash | NaN Builders | 140 GB | 0.76s latencia, barato, profundo en álgebra |
| Deep reasoning | Kimi K2.6 | Ollama Cloud | 595 GB | Cadenas largas. Cuidado con álgebra abstracta |
| Bias alternativo | Qwen 3.6 | NaN Builders | 397 GB | Ve patrones que otros no buscan |
| Verificador | Cogito 2.1 | Ollama Cloud | 689 GB | Verificación independiente sin contexto compartido |

**Regla clave:** match model al tipo de razonamiento, no al tamaño. El modelo "pequeño" (DeepSeek 140GB) a veces piensa más profundo que el "grande" (Kimi 595GB) en ciertos tipos de problemas.

---

## Rendimiento real con NaN Builders

| Métrica | Valor | Contexto |
|---------|-------|----------|
| Latencia mediana | 0.76s | DeepSeek V4 Flash en NaN (vs 2.37s en Ollama Cloud) |
| Caching estabilizado | 0.57–0.78s | Tras cold start, runs repetidas |
| Cold start | 3.29s | Primera llamada |
| Throughput | ~145 tok/s | Paridad con Ollama Cloud |
| Cuota | 500M tokens/mes por modelo | Efectivamente ilimitado para trabajo normal |
| Cache discount | ~98% en cached tokens | DeepSeek — una de las políticas más agresivas |

¿Qué significa en práctica? Puedes lanzar 3 sub-agentes en paralelo, si uno falla lo reasignas, iteras sin mirar el contador. "¿Podemos permitirnos otro intento?" deja de ser la pregunta. "Lanza todos los que quieras" es la respuesta.

---

## Inicio rápido

```python
# Pseudocódigo — adapta a tu harness (OpenClaw, Claude Code, OpenCode, etc.)

# 1. El orquestador define el plan
plan = glm52.analyze(objetivo, contexto)
tareas = plan.divide_en_subtareas_independientes()

# 2. Calentar caché: primer sub-agente solo
primer_resultado = deepseek_flash.ejecutar(tareas[0], contrato=CONTRATO_BASE)
# → prefijo del prompt ahora en caché

# 3. Resto en paralelo (caché caliente)
resultados = parallel([deepseek_flash.ejecutar(t, contrato=CONTRATO_BASE) for t in tareas[1:]])

# 4. Verificación cruzada
verificacion = cogito.verificar_desde_cero(resultados, sin_contexto_de_produccion=True)

# 5. Orquestador sintetiza
sintesis = glm52.sintetizar(resultados + verificacion)
```

---

## ¿Para quién es esto?

- **Desarrolladores usando NaN Builders** que quieren sacarle más provecho a su cuota de 500M tokens
- **Equipos experimentando con agentes** que quieren ir más allá de "un modelo, un prompt"
- **Investigadores** que necesitan confirmar hallazgos desde múltiples ángulos independientes
- **Cualquiera curioso** sobre cómo se ve la orquestación multi-modelo en la práctica, no en teoría

No necesitas ser matemático. No necesitas trabajar en IA. Si escribes código o tomas decisiones complejas, esto es para ti.

---

## Contribuir

Esto es un documento vivo. Si has experimentado con multi-modelo y tienes lecciones que añadir:

1. Abre un issue con tu experiencia
2. O envía un PR con mejoras, nuevos ejemplos, o correcciones
3. Cuanto más diversidad de experiencias, mejor para todos

**Áreas donde buscamos contribuciones:**
- Casos de estudio adicionales (no solo Riemann)
- Benchmarks comparativos de modelos en tareas específicas
- Patrones nuevos no cubiertos aquí
- Traducciones a otros idiomas

---

## Créditos

- **Elcano Research Program** — investigación original y documentación
- **NaN Builders ([@borjaperfra](https://x.com/borjaperfra))** — infraestructura que hizo posible el experimento
- **Helmcode** — el post sobre GLM-5.2 + DeepSeek que inspiró sistematizar el caching
- **Anthropic / Claude Code (Boris Cherny)** — arquitectura de sub-agentes que extendemos con multi-modelo

---

## Licencia

- **Código y templates:** MIT
- **Documentación y guías:** CC-BY-4.0

Ver [`LICENSE`](LICENSE) para detalles.

---

*Si esta guía te resulta útil, el experimento completo que la validó está en [github.com/elCanosail/riemann-conjecture](https://github.com/elCanosail/riemann-conjecture).*