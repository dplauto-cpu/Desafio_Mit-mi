# README — Plantilla de Agente Especializado

Proyecto: **Gestión Inteligente de Eventos**  
Tipo de componente: **Agente especializado ejecutable localmente, pero dependiente del orquestador en arquitectura final**  
Versión plantilla: **1.1.0**

---

## 0. Principio arquitectónico obligatorio

Cada equipo Data desarrolla su agente como un **subproyecto propio**. El agente puede ejecutarse solo para desarrollo y pruebas locales:

```bash
python main.py
```

Pero en la arquitectura final **no actúa como agente autónomo**. Será llamado por el **agente orquestador** mediante una interfaz común.

```text
Backend / Orquestador
        ↓
ejecutar_agente(payload)
        ↓
Agente especializado
        ↓
Respuesta estructurada
        ↓
Orquestador / Backend / Validación humana
```

Regla principal:

```text
El agente especializado analiza, interpreta, redacta y propone.
El orquestador coordina y enruta.
El backend valida, guarda y ejecuta acciones reales.
El humano aprueba acciones sensibles.
La BBDD es la fuente final de verdad.
```

---

## 1. Regla crítica no modificable

La estructura interna de cada agente puede adaptarse a sus necesidades, **excepto la comunicación con el orquestador**.

Esto es obligatorio para todos los equipos:

```text
src/agents/[nombre_agente]/src/agente.py
```

Debe exponer siempre esta función:

```python
def ejecutar_agente(payload: dict) -> dict:
    """
    Punto de entrada común del agente.
    Lo usa el main.py local, el orquestador o una futura API.
    """
    ...
```

También debe respetar siempre:

```text
1. Mismo contrato de entrada.
2. Mismo contrato de salida.
3. Salida siempre estructurada.
4. Ningún agente invoca directamente a otro agente.
5. Ningún agente escribe directamente en la BBDD final.
6. Ningún agente ejecuta acciones externas reales sin validación.
```

La comunicación agente-orquestador es lo único que **no se puede cambiar** estructuralmente.

---

## 2. Identificación del agente

| Campo | Valor |
|---|---|
| **Nombre del agente** | `[nombre_agente]` |
| **Equipo responsable** | `[equipo / personas]` |
| **Fase del evento que cubre** | `[espacios / presupuesto / ponentes / comunicación / producción / cierre / otra]` |
| **Propósito en una frase** | `[explicar qué problema resuelve]` |
| **Tipo de agente** | Especializado dependiente del orquestador |
| **Modo por defecto** | `propuesta` |
| **Estado** | Experimental / MVP / Validado |
| **Última actualización** | `[DD/MM/AAAA]` |

---

## 3. Qué hace este agente

Describir capacidades concretas, no frases genéricas.

Ejemplo:

```text
Este agente revisa la información disponible de los ponentes de un evento,
detecta documentación pendiente y genera propuestas de comunicación para reclamar
foto, CV, presentación o datos logísticos.
```

### Capacidades principales

- `[Capacidad 1]`
- `[Capacidad 2]`
- `[Capacidad 3]`

### Ejemplos de uso

- `[Ejemplo 1]`
- `[Ejemplo 2]`
- `[Ejemplo 3]`

---

## 4. Qué NO hace este agente

Este apartado es obligatorio para evitar solapes entre equipos.

El agente **no debe**:

- escribir directamente en la base de datos final;
- enviar emails reales sin aprobación;
- enviar mensajes reales por Telegram/WhatsApp sin aprobación;
- confirmar reservas de espacios, hoteles, vuelos o proveedores;
- aprobar presupuestos;
- modificar fechas críticas del evento;
- ejecutar acciones irreversibles;
- invocar directamente a otros agentes;
- sustituir al orquestador;
- sustituir al backend.

Añadir límites propios:

- `[Límite específico 1]`
- `[Límite específico 2]`
- `[Límite específico 3]`

---

## 5. Estructura conceptual del agente

Cada agente puede adaptar carpetas según su necesidad concreta. Esta es la estructura recomendada para trabajar de forma ordenada por equipos.

