"""
cargador_agentes.py — carga los agentes de data dentro del proceso del backend unificado.

Problema que resuelve: cada agente es un proyecto Python independiente con paquetes de
primer nivel que se llaman IGUAL (src, config, data...). No se pueden importar los dos a
la vez de la forma normal, porque el segundo import de "src.agente" devolveria el del
primero (Python cachea los modulos por nombre en sys.modules).

Estrategia (sin tocar el codigo de ningun agente):
    1. Lumen se carga primero: se mete su carpeta en sys.path, se importan sus modulos,
       se GUARDAN las referencias a sus funciones (siguen vivas aunque el modulo salga de
       sys.modules, porque cada funcion conserva sus propios globals) y se purgan los
       nombres compartidos de sys.modules.
    2. Operis se carga el ULTIMO y sus modulos se quedan RESIDENTES en sys.modules,
       porque hace un import perezoso en tiempo de peticion (src/nucleo.py:
       "from src.llm import extraer_briefing_llm" cuando motor="llm") que debe resolver
       a SU src.llm, no al de Lumen.
    Verificado: Lumen no tiene imports perezosos de sus paquetes propios, asi que puede
    vivir fuera de sys.modules sin problema. Si algun dia se anade uno, este orden deja
    de valer y ese agente tendria que pasar a ser el residente (solo puede haber uno).

.env: el settings.py de Lumen busca el .env en la raiz de Agente_04_Copilot_Raul/, pero
el archivo real esta en lumen_agente_04/.env. Como su cargar_env() da prioridad a
os.environ sobre el archivo, aqui se inyectan esas variables en os.environ antes de
importar y el agente ve su configuracion real sin modificarlo.

Para anadir un agente nuevo (alertas, telegram...): replicar el patron de _cargar_lumen()
y decidir si necesita quedarse residente (solo si tiene imports perezosos de src/config).
"""

import importlib
import os
import sys
from pathlib import Path
from types import SimpleNamespace

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent

RUTA_LUMEN = REPO_DIR / "Agente_04_Copilot_Raul"
ENV_LUMEN = RUTA_LUMEN / "lumen_agente_04" / ".env"
RUTA_OPERIS = REPO_DIR / "agente_operis_autocompletar_Ainara_Dv" / "agente_operis_llm"

# Nombres de paquete de primer nivel que colisionan entre agentes.
_PAQUETES_COMPARTIDOS = {"src", "config", "integrations", "data", "prompts"}


def _inyectar_env(ruta_env):
    """Vuelca un .env en os.environ (sin pisar lo que ya este definido).

    Mismo formato que cargar_env() de los agentes: lineas CLAVE=valor, comentarios
    con # (tambien en linea). os.environ tiene prioridad en los settings de ambos
    agentes, asi que con esto basta para que vean su configuracion real.
    """
    if not ruta_env.exists():
        return
    for linea in ruta_env.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, _, valor = linea.partition("=")
        valor = valor.split("#", 1)[0].strip()
        os.environ.setdefault(clave.strip(), valor)


def _purgar_paquetes_compartidos():
    for nombre in list(sys.modules):
        if nombre.split(".")[0] in _PAQUETES_COMPARTIDOS:
            del sys.modules[nombre]


def _cargar_lumen():
    _inyectar_env(ENV_LUMEN)
    _purgar_paquetes_compartidos()
    sys.path.insert(0, str(RUTA_LUMEN))
    try:
        agente = importlib.import_module("src.agente")
        memoria = importlib.import_module("src.memoria")
    finally:
        sys.path.remove(str(RUTA_LUMEN))
    lumen = SimpleNamespace(
        ejecutar_agente=agente.ejecutar_agente,
        MemoriaConversacion=memoria.MemoriaConversacion,
        construir_payload=memoria.construir_payload,
    )
    _purgar_paquetes_compartidos()  # deja libres los nombres para Operis
    return lumen


def _cargar_operis():
    # Residente: su carpeta se queda en sys.path y sus modulos en sys.modules
    # (necesario para su import perezoso de src.llm — ver cabecera).
    sys.path.insert(0, str(RUTA_OPERIS))
    agente = importlib.import_module("src.agente")
    settings = importlib.import_module("config.settings")
    return SimpleNamespace(
        ejecutar_agente=agente.ejecutar_agente,
        MOTOR_POR_DEFECTO=settings.MOTOR_POR_DEFECTO,
    )


LUMEN = _cargar_lumen()
OPERIS = _cargar_operis()
