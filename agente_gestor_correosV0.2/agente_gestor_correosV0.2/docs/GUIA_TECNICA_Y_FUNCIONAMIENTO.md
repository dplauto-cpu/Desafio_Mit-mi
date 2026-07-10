# Guía técnica — Agente Gestor Correos MITUMI

## Flujo

```text
python main.py
↓
lee Gmail vía Composio
↓
clasifica con LLM obligatorio
↓
genera acciones pendientes
↓
crea borradores reales si ALLOW_CREATE_DRAFTS=True
↓
guarda trazabilidad JSON y SQLite
```

## Principios

- Basado conceptualmente en Secretario AMPA V3.95.
- Mantiene estructura sencilla: `main.py`, `servicio.py`, `src/`, `prompts/`, `data/`, `docs/`, `deploy/`.
- No envía correos reales.
- No borra correos por defecto.
- No escribe en la BBDD final del proyecto MITUMI.
