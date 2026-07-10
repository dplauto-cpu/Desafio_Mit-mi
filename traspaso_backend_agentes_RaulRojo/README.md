# Traspaso — backend de data y conexiones agentes ↔ front

**Para:** Raúl Rojo · **De:** Nora · **Fecha:** 10 de julio de 2026
**Alcance:** el backend propio de data, el acceso de los agentes a la BBDD y la conexión con el front.
Todo lo listado como "definitivo" está **probado y funcionando** a fecha de hoy.

---

## 0. El mapa en 30 segundos

```
FRONT (React :5173)
   │  fetch JSON (CORS ya activado)
   ▼
BACKEND DE DATA — FastAPI :5003  ←— LO QUE RECIBES  (backend_data_Nora/)
   ├── POST /agentes/lumen/chat            (copiloto, memoria por sesion_id)
   ├── POST /agentes/lumen/chat/reset
   └── POST /agentes/operis/autocompletar  (briefing → campos propuestos)
   ▼
AGENTES (su código NO se toca; contrato ejecutar_agente(payload))
   ▼
NEON POSTGRES — rol agente_readonly (SOLO lectura; usuarios vetada; escribir es imposible)
```

Regla de oro vigente: **los agentes leen de Neon y solo proponen; cualquier escritura va
por el backend de full stack con validación humana** (contrato v3 §6).

---

## 1. Piezas definitivas y dónde viven

| Pieza | Dónde | Estado |
|---|---|---|
| **Backend unificado de data** (FastAPI :5003, monta Lumen y Operis) | `backend_data_Nora/` | ✅ probado 10/07 punta a punta contra Neon (health, chat con memoria en 2 turnos, reset, Operis motor reglas, errores, 404). Swagger en `/docs`. **Es la pieza principal que recibes.** |
| **Kit de conexión a Neon** (plantilla `bd_backend.py` + `test_conexion.py` + reglas) | `kit_conexion_agentes_Nora/` | ✅ probado (TODO PASS). Para conectar los agentes que faltan (Telegram, correos…). |
| **Vistas SQL** (contrato de lectura estable para agentes) | `kit_conexion_agentes_Nora/sql/vistas_agentes.sql` | 📋 escrito, sin aplicar — lo ejecuta BBDD cuando quiera; revisar el JOIN de ponencias tras el cambio de esquema de hoy (ver §4). |
| **Documentación canónica** | `API_Nora/api/contrato_api_eventos_3.md` + `endpoints_v4.md` | ✅ el contrato del sistema y el inventario de rutas. v4 sustituye la parte de agentes de v3. |
| **Página de agentes para el front** (React, con los estilos del equipo) | `front_react/` en esta carpeta | ✅ probada dentro del front real (rama local `nora/demo-agentes` en la máquina de Nora; aquí exportada). Ver §2. |
| **Propuesta de 2 endpoints al backend de full stack** | `propuesta_endpoints_fullstack.patch` en esta carpeta | ✅ probada contra su `develop` de hoy (13:50). Ver §3. |
| Demo standalone (HTML suelto, sin React) | `API_Nora/demo_front/demo_agentes.html` | ✅ funciona; útil para probar sin front. Ya superada por lo anterior. |
| Servidores Flask sueltos (`servidor.py` :5001 y :5002) | carpetas de Lumen y Operis | ✅ funcionan; quedan como plan B del :5003. |

## Cómo arrancarlo (2 minutos)

```bash
cd backend_data_Nora
pip install -r requirements.txt        # necesita Python 3.10+ (en el Mac de Nora: /usr/local/bin/python3.12)
python app.py                          # → http://localhost:5003  ·  Swagger: /docs
```

La configuración (DATABASE_URL del rol de solo lectura, clave LLM) se lee del `.env` de
Lumen (`Agente_04_Copilot_Raul/lumen_agente_04/.env`) — **pídele a Nora ese `.env`, no
está en git y no debe estarlo jamás**. Prueba rápida:

