# README — Agente Orquestador MVP

Proyecto: **Gestión Inteligente de Eventos**  
Tipo de componente: **Orquestador ligero de agentes IA**  
Versión plantilla: **1.1.0**

---

## 0. Idea principal

El **agente orquestador** coordina la comunicación entre:

```text
Frontend / Backend de la app
        ↓
Agente orquestador
        ↓
Agentes especializados
        ↓
Agente orquestador
        ↓
Backend de la app
        ↓
Frontend / BBDD
```

El orquestador no es un agente especialista en eventos. No debe contener la lógica concreta de ponentes, espacios, presupuesto, comunicación, producción o cierre.

Debe saber:

```text
1. Recibir una petición del backend o de una prueba local.
2. Pedir contexto al backend si lo necesita.
3. Decidir qué agente especializado debe actuar.
4. Construir el payload común.
5. Llamar al agente correspondiente.
6. Validar la respuesta del agente.
7. Devolver el resultado al backend.
```

---

## 1. Regla arquitectónica clave

```text
El orquestador coordina.
El agente especializado razona y propone.
El backend valida, guarda y ejecuta.
La BBDD es la fuente de verdad.
```

Por tanto, el orquestador:

- no escribe directamente en la BBDD final;
- no envía emails directamente;
- no confirma reservas directamente;
- no modifica estados críticos del evento directamente;
- no contiene prompts específicos de cada agente;
- no contiene RAG específico de cada agente;
- no sustituye al backend;
- no sustituye a los agentes especializados.

---

## 2. Regla crítica no modificable

La comunicación del orquestador con todos los agentes debe ser siempre igual.

Todos los agentes especializados deben exponer:

```python
def ejecutar_agente(payload: dict) -> dict:
    ...
```

El orquestador debe llamar siempre a los agentes usando el mismo contrato:

```text
orquestador → payload común → ejecutar_agente(payload) → respuesta estructurada
```

La llamada podrá hacerse de dos formas:

```text
MVP local:
orquestador importa el agente en Python y llama ejecutar_agente(payload)

Futuro:
orquestador llama a una API del agente que internamente ejecuta ejecutar_agente(payload)
```

La tecnología puede cambiar. **El contrato no cambia**.

---

## 3. Comunicación con el backend

El orquestador también debe comunicarse con el backend de la app.

```text
Backend → Orquestador
```

Para recibir peticiones del usuario, por ejemplo:

```text
"Revisa la documentación pendiente de los ponentes del evento 12"
```

```text
Orquestador → Backend
```

Para:

- pedir datos del evento;
- pedir datos de ponentes, espacios, proveedores o tareas;
- devolver resultados generados por agentes;
- enviar acciones propuestas para validación;
- devolver borradores generados;
- registrar trazabilidad si el backend lo permite.

Regla:

```text
El orquestador puede consultar el backend.
El orquestador puede devolver propuestas al backend.
El backend decide qué guardar o ejecutar.
```

---

## 4. Estructura conceptual del orquestador

```text
src/orchestrator/
│
├── README.md
│   └── Documenta la función del orquestador, límites, contratos y flujo de integración.
│
├── main.py
│   └── Permite ejecutar el orquestador directamente para pruebas locales.
│      Usa inputs de ejemplo y simula la llamada a backend/agentes.
│
├── .env
│   └── Configuración real del orquestador.
│      Puede contener URL del backend, modo local/API, modelo LLM para routing, timeouts y permisos.
│      No debe subirse al repositorio.
│
├── .env.example
│   └── Plantilla sin secretos para documentar variables necesarias.
│
├── config/
│   └── Configuración Python del orquestador:
│      agentes disponibles, endpoints backend, modo demo, timeouts, permisos y routing.
│
├── prompts/
│   └── Prompts propios del orquestador solo si se usa LLM para clasificar intención.
│      No contiene prompts específicos de agentes especializados.
│
├── src/
│   └── Código principal del orquestador:
│      router, registro de agentes, construcción de payloads, validación, backend client y consolidación.
│
├── inputs/
│   └── Peticiones de ejemplo para probar el orquestador sin frontend ni backend real.
│
├── integrations/
│   └── Adaptadores de comunicación:
│      backend de la app, agentes locales o agentes publicados como API.
│
├── data/
│   └── Datos auxiliares del orquestador:
│      mocks del backend, mapa de agentes, ejemplos de rutas y respuestas simuladas.
│
├── outputs/
│   └── Resultados generados en pruebas locales:
│      respuestas consolidadas, payloads enviados a agentes y respuestas para backend.
│
└── logs/
    └── Registro de peticiones, agentes invocados, errores, tiempos y resultados.
```

