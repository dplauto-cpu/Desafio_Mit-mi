from pathlib import Path

ruta = Path("data/rag/correos_historicos.jsonl")
ruta.parent.mkdir(parents=True, exist_ok=True)
ruta.touch(exist_ok=True)
print("RAG inicial preparado:", ruta)
