import json
import re
import time
import requests
from . import parametros as p
from .prompts import PROMPT_CLASIFICACION, PROMPT_REDACCION, REGLAS_COMUNES

class LLMError(Exception):
    pass

def _extraer_json(texto: str) -> dict:
    texto = (texto or "").strip()
    try:
        return json.loads(texto)
    except Exception:
        pass
    m = re.search(r"\{.*\}", texto, flags=re.DOTALL)
    if not m:
        raise LLMError("El LLM no devolvió JSON.")
    return json.loads(m.group(0))

def _segundos_rate_limit(texto: str) -> float:
    """Extrae una espera aproximada de mensajes tipo 'try again in 1.26s'."""
    if not texto:
        return p.LLM_RETRY_BASE_SECONDS
    m = re.search(r"try again in\s+([0-9]+(?:\.[0-9]+)?)s", texto, flags=re.IGNORECASE)
    if m:
        try:
            return float(m.group(1)) + 1.0
        except Exception:
            pass
    return p.LLM_RETRY_BASE_SECONDS

def llamar_llm_json(mensajes, max_tokens=None) -> dict:
    if not p.LLM_ENABLED:
        raise LLMError("LLM_ENABLED=False. Este agente requiere LLM obligatorio.")
    if not p.OPENAI_API_KEY:
        raise LLMError("OPENAI_API_KEY no configurada.")

    url = f"{p.OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {p.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": p.LLM_MODEL,
        "messages": mensajes,
        "temperature": p.LLM_TEMPERATURE,
        "max_tokens": max_tokens or p.LLM_MAX_TOKENS,
    }
    # En Groq, algunos modelos devuelven 400 json_validate_failed si se fuerza
    # response_format y el límite de tokens corta el JSON. Por defecto no se fuerza:
    # el prompt exige JSON y Python valida/extrae el objeto.
    if getattr(p, "LLM_JSON_MODE", False):
        payload["response_format"] = {"type": "json_object"}

    ultimo_error = None
    intentos = max(1, p.LLM_RETRY_MAX_ATTEMPTS)
    for intento in range(1, intentos + 1):
        r = requests.post(url, headers=headers, json=payload, timeout=45)
        if r.status_code == 429 and intento < intentos:
            espera = _segundos_rate_limit(r.text)
            time.sleep(espera)
            ultimo_error = f"Rate limit LLM 429. Reintento tras {espera:.1f}s."
            continue
        if r.status_code >= 400:
            # Si el proveedor falla por validación JSON forzada, reintenta sin JSON mode.
            if r.status_code == 400 and "json_validate_failed" in r.text and payload.get("response_format"):
                payload.pop("response_format", None)
                r = requests.post(url, headers=headers, json=payload, timeout=45)
                if r.status_code < 400:
                    data = r.json()
                    contenido = data["choices"][0]["message"]["content"]
                    return _extraer_json(contenido)
            raise LLMError(f"Error HTTP del LLM: {r.status_code} - {r.text}")
        data = r.json()
        contenido = data["choices"][0]["message"]["content"]
        return _extraer_json(contenido)

    raise LLMError(ultimo_error or "Error desconocido al llamar al LLM.")

def clasificar_con_llm(correo: dict, apoyo_reglas: dict) -> dict:
    asunto = correo.get("asunto", "")
    remitente = correo.get("remitente", "")
    cuerpo = (correo.get("cuerpo", "") or "")[:900]
    adjuntos = correo.get("adjuntos", [])
    resumen_adjuntos = [{"nombre": a.get("nombre"), "mime_type": a.get("mime_type")} for a in adjuntos]

    user = {
        "remitente": remitente,
        "asunto": asunto,
        "cuerpo": cuerpo,
        "adjuntos": resumen_adjuntos,
        "apoyo_reglas": apoyo_reglas,
    }
    mensajes = [
        {"role": "system", "content": PROMPT_CLASIFICACION + "\n" + REGLAS_COMUNES},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
    ]
    return llamar_llm_json(mensajes, max_tokens=min(max(p.LLM_MAX_TOKENS, 300), 350))

def redactar_borrador_con_llm(correo: dict, clasificacion: dict) -> dict:
    asunto = correo.get("asunto", "")
    remitente = correo.get("remitente", "")
    cuerpo = (correo.get("cuerpo", "") or "")[:800]
    payload = {
        "correo": {"remitente": remitente, "asunto": asunto, "cuerpo": cuerpo},
        "clasificacion": clasificacion,
        "instrucciones": "Genera asunto y cuerpo de borrador. No confirmar acciones no validadas.",
    }
    mensajes = [
        {"role": "system", "content": PROMPT_REDACCION + "\nDevuelve SOLO JSON con asunto y cuerpo."},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
    data = llamar_llm_json(mensajes, max_tokens=250)
    return {
        "asunto": data.get("asunto") or f"Re: {asunto}",
        "cuerpo": data.get("cuerpo") or "Hola,\n\nHemos recibido tu correo. Lo revisaremos y te responderemos lo antes posible.\n\nEquipo MITUMI",
    }