```text
src/agents/[nombre_agente]/
│
├── README.md
│   └── Documenta qué hace el agente, qué no hace, cómo se ejecuta y cómo se integra.
│
├── main.py
│   └── Permite ejecutar el agente directamente para pruebas locales.
│      Usa inputs de ejemplo y llama internamente a ejecutar_agente(payload).
│
├── .env
│   └── Archivo local de configuración real del agente.
│      Puede contener API keys, modelo LLM, permisos, rutas, modo demo, tokens, etc.
│      No debe subirse al repositorio.
│
├── .env.example
│   └── Plantilla sin secretos para que el resto del equipo sepa qué variables necesita el agente.
│
├── config/
│   └── Configuración Python del agente.
│      Lee valores desde .env y define parámetros, permisos, fuentes de datos y rutas.
│
├── prompts/
│   └── Instrucciones que se pasan al LLM.
│      Aquí van prompts específicos: rol, análisis, validación, redacción, clasificación, etc.
│
├── src/
│   └── Código interno del agente.
│      Aquí vive el punto crítico de integración: src/agente.py con ejecutar_agente(payload).
│
├── inputs/
│   └── Entradas de trabajo o demo.
│      Puede incluir payloads JSON, emails, PDFs, formularios, alertas, datos manuales o respuestas de APIs.
│
├── integrations/
│   └── Conectores específicos que necesite el agente.
│      Ejemplos: backend, Gmail, Telegram, Calendar, Excel, APIs externas, documentos.
│
├── data/
│   └── Datos propios del agente.
│      Puede incluir mock data, RAG, PDFs, procedimientos, ejemplos, histórico o índices locales.
│
├── outputs/
│   └── Salidas generadas por el agente.
│      Ejemplos: borradores, informes, respuestas JSON, evidencias o resultados intermedios.
│
└── logs/
    └── Registro de ejecuciones, errores, decisiones, fuentes consultadas y resultados.
```

---

## 6. Estructura mínima obligatoria

Para que el orquestador pueda integrar cualquier agente sin rehacer trabajo, cada agente debe tener como mínimo:

```text
src/agents/[nombre_agente]/
│
├── README.md
├── main.py
├── .env.example
│
├── src/
│   ├── agente.py      ← obligatorio: contiene ejecutar_agente(payload)
│   └── schemas.py     ← obligatorio: contrato de entrada/salida del agente
│
├── inputs/
│   └── payload_demo.json
│
└── outputs/
    └── respuestas_json/
```

Todo lo demás puede adaptarse según el agente.

---

## 7. Estructura recomendada completa

Esta estructura es recomendable, pero puede modificarse si el agente lo requiere. Lo único no modificable es la interfaz `ejecutar_agente(payload)` y los contratos.

```text
src/agents/[nombre_agente]/
│
├── README.md
├── main.py
├── .env
├── .env.example
│
├── config/
│   ├── settings.py
│   ├── permisos.py
│   └── fuentes.py
│
├── prompts/
│   ├── prompt_sistema.md
│   ├── prompt_analisis.md
│   ├── prompt_borrador.md
│   ├── prompt_validacion.md
│   └── README.md
│
├── src/
│   ├── agente.py
│   ├── schemas.py
│   ├── funciones.py
│   ├── herramientas.py
│   ├── rag.py
│   ├── memoria.py
│   └── validaciones.py
│
├── inputs/
│   ├── payload_demo.json
│   └── ejemplos/
│
├── integrations/
│   ├── api_backend.py
│   ├── gmail.py
│   ├── telegram.py
│   ├── calendar.py
│   └── documentos.py
│
├── data/
│   ├── mock/
│   ├── rag/
│   │   ├── documentos/
│   │   ├── historico/
│   │   └── indice/
│   ├── pdf/
│   ├── procedimientos/
│   └── ejemplos/
│
├── outputs/
│   ├── borradores/
│   ├── informes/
│   └── respuestas_json/
│
└── logs/
    └── ejecuciones.log
```

---

## 8. Archivo `.env`

Cada equipo define su propio `.env` según las necesidades de su agente.

Ejemplo orientativo:

```env
# Modo de ejecución
MODO_DEMO=True
ENVIRONMENT=local

# LLM
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=1200
OPENAI_API_KEY=poner_api_key_aqui

# Permisos del agente
ALLOW_DB_WRITE=False
ALLOW_EXTERNAL_SEND=False
ALLOW_CREATE_EVENT=False
ALLOW_AUTO_APPROVAL=False

# Backend / BD
BACKEND_BASE_URL=http://localhost:8000
DATABASE_URL=

# Integraciones opcionales
GMAIL_ENABLED=False
GMAIL_TOKEN=
TELEGRAM_ENABLED=False
TELEGRAM_BOT_TOKEN=
CALENDAR_ENABLED=False

# Rutas locales
DATA_DIR=data
RAG_DIR=data/rag
OUTPUTS_DIR=outputs
LOG_LEVEL=INFO
```

Reglas:

```text
.env contiene valores reales y secretos locales.
.env.example contiene la plantilla sin secretos.
.env no se sube al repositorio.
.env.example sí se sube al repositorio.
```

