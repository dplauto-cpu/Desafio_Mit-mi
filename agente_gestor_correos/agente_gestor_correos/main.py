import json
from src import parametros as p
from src.agente import procesar_bandeja_gmail, ejecutar_agente

print("AGENTE_VERSION=", p.AGENTE_VERSION)

if p.GMAIL_ENABLED and p.COMPOSIO_ENABLED:
    resultado = procesar_bandeja_gmail()
    print("RESUMEN_LOTE")
    print(json.dumps(resultado["resumen_lote"], ensure_ascii=False, indent=2))
    print("ARCHIVOS_GENERADOS_EN= outputs/respuestas_json/")
else:
    demo = {
        "id_evento": None,
        "id_registro": "demo-001",
        "tipo_peticion": "analizar_correo",
        "origen": "demo",
        "usuario_solicitante": "sistema",
        "rol_usuario": "sistema",
        "datos": {
            "email_id": "demo-001",
            "remitente": "ponente@empresa.com",
            "asunto": "Envío de fichas de ponentes",
            "cuerpo": "Adjunto las fichas y biografías de los ponentes del evento.",
            "adjuntos": [{"nombre": "fichas_ponentes.pdf", "mime_type": "application/pdf", "size_bytes": 120000}],
        },
        "contexto": {},
        "modo": "propuesta",
    }
    print(json.dumps(ejecutar_agente(demo), ensure_ascii=False, indent=2))
