import json
import time
from datetime import datetime
from pathlib import Path
from . import parametros as p
from .funciones import clasificar_correo, detectar_documentos, construir_acciones, sugerir_acciones_correo
from .llm import redactar_borrador_con_llm, LLMError
from .gmail import GmailClient, GmailError
from .memoria import guardar_respuesta


def _log(texto: str):
    if getattr(p, "SHOW_STEPS", True):
        print(texto)


def _extraer_email_simple(remitente: str) -> str:
    if "<" in remitente and ">" in remitente:
        return remitente.split("<", 1)[1].split(">", 1)[0].strip()
    return remitente.strip()


def procesar_correo(correo: dict, gmail_client: GmailClient | None = None, indice: int | None = None, total: int | None = None) -> dict:
    email_id = correo.get("email_id")
    thread_id = correo.get("thread_id")

    if indice is not None:
        _log("\n" + "=" * 70)
        _log(f"CORREO {indice}/{total or '?'}")
        _log("=" * 70)
    _log(f"[1] Correo detectado")
    _log(f"    Email ID : {email_id}")
    _log(f"    Thread ID: {thread_id or 'no_detectado'}")
    _log(f"    De       : {correo.get('remitente')}")
    _log(f"    Asunto   : {correo.get('asunto')}")
    _log(f"    Adjuntos : {len(correo.get('adjuntos', []))}")
    _log(f"    Cuerpo   : {len(correo.get('cuerpo', '') or '')} caracteres")

    _log("[2] LLM clasificando correo...")
    clasif = clasificar_correo(correo)

    if not clasif.get("ok", True):
        _log("[ERROR] Fallo de clasificación LLM obligatorio")
        _log(f"        {clasif.get('error', clasif.get('motivo'))}")
        respuesta = {
            "ok": False,
            "agente": "agente_gestor_correos_mitumi",
            "tipo_peticion": "analizar_correo",
            "resumen": "No se pudo clasificar el correo porque el LLM obligatorio falló.",
            "datos_detectados": {"email_id": email_id, "thread_id": thread_id, "remitente": correo.get("remitente"), "asunto": correo.get("asunto"), "categoria_correo": "error_llm_obligatorio", "confianza_clasificacion": 0.0},
            "acciones_propuestas": [],
            "bloqueos_detectados": [{"tipo": "llm_obligatorio_no_disponible", "descripcion": clasif.get("error", clasif.get("motivo")), "requiere_revision_humana": True}],
            "borradores_generados": [],
            "acciones_ejecutadas": [],
            "requiere_validacion_humana": True,
            "nivel_riesgo": "alto",
            "errores": [clasif.get("error", clasif.get("motivo"))],
            "trazas": {"fuentes_consultadas": ["gmail_composio"], "timestamp": datetime.now().isoformat(timespec="seconds"), "modo": "propuesta", "version_agente": p.AGENTE_VERSION},
        }
        return respuesta

    cat = clasif["categoria"]
    _log(f"[3] Clasificación: {cat} | confianza: {clasif['confianza']} | riesgo: {clasif.get('riesgo', 'medio')}")
    _log(f"    Motivo: {clasif.get('motivo')}")

    documentos = detectar_documentos(correo, cat)
    _log(f"[4] Documentos detectados: {len(documentos)}")
    for d in documentos:
        _log(f"    - {d.get('nombre_archivo')} | {d.get('tipo_documento_detectado')} | {d.get('estado_documental')}")

    acciones = construir_acciones(correo, clasif, documentos, p.EMAIL_FACTURACION_DESTINO)
    acciones_correo = sugerir_acciones_correo(cat, acciones, documentos)
    _log(f"[5] Acciones propuestas: {len(acciones)}")
    for a in acciones:
        _log(f"    - {a.get('tipo')} | prioridad: {a.get('prioridad')} | front: {a.get('visible_en_front')}")

    borradores = []
    acciones_ejecutadas = []
    borrador_real_creado = False

    debe_borrador = clasif.get("requiere_respuesta") and cat not in {"spam", "phishing_sospechoso", "publicidad", "newsletter", "no_clasificado"}
    _log(f"[6] ¿Requiere borrador?: {bool(debe_borrador)}")

    if debe_borrador:
        try:
            _log("[7] LLM redactando borrador...")
            borrador_texto = redactar_borrador_con_llm(correo, clasif)
            # Para mantener el hilo, el asunto operativo del borrador debe responder al asunto original.
            # El LLM puede proponer otro asunto, pero no se usa para crear el draft real.
            asunto_original = correo.get("asunto") or borrador_texto.get("asunto") or "correo recibido"
            asunto_respuesta = asunto_original if asunto_original.lower().startswith("re:") else f"Re: {asunto_original}"

            borrador = {
                "canal": "email",
                "destinatario": _extraer_email_simple(correo.get("remitente", "")),
                "asunto": asunto_respuesta,
                "asunto_sugerido_llm": borrador_texto.get("asunto"),
                "cuerpo": borrador_texto["cuerpo"],
                "estado": "pendiente_validacion_humana",
                "thread_id": thread_id,
                "reply_to_message_id": email_id,
            }
            borradores.append(borrador)
            _log(f"    Borrador preparado para: {borrador['destinatario']}")
            _log(f"    Asunto borrador: {borrador['asunto']}")

            if gmail_client and p.ALLOW_CREATE_DRAFTS:
                _log("[8] Creando borrador real en Gmail intentando mantener hilo...")
                r = gmail_client.crear_borrador(
                    borrador["destinatario"],
                    borrador["asunto"],
                    borrador["cuerpo"],
                    thread_id=thread_id,
                    message_id=email_id,
                )
                borrador_real_creado = bool(r.get("ok"))
                acciones_ejecutadas.append({"tipo": "crear_borrador_gmail", "ok": r.get("ok"), "detalle": r})
                _log(f"    Resultado borrador Gmail: {r.get('ok')}")
                if r.get("ok"):
                    args_usados = r.get("args_usados", {})
                    _log(f"    Thread enviado a Composio: {args_usados.get('thread_id') or args_usados.get('threadId') or 'no_usado'}")
                else:
                    _log(f"    Error borrador Gmail: {r.get('error')}")
            elif gmail_client:
                _log("[8] Creación real de borrador omitida: ALLOW_CREATE_DRAFTS=False")
        except LLMError as e:
            _log(f"[ERROR] No se pudo generar borrador: {e}")
            acciones.append({"tipo": "error_generar_borrador", "descripcion": str(e), "prioridad": "media", "requiere_validacion_humana": True, "visible_en_front": True, "estado_sugerido": "pendiente_humano", "email_id": email_id, "accion_tecnica": {}})

    # Regla operativa solicitada por el usuario:
    # si el agente lee un email y crea borrador real correctamente, puede marcarlo como leído
    # siempre que ALLOW_MARK_AS_READ=True. No se marca si no se creó borrador real.
    if gmail_client and p.ALLOW_MARK_AS_READ and p.MARK_READ_AFTER_DRAFT and borrador_real_creado:
        _log("[9] Marcando correo como leído porque el borrador real se creó correctamente...")
        r = gmail_client.marcar_como_leido(email_id, thread_id=thread_id)
        acciones_ejecutadas.append({"tipo": "marcar_como_leido", "ok": r.get("ok"), "detalle": r})
        _log(f"    Resultado marcar leído: {r.get('ok')}")
    elif gmail_client and p.ALLOW_MARK_AS_READ and acciones_correo.get("marcar_como_leido"):
        _log("[9] Marcando correo como leído por regla de correo...")
        r = gmail_client.marcar_como_leido(email_id, thread_id=thread_id)
        acciones_ejecutadas.append({"tipo": "marcar_como_leido", "ok": r.get("ok"), "detalle": r})
        _log(f"    Resultado marcar leído: {r.get('ok')}")
    else:
        _log("[9] No se marca como leído en esta ejecución.")

    resumen = f"Correo clasificado como {cat} con confianza {clasif['confianza']}."
    if documentos:
        resumen += f" Se han detectado {len(documentos)} adjunto(s) pendientes de revisión."
    if acciones:
        resumen += f" Se han generado {len(acciones)} acción(es) propuesta(s)."
    if borradores:
        resumen += f" Se ha generado {len(borradores)} borrador(es)."

    # Si se creó borrador real y se permite marcar como leído, reflejarlo en la sugerencia.
    if borrador_real_creado and p.ALLOW_MARK_AS_READ and p.MARK_READ_AFTER_DRAFT:
        acciones_correo = dict(acciones_correo)
        acciones_correo["marcar_como_leido"] = True
        acciones_correo["motivo"] = "Borrador real creado correctamente; se puede marcar como leído según configuración."

    respuesta = {
        "ok": True,
        "agente": "agente_gestor_correos_mitumi",
        "tipo_peticion": "analizar_correo",
        "resumen": resumen,
        "datos_detectados": {
            "email_id": email_id,
            "thread_id": thread_id,
            "remitente": correo.get("remitente"),
            "asunto": correo.get("asunto"),
            "categoria_correo": cat,
            "confianza_clasificacion": clasif["confianza"],
            "prioridad": clasif.get("prioridad", "media"),
            "riesgo": clasif.get("riesgo", "medio"),
            "motivo_clasificacion": clasif.get("motivo"),
            "metodo_clasificacion": clasif.get("metodo_clasificacion"),
            "datos_extraidos": clasif.get("datos_extraidos", {}),
            "documentos_detectados": documentos,
            "acciones_correo_sugeridas": acciones_correo,
            "estado_correo_sugerido": "clasificado" if cat != "no_clasificado" else "no_clasificado",
        },
        "acciones_propuestas": acciones,
        "bloqueos_detectados": [] if cat != "no_clasificado" else [{"tipo": "clasificacion_insuficiente", "descripcion": "Clasificación insegura. Revisión manual.", "requiere_revision_humana": True}],
        "borradores_generados": borradores,
        "acciones_ejecutadas": acciones_ejecutadas,
        "requiere_validacion_humana": bool(acciones or borradores or documentos or cat == "no_clasificado"),
        "nivel_riesgo": clasif.get("riesgo", "medio"),
        "errores": [],
        "trazas": {"fuentes_consultadas": ["gmail_composio"], "timestamp": datetime.now().isoformat(timespec="seconds"), "modo": "propuesta", "version_agente": p.AGENTE_VERSION},
    }
    guardar_respuesta(email_id, correo.get("asunto", ""), cat, True, respuesta)
    _log("[10] Correo procesado correctamente.")
    return respuesta


