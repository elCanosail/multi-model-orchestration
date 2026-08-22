# Guía completa de orquestación multi-modelo

> **Audiencia:** desarrolladores de la comunidad NaN Builders que quieren diseñar sistemas con varios modelos de IA en lugar de confiar ciegamente en uno solo.  
> **Enfoque:** práctico, pedagógico, con datos reales obtenidos en nuestra investigación sobre la hipótesis de Riemann.

---

## 1. Introducción

### 1.1. Qué es la orquestación multi-modelo y por qué importa

La orquestación multi-modelo no es usar varios modelos por si acaso. Es diseñar un sistema en el que cada modelo ejecuta una **responsabilidad** distinta, el mismo tipo de especialización que tendría un equipo de ingeniería: arquitectos, codificadores, revisores, testers.

La idea central es sencilla: ningún modelo grande es óptimo para todo. Cada familia de modelos tiene sesgos de entrenamiento, costes de latencia distintos, fortalezas en razonamiento profundo o en generación rápida, y debilidades específicas. Si tu sistema solo tiene un modelo, hereda todas sus limitaciones. Si diseñas un panel de modelos y un protocolo de handoff, el sistema es más robusto, más rápido y, en muchos casos, más barato.

### 1.2. La diferencia entre "usar un modelo bueno" y "orquestar varios modelos especializados"

Usar un modelo bueno es como contratar a un ingeniero brillante y pedirle que haga todo. Al principio funciona, pero cuando la tarea crece o cambia de naturaleza, aparecen tres problemas:

1. **Latencia.** Un modelo de 1,5 billones de parámetros puede ser excesivamente lento para tareas simples.
2. **Ruido.** Un modelo diseñado para seguir instrucciones generales introduce detalles irrelevantes cuando la tarea es técnica y concreta.
3. **Ceguera sistemática.** Cada modelo comete errores propios; si no hay verificación externa, esos errores pasan desapercibidos.

Orquestar modelos significa aceptar que cada uno es una herramienta y asignarle la tarea correcta. El orquestador decide quién hace qué, verifica la calidad y gestiona el contexto. El resto del sistema ejecuta.

### 1.3. Analogía: equipo de ingeniería vs. un solo hacker brillante

Imagina dos startups:

- **Startup A** tiene un hacker brillante que lo hace todo. Es rápido, pero cuando se equivoca nadie lo corrige. Si se va, se lleva el conocimiento. Si está sobrecargado, todo se ralentiza.
- **Startup B** tiene un arquitecto que diseña, dos desarrolladores que ejecutan, un revisor de código y un tester. Cada uno tiene un rol claro, se pasan especificaciones concretas y revisan el trabajo del otro. Es más robusta y escalable.

La orquestación multi-modelo es la Startup B. El orquestador es el arquitecto. Los sub-agentes son desarrolladores especializados. El verificador es el revisor. Y, al igual que en un equipo humano, la calidad depende de los **contratos de trabajo**, no de la inteligencia individual.

---

## 2. El panel de modelos

A continuación describimos el panel de modelos que usamos en nuestra investigación de Riemann. Cada modelo tiene un rol distinto. No los elegimos porque fueran los más grandes; los elegimos porque cubren responsabilidades complementarias.

### 2.1. GLM-5.2 — el orquestador

| Característica | Valor |
|---|---|
| Parámetros | 1,5 T (1.508 GB en Ollama Cloud) |
| Contexto | 1M tokens |
| Plataforma | Ollama Cloud |
| Alias de uso | `glm` / default en Elcano |

GLM-5.2 es el modelo más grande del panel. Sin embargo, su trabajo no es ejecutar tareas directamente, sino **tomar decisiones arquitectónicas**: elegir qué sub-agente ejecuta qué, diseñar contratos de trabajo, verificar que el plan cubre los ángulos necesarios y detectar cuando un resultado es sospechoso.

**Por qué orquesta y no ejecuta:**

- Tiene el contexto más amplio, lo cual es esencial para mantener una visión global del proyecto.
- Es el modelo más costoso en latencia. Usarlo para tareas repetitivas o paralelas es un desperdicio.
- Su fortaleza no está en generar líneas de código rápidamente, sino en razonar sobre estructura, dependencias y riesgos.