---

## 5. Estructura mínima obligatoria

```text
src/orchestrator/
│
├── README.md
├── main.py
├── .env.example
│
├── src/
│   ├── orquestador.py
│   ├── router.py
│   ├── schemas.py
│   ├── registry.py
│   ├── payload_builder.py
│   ├── backend_client.py
│   └── agent_client.py
│
├── inputs/
│   └── payload_demo.json
│
└── outputs/
    ├── respuestas_backend/
    └── respuestas_agentes/
```

---

## 6. Estructura recomendada completa

```text
src/orchestrator/
│
├── README.md
├── main.py
├── .env
├── .env.example
│
├── config/
│   ├── settings.py
│   ├── agentes.py
│   ├── backend.py
│   └── permisos.py
│
├── prompts/
│   ├── prompt_clasificar_intencion.md
│   └── README.md
│
├── src/
│   ├── orquestador.py
│   ├── router.py
│   ├── registry.py
│   ├── schemas.py
│   ├── validaciones.py
│   ├── payload_builder.py
│   ├── consolidacion.py
│   ├── backend_client.py
│   ├── agent_client.py
│   ├── auditoria.py
│   └── errores.py
│
├── inputs/
│   ├── payload_demo_ponentes.json
│   ├── payload_demo_espacios.json
│   ├── payload_demo_presupuesto.json
│   └── payload_demo_comunicacion.json
│
├── integrations/
│   ├── backend_api.py
│   ├── agentes_locales.py
│   └── agentes_api.py
│
├── data/
│   ├── mock_backend/
│   ├── mapa_agentes.json
│   └── ejemplos/
│
├── outputs/
│   ├── respuestas_backend/
│   ├── respuestas_agentes/
│   ├── payloads_generados/
│   └── trazas/
│
└── logs/
    └── orquestador.log
```

---

## 7. Archivo `.env` del orquestador

Ejemplo orientativo:

```env
# Modo de ejecución
MODO_DEMO=True
ENVIRONMENT=local

# Backend de la app
BACKEND_BASE_URL=http://localhost:8000
BACKEND_TIMEOUT_SECONDS=20

# Modo de llamada a agentes
AGENTS_CALL_MODE=local
AGENTS_BASE_URL=

# Routing
USAR_LLM_ROUTER=False
MAX_AGENTES_POR_PETICION=1
TIMEOUT_AGENTES_SEGUNDOS=30

# LLM opcional para clasificar intención
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.0
OPENAI_API_KEY=poner_api_key_aqui

# Permisos de seguridad
ALLOW_DB_WRITE=False
ALLOW_EXTERNAL_SEND=False
ALLOW_AUTO_APPROVAL=False

# Logs
LOG_LEVEL=INFO
```

Reglas:

```text
.env contiene configuración real y secretos locales.
.env.example contiene la plantilla sin secretos.
.env no se sube al repositorio.
.env.example sí se sube al repositorio.
```

El `.gitignore` del proyecto debe incluir:

```gitignore
.env
*.log
outputs/
```

---

## 8. Mapa de agentes

El orquestador debe tener un registro claro de agentes disponibles.

Ejemplo en `config/agentes.py` o `data/mapa_agentes.json`:

