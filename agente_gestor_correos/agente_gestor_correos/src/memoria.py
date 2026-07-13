import json
import sqlite3
from datetime import datetime
from pathlib import Path
from .parametros import BASE_DIR

DB_PATH = BASE_DIR / "data" / "gestor_correos_mitumi.db"

def inicializar_memoria():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ejecuciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        email_id TEXT,
        asunto TEXT,
        categoria TEXT,
        ok INTEGER,
        respuesta_json TEXT
    )
    """)
    con.commit(); con.close()

def guardar_respuesta(email_id: str, asunto: str, categoria: str, ok: bool, respuesta: dict):
    inicializar_memoria()
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT INTO ejecuciones(timestamp,email_id,asunto,categoria,ok,respuesta_json) VALUES(?,?,?,?,?,?)",
        (datetime.now().isoformat(timespec="seconds"), email_id, asunto, categoria, 1 if ok else 0, json.dumps(respuesta, ensure_ascii=False))
    )
    con.commit(); con.close()
