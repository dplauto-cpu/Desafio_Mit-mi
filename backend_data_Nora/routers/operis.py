"""
routers/operis.py — ruta HTTP de Operis (autocompletar briefings) en el backend de data.

Mismo contrato que el servidor Flask original de Operis
(agente_operis_autocompletar_Ainara_Dv/agente_operis_llm/servidor.py): el front manda
el texto del briefing y recibe datos_detectados con los 6 bloques, bloqueos_detectados
con los campos que faltan y requiere_validacion_humana=True SIEMPRE — el front debe
mostrar los campos como PROPUESTA editable, nunca guardarlos solos.

Sin estado: cada peticion es independiente (a diferencia del chat de Lumen).
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from cargador_agentes import OPERIS

router = APIRouter(tags=["operis"])


def _error(codigo, mensaje, http=400):
    return JSONResponse({"error": True, "codigo": codigo, "mensaje": mensaje}, status_code=http)


@router.post("/autocompletar")
async def autocompletar(request: Request):
    try:
        cuerpo = await request.json()
    except Exception:
        cuerpo = None
    if not cuerpo or not isinstance(cuerpo, dict):
        return _error("CUERPO_INVALIDO", "Manda un JSON con al menos 'texto_briefing'.")

    texto_briefing = (cuerpo.get("texto_briefing") or "").strip()
    if not texto_briefing:
        return _error("CAMPO_OBLIGATORIO", "El campo 'texto_briefing' es obligatorio.")

    motor = cuerpo.get("motor") or OPERIS.MOTOR_POR_DEFECTO
    if motor not in ("reglas", "llm"):
        return _error("MOTOR_INVALIDO", "El campo 'motor' debe ser 'reglas' o 'llm'.")

    # Contrato de entrada comun del agente (README de Operis, seccion 9.2):
    # el front solo manda el texto, el resto lo fija esta capa.
    payload = {
        "id_evento": None,
        "id_registro": None,
        "tipo_peticion": "extraer_briefing",
        "origen": "frontend",
        "usuario_solicitante": "frontend",
        "rol_usuario": "organizador",
        "datos": {
            "texto_briefing": texto_briefing,
            "motor": motor,
        },
        "contexto": {},
        "modo": "propuesta",
    }

    salida = OPERIS.ejecutar_agente(payload)
    return JSONResponse(salida, status_code=200 if salida.get("ok") else 422)
