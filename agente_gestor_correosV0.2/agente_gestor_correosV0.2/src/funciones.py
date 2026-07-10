import hashlib
import re
from html import unescape
from .llm import clasificar_con_llm, LLMError

CATEGORIAS_PERMITIDAS = {
    "nuevo_evento_lead", "cliente_briefing", "cliente_cambio_fecha", "cliente_cambio_aforo",
    "cliente_aprobacion", "cliente_duda", "cliente_cancelacion", "cliente_queja",
    "ponente_confirmacion", "ponente_informacion_general", "ponente_documentacion_cv",
    "ponente_documentacion_foto", "ponente_presentacion", "ponente_actualizacion_presentacion",
    "ponente_duda_hotel", "ponente_duda_viaje", "ponente_necesidad_tecnica",
    "ponente_restriccion_alimentaria", "ponente_cancelacion",
    "espacio_disponibilidad", "espacio_presupuesto", "proveedor_presupuesto",
    "proveedor_confirmacion", "proveedor_incidencia", "contrato", "albaran",
    "factura_cliente", "factura_proveedor", "factura_ponente", "justificante_pago",
    "recordatorio_pago", "documento_fiscal", "publicidad", "newsletter", "spam",
    "phishing_sospechoso", "rebote_email", "fuera_oficina", "respuesta_automatica",
    "duplicado", "no_relacionado", "no_clasificado"
}

ALIAS_CATEGORIAS = {
    "consulta_logistica_ponente": "ponente_duda_viaje",
    "ponente_logistica": "ponente_duda_viaje",
    "documentacion_vuelo": "ponente_duda_viaje",
    "duda_vuelo": "ponente_duda_viaje",
    "duda_hotel": "ponente_duda_hotel",
    "alojamiento_ponente": "ponente_duda_hotel",
    "fichas_ponentes": "ponente_documentacion_cv",
    "datos_ponentes": "ponente_documentacion_cv",
    "biografia_ponente": "ponente_documentacion_cv",
    "cv_ponente": "ponente_documentacion_cv",
    "presupuesto_evento": "nuevo_evento_lead",
    "solicitud_presupuesto": "nuevo_evento_lead",
    "lead_evento": "nuevo_evento_lead",
    "factura": "factura_proveedor",
    "correo_publicitario": "publicidad",
    "confirmacion_reservas": "ponente_confirmacion",
    "confirmacion_reserva": "ponente_confirmacion",
    "reserva_confirmada": "ponente_confirmacion",
    "logistica_ponente": "ponente_duda_viaje",
    "consulta_vuelo": "ponente_duda_viaje",
    "documentacion_de_vuelo": "ponente_duda_viaje",
    "consulta_documentacion_vuelo": "ponente_duda_viaje",
}

def limpiar_html(texto: str) -> str:
    if not texto:
        return ""
    texto = unescape(texto)
    texto = re.sub(r"<br\s*/?>", "\n", texto, flags=re.IGNORECASE)
    texto = re.sub(r"<[^>]+>", " ", texto)
    return " ".join(texto.split())

def apoyo_reglas(correo: dict) -> dict:
    texto = f"{correo.get('asunto','')} {correo.get('cuerpo','')}".lower()
    candidatos = []
    def add(cat, palabra):
        if palabra in texto:
            candidatos.append({"categoria": cat, "motivo": palabra})
    for palabra in ["ponente", "ponentes", "ficha", "fichas", "biografia", "cv"]:
        add("ponente_documentacion_cv" if palabra in ["ficha", "fichas", "biografia", "cv"] else "ponente_informacion_general", palabra)
    for palabra in ["vuelo", "billete", "tren", "taxi", "traslado", "aeropuerto"]:
        add("ponente_duda_viaje", palabra)
    for palabra in ["reserva", "reservas", "confirmación", "confirmacion", "servicio de traslado"]:
        add("ponente_confirmacion", palabra)
    for palabra in ["hotel", "alojamiento", "habitación", "habitacion"]:
        add("ponente_duda_hotel", palabra)
    for palabra in ["presupuesto", "propuesta", "organizar", "evento", "jornada"]:
        add("nuevo_evento_lead", palabra)
    for palabra in ["factura", "iva", "base imponible"]:
        add("factura_proveedor", palabra)
    for palabra in ["newsletter", "unsubscribe", "oferta"]:
        add("newsletter", palabra)
    return {"candidatos": candidatos[:5], "hay_adjuntos": bool(correo.get("adjuntos"))}

