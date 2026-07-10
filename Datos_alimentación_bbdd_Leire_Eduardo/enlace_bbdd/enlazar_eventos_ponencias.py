"""
enlazar_eventos_ponencias.py — Rellena eventos.id_ponencia (y opcionalmente propone id_sala)
en la BBDD real de Neon, a partir de los vínculos de evento_ponente.csv.

POR QUÉ EXISTE
La carga inicial dejó eventos.id_ponencia e id_sala a NULL en los 40 eventos porque
eventos.csv no traía esas columnas. Los vínculos evento↔ponente SÍ existen en
evento_ponente.csv, pero con ids enteros, y la BBDD usa UUIDs. Este script reconstruye
la correspondencia cruzando por campos únicos:

    evento_ponente.csv (id_evento, id_ponente)
        id_ponente(int) → ponentes.csv → email → BBDD ponentes.id (UUID)
        BBDD ponencias.id_ponente → ponencia (UUID)   [1 ponencia por ponente]
        id_evento(int)  → eventos.csv  → nombre_evento → BBDD eventos.id (UUID)
    ⇒ UPDATE eventos SET id_ponencia = <uuid> WHERE id = <uuid evento>

MODO DE USO (Leire / Eduardo)
    export OWNER_DATABASE_URL='postgresql://neondb_owner:...@.../neondb?sslmode=require'
    python3 enlazar_eventos_ponencias.py              # SIMULACRO: solo lee y muestra el plan
    python3 enlazar_eventos_ponencias.py --aplicar    # ejecuta los UPDATE (pide confirmación)
    python3 enlazar_eventos_ponencias.py --proponer-salas   # además, imprime una PROPUESTA
                                                            # de sala por evento (no la aplica)

SEGURIDAD
- Sin --aplicar NO escribe nada (la sesión se mantiene en solo-lectura).
- Con --aplicar: anula el default read-only de la base, ejecuta todo en UNA transacción,
  muestra el resumen y pide confirmación por teclado antes del COMMIT.
- Si un evento tiene MÁS DE UN ponente en el CSV, no se toca y se lista como conflicto:
  el esquema actual (eventos.id_ponencia) solo admite uno — es la limitación del modelo
  muchos-a-muchos ya reportada al equipo de backend.

Requiere: pip install "psycopg[binary]"
"""

import csv
import os
import sys
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

CARPETA_CSV = Path(__file__).resolve().parent.parent  # Datos_alimentación_bbdd_Leire_Eduardo/
APLICAR = "--aplicar" in sys.argv
PROPONER_SALAS = "--proponer-salas" in sys.argv


