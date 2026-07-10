"""
routers/lumen.py — rutas HTTP de Lumen (chat con memoria por sesion) en el backend de data.

Mismo contrato de entrada/salida que el servidor Flask original de Lumen
(Agente_04_Copilot_Raul/servidor.py), para que el front solo tenga que cambiar
la URL base. La logica de sesiones es identica: viven en RAM del proceso
(dict sesion_id -> MemoriaConversacion) y se pierden al reiniciar — limitacion
aceptada de la fase demo.

Los endpoints leen el body a mano (request.json()) en vez de usar modelos
pydantic para conservar exactamente los errores del contrato original
({"error": true, "codigo": ..., "mensaje": ...} con HTTP 400), en lugar del
422 con formato propio que devolveria FastAPI al validar.
"""

import uuid

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from cargador_agentes import LUMEN

router = APIRouter(tags=["lumen"])

# sesion_id -> MemoriaConversacion (solo RAM, ver cabecera)
_sesiones = {}


def sesiones_activas():
    return len(_sesiones)


def _obtener_memoria(sesion_id):
    if sesion_id not in _sesiones:
        _sesiones[sesion_id] = LUMEN.MemoriaConversacion()
    return _sesiones[sesion_id]


def _error(codigo, mensaje, http=400):
    return JSONResponse({"error": True, "codigo": codigo, "mensaje": mensaje}, status_code=http)


async def _leer_json(request):
    try:
        cuerpo = await request.json()
    except Exception:
        return {}
    return cuerpo if isinstance(cuerpo, dict) else {}


@router.post("/chat")
async def chat(request: Request):
    cuerpo = await _leer_json(request)
    pregunta = (cuerpo.get("pregunta") or "").strip()

    if not pregunta:
        return _error("PREGUNTA_VACIA", "Falta el campo 'pregunta'.")

    sesion_id = cuerpo.get("sesion_id") or str(uuid.uuid4())
    memoria = _obtener_memoria(sesion_id)

    id_evento, _usando_memoria, nombres_ambiguos = memoria.resolver_id_evento(pregunta)
    if nombres_ambiguos:
        return {
            "sesion_id": sesion_id,
            "resumen": (
                "Hay mas de un evento que coincide con lo que preguntas: " +
                ", ".join(nombres_ambiguos) + ". ¿A cual te refieres?"
            ),
            "bloqueos_detectados": ["nombre de evento ambiguo"],
            "requiere_validacion_humana": False,
            "nivel_riesgo": "bajo",
            "datos_detectados": {"eventos_candidatos": nombres_ambiguos},
            "id_evento_actual": memoria.id_evento_actual,
            "errores": [],
        }

    payload = LUMEN.construir_payload(
        id_evento, memoria.historial_para_payload(), pregunta, origen="frontend_react"
    )

    respuesta = LUMEN.ejecutar_agente(payload)
    memoria.registrar_turno(pregunta, respuesta, id_evento)

    return {
        "sesion_id": sesion_id,
        "resumen": respuesta.get("resumen", ""),
        "bloqueos_detectados": respuesta.get("bloqueos_detectados", []),
        "requiere_validacion_humana": respuesta.get("requiere_validacion_humana", False),
        "nivel_riesgo": respuesta.get("nivel_riesgo", "bajo"),
        "datos_detectados": respuesta.get("datos_detectados", {}),
        # Estado de memoria DESPUES de este turno — util para que el front muestre
        # "hablando del evento X" de forma persistente, no solo en el turno que lo detecto.
        "id_evento_actual": memoria.id_evento_actual,
        "errores": respuesta.get("errores", []),
    }


@router.post("/chat/reset")
async def chat_reset(request: Request):
    cuerpo = await _leer_json(request)
    sesion_id = cuerpo.get("sesion_id")

    if not sesion_id:
        return _error("FALTA_SESION_ID", "Falta el campo 'sesion_id'.")

    if sesion_id in _sesiones:
        _sesiones[sesion_id].reiniciar()

    return {"ok": True, "sesion_id": sesion_id}