```json
{
  "agente_espacios": {
    "nombre": "agente_espacios",
    "fase": "captacion_espacio",
    "modo_llamada": "local",
    "ruta_import": "src.agents.agente_espacios.src.agente",
    "funcion": "ejecutar_agente",
    "tipos_peticion": [
      "buscar_espacios",
      "comparar_espacios",
      "analizar_requisitos_espacio"
    ]
  },
  "agente_ponentes": {
    "nombre": "agente_ponentes",
    "fase": "ponentes_contenido",
    "modo_llamada": "local",
    "ruta_import": "src.agents.agente_ponentes.src.agente",
    "funcion": "ejecutar_agente",
    "tipos_peticion": [
      "revisar_documentacion_ponentes",
      "generar_recordatorio_ponente",
      "analizar_logistica_ponente"
    ]
  }
}
```

---

## 9. Contrato de entrada desde backend al orquestador

El backend puede enviar una petición como esta:

```json
{
  "id_evento": 12,
  "mensaje_usuario": "Revisa qué documentación falta de los ponentes",
  "tipo_peticion": "revisar_documentacion_ponentes",
  "usuario_solicitante": "admin",
  "rol_usuario": "organizador",
  "origen": "frontend",
  "datos": {},
  "modo": "propuesta"
}
```

---

## 10. Payload que el orquestador envía al agente

El orquestador transforma la petición del backend en el contrato común del agente:

```json
{
  "id_evento": 12,
  "id_registro": null,
  "tipo_peticion": "revisar_documentacion_ponentes",
  "origen": "orquestador",
  "usuario_solicitante": "admin",
  "rol_usuario": "organizador",
  "datos": {},
  "contexto": {
    "fase_evento": "ponentes",
    "fecha_evento": "2026-07-17",
    "estado_evento": "en_preparacion"
  },
  "modo": "propuesta"
}
```

---

## 11. Respuesta que recibe del agente

Todos los agentes devuelven el mismo formato:

```json
{
  "ok": true,
  "agente": "agente_ponentes",
  "tipo_peticion": "revisar_documentacion_ponentes",
  "resumen": "Hay 3 ponentes con documentación incompleta.",
  "datos_detectados": {},
  "acciones_propuestas": [],
  "bloqueos_detectados": [],
  "borradores_generados": [],
  "requiere_validacion_humana": true,
  "nivel_riesgo": "medio",
  "errores": [],
  "trazas": {
    "fuentes_consultadas": [],
    "timestamp": "2026-07-08T09:00:00",
    "modo": "propuesta"
  }
}
```

---

## 12. Respuesta que el orquestador devuelve al backend

El orquestador puede envolver la respuesta del agente y devolverla al backend:

```json
{
  "ok": true,
  "orquestador": "orquestador_mvp",
  "agente_invocado": "agente_ponentes",
  "id_evento": 12,
  "respuesta_agente": {
    "ok": true,
    "agente": "agente_ponentes",
    "resumen": "Hay 3 ponentes con documentación incompleta.",
    "acciones_propuestas": [],
    "bloqueos_detectados": [],
    "borradores_generados": [],
    "requiere_validacion_humana": true
  },
  "acciones_para_backend": [],
  "errores": [],
  "trazas": {
    "routing": "tipo_peticion",
    "timestamp": "2026-07-08T09:00:00"
  }
}
```

---

## 13. Flujo interno del orquestador

```text
1. Recibe petición desde backend o inputs demo.
2. Valida la entrada.
3. Consulta backend si necesita contexto del evento.
4. Decide qué agente invocar.
5. Construye payload común para el agente.
6. Llama al agente: ejecutar_agente(payload).
7. Valida respuesta estructurada.
8. Consolida resultado.
9. Devuelve respuesta al backend.
10. Registra trazabilidad.
```

---

## 14. Routing recomendado para el MVP

Para el MVP, usar reglas simples antes que LLM.

Ejemplo:

```python
MAPA_TIPO_PETICION = {
    "buscar_espacios": "agente_espacios",
    "comparar_espacios": "agente_espacios",
    "revisar_documentacion_ponentes": "agente_ponentes",
    "generar_recordatorio_ponente": "agente_ponentes",
    "analizar_presupuesto": "agente_presupuesto",
    "generar_borrador_comunicacion": "agente_comunicacion"
}
```

