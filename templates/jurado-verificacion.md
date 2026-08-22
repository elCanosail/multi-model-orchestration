# Plantilla de jurado — verificación independiente multi-modelo

> **Propósito:** estandarizar el patrón **swarm de jurado** (ver `docs/swarm-patterns.md#2`): N jueces verifican un resultado sin contexto de producción.
> **Modelos sugeridos (NaN):** jueces = `deepseek-v4-flash` (escepticismo) y `qwen3.6` (alternativo); ejecutor típico = `gemma4`.
> **Regla de oro:** el juez NUNCA ve el prompt completo del ejecutor — solo el resultado y los criterios de éxito.

---

## 1. Paquete que recibe cada juez

```markdown
## Solicitud de veredicto

### Resultado a evaluar
[{cita: resultado final del ejecutor — sin historial, sin razonamiento intermedio}]

### Criterios de éxito (la verificación es binaria)
- [ ] Criterio 1 — verificable
- [ ] Criterio 2 — verificable
- [ ] Criterio 3 — verificable

### Tu rol
Modelo {juez}: evalúa con tu sesgo ({escepticismo | alternativo | detalle}). No reescribas el resultado. No lo "mejores". Solo dictamina.

### Veredicto exigido
- PASS / FAIL (una línea de causa)
- Si FAIL: la evidencia concreta (archivo:línea, fragmento, comando que lo prueba)
- Riesgo restante si PASS (opcional)
```

---

## 2. Regla de decisión (árbitro / orquestador)

| Firmas | Decisión |
|--------|----------|
| 2+ jueces PASS | ✔ Aprobado |
| 1 PASS + 1 FAIL (causa distinta) | ⚠️ Revisar la causa; si es crítico, tercera ronda |
| 2+ FAIL | ✖ Rechazado — volver al ejecutor con las causas concatenadas |
| Jueces no coinciden en la causa | 🧠 Señal de ambigüedad del contrato → revisar criterio de éxito |

**Anti-patrón:** pedir al MISMO modelo que verifique su propio output (“¿te parece bien?”) → *rubber-stamping* casi garantizado. El jurado solo funciona con modelos de sesgo distinto y contexto aislado.

---

## 3. Variante económica (2 jueces, 1 modelo)

Si el presupuesto de concurrencia es 5 y ya hay 3 ejecutores, puedes usar **un solo juez** (deepseek-v4-flash) pero con dos "lentes" encadenadas:

1. Pasa 1: juzga el resultado con criterio de éxito.
2. Pasa 2 (mismo modelo): actúa como "segundo miembro del jurado" que **revisa críticamente el veredicto de la pasa 1** (cambio de sesgo explícito). Mejor que nada, peor que 2 modelos.

---

## 4. Plantilla en blanco

```markdown
## Solicitud de veredicto

### Tarea a evaluar
{evaluator_id}

### Resultado (sin contexto de producción)
```{código/texto resultado}```

### Criterios de éxito
- [ ] {verificable 1}
- [ ] {verificable 2}

### Veredicto
Veredicto: PASS | FAIL
Causa (una línea):
```