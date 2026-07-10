# Acuerdos de equipo — reunión del lunes

**Proyecto:** Gestión de eventos y ponentes
**Equipo:** Full-stack (6) + Data Science (12)
**Entrega:** jueves de la semana que viene
**Objetivo de la reunión:** cerrar lo imprescindible antes de que nadie escriba código, para que los 3 equipos trabajen en paralelo sin bloquearse.

---

## PARTE 1 — Qué cerrar antes de picar código

De más importante a menos. Lo ideal es salir del lunes con los 4 primeros atados.

### 1. Contrato de la API (el "idioma común") — PRIORIDAD MÁXIMA
Cómo se hablan la app y la IA: qué datos entran y salen, y en qué formato.
→ Ya hay un borrador en el documento aparte. Repasarlo y subirlo al repositorio como versión 1.

### 2. Repositorio y forma de trabajar
- Dónde vive el código.
- Cómo se junta el trabajo de todos sin pisarse (ramas, cada cuánto se une).
- **Acuerdo clave:** juntar el trabajo a menudo, no dejarlo para el final.

### 3. Entorno común
- Mismas versiones de herramientas para todos.
- Misma base de datos de prueba.
- Todo en UTF-8 (importante con euskera y castellano: acentos, eñes).
- Evita el clásico "en mi ordenador funciona".

### 4. Datos de prueba realistas y pronto
- Los 2 de "datos y ejemplos" los generan el lunes/martes.
- Eventos, ponentes y facturas de mentira que todos compartan.
- Sin esto, cada equipo se inventa los suyos y luego no encajan.

### 5. Login: quién entra y qué ve
- Doble acceso: admin y ponente.
- Acordar cómo se distingue uno de otro y qué ve cada uno.
- Para la demo no hace falta seguridad de banco: basta con la regla clara.

### 6. Cómo se hablan app e IA en la práctica
- ¿La app pide a la IA y espera respuesta al momento, o la IA trabaja por detrás y avisa al terminar?
- Para agentes que tardan (leer documentos, generar borradores) suele ir mejor lo segundo.
- Lo acuerdan backend + data science.

### 7. Alcance de la demo
- Media hora que ahorra días. → Ver PARTE 2.

---

## PARTE 2 — Alcance de la demo

**La historia que se cuenta el jueves:**
Crear un evento → ver sus ponentes → la IA ayuda con uno → cerrar con el presupuesto.
De principio a fin, enseñando las dos patas: app + IA.

### Lo que TIENE que funcionar (mínimo)

| # | Qué | Por qué |
|---|---|---|
| 1 | **Crear un evento** (guardándose en la BD) | Es el punto de partida. Sin esto no hay demo |
| 2 | **Dashboard de ponentes** del evento | La pantalla más vistosa; conecta con toda la lógica. Con datos reales |
| 3 | **Agente documental** de punta a punta | El corazón de la parte IA. Sube documento → detecta faltantes → propone tarea/bloqueo |
| 4 | **Presupuesto** con desviaciones | El cierre visual. Impacta y da sensación de producto acabado |

> Si solo funciona un agente, que sea el documental: es el más autónomo y el más fácil de enseñar.

### Lo que queda FUERA del mínimo (bien si sobra tiempo)

- Segundo agente (comunicación / logística) — puede quedarse más simple.
- Portal del ponente — vista secundaria para la historia.
- Autocompletado del briefing — vistoso, pero extra.
- Login doble real — para la demo se puede "entrar ya como admin".

### Regla de oro
Mejor 4 cosas funcionando de verdad y conectadas entre sí, que 7 pantallas a medias.
Una demo que hace poco pero bien, convence. Una que lo intenta todo y se cae, no.

### Plan B para el jueves
Tened una **captura o vídeo corto** de cada parte funcionando. Si en directo se cae la conexión o el agente tarda, se enseña la grabación y se sigue.

---

## Checklist de salida del lunes

- [ ] Contrato de la API repasado y subido al repositorio (v1).
- [ ] Repositorio creado y forma de trabajar acordada.
- [ ] Entorno común y datos de prueba en marcha.
- [ ] Alcance de la demo decidido (qué sí, qué no).
- [ ] Cada equipo sabe qué construye y qué consume.
- [ ] Regla del login acordada.

---

## Calendario resumido

| Cuándo | Qué |
|---|---|
| **Lunes** | Kickoff. Cerrar este documento. Nadie programa "de verdad" hasta acordar el contrato |
| **Martes–jueves** | Cada equipo su parte, contra datos de prueba |
| **Viernes** | Primera integración: juntar todo y ver qué falla |
| **Lunes–martes (sem. 2)** | Cerrar features y arreglar lo de la integración |
| **Miércoles** | Integración final. Desde la tarde: solo pulir, nada nuevo |
| **Jueves** | Presentación |
