# Hello swarm — ejemplo ejecutable (NaN Builders)

Fan-out mínimo con 3 roles sobre la API real de NaN (`/v1/chat/completions`),
siguiendo el patrón del playbook. Sin dependencias externas (`urllib` de stdlib).

## Uso

```bash
export NAN_API_KEY="sk-tu-key"
python3 hello_swarm.py
```

## Qué hace

1. **Fan-out:** lanza 3 llamadas en paralelo a `gemma4`, `qwen3.6` y
   `deepseek-v4-flash` con el mismo contrato pero distinto rol (ejecutar /
   alternar / juzgar), usando `ThreadPoolExecutor(max_workers=3)`.
2. **Fan-in:** la terminal reduce los tres resultados y los muestra juntos,
   con un cross-check de errores.
3. **Límites respetados:** 3 concurrentes < 5 máx de NaN.

> Es deliberadamente mínimo por claridad. En un harness real (OpenClaw, etc.)
> la orquestación y el jurado se hacen con sub-agentes, no con `urllib` —
> este script es para ver el flujo cableado de pe a pa y poder adaptarlo.