def leer_csv(nombre):
    with open(CARPETA_CSV / nombre, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    url = os.environ.get("OWNER_DATABASE_URL")
    if not url:
        sys.exit("Falta OWNER_DATABASE_URL en el entorno (la cadena del owner, no la del rol readonly).")

    ponentes_csv = leer_csv("ponentes.csv")
    eventos_csv = leer_csv("eventos.csv")
    vinculos_csv = leer_csv("evento_ponente.csv")

    email_por_id_ponente = {p["id_ponente"]: p["email"].strip().lower() for p in ponentes_csv}
    nombre_por_id_evento = {e["id_evento"]: e["nombre_evento"].strip() for e in eventos_csv}

    with psycopg.connect(url, connect_timeout=15, row_factory=dict_row) as conn:
        cur = conn.cursor()

        uuid_ponente_por_email = {
            r["email"].strip().lower(): r["id"]
            for r in cur.execute("SELECT id, email FROM ponentes").fetchall()
        }
        ponencia_por_ponente = {}
        for r in cur.execute("SELECT id, id_ponente FROM ponencias").fetchall():
            ponencia_por_ponente.setdefault(str(r["id_ponente"]), []).append(r["id"])

        eventos_bd = cur.execute(
            "SELECT id, nombre_evento, lugar_confirmado, numero_personas, id_ponencia, id_sala FROM eventos"
        ).fetchall()
        uuid_evento_por_nombre = {}
        for r in eventos_bd:
            uuid_evento_por_nombre.setdefault(r["nombre_evento"].strip(), []).append(r)

        # ---- construir el plan de enlace ----
        plan, conflictos, huerfanos = {}, [], []
        for v in vinculos_csv:
            id_ev, id_po = v["id_evento"], v["id_ponente"]
            email = email_por_id_ponente.get(id_po)
            nombre_ev = nombre_por_id_evento.get(id_ev)
            uuid_po = uuid_ponente_por_email.get(email) if email else None
            candidatos_ev = uuid_evento_por_nombre.get(nombre_ev, [])
            ponencias = ponencia_por_ponente.get(str(uuid_po), []) if uuid_po else []

            if not (email and nombre_ev and uuid_po and ponencias) or len(candidatos_ev) != 1 or len(ponencias) != 1:
                huerfanos.append(f"csv id_evento={id_ev} id_ponente={id_po}: "
                                 f"email={'ok' if uuid_po else email} evento={'ok' if len(candidatos_ev)==1 else nombre_ev} "
                                 f"ponencias={len(ponencias)}")
                continue

            evento = candidatos_ev[0]
            if evento["id"] in plan:  # segundo ponente para el mismo evento
                conflictos.append(f"{nombre_ev}: más de un ponente en el CSV — el esquema actual solo admite uno")
                continue
            plan[evento["id"]] = (nombre_ev, ponencias[0], evento["id_ponencia"])

        # ---- informe ----
        print(f"Vínculos en CSV: {len(vinculos_csv)}  ·  Enlazables: {len(plan)}  ·  "
              f"Conflictos (multi-ponente): {len(conflictos)}  ·  No resueltos: {len(huerfanos)}")
        for c in conflictos:
            print("  CONFLICTO:", c)
        for h in huerfanos:
            print("  NO RESUELTO:", h)
        ya_enlazados = sum(1 for _, (_, pon, actual) in plan.items() if actual is not None)
        if ya_enlazados:
            print(f"  Nota: {ya_enlazados} eventos ya tienen id_ponencia (se sobreescribiría con --aplicar).")

        # ---- propuesta de salas (solo informe, nunca se aplica) ----
        if PROPONER_SALAS:
            print("\nPROPUESTA de id_sala (heurística lugar_confirmado→espacio, sala de mayor aforo que cubra el evento):")
            espacios = {r["nombre_espacio"].strip().lower(): r["id"]
                        for r in cur.execute("SELECT id, nombre_espacio FROM espacios").fetchall()}
            salas = cur.execute(
                "SELECT id, nombre_sala, capacidad_max_sala, id_espacio FROM salas ORDER BY capacidad_max_sala DESC"
            ).fetchall()
            for ev in eventos_bd:
                lugar = (ev["lugar_confirmado"] or "").strip().lower()
                uuid_esp = espacios.get(lugar)
                if not uuid_esp:
                    print(f"  {ev['nombre_evento']}: sin espacio que case con «{ev['lugar_confirmado']}»")
                    continue
                del_espacio = [s for s in salas if s["id_espacio"] == uuid_esp]
                aptas = [s for s in del_espacio if (s["capacidad_max_sala"] or 0) >= (ev["numero_personas"] or 0)]
                elegida = (aptas or del_espacio)[-1] if (aptas or del_espacio) else None
                if elegida:
                    print(f"  {ev['nombre_evento']} ({ev['numero_personas']} pers.) → {elegida['nombre_sala']} "
                          f"(cap. {elegida['capacidad_max_sala']})")
            print("  ⚠ Es una PROPUESTA para revisar a mano: este script no escribe id_sala nunca.")

        # ---- aplicar ----
        if not APLICAR:
            print("\nSIMULACRO terminado — no se ha escrito nada. Ejecuta con --aplicar para enlazar.")
            return

        print(f"\nSe van a actualizar {len(plan)} eventos (id_ponencia). ¿Continuar? [escribe SI] ", end="")
        if input().strip() != "SI":
            print("Cancelado, no se ha escrito nada.")
            return

        cur.execute("SET default_transaction_read_only = off")  # la base tiene read-only por defecto
        with conn.transaction():
            for uuid_ev, (_, uuid_ponencia, _) in plan.items():
                cur.execute("UPDATE eventos SET id_ponencia = %s WHERE id = %s", (uuid_ponencia, uuid_ev))
        n = cur.execute("SELECT count(id_ponencia) FROM eventos").fetchone()
        print(f"Hecho. Eventos con id_ponencia en la BBDD: {list(n.values())[0]}")


if __name__ == "__main__":
    main()
