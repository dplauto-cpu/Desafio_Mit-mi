# Endpoints del sistema · v4 — backend unificado de data

**Fecha:** 10 de julio de 2026 · Acompaña a `contrato_api_eventos_3.md` (convenciones y reglas, sigue vigente).
**Sustituye** la sección **2 (Agentes)** de `endpoints_v3.md`. La sección 1 (backend Express)
de v3 **sigue siendo la referencia** del backend full stack — aquí no se repite.

**Qué cambia:** el profe de data pide que data tenga su propio back. Los agentes dejan de
exponerse como mini-servidores sueltos (:5001, :5002) y pasan a ser rutas de **una única
API de data** (FastAPI, puerto **5003**, carpeta `backend_data_Nora/`). Los agentes en sí
no cambian: misma lógica, mismos contratos de entrada/salida, mismo formato de errores.
Los servidores sueltos siguen existiendo como plan B y pueden convivir con el unificado.

Leyenda: ✅ implementado y probado · 🔨 implementado, no probado por nosotros · ⚠️ pendiente de construir

---

## 2. Backend de data (agentes) — `http://localhost:5003` ✅

Arrancar: `cd backend_data_Nora && pip install -r requirements.txt && python app.py`
(Python 3.10+; detalles y límites en el README de esa carpeta).
Sin autenticación, CORS abierto (fase demo, solo lectura de Neon con rol `agente_readonly`).
Documentación interactiva: `GET /docs` (Swagger, la genera FastAPI).

| Ruta | Body | Devuelve | Estado |
|---|---|---|---|
| `GET /` | — | health general: estado, rutas y sesiones de cada agente | ✅ |
| `POST /agentes/lumen/chat` | `{"pregunta": "...", "sesion_id": "..."(opcional)}` | `{resumen, datos_detectados, sesion_id, id_evento_actual, ...}` — **guardar `sesion_id`** y reenviarlo para mantener la memoria de conversación | ✅ |
| `POST /agentes/lumen/chat/reset` | `{"sesion_id": "..."}` | `{ok, sesion_id}` — olvida esa conversación | ✅ |
| `POST /agentes/operis/autocompletar` | `{"texto_briefing": "...", "motor": "reglas"\|"llm"(opcional)}` | contrato de salida común: `datos_detectados` (6 bloques), `bloqueos_detectados`, `requiere_validacion_humana: true` SIEMPRE — el front muestra los campos como propuesta editable, nunca los guarda solo | ✅ |

**Alias de compatibilidad** (mismas rutas que en v3, solo cambia el puerto): `POST /chat`,
`POST /chat/reset` y `POST /autocompletar` responden igual en la raíz de :5003. El front
actual migra cambiando la URL base; cuando adopte las rutas `/agentes/...`, los alias se
podrán retirar.

**Errores** (formato común, igual que en v3): `{"error": true, "codigo": "...", "mensaje": "..."}`
con HTTP 400 (validación), 404 (`RUTA_NO_ENCONTRADA`) o 422 (Operis, briefing no procesable).

Probado el 10/07: health, Operis motor reglas (ruta nueva y alias), Lumen contra Neon real
(44 eventos), memoria de sesión en dos turnos, reset, contratos de error y 404.

### Rutas previstas en este backend ⚠️
| Ruta | Agente | Estado |
|---|---|---|
| `/agentes/alertas/...` | Agente de alertas (Roberto) | ⚠️ pendiente de definir |
| `/agentes/telegram/...` | Agente Telegram ponentes | ⚠️ pendiente de definir (ojo: solapa con historias de usuario del full stack) |

---

## Servidores sueltos (v3) — siguen operativos como plan B

Lumen `:5001` y Operis `:5002` (ver `endpoints_v3.md` §2). No arrancar el suelto y el
unificado a la vez apuntando el front a los dos: las sesiones de chat de Lumen no se
comparten entre procesos.