def normalizar_categoria(categoria: str) -> str:
    cat = (categoria or "no_clasificado").strip().lower()
    cat = cat.replace(" ", "_").replace("-", "_")
    cat = ALIAS_CATEGORIAS.get(cat, cat)
    if cat not in CATEGORIAS_PERMITIDAS:
        return "no_clasificado"
    return cat

def clasificar_correo(correo: dict) -> dict:
    apoyo = apoyo_reglas(correo)
    try:
        data = clasificar_con_llm(correo, apoyo)
    except LLMError as e:
        return {
            "ok": False,
            "categoria": "error_llm_obligatorio",
            "confianza": 0.0,
            "prioridad": "alta",
            "riesgo": "alto",
            "motivo": str(e),
            "requiere_respuesta": False,
            "requiere_accion_front": True,
            "datos_extraidos": {},
            "metodo_clasificacion": "llm_obligatorio_error",
            "error": str(e),
        }
    cat_original = (data.get("categoria") or "").strip().lower()
    cat = normalizar_categoria(cat_original)
    try:
        confianza = float(data.get("confianza", 0.0))
    except Exception:
        confianza = 0.0

    metodo = "llm_obligatorio_con_apoyo_reglas"
    motivo = data.get("motivo", "Clasificación LLM.")

    # Si el LLM funciona pero responde no_clasificado con confianza alta,
    # se admite una corrección por reglas de apoyo, no como fallback autónomo.
    candidatos_apoyo = apoyo.get("candidatos", [])
    if cat == "no_clasificado" and confianza >= 0.80 and candidatos_apoyo:
        cat = normalizar_categoria(candidatos_apoyo[0].get("categoria"))
        confianza = min(confianza, 0.82)
        metodo = "llm_obligatorio_corregido_por_apoyo_reglas"
        motivo = f"LLM ejecutado, pero la categoría se normaliza con apoyo de reglas: {candidatos_apoyo[0].get('motivo')}"

    if confianza < 0.80:
        cat = "no_clasificado"

    # Un no_clasificado no debe salir con confianza 1.0, aunque el LLM lo devuelva así.
    if cat == "no_clasificado" and confianza >= 0.80:
        confianza = 0.79
        metodo = "llm_obligatorio_no_clasificado_normalizado"

    return {
        "ok": True,
        "categoria": cat,
        "confianza": confianza,
        "prioridad": data.get("prioridad", "media"),
        "riesgo": data.get("riesgo", "medio"),
        "motivo": motivo,
        "requiere_respuesta": bool(data.get("requiere_respuesta", False)),
        "requiere_accion_front": bool(data.get("requiere_accion_front", True)),
        "datos_extraidos": data.get("datos_extraidos", {}) or {},
        "metodo_clasificacion": metodo,
    }

def detectar_documentos(correo: dict, categoria: str) -> list:
    docs = []
    for adj in correo.get("adjuntos", []) or []:
        nombre = adj.get("nombre") or adj.get("filename") or "adjunto_sin_nombre"
        mime = adj.get("mime_type") or adj.get("mimeType") or ""
        base = f"{correo.get('email_id','')}|{nombre}|{adj.get('size_bytes',0)}"
        h = hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]
        lower = nombre.lower()
        if categoria.startswith("factura") or "factura" in lower:
            tipo = "factura"
        elif lower.endswith((".ppt", ".pptx", ".pdf")) and "present" in lower:
            tipo = "presentacion"
        elif "cv" in lower or "bio" in lower or "ficha" in lower:
            tipo = "ficha_ponente"
        elif lower.endswith((".jpg", ".jpeg", ".png")):
            tipo = "foto"
        elif lower.endswith(".pdf"):
            tipo = "pdf_pendiente_clasificacion"
        else:
            tipo = "documento_pendiente_clasificacion"
        docs.append({
            "documento_id_temporal": f"doc_tmp_{h}",
            "email_id": correo.get("email_id"),
            "nombre_archivo": nombre,
            "mime_type": mime,
            "size_bytes": adj.get("size_bytes", 0),
            "tipo_documento_detectado": tipo,
            "categoria_correo": categoria,
            "estado_documental": "pendiente_revision_humana",
            "requiere_validacion_humana": True,
            "hash_control": h,
        })
    return docs

