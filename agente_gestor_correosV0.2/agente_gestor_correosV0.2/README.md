# Agente Gestor de Correos MITUMI

Versión basada conceptualmente en **Secretario AMPA V3.95**.

## Objetivo

Leer correos reales de Gmail, clasificarlos con LLM obligatorio y actuar como gestor operativo de bandeja para MITUMI.

## Qué hace

- Lee Gmail vía Composio.
- Clasifica correos con LLM obligatorio.
- Detecta correos de ponentes, clientes, nuevos eventos, facturas, proveedores, publicidad y spam.
- Detecta adjuntos y los marca como documentos pendientes de revisión.
- Genera acciones pendientes para front/admin.
- Crea borradores reales en Gmail si `ALLOW_CREATE_DRAFTS=True`.
- Marca leído solo si `ALLOW_MARK_AS_READ=True` y la regla lo permite.
- Guarda salidas en `outputs/respuestas_json/`.
- Guarda trazabilidad en SQLite local.

## Qué no hace

- No envía emails reales.
- No modifica la BBDD final de MITUMI.
- No valida documentos automáticamente.
- No confirma reservas, vuelos, hoteles ni presupuestos.
- No reenvía facturas si no existe destino/procedimiento configurado.

## Ejecución

```powershell
cd "C:\Users\Dario\Documents\Caperta_Botcamp\agente_gestor_correos_mitumi"
python main.py
```

## Configuración mínima `.env`

Copia `.env.example` a `.env` y configura:

```env
COMPOSIO_ENABLED=True
COMPOSIO_API_KEY=...
GMAIL_ENABLED=True
GMAIL_ACCOUNT_LABEL=secretario_ampa_pruebas
LLM_ENABLED=True
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
ALLOW_CREATE_DRAFTS=True
ALLOW_MARK_AS_READ=False
```

## Control de volumen

Para evitar límite de tokens:

```env
GMAIL_MAX_RESULTS=5
LLM_MAX_TOKENS=350
LLM_CALL_DELAY_SECONDS=1.5
```

Si Groq devuelve 429:

```env
GMAIL_MAX_RESULTS=3
LLM_CALL_DELAY_SECONDS=3
```


## Nota versión 0.1.1

Ajustes aplicados tras prueba real con Gmail:

- Reintento automático ante `429 rate_limit_exceeded` del LLM.
- Prompt de clasificación reducido para consumir menos tokens.
- `LLM_MAX_TOKENS` limitado internamente a 350.
- Corrección controlada de categorías cuando el LLM devuelve `no_clasificado` con confianza alta pero las reglas de apoyo detectan una señal clara.
- `no_clasificado` ya no puede salir con confianza 1.0.

Para pruebas con Groq gratuito se recomienda:

```env
GMAIL_MAX_RESULTS=5
LLM_MAX_TOKENS=300
LLM_CALL_DELAY_SECONDS=3
LLM_RETRY_MAX_ATTEMPTS=2
LLM_RETRY_BASE_SECONDS=4
```
