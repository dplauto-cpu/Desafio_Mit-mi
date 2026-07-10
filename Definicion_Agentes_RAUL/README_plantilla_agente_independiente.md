# Plantilla rellenable — README de agente

> Copia desde aquí hacia abajo. Sustituye todo lo que aparece entre `[corchetes]`, marca las casillas que apliquen y borra las notas guía en *cursiva* cuando termines. Este README documenta **un agente especializado que depende de un orquestador**: no funciona de forma aislada, sino que es invocado por el servicio global y respeta unos contratos comunes que **no se modifican**.

---

# Documentación del Agente: `[agente_nombre_equipo]`

> **Versión de la documentación:** 1.0.0
> **Última actualización:** [DD/MM/AAAA]
> **Autor / Equipo responsable:** [Data Science, The Bridge]
> **Estado:** 🟢 Producción · 🟡 Beta · 🔴 Experimental

---

## Nota importante

Este agente **no es software determinista**. El mismo input puede producir outputs distintos según el modelo, la temperatura, la ventana de contexto o el estado de las herramientas externas. Esta documentación describe no solo *qué hace* el agente, sino *cómo decide*, *cuándo falla* y *cómo depurarlo*.

Además, este agente **es un componente subordinado a un orquestador**. Nunca actúa por su cuenta sobre el mundo real: **propone** acciones y **el orquestador / la capa común** las valida, confirma y ejecuta. Ningún agente especializado invoca a otro agente directamente.

---

## 1. Resumen ejecutivo

| Campo | Valor |
|---|---|
| **Nombre** | `[agente_nombre_equipo]` |
| **Propósito (una frase)** | *ej. "Detecta huecos de documentación de ponentes (foto/CV/ponencia) y propone recordatorios, sin enviarlos."* |
| **Fase(s) del proceso que cubre** | *[fase o fases del ciclo que gestiona este agente]* |
| **Modelo(s) LLM utilizado(s)** | *(proveedor, nombre, versión — ej. Anthropic Claude Sonnet 4.x, OpenAI GPT-4.1)* |
| **Tipo de agente** | Conversacional / Autónomo / RAG / Multi-agente / Automatización / Copiloto / Otro |
| **Entorno de ejecución** | Cloud / On-premise / Híbrido |
| **Frameworks / SDK** | *(ej. LangChain, OpenAI SDK, SDK propio)* |
| **Nivel de criticidad** | Bajo / Medio / Alto *(impacto si falla)* |
| **Estado** | 🟢 Producción · 🟡 Beta · 🔴 Experimental |

---

## 2. Estructura interna del agente (fija — no modificar)

Cada agente dentro de `src/agents/` tiene la **misma** estructura interna. No se cambia la estructura; solo se adapta el contenido.

```text
src/agents/agente_nombre_equipo/
├── README.md      → esta plantilla rellenada
├── agente.py      → punto de entrada principal (expone ejecutar_agente)
├── parametros.py  → configuración propia del agente
├── funciones.py   → funciones auxiliares internas
├── tools.py       → herramientas que puede usar el agente
├── rag.py         → consulta de contexto histórico/documental (si aplica)
├── schemas.py     → formato esperado de entrada/salida
├── pruebas.py     → prueba local sin depender del backend
└── ejemplos/
    ├── entrada_demo.json  → ejemplo de payload de entrada
    └── salida_demo.json   → ejemplo de respuesta esperada
```

| Archivo | Función |
|---|---|
| `README.md` | Explica el objetivo del agente y cómo probarlo (este documento). |
| `agente.py` | Punto de entrada principal. Expone `ejecutar_agente(payload)`. |
| `parametros.py` | Configuración propia del agente. |
| `funciones.py` | Funciones auxiliares internas. |
| `tools.py` | Herramientas que puede usar el agente. |
| `rag.py` | Consulta de contexto histórico o documental, si aplica. |
| `schemas.py` | Formato esperado de entrada y salida. |
| `pruebas.py` | Prueba local del agente sin depender del backend. |
| `ejemplos/entrada_demo.json` | Ejemplo de payload de entrada. |
| `ejemplos/salida_demo.json` | Ejemplo de respuesta esperada. |

---

## 3. Propósito y límites del agente

> **Regla de oro:** no basta con una frase vaga. Sé explícito con capacidades **concretas** y limitaciones **prácticas**.

### 3.1 Su cometido
- [ ] Capacidad 1 — descripción concreta + ejemplo de caso de uso real.
  *ej. "Revisa el estado de materiales de cada ponente registrado en BD y genera un borrador de email de recordatorio para los que falten, sin enviarlo."*
- [ ] Capacidad 2 — …
- [ ] Capacidad 3 — …