El LLM para clasificar intención puede añadirse después, pero no debe ser imprescindible para la demo.

---

## 15. Funciones principales esperadas

### `src/orquestador.py`

```python
def ejecutar_orquestador(payload_backend: dict) -> dict:
    ...
```

### `src/router.py`

```python
def seleccionar_agente(payload_backend: dict) -> str:
    ...
```

### `src/payload_builder.py`

```python
def construir_payload_agente(payload_backend: dict, contexto_backend: dict) -> dict:
    ...
```

### `src/agent_client.py`

```python
def llamar_agente(nombre_agente: str, payload_agente: dict) -> dict:
    ...
```

### `src/backend_client.py`

```python
def obtener_contexto_evento(id_evento: int) -> dict:
    ...

def devolver_resultado_backend(resultado: dict) -> dict:
    ...
```

---

## 16. Qué NO debe ir en el orquestador

```text
No debe ir la lógica de selección de espacios.
No debe ir la lógica de presupuesto.
No debe ir la lógica de ponentes.
No debe ir la lógica de comunicación.
No debe ir RAG específico de agentes.
No deben ir prompts de agentes especializados.
No debe escribir directamente en la BBDD.
No debe enviar emails ni Telegram.
No debe confirmar reservas.
```

---

## 17. Modo seguro por defecto

```python
ALLOW_DB_WRITE = False
ALLOW_EXTERNAL_SEND = False
ALLOW_AUTO_APPROVAL = False
MAX_AGENTES_POR_PETICION = 1
USAR_LLM_ROUTER = False
MODO_DEMO = True
```

Esto significa:

```text
El orquestador enruta y coordina.
Los agentes proponen.
El backend valida y ejecuta.
El humano aprueba acciones sensibles.
```

---

## 18. Ejecución local

Ejemplo:

```bash
cd src/orchestrator
cp .env.example .env
python main.py
```

`main.py` debe:

```text
1. Cargar variables de .env.
2. Leer una petición de inputs/payload_demo.json.
3. Ejecutar ejecutar_orquestador(payload_backend).
4. Simular backend si no existe todavía.
5. Invocar el agente correspondiente.
6. Mostrar resultado por consola.
7. Guardar resultado en outputs/.
```

---

## 19. Casos de fallo que debe controlar

| Fallo | Comportamiento esperado |
|---|---|
| Falta `id_evento` | Devolver `ok=false` y error estructurado. |
| No existe agente para `tipo_peticion` | Devolver error claro: agente no encontrado. |
| El backend no responde | Usar mock si `MODO_DEMO=True`; si no, devolver error. |
| El agente no responde | Devolver error controlado y no bloquear el sistema. |
| El agente devuelve salida mal formada | Rechazar salida y registrar error. |
| La petición requiere varios agentes | En MVP limitar a uno o devolver bloqueo. |
| Permiso en `.env` está en `False` | No ejecutar acción; devolver propuesta al backend. |

---

## 20. Checklist final del orquestador

Antes de entregar el orquestador, comprobar:

- [ ] Existe `README.md`.
- [ ] Existe `.env.example` sin secretos.
- [ ] `.env` está en `.gitignore`.
- [ ] Existe `main.py` para ejecución local.
- [ ] Existe `src/orquestador.py`.
- [ ] Existe `src/router.py`.
- [ ] Existe `src/agent_client.py`.
- [ ] Existe `src/backend_client.py`.
- [ ] El orquestador puede recibir petición del backend o mock.
- [ ] El orquestador puede construir payload común para agentes.
- [ ] El orquestador llama a `ejecutar_agente(payload)`.
- [ ] El orquestador valida la salida estructurada.
- [ ] El orquestador devuelve respuesta clara al backend.
- [ ] El orquestador no contiene lógica específica de agentes.
- [ ] El orquestador no escribe directamente en BBDD.
- [ ] El orquestador no ejecuta acciones externas reales.
- [ ] El orquestador puede ejecutarse con `python main.py`.