**Ejemplo real en Riemann:** GLM-5.2 decidió que la investigación debía dividirse en tres fases (refutación numérica, análisis funcional, verificación de álgebra abstracta) y asignó a cada modelo un ángulo. También diseñó los contratos de trabajo para los seis sub-agentes.

### 2.2. DeepSeek V4 Flash — el ejecutor rápido

| Característica | Valor |
|---|---|
| Parámetros | 140 GB |
| Plataforma | NaN Builders |
| Latencia mediana | 0,76 s |
| Throughput | ~145 tok/s |

DeepSeek V4 Flash es el caballo de batalla para tareas masivamente paralelas. Es lo suficientemente inteligente como para producir resultados de calidad, pero lo suficientemente rápido como para lanzar docenas de instancias simultáneas.

**Por qué a veces piensa más profundo que modelos más grandes:**

En nuestra investigación observamos que DeepSeek V4 Flash detectó patrones en series de ceros de Riemann que modelos más grandes pasaron por alto. Esto no es casualidad. Los modelos grandes tienen una tendencia a "rellenar" con argumentos generales; un modelo de tamaño intermedio, bien dirigido por un contrato claro, puede concentrarse mejor en el problema concreto.

**Ejemplo real en Riemann:** DeepSeek V4 Flash fue el motor principal de la fase de refutación numérica y de la verificación de hipótesis analíticas. Su rapidez permitió iterar cientos de veces.

### 2.3. Kimi K2.6 — el razonador profundo

| Característica | Valor |
|---|---|
| Parámetros | 595 GB |
| Contexto | 1M tokens |
| Plataforma | Ollama Cloud |

Kimi K2.6 brilla cuando una tarea requiere mantener una cadena de razonamiento larga y coherente. Especialmente útil en matemáticas donde cada paso depende del anterior.

**Cuándo brilla:**

- Demostraciones largas con dependencias entre pasos.
- Análisis de textos científicos extensos.
- Tareas donde el contexto de 1M tokens permite no perder detalles.

**Cuándo falla (lección real de Riemann Fase 2):**

En la fase de álgebra abstracta, Kimi K2.6 produjo un razonamiento que parecía coherente pero contenía un error estructural en la manipulación de una serie de Dirichlet. El problema no fue falta de inteligencia, sino que el modelo confundió una hipótesis auxiliar con una equivalencia demostrada. Es decir, razonó profundamente **sobre una base incorrecta** y no la cuestionó. Este tipo de fallo solo se detecta con verificación cruzada.

### 2.4. Qwen 3.6 — el sesgo alternativo

| Característica | Valor |
|---|---|
| Parámetros | 397 GB |
| Plataforma | NaN Builders |

Qwen 3.6 no está en el panel porque sea "mejor" que los demás. Está porque tiene un **sesgo distinto**. Su entrenamiento y arquitectura le hacen abordar ciertos problemas desde ángulos que GLM-5.2, DeepSeek o Kimi no exploran.

**Por qué un modelo con sesgo alternativo es valioso:**

En un sistema de consenso, la utilidad de un modelo no depende solo de su precisión media, sino de qué errores comete y si esos errores son diferentes a los del resto. Si tres modelos se equivocan de la misma manera, el consenso no sirve. Si el cuarto se equivoca de forma distinta, su discrepancia alerta del problema.

**Ejemplo real en Riemann:** Qwen 3.6 fue usado como sexto ángulo en una fase posterior, precisamente para detectar ciegos compartidos entre GLM-5.2, DeepSeek y Kimi.

### 2.5. Cogito 2.1 — el verificador independiente

| Característica | Valor |
|---|---|
| Parámetros | 689 GB |
| Plataforma | Ollama Cloud |

Cogito 2.1 tiene una tendencia natural a razonar de forma escéptica, lo cual lo convierte en un excelente verificador. No le das el contexto completo del builder; le das el resultado y le pides que lo valide desde cero.

**Por qué la verificación independiente importa:**

Un modelo que verifica su propio trabajo sufre de *rubber-stamping*: tiende a aceptar lo que ya ha generado. Un verificador externo no tiene ese compromiso emocional y puede detectar saltos lógicos, supuestos ocultos o errores de notación.