El `.gitignore` del proyecto debe incluir:

```gitignore
.env
*.log
outputs/
data/rag/indice/
```

---

## 9. Comunicación obligatoria con el orquestador

### 9.1. Punto de entrada obligatorio

Todos los agentes deben poder ser llamados así:

```python
from src.agente import ejecutar_agente

respuesta = ejecutar_agente(payload)
```

En integración final, el orquestador podrá llamar al agente de dos formas:

```text
Opción A — Import local Python:
orquestador → import agente → ejecutar_agente(payload)

Opción B — API futura:
orquestador → endpoint del agente → ejecutar_agente(payload)
```

La forma puede cambiar, pero el contrato **no cambia**.

---

## 10. Contrato común de entrada

Todos los agentes deben aceptar este formato mínimo:

```json
{
  "id_evento": 1,
  "id_registro": null,
  "tipo_peticion": "analizar_estado",
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

### Campos

| Campo | Obligatorio | Uso |
|---|---:|---|
| `id_evento` | Sí | Evento sobre el que trabaja el agente. |
| `id_registro` | No | Registro concreto si aplica: ponente, espacio, proveedor, tarea, documento. |
| `tipo_peticion` | Sí | Qué se pide al agente. |
| `origen` | Sí | `orquestador`, `backend`, `frontend`, `gmail`, `telegram`, `manual`, `demo`. |
| `usuario_solicitante` | Sí | Usuario o sistema que activa la petición. |
| `rol_usuario` | Sí | Rol del usuario: admin, organizador, ponente, staff, sistema. |
| `datos` | Sí | Datos concretos de la petición. Puede estar vacío. |
| `contexto` | Sí | Estado general del evento o información adicional. |
| `modo` | Sí | `simulacion`, `propuesta`, `ejecucion_controlada`. En MVP usar `propuesta`. |

---

## 11. Contrato común de salida

Todos los agentes deben devolver este formato mínimo:

```json
{
  "ok": true,
  "agente": "nombre_agente",
  "tipo_peticion": "analizar_estado",
  "resumen": "Resumen breve de lo detectado.",
  "datos_detectados": {},
  "acciones_propuestas": [],
  "bloqueos_detectados": [],
  "borradores_generados": [],
  "requiere_validacion_humana": true,
  "nivel_riesgo": "bajo",
  "errores": [],
  "trazas": {
    "fuentes_consultadas": [],
    "timestamp": "2026-07-08T09:00:00",
    "modo": "propuesta"
  }
}
```

### Campos

| Campo | Obligatorio | Uso |
|---|---:|---|
| `ok` | Sí | Indica si el agente ha podido procesar la petición. |
| `agente` | Sí | Nombre del agente que responde. |
| `tipo_peticion` | Sí | Debe coincidir con la petición procesada. |
| `resumen` | Sí | Resumen entendible para el usuario/backend. |
| `datos_detectados` | Sí | Datos interpretados o calculados. |
| `acciones_propuestas` | Sí | Acciones sugeridas, no ejecutadas. |
| `bloqueos_detectados` | Sí | Problemas, datos faltantes o riesgos. |
| `borradores_generados` | Sí | Emails, mensajes, informes o textos pendientes de revisión. |
| `requiere_validacion_humana` | Sí | `true` si cualquier acción necesita aprobación. |
| `nivel_riesgo` | Sí | `bajo`, `medio`, `alto`. |
| `errores` | Sí | Lista de errores técnicos o funcionales. |
| `trazas` | Sí | Fuentes, modo, timestamp y datos mínimos de trazabilidad. |

---

## 12. Flujo interno recomendado del agente

```text
1. main.py o el orquestador construye un payload.
2. ejecutar_agente(payload) recibe la petición.
3. schemas.py valida entrada mínima.
4. config/ carga permisos, modelo LLM, rutas y fuentes desde .env.
5. integrations/ o data/mock/ obtienen datos necesarios.
6. rag.py consulta contexto documental si aplica.
7. prompts/ aporta instrucciones al LLM.
8. funciones.py aplica reglas deterministas.
9. validaciones.py comprueba que no se inventan datos críticos.
10. El agente genera salida estructurada.
11. La salida se guarda opcionalmente en outputs/ para demo.
12. Se registra trazabilidad en logs/.
13. Se devuelve respuesta al orquestador.
```

---

## 13. Prompts

Los prompts específicos del agente van dentro de `prompts/`.

Ejemplo:

```text
prompts/
├── prompt_sistema.md
├── prompt_clasificar_peticion.md
├── prompt_analizar_estado.md
├── prompt_generar_borrador.md
├── prompt_validar_salida.md
└── README.md
```

Regla:

```text
Prompts específicos del agente → dentro del agente.
Prompts comunes del proyecto → fuera del agente, en carpeta común si se crea.
El orquestador no debe contener prompts específicos de cada agente.
```

---

## 14. RAG y datos

### RAG específico del agente

Va dentro del propio agente:

```text
src/agents/[nombre_agente]/data/rag/
├── documentos/
├── historico/
└── indice/
```

Ejemplos:

```text
agente_ponentes/data/rag/documentos/ficha_base_ponente.md
agente_espacios/data/rag/documentos/directorio_espacios.md
agente_presupuesto/data/rag/documentos/criterios_costes.md
```

### RAG común del proyecto

Si un documento sirve a todos los agentes, debe ir en una zona común del proyecto, no duplicado por agente:

```text
data/rag/global/
```

---

## 15. Integraciones

Cada agente puede tener las integraciones que necesite.

Ejemplos:

```text
integrations/
├── api_backend.py
├── gmail.py
├── telegram.py
├── calendar.py
├── excel.py
└── documentos.py
```

Reglas:

```text
Las integraciones pueden leer datos.
Las integraciones pueden preparar propuestas.
No deben ejecutar acciones reales si el permiso está en False.
No deben saltarse la validación humana.
```

---

## 16. Modo seguro por defecto

En el MVP todos los agentes deben arrancar en modo seguro:

```python
ALLOW_DB_WRITE = False
ALLOW_EXTERNAL_SEND = False
ALLOW_CREATE_EVENT = False
ALLOW_AUTO_APPROVAL = False
MODO_DEMO = True
```

Esto significa:

```text
Puede leer datos.
Puede analizar.
Puede generar borradores.
Puede proponer acciones.
No puede ejecutar acciones externas reales sin validación.
No puede modificar la BD final directamente.
```

---

## 17. Ejecución local

Ejemplo de ejecución:

```bash
cd src/agents/[nombre_agente]
cp .env.example .env
python main.py
```

`main.py` debe:

```text
1. Cargar variables de .env.
2. Leer un payload de inputs/payload_demo.json.
3. Llamar a ejecutar_agente(payload).
4. Mostrar la respuesta por consola.
5. Guardar la respuesta opcionalmente en outputs/respuestas_json/.
```

---

## 18. Ejemplo mínimo de `main.py`

```python
import json
from pathlib import Path
from src.agente import ejecutar_agente

