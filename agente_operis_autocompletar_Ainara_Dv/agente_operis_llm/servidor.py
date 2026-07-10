"""
servidor.py — API HTTP de agente_operis (autocompletar briefings) para el frontend React.

Mismo patron que Agente_04_Copilot_Raul/lumen_agente_04/servidor.py: una capa HTTP fina
pensada para que el frontend pueda mandar el texto de un briefing y recibir los campos del
evento ya extraidos, en JSON. No sustituye el contrato de integracion real del proyecto
(ejecutar_agente(payload) en src/agente.py, que sigue siendo lo que usaria el orquestador).

Arrancar:
    cd agente_operis_llm
    pip install -r requirements_servidor.txt   # flask + flask-cors (solo para este servidor)
    python servidor.py

Por defecto escucha en http://localhost:5002 (el mock de API_Nora usa el 5000 y Lumen el
5001, para poder tener los tres arrancados a la vez).

Endpoints:
    GET  /               -> estado del servidor (health check)
    POST /autocompletar  -> body: {"texto_briefing": "...", "motor": "reglas"|"llm" (opcional)}
                            Devuelve el contrato de salida comun del agente: datos_detectados
                            con los 6 bloques (evento, cliente, espacio, sala, presupuesto,
                            ponentes), bloqueos_detectados con los campos que faltan, y
                            requiere_validacion_humana=True SIEMPRE — el front debe mostrar
                            los campos como PROPUESTA editable, nunca guardarlos solos.

Notas:
    - Sin GROQ_API_KEY en .env, usar "motor": "reglas" (gratis y determinista). El motor
      "llm" fallara de forma controlada si no hay clave (ver src/llm.py).
    - Este servidor no guarda estado: cada peticion es independiente (a diferencia del chat
      de Lumen, aqui no hay memoria de conversacion que mantener).
"""

import sys
from pathlib import Path

from flask import Flask, request, jsonify

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))  # permite "from src.agente import ..." y "from config import ..."

from src.agente import ejecutar_agente  # noqa: E402
from config import settings  # noqa: E402

app = Flask(__name__)

# CORS: permite que el frontend React (otro puerto, p.ej. localhost:3000) llame a esta API
# desde el navegador. Sin esto, el navegador bloquea las peticiones aunque el servidor responda.
try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    print("Aviso: flask-cors no instalado. El frontend en el navegador puede fallar por CORS.")


def _error(codigo, mensaje, http=400):
    return jsonify({"error": True, "codigo": codigo, "mensaje": mensaje}), http


@app.get("/")
def inicio():
    return jsonify({
        "servicio": "agente_operis - autocompletar briefings",
        "estado": "en marcha",
        "motor_por_defecto": settings.MOTOR_POR_DEFECTO,
        "prueba": 'POST /autocompletar con {"texto_briefing": "..."}',
    })


@app.post("/autocompletar")
def autocompletar():
    cuerpo = request.get_json(silent=True)
    if not cuerpo or not isinstance(cuerpo, dict):
        return _error("CUERPO_INVALIDO", "Manda un JSON con al menos 'texto_briefing'.")

    texto_briefing = (cuerpo.get("texto_briefing") or "").strip()
    if not texto_briefing:
        return _error("CAMPO_OBLIGATORIO", "El campo 'texto_briefing' es obligatorio.")

    motor = cuerpo.get("motor") or settings.MOTOR_POR_DEFECTO
    if motor not in ("reglas", "llm"):
        return _error("MOTOR_INVALIDO", "El campo 'motor' debe ser 'reglas' o 'llm'.")

    # Se construye el contrato de entrada comun del agente (README.md, seccion 9.2):
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

    salida = ejecutar_agente(payload)
    http = 200 if salida.get("ok") else 422
    return jsonify(salida), http


if __name__ == "__main__":
    print("agente_operis — servidor HTTP para el frontend")
    print("Escuchando en http://localhost:5002  (Ctrl+C para parar)")
    app.run(host="0.0.0.0", port=5002, debug=False)