**Ejemplo real en Riemann:** Cogito verificó los resultados de DeepSeek V4 Flash en la fase de refutación. Encontró dos casos en los que una "contradicción" aparente era en realidad un error de normalización en los datos de entrada. Sin esa verificación, habríamos llegado a una conclusión falsa.

### 2.6. Tabla comparativa del panel

| Modelo | Tamaño | Contexto | Plataforma | Rol | Fortalezas | Debilidades |
|---|---|---|---|---|---|---|
| GLM-5.2 | 1,5 T / 1.508 GB | 1M | Ollama Cloud | Orquestador | Visión global, diseño de planes, detección de riesgos | Lento y caro para tareas repetitivas |
| DeepSeek V4 Flash | 140 GB | Estándar | NaN Builders | Ejecutor rápido | Baja latencia, buen throughput, razonamiento concentrado | Puede perder detalles en contextos muy largos |
| Kimi K2.6 | 595 GB | 1M | Ollama Cloud | Razonador profundo | Cadenas largas, dependencias complejas | Puede fallar en álgebra abstracta por confianza excesiva |
| Qwen 3.6 | 397 GB | Estándar | NaN Builders | Sesgo alternativo | Ángulos diferentes, detección de ciegos compartidos | Menos potente para razonamiento profundo |
| Cogito 2.1 | 689 GB | Estándar | Ollama Cloud | Verificador | Escrutinio independiente, detección de saltos lógicos | No debe ejecutar; solo verificar |

---

## 3. Contratos de trabajo (handoff)

### 3.1. Qué es un contrato y por qué no pasar todo el contexto

Un contrato de trabajo es la especificación que el orquestador entrega a un sub-agente. Su objetivo es comunicar **solo lo necesario** para que el sub-agente ejecute bien, sin saturarlo con el historial completo del proyecto.

Pasar todo el contexto parece intuitivo: cuanta más información, mejor. En la práctica, no. El contexto completo introduce ruido, aumenta el coste y eleva la probabilidad de que el modelo se distraiga con detalles irrelevantes o reprocese decisiones ya tomadas.

### 3.2. Los 4 elementos de un buen contrato

1. **Objetivo.** Qué debe lograrse, expresado como un resultado concreto y verificable.
2. **Entradas.** Datos, archivos, funciones o hipótesis que el sub-agente necesita.
3. **Restricciones.** Lo que no debe hacerse: formatos prohibidos, supuestos no autorizados, dependencias no tocar.
4. **Criterio de éxito.** Cómo saber que el trabajo está bien. Debe ser binario siempre que sea posible.

### 3.3. Ejemplo concreto: buen contrato vs. mal contrato

**Mal contrato:**

> "Mira el proyecto y mejora el código de tests."

Problemas: no define qué parte del proyecto, qué significa "mejorar", qué formato espera, ni cómo se verifica. El sub-agente puede reformatear todo, cambiar dependencias o producir algo inusable.

**Buen contrato:**

> **Objetivo:** Migrar los tests de `tests_legacy/test_calculo.py` de `unittest` a `pytest`, manteniendo el comportamiento exacto de cada test.  
> **Entradas:** El archivo `tests_legacy/test_calculo.py` y la lista de dependencias en `requirements-dev.txt`.  
> **Restricciones:** No modificar la lógica de negocio. No añadir dependencias nuevas. No eliminar tests; solo convertir sintaxis.  
> **Criterio de éxito:** `pytest tests/test_calculo.py` pasa con el mismo número de tests que `unittest discover` reportaba antes de la migración.

La diferencia es abismal: el segundo contrato elimina la ambigüedad y permite verificar el resultado mecánicamente.

### 3.4. Por qué pasar contexto completo falla

Cuando un sub-agente recibe demasiado contexto, ocurren tres cosas:

1. **Ruido.** El modelo empieza a considerar hipótesis, discusiones y decisiones del orquestador que no son relevantes para su tarea.
2. **Coste.** Cada token adicional cuesta latencia y dinero. En un sistema con muchos sub-agentes paralelos, esto se multiplica.
3. **Errores de atención.** Los modelos tienen atención finita. Si les das 50.000 tokens para una tarea que podría resolverse con 2.000, la calidad baja.

El contrato de trabajo es, en esencia, un filtro de contexto.

---

## 4. Prompt caching consciente

