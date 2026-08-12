# Caso de estudio: investigación de la hipótesis de Riemann con orquestación multi-modelo

> **Repo completo:** [github.com/elCanosail/riemann-conjecture](https://github.com/elCanosail/riemann-conjecture)  
> **Objetivo del caso:** mostrar cómo se aplican en la práctica los principios de orquestación multi-modelo descritos en la guía general.

---

## 1. El problema y por qué era un buen test

La **hipótesis de Riemann** afirma que todos los ceros no triviales de la función zeta de Riemann tienen parte real igual a 1/2. Es uno de los problemas abiertos más importantes de las matemáticas. Desde el punto de vista de la orquestación multi-modelo, es un excelente banco de pruebas porque cumple tres condiciones:

1. **Es difícil en múltiples dimensiones:** requiere razonamiento numérico, análisis complejo, álgebra abstracta, teoría analítica de números y programación científica.
2. **No basta con una respuesta vagamente correcta.** Un error sutil en una demostración puede invalidar toda la conclusión.
3. **Los modelos actuales no lo resuelven solos.** Esto obliga a diseñar un sistema que compense las debilidades individuales.

Nuestra pregunta de investigación no era "demostrar Riemann". Era más modesta y más realista: **¿puede un panel de modelos especializados avanzar de forma fiable en un problema matemático de alto nivel, detectar sus propios errores y producir un resultado negativo pero preciso?**

Un resultado negativo —es decir, no demostrar la hipótesis— puede ser tan valioso como un resultado positivo, siempre que la razón del fracaso esté bien documentada.

---

## 2. La arquitectura usada

### 2.1. Panel de modelos

| Modelo | Rol en Riemann | Plataforma |
|---|---|---|
| GLM-5.2 | Orquestador y árbitro | Ollama Cloud |
| DeepSeek V4 Flash | Ejecutor numérico y analítico rápido | NaN Builders |
| Kimi K2.6 | Razonador profundo en cadenas largas | Ollama Cloud |
| Qwen 3.6 | Ángulo alternativo y detección de ciegos compartidos | NaN Builders |
| Cogito 2.1 | Verificador independiente | Ollama Cloud |

### 2.2. Seis ángulos de ataque

El orquestador (GLM-5.2) diseñó seis ángulos de ataque, cada uno asignado a un modelo según su fortaleza:

1. **Ángulo numérico:** verificación computacional de ceros en la línea crítica. DeepSeek V4 Flash.
2. **Ángulo funcional:** análisis de propiedades analíticas de ζ(s). DeepSeek V4 Flash + Kimi K2.6.
3. **Ángulo algebraico abstracto:** manipulación formal de series de Dirichlet. Kimi K2.6.
4. **Ángulo histórico-crítico:** revisión de intentos previos y supuestos ocultos. Qwen 3.6.
5. **Ángulo de refutación:** búsqueda de contraejemplos o contradicciones. Cogito 2.1 como verificador de DeepSeek.
6. **Ángulo de síntesis:** integración de resultados parciales y decisión sobre continuar o parar. GLM-5.2.

### 2.3. Tres fases de trabajo

**Fase 1 — Refutación numérica y verificación de datos**

Objetivo: comprobar si existía algún indicio numérico de contraejemplo en los primeros miles de ceros no triviales. DeepSeek V4 Flash lideró la fase, con Cogito verificando desde cero cada "anomalía" detectada.

**Fase 2 — Análisis funcional y álgebra abstracta**

Objetivo: explorar si alguna identidad funcional o manipulación algebraica podía abrir un camino de demostración. Kimi K2.6 lideró el análisis algebraico. Qwen 3.6 revisó los supuestos desde un ángulo distinto.

**Fase 3 — Síntesis y verificación final**

Objetivo: integrar todo, documentar el resultado y decidir si el sistema había producido algo publicable. GLM-5.2 coordinó la síntesis y Cogito realizó una verificación final de los argumentos centrales.

---

## 3. El fallo de Kimi y la recuperación

### 3.1. El fallo

En la **Fase 2**, Kimi K2.6 produjo un razonamiento que parecía avanzar hacia una posible demostración. Sin embargo, contenía un error estructural: el modelo confundió una **hipótesis auxiliar** con una **equivalencia demostrada**.

Concretamente, en la manipulación de una serie de Dirichlet, Kimi asumió que cierta propiedad asintótica implicaba una identidad exacta en un dominio mayor. El razonamiento subsiguiente era coherente y largo, pero partía de una base incorrecta.

Este tipo de error es especialmente peligroso porque:

- El resto del razonamiento es lógicamente válido.
- El modelo no cuestiona su propio paso inicial.
- Un lector superficial puede encontrar la cadena "elegante" y aceptarla.

### 3.2. Cómo se detectó

El error no fue detectado por Kimi mismo. Fue detectado por **Qwen 3.6**, actuando como modelo de sesgo alternativo, y luego confirmado por **Cogito 2.1** en modo verificador independiente.

Qwen señaló que el paso problemático no estaba justificado en la literatura y que la notación de Kimi oscilaba entre dos definiciones distintas de una misma función. Cogito, sin ver el razonamiento de Kimi, recibió solo el enunciado del lema y los datos, y concluyó que el lema era falso o al menos no demostrado.

### 3.3. Recuperación

El orquestador (GLM-5.2) decidió:

1. **No descartar a Kimi.** El error era un fallo de validación, no de capacidad.
2. **Ajustar el contrato.** En adelante, los argumentos algebraicos debían incluir una sección explícita de "supuestos no demostrados".
3. **Añadir una verificación externa obligatoria.** Ningún resultado algebraico pasaba a la fase de síntesis sin ser revisado por Cogito o Qwen.
4. **Documentar el fallo.** El error se convirtió en una lección del sistema.

Este incidente ilustra por qué la orquestación no es solo paralelización: es diseño de salvaguardas.

---

## 4. Métricas reales

A continuación resumimos métricas reales obtenidas durante la investigación.

### 4.1. Uso de modelos

| Modelo | Nº aprox. de llamadas | Rol principal |
|---|---|---|
| GLM-5.2 | ~150 | Orquestación, arbitraje, síntesis |
| DeepSeek V4 Flash | ~800 | Ejecución numérica/analítica en paralelo |
| Kimi K2.6 | ~200 | Razonamiento profundo, álgebra abstracta |
| Qwen 3.6 | ~120 | Ángulo alternativo, detección de ciegos |
| Cogito 2.1 | ~180 | Verificación independiente |

### 4.2. Tiempo y tokens

| Métrica | Valor aproximado |
|---|---|
| Duración total del proyecto | ~3 semanas de iteración (~8 horas de cómputo activo) |
| Tokens consumidos | ~120M tokens (mayoría en Ollama Cloud) |
| Latencia mediana sub-agente (NaN Builders, estimación operativa) | 0.76 s |
| Latencia mediana sub-agente (Ollama Cloud, estimación operativa) | 2.37 s |
| Cold start NaN Builders (estimación operativa) | 3.29 s |
| Latencia tras caché caliente (estimación operativa) | 0.57–0.78 s |
| Throughput medio estimado | ~145 tok/s |

### 4.3. Rendimiento del caching

En las fases con prefijo constante (por ejemplo, el contrato base para análisis de ceros), el uso consciente del caching redujo la latencia efectiva en un factor de 3–4 en NaN Builders. DeepSeek V4 Flash, con su descuento estimado del ~98 % en cached tokens, fue especialmente económico para lotes de verificación masiva.

---

## 5. El resultado: negative result, pero preciso

La investigación no demostró la hipótesis de Riemann. Tampoco la refutó. El resultado fue **negativo en el sentido epistemológico**: no generamos una demostración ni un contraejemplo.

Pero el resultado fue **positivo en el sentido metodológico**:

- Producimos una exploración sistemática con seis ángulos.
- Detectamos y corregimos errores internos gracias a la verificación cruzada.
- Documentamos exactamente dónde se detuvo cada línea de ataque y por qué.
- Generamos un corpus reusable de razonamientos, contratos y prompts.

Ese tipo de resultado negativo pero preciso es valioso porque evita que otros malgasten tiempo en caminos ya examinados, y porque demuestra que la orquestación multi-modelo puede funcionar incluso en dominios donde ningún modelo es fiable por sí solo.

---

## 6. Lecciones extraídas

### 6.1. La calidad del contrato importa más que el tamaño del modelo

Un buen contrato de trabajo hizo que DeepSeek V4 Flash superara en utilidad a modelos más grandes en tareas concretas. Un mal contrato hizo que Kimi K2.6, a pesar de su tamaño, introdujera un error sutil.

### 6.2. El sesgo alternativo es un recurso, no una redundancia

Qwen 3.6 no estaba ahí por si fallaba otro modelo. Estaba ahí porque su sesgo distinto detectó un error que otros no detectaron. Eso es distinto de la redundancia.

### 6.3. La verificación cruzada es costosa pero imprescindible en dominios críticos

Cogito 2.1 añadió latencia y coste. Sin él, habríamos aceptado resultados incorrectos. En investigación matemática, un error no detectado es peor que una respuesta lenta.

### 6.4. El caching consciente cambia la economía del sistema

Sin caching, las fases masivamente paralelas habrían sido mucho más lentas y costosas. Con caching, DeepSeek V4 Flash se convirtió en una herramienta económicamente viable para verificación a gran escala.

### 6.5. Un buen orquestador no optimiza solo velocidad; optimiza decisiones

GLM-5.2 no era el modelo más rápido, pero era el mejor para decidir cuándo parar, cuándo reintentar y cuándo escalarar un conflicto a verificación cruzada. Esa capacidad de decisión compensaba con creces su coste.

---

## 7. Enlace al repositorio

El código, los prompts, los contratos de trabajo y los logs de la investigación están disponibles en:

**[github.com/elCanosail/riemann-conjecture](https://github.com/elCanosail/riemann-conjecture)**

Se incluyen scripts reutilizables para orquestación con NaN Builders y Ollama Cloud, así como plantillas de contratos de trabajo basadas en los usados durante la investigación.