def procesar_bandeja_gmail() -> dict:
    gmail = GmailClient()
    _log("=" * 70)
    _log("AGENTE GESTOR CORREOS MITUMI")
    _log("=" * 70)
    _log(f"Versión: {p.AGENTE_VERSION}")
    _log(f"Gmail query: {p.GMAIL_QUERY}")
    _log(f"Máx. correos: {p.GMAIL_MAX_RESULTS}")
    _log(f"Crear borradores: {p.ALLOW_CREATE_DRAFTS}")
    _log(f"Marcar como leído: {p.ALLOW_MARK_AS_READ}")
    _log("[0] Leyendo Gmail vía Composio...")
    correos = gmail.fetch_emails()
    _log(f"[0] Correos detectados: {len(correos)}")

    resumen_lote = []
    out_dir = p.OUTPUTS_DIR / "respuestas_json"
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, correo in enumerate(correos, start=1):
        respuesta = procesar_correo(correo, gmail_client=gmail, indice=i, total=len(correos))
        email_id = correo.get("email_id", f"sin_id_{i}")
        with open(out_dir / f"respuesta_gmail_{i}_{email_id}.json", "w", encoding="utf-8") as f:
            json.dump(respuesta, f, ensure_ascii=False, indent=2)
        resumen_lote.append({
            "n": i,
            "email_id": email_id,
            "thread_id": correo.get("thread_id"),
            "remitente": correo.get("remitente"),
            "asunto": correo.get("asunto"),
            "categoria": respuesta.get("datos_detectados", {}).get("categoria_correo"),
            "confianza": respuesta.get("datos_detectados", {}).get("confianza_clasificacion"),
            "adjuntos": len(correo.get("adjuntos", [])),
            "borradores": len(respuesta.get("borradores_generados", [])),
            "acciones_ejecutadas": respuesta.get("acciones_ejecutadas", []),
            "marcar_como_leido_sugerido": respuesta.get("datos_detectados", {}).get("acciones_correo_sugeridas", {}).get("marcar_como_leido"),
            "ok": respuesta.get("ok"),
            "errores": respuesta.get("errores", []),
        })
        time.sleep(p.LLM_CALL_DELAY_SECONDS)
    return {"ok": True, "total": len(correos), "resumen_lote": resumen_lote}


def ejecutar_agente(payload: dict) -> dict:
    datos = payload.get("datos", {})
    correo = {
        "email_id": datos.get("email_id") or payload.get("id_registro"),
        "thread_id": datos.get("thread_id"),
        "remitente": datos.get("remitente", ""),
        "asunto": datos.get("asunto", ""),
        "cuerpo": datos.get("cuerpo", ""),
        "adjuntos": datos.get("adjuntos", []),
    }
    return procesar_correo(correo, gmail_client=None)