### 4.1. Cómo funciona el caching por prefijos en NaN Builders

NaN Builders ofrece caching por prefijos: si varias peticiones comparten un prefijo inicial idéntico, ese prefijo no se reprocesa. El ahorro puede ser enorme, especialmente con modelos como DeepSeek que ofrecen un descuento estimado del **98 % en cached tokens**.

El caching funciona a nivel de tokenización: la plataforma detecta que la secuencia de tokens iniciales coincide con una petición anterior y reutiliza la representación interna. Esto reduce tanto la latencia como el coste.

### 4.2. Estructura óptima del prompt

Para maximizar el caching, estructura el prompt en dos partes:

1. **Prefijo constante:** instrucciones, convenciones, formato de salida, ejemplos, personalidad del rol. Todo lo que no cambia entre peticiones.
2. **Sufijo variable:** la tarea concreta, los datos de entrada, las preguntas específicas.

Ejemplo:

```text
[PREFIJO CONSTANTE]
Eres un asistente matemático especializado en análisis numérico.
Reglas:
- Usa notación LaTeX para fórmulas.
- No inventes datos; indica explícitamente si falta información.
- Responde en español, con secciones numeradas.

[SUFIJO VARIABLE]
Analiza la siguiente serie de ceros no triviales de la función zeta de Riemann:
{datos}

Pregunta: ¿Existe algún par de ceros consecutivos cuya separación supere 3.5 unidades críticas?
```

### 4.3. El truco de calentar caché

Si vas a lanzar 20 sub-agentes en paralelo con el mismo prefijo, no los lances todos a la vez en frío. El primer sub-agente "calienta" la caché; los 19 siguientes se benefician.

**Pseudocódigo:**

```python
# 1. Enviar una petición de calentamiento con el prefijo completo
warmup = call_model(prefix=PREFIX_CONSTANTE, suffix="Tarea de calentamiento.")

# 2. Esperar la respuesta (cold start ~3.29s en NaN Builders, estimación operativa)
wait(warmup)

# 3. Lanzar el resto en paralelo; ahora el prefijo está en caché
results = parallel([
    call_model(prefix=PREFIX_CONSTANTE, suffix=tarea)
    for tarea in tareas
])
```

### 4.4. Lista de verificación para prompts cacheables

- ¿El prefijo es idéntico entre peticiones? Un solo cambio de coma rompe la caché.
- ¿He separado claramente lo constante de lo variable?
- ¿He usado marcadores explícitos como `[PREFIJO_CONSTANTE]` y `[SUFIJO_VARIABLE]`?
- ¿He calentado la caché antes de lanzar la carga masiva?
- ¿He medido latencia con y sin caché para confirmar el ahorro?

---

## 5. Verificación cruzada

### 5.1. Por qué un modelo no debe verificarse a sí mismo

Cuando un modelo verifica su propio resultado, tiene acceso a su propio razonamiento y tiende a confirmarlo. Este fenómeno, conocido coloquialmente como *rubber-stamping*, es especialmente peligroso en matemáticas y en código: el modelo no revisa realmente, sino que reescribe su propia conclusión con otras palabras.

### 5.2. Arquitectura Builder → Judge

La arquitectura básica es:

1. **Builder:** produce un resultado (demostración, código, análisis).
2. **Judge:** recibe solo el resultado y las entradas, sin ver el razonamiento del builder, y debe validarlo o refutarlo desde cero.
3. **Discrepancia:** si judge y builder no coinciden, se activa un tercer agente de arbitraje o se devuelve el caso al orquestador.

La clave es que el juez **no ve el proceso**, solo el producto. Esto fuerza una verificación genuina.

### 5.3. Qué pasa cuando discrepan

Cuando builder y judge discrepan, no asumas automáticamente que el judge tiene razón. Lo correcto es:

1. Registrar ambas posiciones.
2. Solicitar una justificación detallada al judge.
3. Revisar si la discrepancia viene de una ambigüedad en el contrato.
4. Si persiste, lanzar un tercer modelo como árbitro con un contrato neutral.
5. Si el árbitro confirma el fallo, devolver al builder para corrección.

### 5.4. Ejemplo real: Cogito verificando a DeepSeek en Riemann

