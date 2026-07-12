# src/nucleo.py
# =====================================================================
# NÚCLEO - LÓGICA PRINCIPAL DEL AGENTE OPERIS
# =====================================================================
# Punto de entrada ejecutar_agente(payload).
# Valida la entrada, elige el motor (ahora solo LLM), ejecuta la
# extracción, genera la validación y construye la salida.
#
# Cambios principales:
#   - Solo motor LLM (eliminado motor de reglas)
#   - Acepta historial_anterior en el contexto para modo actualización
#   - id_evento es obligatorio (para el histórico)
#   - NUEVO: acepta bloques_a_actualizar para actualización parcial
# =====================================================================

from datetime import datetime
from src.validaciones import validar_entrada
from src.llm import extraer_briefing_llm
from src.schemas import (
    crear_estructura_vacia_completa,
    generar_aviso_y_validacion,
    construir_salida_base
)


# =====================================================================
# 1. FUNCIÓN PRINCIPAL
# =====================================================================
def ejecutar_agente(payload):
    """
    Punto de entrada único del agente Operis.
    
    Args:
        payload (dict): Contrato de entrada con los siguientes campos:
            - id_evento (str): OBLIGATORIO. ID del evento para el histórico
            - id_registro (str, optional)
            - tipo_peticion (str): "extraer_briefing"
            - origen (str): "backend", "manual", etc.
            - usuario_solicitante (str)
            - rol_usuario (str)
            - datos (dict):
                - texto_briefing (str): Texto del briefing a procesar
                - motor (str, optional): "llm" (por defecto)
                - groq_api_key (str, optional): API key de Groq
                - bloques_a_actualizar (list, optional): Bloques a actualizar
            - contexto (dict, optional):
                - historial_anterior (dict, optional): Estado previo para actualización
                - modo_actualizacion (str, optional): "fusionar" (por defecto)
            - modo (str): "propuesta" (siempre)
    
    Returns:
        dict: Salida completa del agente siguiendo el contrato
    """
    try:
        # ----- 1. VALIDAR ENTRADA -----
        errores_validacion = validar_entrada(payload)
        if errores_validacion:
            return _construir_respuesta_error(errores_validacion)
        
        # ----- 2. EXTRAER DATOS DEL PAYLOAD -----
        texto = payload["datos"]["texto_briefing"]
        motor = payload["datos"].get("motor", "llm")
        api_key = payload["datos"].get("groq_api_key")
        evento_id = payload.get("id_evento")
        historial_anterior = payload.get("contexto", {}).get("historial_anterior")
        modo_actualizacion = payload.get("contexto", {}).get("modo_actualizacion", "fusionar")

        # Si quien llama no pasó contexto.historial_anterior explícito,
        # se intenta autocargar el estado ACTUAL del evento desde la BD
        # real (kit_conexion_agentes_Nora, ver src/lectura_bd.py) --
        # así el modo actualización funciona sin depender de que un
        # backend externo guarde y pase el histórico. Si la BD no está
        # disponible (sin DATABASE_URL, sin psycopg, o el evento no
        # existe todavía en la BD real), esto devuelve None sin fallar
        # -- se procesa igual, como una extracción inicial sin histórico.
        historial_desde_bd = False
        if not historial_anterior and evento_id:
            try:
                from src.lectura_bd import construir_historial_desde_bd
                historial_anterior = construir_historial_desde_bd(evento_id)
                historial_desde_bd = historial_anterior is not None
            except ImportError:
                historial_anterior = None
        
        # NUEVO: Extraer bloques_a_actualizar
        bloques_a_actualizar = payload["datos"].get("bloques_a_actualizar")
        
        # ----- 3. VERIFICAR MOTOR (SOLO LLM) -----
        if motor != "llm":
            return _construir_respuesta_error(
                [f"Motor '{motor}' no soportado. El único motor disponible es 'llm'."]
            )
        
        # ----- 4. VERIFICAR ID EVENTO (OBLIGATORIO) -----
        if not evento_id:
            return _construir_respuesta_error(
                ["id_evento es obligatorio. El agente solo funciona para eventos existentes."]
            )
        
        # ----- 5. EJECUTAR EXTRACCIÓN CON LLM -----
        try:
            resultado = extraer_briefing_llm(
                texto=texto,
                api_key=api_key,
                historial_anterior=historial_anterior,
                bloques_a_actualizar=bloques_a_actualizar  # NUEVO
            )
        except Exception as e:
            return _construir_respuesta_error(
                [f"Error en el motor LLM: {str(e)}"]
            )
        
        # ----- 6. GENERAR VALIDACIÓN Y AVISOS -----
        resultado = generar_aviso_y_validacion(resultado)
        
        # ----- 7. AÑADIR METADATOS DE ACTUALIZACIÓN -----
        if historial_anterior:
            # Añadir entrada al histórico si no existe
            if "historico_actualizaciones" not in resultado["nota_bene"]["informacion_adicional"]:
                resultado["nota_bene"]["informacion_adicional"]["historico_actualizaciones"] = []
            
            # Obtener versión anterior
            version_anterior = len(historial_anterior.get("versiones", []))
            
            # Generar resumen de cambios
            if bloques_a_actualizar:
                cambios = f"Actualización de bloques: {', '.join(bloques_a_actualizar)}"
            else:
                cambios = "Actualización completa del briefing"
            
            # Añadir entrada
            nueva_entrada = {
                "fecha": datetime.now().isoformat(),
                "cambios_detectados": cambios,
                "version": version_anterior + 1
            }
            
            # Si el LLM ya puso cambios más detallados, usarlos
            historico_existente = resultado["nota_bene"]["informacion_adicional"]["historico_actualizaciones"]
            if historico_existente and isinstance(historico_existente, list):
                ultima = historico_existente[-1] if historico_existente else {}
                if ultima.get("cambios_detectados"):
                    nueva_entrada["cambios_detectados"] = ultima.get("cambios_detectados")
            
            resultado["nota_bene"]["informacion_adicional"]["historico_actualizaciones"].append(nueva_entrada)
            
            # Actualizar timestamp
            resultado["nota_bene"]["cabecera"]["ultima_actualizacion"] = datetime.now().isoformat()
        
        # ----- 8. CONSTRUIR SALIDA BASE -----
        salida = construir_salida_base(
            datos_detectados=resultado,
            motor_usado="llm",
            errores=None
        )

        # Traza de transparencia: si el histórico se autocargó de la BD
        # real (en vez de venir explícito en el payload), que quede
        # constancia en trazas.fuentes_consultadas -- útil para depurar
        # por qué un bloque salió "protegido"/fusionado sin que quien
        # llamó pasara contexto.historial_anterior él mismo.
        if historial_desde_bd:
            salida["trazas"]["fuentes_consultadas"].append("bd:eventos(historial_anterior)")

        return salida
        
    except Exception as e:
        return _construir_respuesta_error([f"Error inesperado: {str(e)}"])


