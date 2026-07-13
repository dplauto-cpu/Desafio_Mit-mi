import base64
import requests
from . import parametros as p
from .funciones import limpiar_html

COMPOSIO_EXECUTE = "https://backend.composio.dev/api/v3/tools/execute/{tool}"


def _headers():
    return {"x-api-key": p.COMPOSIO_API_KEY, "Content-Type": "application/json"}


class GmailError(Exception):
    pass


class GmailClient:
    def __init__(self):
        if not p.COMPOSIO_API_KEY:
            raise GmailError("COMPOSIO_API_KEY no configurada.")
        self.user_id = p.GMAIL_ACCOUNT_LABEL

    def ejecutar_tool(self, tool: str, arguments: dict) -> dict:
        url = COMPOSIO_EXECUTE.format(tool=tool)
        payload = {"user_id": self.user_id, "arguments": arguments}
        r = requests.post(url, headers=_headers(), json=payload, timeout=45)
        if r.status_code >= 400:
            raise GmailError(f"Error Composio {tool}: {r.status_code} - {r.text}")
        return r.json()

    def fetch_emails(self, query=None, max_results=None) -> list:
        data = self.ejecutar_tool("GMAIL_FETCH_EMAILS", {
            "query": query or p.GMAIL_QUERY,
            "max_results": max_results or p.GMAIL_MAX_RESULTS,
        })
        messages = data.get("data", {}).get("messages", [])
        return [self.normalizar_email(m) for m in messages]

    def crear_borrador(self, to: str, subject: str, body: str, thread_id: str | None = None, message_id: str | None = None) -> dict:
        """
        Crea un borrador real en Gmail.

        Objetivo: mantener el hilo cuando el correo procede de Gmail.
        Composio/Gmail puede variar los nombres de argumentos según versión, por eso se prueban
        varias combinaciones. Las primeras incluyen thread_id/message_id; las últimas son fallback
        para no bloquear la creación del borrador si el proveedor no acepta threading.
        """
        if not p.ALLOW_CREATE_DRAFTS:
            return {"ok": False, "omitido": True, "motivo": "ALLOW_CREATE_DRAFTS=False"}

        asunto_respuesta = subject or "Re: correo recibido"
        if subject and not subject.lower().startswith("re:"):
            asunto_respuesta = f"Re: {subject}"

        intentos = []

        if thread_id:
            intentos.extend([
                {"recipient_email": to, "subject": asunto_respuesta, "body": body, "thread_id": thread_id},
                {"recipient_email": to, "subject": asunto_respuesta, "body": body, "threadId": thread_id},
                {"to": to, "subject": asunto_respuesta, "body": body, "thread_id": thread_id, "is_html": False},
                {"to": [to], "subject": asunto_respuesta, "body": body, "thread_id": thread_id},
            ])

        if message_id:
            intentos.extend([
                {"recipient_email": to, "subject": asunto_respuesta, "body": body, "message_id": message_id},
                {"recipient_email": to, "subject": asunto_respuesta, "body": body, "reply_to_message_id": message_id},
                {"to": to, "subject": asunto_respuesta, "body": body, "message_id": message_id, "is_html": False},
            ])

        # Fallback sin hilo. Solo se usará si Composio rechaza todos los intentos con thread/message.
        intentos.extend([
            {"recipient_email": to, "subject": asunto_respuesta, "body": body},
            {"to": to, "subject": asunto_respuesta, "body": body, "is_html": False},
            {"to": [to], "subject": asunto_respuesta, "body": body},
        ])

        ultimo_error = None
        for args in intentos:
            try:
                return {"ok": True, "respuesta": self.ejecutar_tool("GMAIL_CREATE_EMAIL_DRAFT", args), "args_usados": args}
            except Exception as e:
                ultimo_error = str(e)

        return {"ok": False, "error": ultimo_error}

    def marcar_como_leido(self, email_id: str, thread_id: str | None = None) -> dict:
        """
        Marca como leído eliminando la etiqueta UNREAD.

        Composio cambia nombres de herramientas/esquemas entre versiones. La herramienta heredada
        GMAIL_MODIFY_EMAIL_LABELS no existe en el toolkit actual. Según el toolkit Gmail actual,
        las herramientas vigentes incluyen GMAIL_BATCH_MODIFY_MESSAGES y
        GMAIL_MODIFY_THREAD_LABELS. Por eso se prueban varias combinaciones seguras.
        """
        if not p.ALLOW_MARK_AS_READ:
            return {"ok": False, "omitido": True, "motivo": "ALLOW_MARK_AS_READ=False"}

        intentos = []

        # Opción preferente: batch modify por mensaje.
        intentos.extend([
            ("GMAIL_BATCH_MODIFY_MESSAGES", {"ids": [email_id], "removeLabelIds": ["UNREAD"], "addLabelIds": []}),
            ("GMAIL_BATCH_MODIFY_MESSAGES", {"ids": [email_id], "remove_label_ids": ["UNREAD"], "add_label_ids": []}),
            ("GMAIL_BATCH_MODIFY_MESSAGES", {"message_ids": [email_id], "remove_label_ids": ["UNREAD"], "add_label_ids": []}),
            ("GMAIL_BATCH_MODIFY_MESSAGES", {"messageIds": [email_id], "removeLabelIds": ["UNREAD"], "addLabelIds": []}),
        ])

        # Opción por hilo, útil cuando Gmail trabaja mejor con thread_id.
        if thread_id:
            intentos.extend([
                ("GMAIL_MODIFY_THREAD_LABELS", {"thread_id": thread_id, "remove_label_ids": ["UNREAD"], "add_label_ids": []}),
                ("GMAIL_MODIFY_THREAD_LABELS", {"id": thread_id, "remove_label_ids": ["UNREAD"], "add_label_ids": []}),
                ("GMAIL_MODIFY_THREAD_LABELS", {"threadId": thread_id, "removeLabelIds": ["UNREAD"], "addLabelIds": []}),
            ])

        # Compatibilidad con toolkits antiguos o nombres alternativos.
        intentos.extend([
            ("GMAIL_ADD_LABEL_TO_EMAIL", {"message_id": email_id, "remove_label_ids": ["UNREAD"], "add_label_ids": []}),
            ("GMAIL_ADD_LABEL_TO_EMAIL", {"id": email_id, "removeLabelIds": ["UNREAD"], "addLabelIds": []}),
            ("GMAIL_MODIFY_EMAIL", {"message_id": email_id, "remove_label_ids": ["UNREAD"], "add_label_ids": []}),
            ("GMAIL_MODIFY_MESSAGE", {"message_id": email_id, "remove_label_ids": ["UNREAD"], "add_label_ids": []}),
        ])

        errores = []
        for tool, args in intentos:
            try:
                return {"ok": True, "respuesta": self.ejecutar_tool(tool, args), "tool_usada": tool, "args_usados": args}
            except Exception as e:
                errores.append({"tool": tool, "args": args, "error": str(e)})

        return {"ok": False, "error": errores[-1]["error"] if errores else "Sin intentos", "errores_intentos": errores}

    def normalizar_email(self, email: dict) -> dict:
        email_id = email.get("id") or email.get("messageId") or email.get("message_id") or email.get("threadId") or "gmail_real_sin_id"
        thread_id = email.get("threadId") or email.get("thread_id") or email.get("threadID")
        remitente = email.get("sender") or email.get("from") or ""
        asunto = email.get("subject") or email.get("preview", {}).get("subject") or ""
        cuerpo = self._extraer_cuerpo(email)
        adjuntos = self._extraer_adjuntos(email)
        return {
            "email_id": email_id,
            "thread_id": thread_id,
            "remitente": remitente,
            "asunto": asunto,
            "cuerpo": cuerpo,
            "adjuntos": adjuntos,
            "raw": email,
        }

    def _extraer_cuerpo(self, email: dict) -> str:
        campos = [email.get("messageText"), email.get("body"), email.get("text"), email.get("snippet"), email.get("preview", {}).get("body")]
        for c in campos:
            limpio = limpiar_html(c or "")
            if limpio:
                return limpio
        textos = []

        def recorrer(obj):
            if isinstance(obj, dict):
                mime = obj.get("mimeType", "")
                body = obj.get("body", {})
                data = body.get("data") if isinstance(body, dict) else None
                if data and ("text/plain" in mime or "text/html" in mime):
                    try:
                        raw = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="ignore")
                        textos.append(limpiar_html(raw))
                    except Exception:
                        pass
                for v in obj.values():
                    recorrer(v)
            elif isinstance(obj, list):
                for x in obj:
                    recorrer(x)

        recorrer(email.get("payload", {}))
        return "\n".join([t for t in textos if t]).strip()

    def _extraer_adjuntos(self, email: dict) -> list:
        adjuntos = []
        for adj in email.get("attachments", []) or []:
            if isinstance(adj, dict):
                adjuntos.append({"nombre": adj.get("filename") or adj.get("name") or "adjunto_sin_nombre", "mime_type": adj.get("mimeType") or adj.get("mime_type") or "", "size_bytes": adj.get("size") or adj.get("size_bytes") or 0})

        def recorrer(obj):
            if isinstance(obj, dict):
                filename = obj.get("filename")
                if filename:
                    body = obj.get("body", {}) if isinstance(obj.get("body"), dict) else {}
                    adjuntos.append({"nombre": filename, "mime_type": obj.get("mimeType", ""), "size_bytes": body.get("size", 0), "attachment_id": body.get("attachmentId")})
                for v in obj.values():
                    recorrer(v)
            elif isinstance(obj, list):
                for x in obj:
                    recorrer(x)

        recorrer(email.get("payload", {}))
        vistos = set()
        limpios = []
        for a in adjuntos:
            key = (a.get("nombre"), a.get("size_bytes"))
            if key not in vistos:
                vistos.add(key)
                limpios.append(a)
        return limpios
