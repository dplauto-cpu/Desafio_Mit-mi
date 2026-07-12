# backend_data — backend unificado de los agentes de data

**Qué es:** un solo servicio HTTP (FastAPI) que expone todos los agentes de data como
rutas de una misma API, en vez de un mini-servidor Flask suelto por agente. Responde a
la petición del profe de data de que **data tenga su propio back**.

**Qué NO cambia:** los agentes no se tocan. Su lógica sigue viviendo en sus carpetas
(`Agente_04_Copilot_Raul/`, `agente_operis_autocompletar_Ainara_Dv/agente_operis_llm/`)
y su contrato interno sigue siendo `ejecutar_agente(payload)`. Los servidores sueltos
(`servidor.py` en :5001 y :5002) siguen existiendo y pueden convivir con éste.

## Arrancar

```bash
cd backend_data_Nora
pip install -r requirements.txt
python app.py            # escucha en http://localhost:5003
```

También vale `uvicorn app:app --port 5003`. Variables `PORT` y `HOST` para cambiar
puerto/host. Mapa de puertos del proyecto: 5000 mock API_Nora · 5001 Lumen suelto ·
5002 Operis suelto · **5003 este backend** · 3000 backend full stack.

Requiere Python 3.10+ (FastAPI moderno no soporta el 3.9 de macOS; en este Mac:
`/usr/local/bin/python3.12`). El `.env` con `DATABASE_URL` (rol solo-lectura de Neon),
clave LLM, etc. se lee de `Agente_04_Copilot_Raul/lumen_agente_04/.env` — no hay que
copiar nada.

## Rutas

Documentación interactiva (Swagger) en **http://localhost:5003/docs**.

| Ruta | Body | Qué hace |
|---|---|---|
| `GET /` | — | health: estado y rutas de cada agente |
| `POST /agentes/lumen/chat` | `{"pregunta": "...", "sesion_id": "..."(opcional)}` | chat de Lumen con memoria por sesión — guardar el `sesion_id` devuelto y reenviarlo |
| `POST /agentes/lumen/chat/reset` | `{"sesion_id": "..."}` | olvida esa conversación |
| `POST /agentes/operis/autocompletar` | `{"texto_briefing": "...", "motor": "reglas"\|"llm"(opcional)}` | extrae los campos del evento de un briefing; SIEMPRE propuesta editable (`requiere_validacion_humana: true`) |

**Alias de compatibilidad:** `POST /chat`, `/chat/reset` y `/autocompletar` funcionan
igual en la raíz — el front actual solo tiene que cambiar la URL base (`:5001`/`:5002`
→ `:5003`). Contratos de entrada/salida y formato de errores idénticos a los servidores
originales: ver `API_Nora/api/endpoints_v4.md`.

## Cómo funciona por dentro (y cómo añadir un agente)

- `app.py` — la app FastAPI: CORS, health, montaje de routers (con prefijo
  `/agentes/<nombre>` + alias legacy en la raíz), 404 con el formato de error común.
- `routers/lumen.py`, `routers/operis.py` — la capa HTTP de cada agente, portada 1:1 de
  su `servidor.py` original.
- `cargador_agentes.py` — la pieza delicada: los agentes tienen paquetes que se llaman
  igual (`src`, `config`...) y no pueden importarse a la vez de forma normal. Este módulo
  los carga secuencialmente aislando `sys.modules`. **Leer su docstring antes de añadir
  un agente nuevo** (alertas de Roberto, Telegram): en resumen, replicar el patrón de
  `_cargar_lumen()` y dejar como residente solo al agente que tenga imports perezosos
  de sus propios paquetes.

## Límites conocidos (fase demo)

- Sin autenticación y CORS abierto — igual que los servidores sueltos de la demo.
- Las sesiones de chat de Lumen viven en RAM del proceso: se pierden al reiniciar.
- Un solo proceso/worker: si algún día se lanza con varios workers, cada uno tendría
  sus propias sesiones (haría falta Redis/BD para compartirlas).
- Solo lectura de Neon (rol `agente_readonly`); las escrituras siguen siendo del
  backend full stack, según la arquitectura acordada.
