# Orquestación Multi-Modelo con NaN Builders

**Un playbook open-source y pedagógico de lecciones de proceso agentico.**

*Destilado de un experimento real contra la Hipótesis de Riemann. Aplicable a tu día a día.*

---

## Status

This is a playbook of agentic process lessons, not a software framework. No runtime, CLI, or executable pipeline is included.

This repository contains documentation, field notes, templates, and a case study. Use it as a source of patterns, not as installable software.

---

## ¿Qué es esto?

La mayoría de gente usa un modelo de IA. Le da un prompt, recibe una respuesta. Si la respuesta no es buena, prueba otro prompt, o cambia de modelo.

Esto es sobre algo distinto: **orquestar varios modelos especializados en paralelo**, cada uno con un rol asignado, para atacar problemas que ningún modelo individual puede resolver bien.

No es teoría. Lo usamos para investigar la barrera del 2/3 en los ceros de la función zeta de Riemann — un problema de matemáticas abierto desde 1859. Cinco modelos, seis ángulos de ataque, ~8 horas de cómputo activo distribuidas en ~3 semanas de iteración, resultado negativo pero preciso. [El repo de ese experimento está aquí](https://github.com/elCanosail/riemann-conjecture).

Esta guía extrae lo que aprendimos y lo hace práctico.

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
| [Patrones swarm](docs/swarm-patterns.md) | **Nuevo.** Fan-out/fan-in, jurado de votación, especialistas cruzados, red-team, multiverse. Cómo lanzar enjambres de modelos NaN con límites reales |
| [Caso de estudio: Riemann](examples/riemann-case-study.md) | El experimento real que inspiró estas lecciones. 5 modelos, 6 ángulos, fallo real de Kimi K2.6 y recuperación |
| [Plantilla: Contrato de trabajo](templates/contrato-trabajo.md) | Template reutilizable para handoffs orquestador → sub-agente |
| [Plantilla: Prompt caching](templates/prompt-caching.md) | Cómo estructurar prompts para maximizar cache hits en NaN Builders (98% descuento estimado) |

---

## Panel de modelos recomendado (orientado NaN)

El panel del experimento original mezcla plataformas (ver guía completa). Para un stack **NaN-first** con cuotas amplias y latencia baja, este es el panel mínimo verificado (2026-08-22):

| Rol | Modelo | Plataforma | Contexto | Por qué |
|-----|--------|-----------|-----------|--------|
| Ejecución rápida / tool-calls | `gemma4` | NaN | 256K | Respuestas cortas y disciplinadas, JSON limpio — el mejor para sub-agentes con contratos |
| Análisis / razonamiento medio | `qwen3.6` | NaN | 256K | Flagship, MTP 2x, multimodal; bueno para análisis y síntesis |
| Revisión / jueces / escepticismo | `deepseek-v4-flash` | NaN | 1M | Reasoning profundo, ideal como verificador externo (cuidado: respuestas cortas en NaN si no se pide longitud) |
| *Omnimodal (texto+vision+audio)* | `mimo-v2.5` | NaN | 1M | NO recomendado para agentes/swarm (falla disciplina JSON); útil solo para tareas multimodales |
| Full-context orquestador (si está en el stack) | `glm-5.2` | Ollama Cloud | 1M | 1M de contexto y síntesis; caro, reservado para orquestación final |

**Panel swarm mínimo recomendado:** `gemma4` + `qwen3.6` + `deepseek-v4-flash` (3 roles: ejecutar, alternar, juzgar). Los 3 caben en 5 concurrentes de NaN.

---

## Rendimiento observado con NaN Builders (estimaciones operativas)

| Métrica | Valor | Contexto |
|---------|-------|----------|
| Latencia mediana aproximada | 0.76s | DeepSeek V4 Flash en NaN (vs 2.37s en Ollama Cloud) |
| Caching estabilizado aproximado | 0.57–0.78s | Tras cold start, runs repetidas |
| Cold start aproximado | 3.29s | Primera llamada |
| Throughput estimado | ~145 tok/s | Paridad aproximada con Ollama Cloud |
| Cuota mensual | **deepseek-v4-flash 2B · mimo-v2.5 1B** | Actualizado 2026-08-22 desde docs oficiales (antes figuraba 500M) |
| Rate limits | **60 rpm / 5 concurrentes / 1.5M tpm por modelo** | Actualizado 2026-08-22; clave para diseñar el fan-out (N modelos = N×1.5M tpm) |
| Cache discount estimado | ~98% en cached tokens | DeepSeek — una de las políticas más agresivas |

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

- **Desarrolladores usando NaN Builders** que quieren sacarle más provecho a sus cuotas (2B tok/mes en deepseek-v4-flash, 1B en mimo-v2.5)
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

- **Templates y documentación:** MIT
- **Documentación y guías:** CC-BY-4.0

Ver [`LICENSE`](LICENSE) para detalles.

---

*Si este playbook te resulta útil, el experimento completo que lo inspiró está en [github.com/elCanosail/riemann-conjecture](https://github.com/elCanosail/riemann-conjecture).*