En Riemann, DeepSeek V4 Flash produjo una cadena de argumentos que sugería una posible contradicción en los datos numéricos. Cogito 2.1 recibió solo el enunciado del argumento y los datos de entrada, sin ver el razonamiento de DeepSeek.

Cogito detectó que la "contradicción" desaparecía si se normalizaban los ceros con una constante de escala diferente. No era un error de razonamiento, sino un problema de normalización. Gracias a esa verificación cruzada, evitamos publicar un falso negativo.

---

## 6. Patrones de despliegue

### 6.1. Patrón 1: Orquestador con sub-agentes paralelos

**Analogía:** Un arquitecto dibuja el plano y manda a varios albañiles a construir paredes diferentes al mismo tiempo.

**Cuándo usarlo:**

- La tarea se puede dividir en subproblemas independientes.
- Quieres reducir latencia total mediante paralelización.
- Cada subproblema requiere un sesgo o una especialidad distinta.

**Ejemplo real:** En Riemann, el orquestador lanzó seis sub-agentes en paralelo, cada uno atacando la hipótesis desde un ángulo diferente (numérico, funcional, algebraico, histórico, computacional, crítico).

**Pros:** rápido, robusto ante sesgos individuales, fácil de escalar horizontalmente.  
**Contras:** requiere buenos contratos de trabajo; si las subtareas no son independientes, se generan conflictos.

### 6.2. Patrón 2: Cadena de especialistas secuenciales

**Analogía:** Una cadena de montaje: el producto pasa por estaciones especializadas, y cada estación añade o refina algo.

**Cuándo usarlo:**

- La salida de una fase es la entrada de la siguiente.
- Cada fase requiere un tipo de razonamiento distinto (ej. planificación → codificación → revisión → testing).

**Ejemplo real:** En un flujo de desarrollo de software: GLM-5.2 diseña la arquitectura, DeepSeek genera el código, Cogito revisa, y un tester automático ejecuta los tests.

**Pros:** claro, fácil de depurar por fases, permite puntos de control.  
**Contras:** la latencia total es la suma de las latencias; un cuello de botella ralentiza todo.

### 6.3. Patrón 3: Builder-Judge-Arbitro

**Analogía:** Un autor escribe un artículo, un revisor independiente lo corrige, y si no se ponen de acuerdo, interviene un editor jefe.

**Cuándo usarlo:**

- El coste de un error es alto.
- Necesitas confianza alta antes de aceptar un resultado.
- Tienes un modelo adecuado para juzgar de forma independiente.

**Ejemplo real:** Cogito verificando a DeepSeek en Riemann; cuando había discrepancias, GLM-5.2 actuaba como árbitro.

**Pros:** alta calidad, detección de errores sutiles.  
**Contras:** más lento y más caro; no es necesario para tareas de bajo riesgo.

---

## 7. Métricas de rendimiento en NaN Builders

A continuación resumimos métricas reales obtenidas en nuestras pruebas con NaN Builders, especialmente con DeepSeek V4 Flash.

| Métrica | Valor | Interpretación práctica |
|---|---|---|
| Latencia mediana aproximada | 0,76 s | Respuesta rápida para sub-agentes en paralelo |
| Latencia Ollama Cloud aproximada (mismo modelo) | 2,37 s | NaN Builders es ~3× más rápido para este modelo |
| Throughput estimado | ~145 tok/s | Adecuado para respuestas de moderada longitud |
| Cold start aproximado | 3,29 s | Primera petición tras inactividad; esperable |
| Latencia tras caché caliente aproximada | 0,57–0,78 s | Muy estable una vez el prefijo está cacheado |
| Cuota | 500M tokens/mes por modelo | Suficiente para cientos de miles de llamadas |

### Qué significan estos números en la práctica

Supongamos que cada sub-agente consume 2.000 tokens de salida y 1.000 de entrada, y que un flujo típico lanza 20 sub-agentes en paralelo.

- 20 sub-agentes × 3.000 tokens = 60.000 tokens por ejecución.
- Con 500M tokens/mes, puedes ejecutar ese flujo unas 8.300 veces al mes, es decir, ~275 veces al día.

Si usas caché consciente, la cuota se estira mucho más. Y si alternas entre NaN Builders para tareas rápidas y Ollama Cloud para tareas de razonamiento profundo, optimizas costes sin sacrificar calidad.

---

