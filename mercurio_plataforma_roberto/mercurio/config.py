"""Configuración de Vigil Ponente: API de la plataforma, salida y LLM.

A diferencia de Vigil, este agente **no tiene base de datos propia**: lee los
datos de ponentes y eventos de la **API REST de la plataforma** (el backend que
el equipo full-stack expone sobre su Postgres con Prisma) y solo escribe su
salida (JSON + PDF) para que la plataforma la muestre. Todo lo sensible viene
de variables de entorno; nada de secretos hardcodeados.
"""

# traigo os para poder leer variables de entorno del sistema
import os

# --- API de la plataforma (la fuente de datos: ponentes, eventos, ponencias) ---
# URL base de la API del backend full-stack (p. ej. https://mi-plataforma/api)
PLATFORM_API_URL = os.environ.get("VIGIL_PONENTE_API_URL", "")
# token de autenticación para esa API (si la plataforma lo exige)
PLATFORM_API_TOKEN = os.environ.get("VIGIL_PONENTE_API_TOKEN", "")
# rutas de cada colección dentro de la API (ajustables a los endpoints reales)
EP_EVENTOS = os.environ.get("VIGIL_PONENTE_EP_EVENTOS", "eventos")
EP_PONENCIAS = os.environ.get("VIGIL_PONENTE_EP_PONENCIAS", "ponencias")
EP_PONENTES = os.environ.get("VIGIL_PONENTE_EP_PONENTES", "ponentes")

# --- LLM (Groq), opcional: solo se usa para redactar el informe en modo real ---
# leo la clave de la API de Groq desde el entorno (vacía si no está puesta)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
# leo qué modelo usar; si no me lo dan, uso el mismo que la demo de Vigil
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# --- Salida hacia la plataforma ---
# Igual que Vigil, esta versión no manda email: escribe un JSON con las
# propuestas de viaje (más un PDF por ponencia) que la plataforma lee.
# decido en qué carpeta dejo los archivos de salida; por defecto "salida_ponente"
OUTPUT_DIR = os.environ.get(
    "VIGIL_PONENTE_OUTPUT_DIR",
    os.path.join(os.path.dirname(__file__), "..", "salida_ponente"),
)

# --- Parámetros del viaje ---
# cuántos días antes del inicio del evento llega el ponente (para descansar)
DIAS_ANTES = int(os.environ.get("VIGIL_PONENTE_DIAS_ANTES", "1"))
# cuántos días después del fin del evento se marcha el ponente
DIAS_DESPUES = int(os.environ.get("VIGIL_PONENTE_DIAS_DESPUES", "1"))
# cuántas sugerencias de cada tipo (hoteles, vuelos, trenes) ofrezco
SUGERENCIAS_POR_TIPO = int(os.environ.get("VIGIL_PONENTE_SUGERENCIAS", "3"))

# --- CORS (para que el front de la plataforma pueda llamar a esta API) ---
# leo los orígenes permitidos separados por comas; por defecto "*" (cualquiera),
# cómodo para la demo. En producción pongo aquí solo el dominio de la plataforma.
CORS_ORIGINS = [
    origen.strip()
    for origen in os.environ.get("VIGIL_PONENTE_CORS_ORIGINS", "*").split(",")
    if origen.strip()
]