```bash
curl -X POST http://localhost:5003/agentes/lumen/chat \
  -H "Content-Type: application/json" -d '{"pregunta": "¿Cuántos eventos hay?"}'
```

---

## 2. Conexión con el front (`front_react/`)

Los tres archivos exportados son la página de agentes **ya integrada y probada dentro del
front real del equipo** (repo `backstage-frontend`), escrita con SUS variables SCSS:

- `AgentePage.jsx` → va en `src/pages/` (chat Lumen + Operis; maneja `sesion_id`, estados
  de carga, servicios caídos y el aviso "propuesta — requiere validación humana").
- `agente.scss` → va en `src/components/agentes/`.
- `AppRoutes.jsx` → añade la ruta `/agentes` **e incluye el fix del bug `Navigate`**
  (sin ese import, TODA su app crashea — avísales, es de su rama, no nuestro).

⚠️ Los archivos apuntan a los servidores sueltos (:5001/:5002). Con el backend unificado,
cambiar dos constantes al principio de `AgentePage.jsx`:
`LUMEN_URL = 'http://localhost:5003/agentes/lumen'` y
`OPERIS_URL = 'http://localhost:5003/agentes/operis'` (los alias `/chat` y
`/autocompletar` de la raíz también funcionan tal cual, ver README del backend).

---

## 3. Propuesta al backend de full stack (`propuesta_endpoints_fullstack.patch`)

Dos endpoints que su API aún no tiene y los agentes necesitarán (se aplican con
`git am propuesta_endpoints_fullstack.patch` sobre su `develop`):

- `GET /ponentes/by-telegram/{telegram_user_id}` — responde **501 con instrucciones**
  hasta que exista la columna `telegram_user_id` (su migración pendiente); en cuanto
  exista, funciona sin tocar código.
- `GET /eventos/{id}/ponentes` — ya adaptado al **esquema nuevo de hoy** (David invirtió
  la relación: `ponencias.id_evento`); devuelve array de ponentes con su logística.

Contexto: los CRUD de estados/presupuestos que también les propusimos ya los hizo Rafa
por su cuenta (10/07), así que el patch se quedó solo con lo que falta.

---

## 4. Estado del entorno a 10/07 por la tarde (leer antes de depurar nada)

1. **La BBDD está VACÍA**: la remigración de las 13:48 (cambio de esquema evento↔ponencia)
   borró los datos y aún no han recargado. Hasta el reseed, los agentes responden "no hay
   eventos" — **es normal, no es un bug**.
2. Con el esquema nuevo, el enlace evento↔ponente viene de fábrica si el seed carga
   `ponencias.id_evento`. Del script `Datos_alimentación_bbdd_Leire_Eduardo/enlace_bbdd/`
   solo sigue siendo relevante la parte de `id_sala` (propuesta, decisión humana).
3. **Sigue faltando `telegram_user_id`** en `ponentes` (bloquea el bot de Telegram).
4. Para probar contra su backend (:3000) en desarrollo: `POST /auth/login` con cabecera
   `Authorization: Bearer admin-test-token` (login de test oficial de Soufiane, 10/07).
5. Su middleware **solo acepta cookie**, no Bearer, en el resto de rutas — pendiente nº1
   con full stack.

## 5. Seguridad (no negociable)

- Los agentes usan SIEMPRE el rol `agente_readonly` (pedir credencial a Nora). Nunca la
  cadena de `neondb_owner`, y nunca credenciales en git.
- El LLM jamás escribe SQL: consultas fijas y parametrizadas (así están hechas todas).
- Verificación de un vistazo: `python3 kit_conexion_agentes_Nora/test_conexion.py
  ruta/al/.env` → debe salir TODO PASS (incluye comprobar que escribir es imposible).

---

*Dudas de contexto histórico: el resumen del proyecto y decisiones están en
`API_Nora/api/contrato_api_eventos_3.md` (§1 y §7). Lo que no esté ahí, preguntar a Nora.*