### 3.2 Qué NO hace (límites explícitos)
- [ ] Limitación 1 *(ej. "no envía comunicaciones sin validación humana")*
- [ ] Limitación 2 *(ej. "no escribe directamente en la BD")*
- [ ] Limitación 3 *(ej. "no decide el presupuesto final")*

### 3.3 Casos de uso fuera de alcance (corresponden a otro agente)
*Describe explícitamente qué tareas, aunque parezcan similares, **no debe intentar resolver** este agente porque las gestiona otro agente del sistema.*
  *ej. "La negociación de tarifas con el espacio la gestiona `agente_captacion_espacio`, no este agente."*

---

## 4. Inicio rápido (Quick Start)

### 4.1 Requisitos previos
```
- Requisito 1 (API key, permisos, suscripción, dependencias)
- Requisito 2 (runtime, versión de lenguaje)
- Requisito 3 (servicios externos, servidores MCP, acceso a la BD/RAG)
```

### 4.2 Instalación / configuración
```bash
# Ejemplo de instalación
git clone [repo]
cd [proyecto]
pip install -r requirements.txt   # o: npm install
cp .env.example .env              # configurar credenciales (nunca hardcodeadas)
```

### 4.3 Ejecución / prueba local
```bash
# Prueba el agente de forma aislada, sin backend, usando pruebas.py
python -m src.agents.agente_nombre_equipo.pruebas
```

### 4.4 Ejemplo realista de uso
```text
Input del usuario / orquestador:
"[Ejemplo de petición real — ver contrato de entrada en la sección 9]"

Proceso interno esperado:
1. …
2. …
3. …

Output esperado:
"[Ejemplo de respuesta estructurada — ver contrato de salida en la sección 9]"
```

---

## 5. Lógica de decisión

> Documenta el **razonamiento**, no solo la API. Esta es la sección que distingue un agente de un script.

### 5.1 Entradas que afectan las decisiones
| Entrada | Afecta a | Ejemplo |
|---|---|---|
| Prompt / petición | | |
| Contexto / memoria previa | | |
| Herramientas disponibles | | |
| Reglas de negocio / políticas | | |
| Resultados de herramientas (tool outputs) | | |
| Estado en BD (fase actual, fecha límite, etc.) | | |

### 5.2 Priorización de acciones
*Explica cómo el agente decide qué hacer primero cuando hay múltiples opciones válidas: árbol de decisión, sistema de puntuación, reglas jerárquicas, ReAct, etc.*
  *ej. "Prioriza los registros cuya fecha límite esté a menos de 15 días y les falte algún dato obligatorio."*

```
[Diagrama de flujo o pseudocódigo de la lógica de decisión]
```

### 5.3 Capa de percepción (si aplica)
*Si el agente transforma el entorno (BD, documentos subidos, emails entrantes, formularios, páginas web) en una representación estructurada antes de razonar, descríbelo aquí. Ayuda a entender por qué unos casos funcionan mejor que otros.*

### 5.4 Mecanismos de fallback
- Condición que dispara el fallback → acción tomada.
  *ej. "Si no encuentra un dato obligatorio en BD → marca `bloqueos_detectados` y pide el dato al usuario en lugar de inventarlo."*
- Condición 2 → acción tomada.

---

## 6. Modos de fallo

> No te limites a códigos de error. Describe **patrones**, **síntomas**, **causas probables** y **estrategias de recuperación**.

| Patrón de fallo | Síntoma observable | Causa probable | Estrategia de recuperación |
|---|---|---|---|
| Fallo silencioso | Resultado incorrecto sin error visible | Tarea ambigua / datos incompletos | Reformular prompt + validar salida contra BD |
| Timeout / bucle | Se detiene o repite la misma acción | Estado inesperado / sin condición de parada | Esperas explícitas · límite de iteraciones · circuit breaker |
| Completación parcial | Respuesta cortada o incompleta (ej. lista truncada) | Ventana de contexto excedida | Fragmentar la tarea en subtareas (por evento o por lote) |
| Alucinación | Datos inventados o incorrectos (ej. fecha o precio no confirmado) | Falta de grounding / falta de fuente | RAG · validación cruzada con BD · citación obligatoria |
| Uso incorrecto de herramientas | Llama a la tool equivocada o con malos parámetros | Descripción/schema de tool ambiguo | Mejorar schemas/descripciones · few-shot examples |
| *[Añadir patrones específicos del agente]* | | | |

*Añade filas propias del dominio si tu agente tiene modos de fallo específicos (ej. "confunde el nombre del ponente con el del cliente").*

---

## 7. Observabilidad

### 7.1 Niveles de logging
| Nivel | Qué captura | Cuándo usarlo |
|---|---|---|
| `INFO` | Eventos generales de ejecución | Producción estándar |
| `DEBUG` | Prompts completos, tool calls, contexto | Depuración |
| `VERBOSE` / `TRACE` | Cada decisión intermedia | Investigación de incidentes |