def construir_acciones(correo: dict, clasif: dict, documentos: list, email_facturacion_destino: str = "") -> list:
    cat = clasif["categoria"]
    email_id = correo.get("email_id")
    acciones = []
    if documentos:
        acciones.append({
            "tipo": "registrar_documentos_pendientes",
            "descripcion": f"Registrar {len(documentos)} adjunto(s) en bandeja documental pendiente de validación.",
            "prioridad": "alta" if cat == "no_clasificado" else "media",
            "requiere_validacion_humana": True,
            "visible_en_front": True,
            "estado_sugerido": "pendiente_humano",
            "email_id": email_id,
            "accion_tecnica": {"registrar_documentos_pendientes": True, "documentos": [d["documento_id_temporal"] for d in documentos]},
        })
    if cat == "nuevo_evento_lead":
        acciones.append({"tipo": "crear_lead_evento_pendiente", "descripcion": "Crear oportunidad comercial pendiente de revisión desde el front.", "prioridad": "media", "requiere_validacion_humana": True, "visible_en_front": True, "estado_sugerido": "pendiente_humano", "email_id": email_id, "accion_tecnica": {}})
    elif cat.startswith("factura") or cat in {"documento_fiscal", "justificante_pago", "recordatorio_pago"}:
        if email_facturacion_destino:
            acciones.append({"tipo": "reenviar_facturacion_pendiente", "descripcion": f"Factura/documento fiscal detectado. Reenvío propuesto a {email_facturacion_destino}.", "prioridad": "alta", "requiere_validacion_humana": True, "visible_en_front": True, "estado_sugerido": "pendiente_humano", "email_id": email_id, "accion_tecnica": {"reenviar": True, "destino": email_facturacion_destino}})
        else:
            acciones.append({"tipo": "definir_flujo_facturacion", "descripcion": "Factura detectada, pero no existe correo/procedimiento de facturación configurado. Revisar manualmente.", "prioridad": "alta", "requiere_validacion_humana": True, "visible_en_front": True, "estado_sugerido": "pendiente_humano", "email_id": email_id, "accion_tecnica": {"reenviar": False, "motivo": "EMAIL_FACTURACION_DESTINO vacío"}})
    elif cat.startswith("ponente"):
        acciones.append({"tipo": f"revisar_{cat}", "descripcion": "Correo relacionado con ponente. Revisar y vincular al ponente/evento si procede.", "prioridad": clasif.get("prioridad", "media"), "requiere_validacion_humana": True, "visible_en_front": True, "estado_sugerido": "pendiente_humano", "email_id": email_id, "accion_tecnica": {}})
    elif cat in {"publicidad", "newsletter", "spam", "no_relacionado"}:
        acciones.append({"tipo": "limpieza_correo_sugerida", "descripcion": f"Correo clasificado como {cat}. Limpieza sugerida según permisos.", "prioridad": "baja", "requiere_validacion_humana": False, "visible_en_front": False, "estado_sugerido": "automatico_si_permitido", "email_id": email_id, "accion_tecnica": {"archivar_o_borrar": True}})
    elif cat == "no_clasificado":
        acciones.append({"tipo": "revisar_clasificacion_correo", "descripcion": "Correo no clasificado por confianza insuficiente. Revisar manualmente.", "prioridad": "alta" if documentos else "media", "requiere_validacion_humana": True, "visible_en_front": True, "estado_sugerido": "pendiente_humano", "email_id": email_id, "accion_tecnica": {"marcar_como_leido": False, "borrar": False, "reenviar": False}})
    return acciones

def sugerir_acciones_correo(cat: str, acciones: list, documentos: list) -> dict:
    hay_front = any(a.get("visible_en_front") for a in acciones)
    if cat in {"publicidad", "newsletter", "spam", "no_relacionado"}:
        return {"marcar_como_leido": True, "archivar": cat in {"newsletter", "no_relacionado"}, "borrar": cat in {"publicidad", "spam"}, "reenviar": False, "motivo": "Correo de baja criticidad clasificado."}
    if cat == "no_clasificado":
        return {"marcar_como_leido": False, "archivar": False, "borrar": False, "reenviar": False, "motivo": "Correo no clasificado o confianza insuficiente."}
    if documentos:
        return {"marcar_como_leido": False, "archivar": False, "borrar": False, "reenviar": False, "motivo": "Correo con adjuntos: no marcar como leído hasta registrar la acción documental pendiente."}
    if hay_front:
        return {"marcar_como_leido": False, "archivar": False, "borrar": False, "reenviar": False, "motivo": "Correo clasificado con acción pendiente visible en front."}
    return {"marcar_como_leido": True, "archivar": False, "borrar": False, "reenviar": False, "motivo": "Correo clasificado sin acción crítica pendiente."}
