import time
from src import parametros as p
from src.agente import procesar_bandeja_gmail

print("[SERVICIO] Agente gestor correos MITUMI iniciado")
print(f"[SERVICIO] Gmail query: {p.GMAIL_QUERY}")

while True:
    try:
        resultado = procesar_bandeja_gmail()
        print("[SERVICIO] Procesados:", resultado.get("total"))
    except Exception as e:
        print("[SERVICIO][ERROR]", e)
    time.sleep(300)
