from pathlib import Path
from .parametros import BASE_DIR

def cargar_prompt(nombre_archivo: str) -> str:
    ruta = BASE_DIR / "prompts" / nombre_archivo
    if not ruta.exists():
        return ""
    return ruta.read_text(encoding="utf-8")

PROMPT_CLASIFICACION = cargar_prompt("prompt_clasificacion.txt")
PROMPT_REDACCION = cargar_prompt("prompt_redaccion.txt")
REGLAS_COMUNES = cargar_prompt("reglas_comunes.txt")
