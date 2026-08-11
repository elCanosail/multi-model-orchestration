# Plantilla de contrato de trabajo entre orquestador y sub-agente

> **Propósito:** estandarizar la comunicación entre el orquestador (modelo central) y los sub-agentes que ejecutan tareas.  
> **Regla de oro:** si no puedes rellenar los cuatro campos con claridad, la tarea no está lista para delegarse.

---

## 1. Los 4 campos de un contrato

Un contrato de trabajo debe contener exactamente cuatro elementos. Ni más, ni menos.

### 1.1. Objetivo

Qué debe lograrse, expresado como un **resultado concreto y verificable**. No una intención, no una dirección general.

- ✅ Bueno: *"Migrar los tests de `tests_legacy/test_calculo.py` de `unittest` a `pytest` manteniendo el mismo número de tests y su comportamiento."*
- ❌ Malo: *"Mejorar los tests."*

### 1.2. Entradas

Qué recursos necesita el sub-agente para hacer su trabajo. Pueden ser archivos, datos, funciones, hipótesis, enlaces, contexto mínimo.

- ✅ Bueno: *"El archivo `tests_legacy/test_calculo.py` y el listado de dependencias en `requirements-dev.txt`."*
- ❌ Malo: *"Mira el repositorio."*

### 1.3. Restricciones

Límites explícitos: qué no debe hacer, qué no debe tocar, qué supuestos no puede tomar, qué formatos no debe usar.

- ✅ Bueno: *"No modificar la lógica de negocio. No añadir dependencias nuevas. No eliminar tests."*
- ❌ Malo: *"No rompas nada."*

### 1.4. Criterio de éxito

Cómo saber que la tarea está bien. Idealmente debe ser **binario**: se cumple o no se cumple. Cuanto más mecánico, mejor.

- ✅ Bueno: *"`pytest tests/test_calculo.py` pasa con el mismo número de tests que `unittest discover` reportaba antes."*
- ❌ Malo: *"Que los tests funcionen bien."*

---

## 2. Ejemplo relleno: migración de unittest a pytest

**Tarea:** migrar tests legacy a pytest.

### Objetivo

Migrar los tests del archivo `tests_legacy/test_calculo.py` de `unittest` a `pytest`, manteniendo el comportamiento exacto de cada test y sin modificar la lógica de negocio.

### Entradas

- `tests_legacy/test_calculo.py`
- `requirements-dev.txt`
- (Opcional) `README.md` sección de desarrollo para entender el entorno

### Restricciones

- No modificar archivos fuera de `tests/`.
- No cambiar la lógica de los tests, solo su sintaxis.
- No añadir dependencias nuevas a `requirements-dev.txt`.
- No eliminar tests; si un test es redundante, marcarlo con `@pytest.mark.skip` y justificarlo en el mensaje de commit.

### Criterio de éxito

- `pytest tests/test_calculo.py` ejecuta todos los tests sin errores.
- El número de tests ejecutados es igual al número reportado previamente por `python -m unittest discover -s tests_legacy`.
- `git diff --stat` muestra cambios solo en el archivo de tests migrado.

---

## 3. Plantilla vacía para copiar

```markdown
## Contrato de trabajo

### Objetivo

[Describir el resultado concreto y verificable]

### Entradas

- [Recurso 1]
- [Recurso 2]
- [Recurso 3]

### Restricciones

- [Restricción 1]
- [Restricción 2]
- [Restricción 3]

### Criterio de éxito

- [Check 1]
- [Check 2]
- [Check 3]
```

---

## 4. Notas sobre claridad

### 4.1. Si no puedes expresar el objetivo con claridad

Es señal de que el orquestador no entiende bien la tarea. Antes de delegar, el orquestador debe:

1. Dividir la tarea en subtareas más pequeñas.
2. Escribir un contrato para cada subtarea.
3. Verificar que los criterios de éxito son mecánicos.

### 4.2. Si no sabes qué entradas son necesarias

Probablemente estás pasando demasiado contexto. Pregúntate: "¿qué necesita saber el sub-agente para no preguntar más?".

### 4.3. Si no puedes definir restricciones

El sub-agente hará supuestos. Esos supuestos serán incorrectos al menos el 30 % de las veces. Las restricciones reducen ese riesgo.

### 4.4. Si no hay criterio de éxito binario

La verificación será subjetiva. Eso genera bucles de revisión costosos. Si el criterio es cualitativo, añade al menos una métrica mensurable.

---

## 5. Checklist rápida antes de enviar el contrato

- [ ] El objetivo se puede responder con "sí, se ha hecho" o "no, no se ha hecho".
- [ ] Las entradas son nombres de archivo, datos o recursos concretos.
- [ ] Las restricciones dicen "no" en lugar de solo "sí".
- [ ] El criterio de éxito puede verificarse automáticamente o con un comando.
- [ ] El contrato cabe en menos de 200 palabras.
