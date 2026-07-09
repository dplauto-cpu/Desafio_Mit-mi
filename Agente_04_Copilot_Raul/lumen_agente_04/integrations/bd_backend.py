"""
integrations/bd_backend.py — Acceso de SOLO LECTURA a la BD real (Neon Postgres).

Misma filosofia que api_backend.py: Lumen solo consulta. Refuerzos:
- La conexion se marca read_only (SESSION CHARACTERISTICS READ ONLY): aunque las
  credenciales permitieran escribir, Postgres rechaza cualquier INSERT/UPDATE/DELETE.
  (No se usa el parametro de arranque `options` porque el pooler de Neon no lo soporta.)
- Solo se aceptan tablas de la lista blanca de este modulo (`usuarios` no esta).
  El nombre de tabla NUNCA viene del LLM: lectura_datos ya valida contra
  TABLAS_PERMITIDAS antes de llamar aqui; esta segunda lista es defensa en profundidad.
- Ademas, el rol agente_readonly de la BD no tiene GRANT sobre `usuarios` (tercera capa).
- Los tipos de Postgres (UUID, datetime, Decimal) se convierten a str/float para que
  las filas tengan la misma forma que los mocks JSON y json.dumps funcione aguas abajo.
"""

import datetime
import decimal
import uuid

import psycopg
from psycopg.rows import dict_row

from config.settings import DATABASE_URL

_TABLAS_BD = {
    "clientes", "eventos", "presupuestos", "ponentes",
    "ponencias", "estados", "salas", "espacios",
}


class BdBackendError(RuntimeError):
    """Fallo de conexion o consulta contra la BD real."""


def bd_disponible() -> bool:
    return bool(DATABASE_URL)


def _normalizar_valor(v):
    if isinstance(v, uuid.UUID):
        return str(v)
    if isinstance(v, datetime.datetime):
        # Prisma guarda fechas de dia como timestamp a medianoche: se devuelven como AAAA-MM-DD
        # (igual que el mock); si hay hora real, ISO completo.
        return v.date().isoformat() if v.time() == datetime.time(0, 0) else v.isoformat()
    if isinstance(v, datetime.date):
        return v.isoformat()
    if isinstance(v, decimal.Decimal):
        return float(v)
    return v


def leer_tabla(tabla: str) -> list:
    """SELECT * de una tabla de la lista blanca, como lista de dicts con la forma del mock."""
    if tabla not in _TABLAS_BD:
        raise BdBackendError("Tabla '" + tabla + "' fuera de la lista blanca de BD.")
    if not bd_disponible():
        raise BdBackendError("DATABASE_URL no configurada en .env.")

    try:
        with psycopg.connect(
            DATABASE_URL,
            connect_timeout=10,
            row_factory=dict_row,
        ) as conn:
            conn.read_only = True
            filas = conn.execute('SELECT * FROM "' + tabla + '"').fetchall()
    except psycopg.Error as exc:
        raise BdBackendError("No se pudo leer la tabla '" + tabla + "' de la BD real.") from exc

    return [{k: _normalizar_valor(v) for k, v in fila.items()} for fila in filas]
