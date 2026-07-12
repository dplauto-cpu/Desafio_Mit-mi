"""
app.py — Backend unificado de data (Backstage / Mitumi).

Un solo servicio HTTP (FastAPI) que monta todos los agentes de data como rutas, en vez
de un mini-servidor Flask suelto por agente. Los agentes no se tocan: su logica sigue
viviendo en sus carpetas (ejecutar_agente(payload) sigue siendo el contrato interno) y
este backend es la unica puerta HTTP de data hacia el front.

Arrancar:
    cd backend_data_Nora
    pip install -r requirements.txt
    python app.py                      # o: uvicorn app:app --port 5003

Por defecto escucha en http://localhost:5003 (5000 mock API_Nora, 5001 Lumen suelto,
5002 Operis suelto — los servidores individuales siguen existiendo y pueden convivir
con este). PORT y HOST se pueden cambiar por variable de entorno.

Rutas (documentacion interactiva en /docs, cortesia de FastAPI):
    GET  /                              -> health general (estado de los dos agentes)
    POST /agentes/lumen/chat            -> chat de Lumen (memoria por sesion_id)
    POST /agentes/lumen/chat/reset      -> olvida una sesion
    POST /agentes/operis/autocompletar  -> extraer campos de un briefing

    Alias de compatibilidad para el front actual (mismas rutas que los servidores
    sueltos, solo cambia el puerto): POST /chat, /chat/reset, /autocompletar.

Contratos de entrada/salida: identicos a los servidores originales — ver
API_Nora/api/endpoints_v4.md.
"""

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from cargador_agentes import OPERIS  # carga ambos agentes al arrancar (falla rapido si algo no importa)
from routers import lumen, operis

app = FastAPI(
    title="Backstage — backend de data",
    description="API unica de los agentes de data (Lumen, Operis). Solo lectura de Neon.",
    version="1.0.0",
)

# CORS: permite que el front React (otro puerto, p.ej. localhost:3000/5173) llame a esta
# API desde el navegador. Abierto a cualquier origen: fase demo, sin autenticacion.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas con espacio de nombres por agente (las canonicas)...
app.include_router(lumen.router, prefix="/agentes/lumen")
app.include_router(operis.router, prefix="/agentes/operis")
# ...y alias en la raiz, compatibles con el front que hoy llama a :5001/chat y
# :5002/autocompletar — le basta cambiar la URL base a :5003.
app.include_router(lumen.router, include_in_schema=False)
app.include_router(operis.router, include_in_schema=False)


@app.get("/")
def salud():
    return {
        "servicio": "Backstage — backend de data",
        "estado": "en marcha",
        "agentes": {
            "lumen": {
                "descripcion": "copiloto de consulta de eventos (lee Neon, solo lectura)",
                "rutas": ["POST /agentes/lumen/chat", "POST /agentes/lumen/chat/reset"],
                "sesiones_activas": lumen.sesiones_activas(),
            },
            "operis": {
                "descripcion": "autocompletar briefings (propuesta editable, valida el humano)",
                "rutas": ["POST /agentes/operis/autocompletar"],
                "motor_por_defecto": OPERIS.MOTOR_POR_DEFECTO,
            },
        },
        "documentacion": "/docs",
    }


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    # Conserva el formato de error de los servidores originales para el 404.
    if exc.status_code == 404:
        return JSONResponse(
            {"error": True, "codigo": "RUTA_NO_ENCONTRADA", "mensaje": "Esa ruta no existe."},
            status_code=404,
        )
    return JSONResponse({"error": True, "codigo": "HTTP_ERROR", "mensaje": str(exc.detail)},
                        status_code=exc.status_code)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "5003") or "5003")
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port)