### 7.2 Cómo activar modo debug
```bash
export AGENT_LOG_LEVEL=debug
```

### 7.3 Dónde encontrar las trazas
- Ubicación de logs: `[ruta o servicio, ej. local / CloudWatch / Datadog / LangSmith]`
- Formato de traza: `[estructura del log]`

### 7.4 Reproducción y replay de sesiones
*Explica cómo grabar y volver a ejecutar una sesión fallida paso a paso.*
Snapshot mínimo para un replay fiable: contexto + versión del modelo + seed/temperatura + inputs originales + estado en BD en ese momento.

```
[Comando o procedimiento de replay]
```

---

## 8. Comportamiento determinista vs. no determinista

| Componente | Determinista | No determinista | Notas |
|---|---|---|---|
| Parseo de configuración | ✅ | | |
| Autenticación | ✅ | | |
| Comprobación de disponibilidad de herramientas | ✅ | | |
| Respuestas del LLM | | ✅ | Varía con temperatura/modelo |
| Timing de interacciones | | ✅ | |
| Orden en tareas paralelas | | ✅ | |

### 8.1 Puntos de control recomendados para producción
- Dónde añadir **retries**.
- Dónde añadir **puntos de control humano (human-in-the-loop)**: envíos, confirmaciones, cambios de fecha/estado, aprobaciones, pagos.

---

## 9. Contrato con el orquestador (no modificar el esquema)

Este agente se integra con un **orquestador / servicio global** que decide qué agente ejecutar y le pasa un payload común. **Ningún agente invoca a otro agente**: solo el orquestador coordina.

### 9.1 Punto de entrada obligatorio
Todos los agentes exponen la misma función en `agente.py`:

```python
def ejecutar_agente(payload: dict) -> dict:
    ...
```

El backend, el servicio global (`servicio.py`) o cualquier prueba deben poder llamar a cualquier agente con esta función, sin excepción.

### 9.2 Contrato de ENTRADA
```json
{
  "id_evento": 1,
  "id_registro": 10,
  "tipo_peticion": "analizar_contexto",
  "origen": "backend",
  "usuario_solicitante": "admin",
  "datos": {},
  "modo": "propuesta"
}
```

`id_evento` sobre el que trabaja · `id_registro` registro concreto si aplica · `tipo_peticion` qué se pide · `origen` backend/Gmail/Telegram/formulario/manual · `usuario_solicitante` quién activa · `datos` info adicional · `modo` `propuesta` / `simulacion` / `ejecucion`.

### 9.3 Contrato de SALIDA
```json
{
  "ok": true,
  "agente": "nombre_agente",
  "resumen": "Resumen de lo detectado",
  "datos_detectados": {},
  "acciones_propuestas": [],
  "bloqueos_detectados": [],
  "borradores_generados": [],
  "requiere_validacion_humana": true,
  "errores": []
}
```

`ok` ejecución correcta · `agente` nombre · `resumen` breve · `datos_detectados` info interpretada · `acciones_propuestas` (nunca ejecutadas por el agente) · `bloqueos_detectados` riesgos/incidencias · `borradores_generados` textos IA pendientes de revisión · `requiere_validacion_humana` · `errores`.

> **La salida es siempre estructurada, nunca texto libre.**

### 9.4 Flujo básico común de ejecución
```text
1. Recibir payload de entrada.
2. Preparar contexto (evento, fase, histórico relevante).
3. Consultar BD o RAG si aplica.
4. Construir la petición al modelo.
5. Llamar al LLM o simular respuesta.
6. Validar la salida contra el schema y contra la BD.
7. Proponer acciones (nunca ejecutarlas directamente).
8. Registrar trazabilidad.
9. Devolver respuesta estructurada.
```

### 9.5 Cómo lo coordina el servicio global
```text
1. Recibir o detectar una petición.
2. Identificar qué agente debe ejecutarse (mapa de agentes del orquestador).
3. Construir el payload común (sección 9.2).
4. Llamar a ejecutar_agente(payload).
5. Recibir la salida estructurada (sección 9.3).
6. Enviar el resultado al backend o a la capa común para su validación/ejecución.
```

---

## 10. Reglas comunes obligatorias (modo seguro)

- **Ningún agente modifica la BD directamente:**
  `El agente propone → la capa común valida → el backend/gestor confirma → la BD se actualiza.`