## 8. Anti-patrones

### 8.1. El monolito de un solo modelo

**Qué es:** usar el modelo más grande para todo.  
**Por qué falla:** lento, caro, y hereda todos los sesgos del modelo.  
**Cómo evitarlo:** diseñar un panel de modelos con roles.

### 8.2. El contexto vampiro

**Qué es:** pasar todo el historial del proyecto a cada sub-agente.  
**Por qué falla:** introduce ruido, aumenta costes y reduce la atención sobre la tarea concreta.  
**Cómo evitarlo:** usar contratos de trabajo con los cuatro elementos.

### 8.3. La verificación de iguales

**Qué es:** pedirle al mismo modelo que genere y verifique.  
**Por qué falla:** sufre de rubber-stamping; no detecta sus propios errores sistemáticos.  
**Cómo evitarlo:** separar builder y judge en modelos distintos, idealmente con sesgos diferentes.

### 8.4. El consenso ingenuo

**Qué es:** asumir que si tres modelos coinciden, la respuesta es correcta.  
**Por qué falla:** los modelos pueden compartir sesgos o datos de entrenamiento comunes.  
**Cómo evitarlo:** incluir al menos un modelo con sesgo alternativo (como Qwen 3.6) y analizar las razones, no solo los votos.

### 8.5. La parálisis por orquestación

**Qué es:** dividir el trabajo en demasiados sub-agentes con contratos excesivamente complejos.  
**Por qué falla:** el overhead de coordinación supera el beneficio de la especialización.  
**Cómo evitarlo:** empezar con dos o tres roles y añadir más solo cuando haya evidencia de que mejora la calidad.

### 8.6. El descuido de métricas

**Qué es:** orquestar sin medir latencia, coste, tokens ni tasa de error.  
**Por qué falla:** no puedes optimizar lo que no mides, y terminas pagando por ineficiencias invisibles.  
**Cómo evitarlo:** instrumentar cada llamada: modelo, tokens, latencia, resultado y discrepancias.

---

## 9. Conclusión

La orquestación multi-modelo no es un truco para usar más GPUs. Es una disciplina de diseño de sistemas. Lo que cambia de verdad es la pregunta central: deja de ser "¿qué modelo uso?" y se convierte en "**qué responsabilidad tiene cada modelo**".

Cuando diseñas con responsabilidades claras, contratos de trabajo precisos, caching consciente y verificación cruzada, obtienes sistemas que son al mismo tiempo más baratos, más rápidos y más fiables que un solo modelo grande usado a ciegas.

Este repo es un trabajo vivo. Si tienes un caso de uso, una métrica o un patrón que no está aquí, contribuye. La comunidad NaN Builders ([@borjaperfra](https://x.com/borjaperfra)) avanza más rápido cuando compartimos no solo prompts, sino arquitecturas.

---

## 10. Más allá de secuencial: patrones swarm

La guía hasta aquí describe orquestación **secuencial** (orquestador → sub-agentes → verificación). Cuando el problema lo permite, el siguiente nivel es la orquestación **enjambre (swarm)**: lanzar N agentes en paralelo sobre la misma pregunta, con sesgos de rol distintos, y reducir con reglas explícitas de voto, arbitraje o consenso.

**Patrones cubiertos en [docs/swarm-patterns.md](docs/swarm-patterns.md):**

1. **Fan-out/fan-in** — divergir en perspectivas complementarias y converger.
2. **Jurado** — jueces independientes (sin contexto de producción) dictaminan PASS/FAIL.
3. **Especialistas cruzados** — dos modelos se contradicen controladamente, el orquestador arbitra.
4. **Red-team** — un adversario deliberado intenta romper el resultado; el defensor lo parchea.
5. **Multiverse** — rutas alternativas con metodologías distintas cuando no se sabe cuál es la vía.

**Plantilla operativa en [templates/jurado-verificacion.md](templates/jurado-verificacion.md)** — el paquete de veredicto y las reglas de decisión para el patrón más usado (jurado).

**Recuerda los límites reales de NaN para swarm:** 60 rpm, 5 concurrentes, 1.5M tpm por modelo, cuotas mensuales (deepseek 2B, mimo 1B). El fan-out bien cacheado es barato; el fan-out sin diseñar el prefijo común es caro.
