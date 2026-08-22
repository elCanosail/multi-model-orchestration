#!/usr/bin/env python3
"""
Hello swarm — fan-out/fan-in mínimo sobre NaN Builders.

Tres modelos NaN, tres roles, un mismo objetivo. Sin dependencias externas.
"""
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://api.nan.builders/v1/chat/completions"
KEY = os.environ.get("NAN_API_KEY", "")

# Contrato base (prefijo común -> cacheable en NaN)
CONTRATO = (
    "Estás en un enjambre. Objetivo: "
    "¿qué ventaja añade orquestar varios modelos pequeños en paralelo "
    "frente a usar un modelo grande solo? "
    "Responde en MÁXIMO 2 frases, en español, dando 1 argumento según tu rol."
)

ROLES = [
    ("gemma4",            "Rol: ejecutor pragmático — argumento más concreto y operativo."),
    ("qwen3.6",           "Rol: analista alternativo — ángulo que los demás no verían."),
    ("deepseek-v4-flash", "Rol: juez escéptico — el contraargumento más fuerte."),
]


def llamar(modelo: str, rol: str) -> str:
    body = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": CONTRATO + "\n\n" + rol},
            {"role": "user", "content": "Ejecuta tu rol."},
        ],
        "max_tokens": 150,
    }
    req = urllib.request.Request(
        BASE,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            # WAF de Cloudflare bloquea el user-agent por defecto de urllib (error 1010)
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    msg = data["choices"][0]["message"]
    # DeepSeek pone el razonamiento en reasoning_content; si content es null
    # (p.ej. max_tokens consumido por el reasoning), usamos reasoning_content.
    texto = (msg.get("content") or "").strip() or (msg.get("reasoning_content") or "").strip()
    if not texto:
        # Último recurso: contenido completo del mensaje serializado
        texto = json.dumps(msg, ensure_ascii=False)[:500]
    return texto


def main() -> int:
    if not KEY:
        print("Set NAN_API_KEY first: export NAN_API_KEY=sk-...", file=sys.stderr)
        return 1

    resultados = {}
    with ThreadPoolExecutor(max_workers=len(ROLES)) as pool:
        futs = {pool.submit(llamar, m, r): m for m, r in ROLES}
        for f in futs:
            modelo = futs[f]
            try:
                resultados[modelo] = f.result()
            except Exception as e:
                resultados[modelo] = f"ERROR: {e}"

    print("=== Fan-out (NaN, 3 roles, 1 pregunta) ===")
    for modelo, _rol in ROLES:
        print(f"\n--- {modelo} ---\n{resultados.get(modelo, '?')}")

    print("\n=== Fan-in: cross-check ===")
    errores = [k for k, v in resultados.items() if v.startswith("ERROR")]
    if errores:
        print(f"⚠️ Fallos: {errores}")
    else:
        print("Coherente: 3/3 roles respondieron. Veredicto del juez: revisar los textos para convergencia/divergencia.")
    print("OK — enjambre completado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())