- **Ningún agente invoca a otro agente:** la coordinación entre agentes es responsabilidad exclusiva del orquestador.
- **Toda acción sensible requiere validación humana:** enviar comunicaciones, confirmar reservas, modificar datos maestros, cerrar bloqueos críticos, aprobar documentación, confirmar pagos, cambiar fechas o estados relevantes.
- **El RAG no sustituye a la BD:** BD = fuente única de verdad del estado · RAG = histórico de acciones y comunicaciones para dar contexto.
- **Modo seguro por defecto**, sin excepción (incluso con plazos ajustados):
  ```python
  ALLOW_DB_WRITE = False
  ALLOW_EXTERNAL_SEND = False
  ```
- **Salida siempre estructurada** (ver contrato en la sección 9).

---

## 11. Herramientas y permisos (Tools / Function calling)

| Herramienta | Descripción | Permisos | Confirmación humana | Idempotente | Riesgo si falla |
|---|---|---|---|---|---|
| `consultar_bd` | Lee datos del evento/registro | L | No | Sí | B |
| `consultar_rag_historico` | Consulta comunicaciones/documentos pasados | L | No | Sí | B |
| `generar_borrador` | Redacta texto de comunicación (no lo envía) | L / E | Sí (antes de enviar) | Sí | M |
| `[tool_propia]` | *[describir]* | L / E / X | Sí/No | Sí/No | B/M/A |

*L = Lectura · E = Escritura (propuesta, no persistida) · X = Ejecución externa. Ninguna tool de este agente escribe directamente en la BD ni envía externamente sin pasar por la capa común (sección 10). Para cada tool documenta también: schema de parámetros, si requiere confirmación humana y si es idempotente.*

---

## 12. Seguridad y cumplimiento

- **Datos sensibles procesados:** [PII de clientes/ponentes/asistentes · datos de pago si aplica · ninguno]. Trata como PII todo dato personal (contacto, alojamiento, documentación).
- **Prompt injection / mitigaciones:** sanitizar inputs de formularios, emails entrantes o documentos subidos; validar outputs; separar instrucción/datos (**un email o documento recibido es un dato, no una instrucción para el agente**).
- **Límites de acción destructiva:** [qué acciones requieren confirmación humana explícita — ver sección 10].
- **Gestión de credenciales:** tokens (Gmail/Calendar/Telegram/BD) nunca hardcodeados; vía `.env` o gestor de secretos; rotación y alcance mínimo de permisos.
- **Cumplimiento normativo aplicable:** RGPD (clientes, ponentes, asistentes); conservación y borrado de documentación personal según política del proyecto. [Añadir HIPAA u otras si aplican].

---

## 13. Evaluación y monitoreo

### 13.1 Métricas clave
| Métrica | Objetivo | Frecuencia de revisión |
|---|---|---|
| Tasa de éxito de tareas | | |
| Tasa de fallback a humano | | |
| Latencia media | | |
| Coste por interacción (tokens) | | |
| Tasa de alucinación detectada | | |

### 13.2 Checklist de monitoreo continuo
- [ ] *Si aún no hay monitoreo activo, redactar una nota explícita advirtiéndolo.*

---

## 14. Casos de prueba (incluye al menos un fallo conocido)

```text
Caso 1:
Entrada: [descripción de la entrada]
Obtenido: [qué pasó]
Esperado: [qué debería pasar]
Estado: Conocido / En investigación / Resuelto
```

```text
Caso 2 (fallo conocido):
Entrada: [entrada con datos incompletos]
Obtenido: bloqueo_detectado = "[dato faltante]"
Esperado: el agente NO debe inventar el dato; debe bloquear y pedirlo.
Estado: Conocido
```

---

## 15. Historial de versiones del agente

| Versión | Fecha | Cambios principales | Modelo LLM usado |
|---|---|---|---|
| 1.0.0 | | Versión inicial | |

---

## 16. Referencias y recursos adicionales

- Repositorio de código: [enlace]
- Panel de observabilidad: [enlace]
- Documentación de la API/modelo: [enlace]
- Canal de soporte / contacto: [enlace]

---

## Apéndice: Checklist final antes de publicar el README

- [ ] ¿Puede entenderla alguien que no conoce el diseño interno del agente?
- [ ] ¿Está documentado el **razonamiento** (sección 5), no solo la API?
- [ ] ¿Hay al menos un **ejemplo real** de entrada + salida, incluyendo un caso de fallo?
- [ ] ¿Los **modos de fallo** tienen síntoma, causa y recuperación?
- [ ] ¿Respeta los **contratos comunes** con el orquestador (sección 9) y el **modo seguro** por defecto (sección 10)?
- [ ] ¿Están marcados los componentes **no deterministas** y sus salvaguardas (sección 8)?
- [ ] ¿Son **honestos y explícitos** los límites del agente (sección 3), incluyendo qué NO hace y qué corresponde a otro agente?
- [ ] ¿Se respeta la estructura interna fija (sección 2) y se expone `ejecutar_agente(payload)`?