# =====================================================================
# 2. FUNCIONES AUXILIARES
# =====================================================================
def _construir_respuesta_error(errores):
    """
    Construye una respuesta de error siguiendo el contrato de salida.
    
    Args:
        errores (list): Lista de mensajes de error
    
    Returns:
        dict: Salida de error del agente
    """
    datos_vacios = crear_estructura_vacia_completa()
    datos_vacios = generar_aviso_y_validacion(datos_vacios)
    
    return {
        "ok": False,
        "agente": "agente_operis",
        "tipo_peticion": "extraer_briefing",
        "resumen": "❌ Error en la extracción",
        "datos_detectados": datos_vacios,
        "acciones_propuestas": [],
        "bloqueos_detectados": [],
        "borradores_generados": [],
        "requiere_validacion_humana": True,
        "nivel_riesgo": "bajo",
        "errores": errores,
        "trazas": {
            "fuentes_consultadas": ["motor:llm"],
            "timestamp": datetime.now().isoformat(),
            "modo": "propuesta"
        },
        "_validacion": datos_vacios.get("_validacion", {}),
        "_aviso_agente": datos_vacios.get("_aviso_agente", {})
    }


# =====================================================================
# 3. EXPORTACIÓN EXPLÍCITA (PARA CONTRATO)
# =====================================================================
# Esta función es la que importa src/agente.py para exponer el contrato.
# No cambiar el nombre ni los argumentos.
__all__ = ["ejecutar_agente"]