BASE_DIR = Path(__file__).resolve().parent

payload_path = BASE_DIR / "inputs" / "payload_demo.json"
output_dir = BASE_DIR / "outputs" / "respuestas_json"
output_dir.mkdir(parents=True, exist_ok=True)

with open(payload_path, "r", encoding="utf-8") as f:
    payload = json.load(f)

respuesta = ejecutar_agente(payload)

print(json.dumps(respuesta, ensure_ascii=False, indent=2))

with open(output_dir / "salida_demo.json", "w", encoding="utf-8") as f:
    json.dump(respuesta, f, ensure_ascii=False, indent=2)
```

---

## 19. Casos de fallo que debe controlar

| Fallo | Comportamiento esperado |
|---|---|
| Falta `id_evento` | Devolver `ok=false` y error estructurado. |
| Tipo de petición no soportado | Devolver bloqueo o error controlado. |
| Faltan datos necesarios | No inventar; devolver `bloqueos_detectados`. |
| LLM devuelve texto no estructurado | Reintentar o devolver error controlado. |
| RAG no encuentra información | Continuar si no es crítica o bloquear si lo es. |
| Integración externa falla | Devolver error y no ejecutar acción. |
| Permiso en `.env` está en `False` | No ejecutar acción; generar propuesta o borrador. |

---

## 20. Checklist final del agente

Antes de entregar el agente, comprobar:

- [ ] Existe `README.md`.
- [ ] Existe `.env.example` sin secretos.
- [ ] `.env` está en `.gitignore`.
- [ ] Existe `main.py` para ejecución local.
- [ ] Existe `src/agente.py`.
- [ ] `src/agente.py` expone `ejecutar_agente(payload: dict) -> dict`.
- [ ] La entrada respeta el contrato común.
- [ ] La salida respeta el contrato común.
- [ ] El agente no invoca a otros agentes.
- [ ] El agente no escribe directamente en la BD final.
- [ ] El agente no envía emails/mensajes reales sin validación.
- [ ] Los permisos por defecto están en modo seguro.
- [ ] Existen datos de ejemplo o payload demo.
- [ ] El agente puede ejecutarse con `python main.py`.
- [ ] Se documenta qué hace y qué no hace.
