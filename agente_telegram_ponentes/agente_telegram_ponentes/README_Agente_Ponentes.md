# Agente de Telegram para Ponentes

> **Versión del proyecto:** 0.9
>
> **Versión del README:** 1.0
>
> **Estado:** MVP Funcional
>
> **Proyecto:** Plataforma MITUMI
>
> **Tipo de agente:** Agente conversacional especializado

---

# Índice

1. Introducción
2. Resumen ejecutivo
3. Objetivo
4. Arquitectura general
5. Responsabilidades
6. Qué NO hace
7. Flujo general
8. Estructura del proyecto
9. Explicación de la estructura

---

# 1. Introducción

El Agente de Telegram para Ponentes es un asistente conversacional desarrollado para la plataforma MITUMI cuyo objetivo es ofrecer soporte automatizado a los ponentes de un evento mediante Telegram.

El agente actúa como punto de comunicación entre el ponente y la información disponible en la plataforma, permitiendo resolver dudas, consultar documentación, acceder a información del evento y facilitar la comunicación con la organización.

Toda la lógica está implementada en Python y se integra con Telegram, un modelo de lenguaje (LLM) y una base de datos PostgreSQL.

---

# 2. Resumen ejecutivo

| Campo | Valor |
|--------|-------|
| Nombre | Agente de Telegram para Ponentes |
| Proyecto | MITUMI |
| Lenguaje | Python |
| Estado | MVP Funcional |
| Canal de comunicación | Telegram |
| Base de datos | PostgreSQL (Neon) |
| Modelo IA | OpenAI |
| Punto de entrada | `servicio.py` |
| Función principal | `ejecutar_agente(payload)` |

---

# 3. Objetivo

El objetivo del agente consiste en proporcionar una atención inmediata a los ponentes sin necesidad de acceder continuamente a la plataforma web.

Entre sus principales funciones se encuentran:

- Resolver dudas frecuentes.
- Consultar información del evento.
- Facilitar información sobre hoteles.
- Consultar información sobre transportes.
- Enviar documentación disponible.
- Mantener conversaciones naturales mediante IA.
- Registrar solicitudes para que sean atendidas por la organización cuando sea necesario.

El agente busca reducir la carga de trabajo del personal organizador respondiendo automáticamente a aquellas consultas que pueden resolverse con la información existente.

---

# 4. Arquitectura general

El agente forma parte del ecosistema MITUMI y se comunica con varios componentes externos.

```text
                    Usuario

                       │

                 Telegram Bot

                       │

                 servicio.py

                       │

              ejecutar_agente()

          ┌──────────┼───────────┐

          │          │           │

     PostgreSQL     LLM      Documentos

          │          │           │

          └──────────┼───────────┘

                 Respuesta

                       │

                 Telegram Bot

                       │

                    Usuario
```

El servicio principal recibe los mensajes enviados desde Telegram y delega su procesamiento al agente.

El agente consulta la información necesaria y genera una respuesta que posteriormente es enviada nuevamente al usuario.

---

# 5. Responsabilidades del agente

Actualmente el agente implementa las siguientes responsabilidades.

## Atención al ponente

Mantener conversaciones mediante lenguaje natural utilizando un modelo LLM.

---

## Consulta de información

Responder preguntas relacionadas con:

- Evento
- Agenda
- Horarios
- Organización
- Ponencias
- Hoteles
- Transportes
- Documentación

---

## Gestión documental

Localizar documentos asociados al ponente.

Entre ellos:

- Billetes
- Presentaciones
- CV
- Documentación enviada por la organización

---

## Comunicación con la organización

Cuando una petición no puede resolverse automáticamente, el agente registra una solicitud para que pueda ser gestionada posteriormente por la organización.

---

## Estado del ponente

Mantiene información sobre el evento activo asociado al usuario de Telegram.

Esto permite ofrecer respuestas personalizadas según el evento en el que participa.

---

# 6. Qué NO hace

Este agente tiene un conjunto de limitaciones intencionadas.

No puede:

- Modificar información de la base de datos.
- Crear eventos.
- Eliminar información.
- Confirmar reservas.
- Comprar billetes.
- Modificar hoteles.
- Gestionar pagos.
- Sustituir al personal organizador.
- Realizar acciones administrativas.

Su función consiste únicamente en consultar información, responder preguntas y facilitar la comunicación.

---

# 7. Flujo general de funcionamiento

Cada mensaje sigue el siguiente proceso.

```text
Usuario

   │

   ▼

Telegram

   │

   ▼

servicio.py

   │

   ▼

ejecutar_agente()

   │

   ├────────► Consulta Base de Datos

   │

   ├────────► Consulta documentos

   │

   ├────────► Consulta estado del usuario

   │

   ├────────► Consulta LLM

   │

   ▼

Respuesta

   │

   ▼

Telegram

   │

   ▼

Usuario
```

Este flujo se ejecuta para cada mensaje recibido por el bot.

---

# 8. Estructura del proyecto

```text
agente_telegram_ponentes/

│

├── config/

├── data/

│   ├── documentos_prueba/

│   ├── estado/

│   └── uploads/

├── integrations/

├── logs/

├── src/

├── tests/

├── .env

├── .env.example

├── requirements.txt

├── servicio.py

└── README.md
```

---

# 9. Explicación de la estructura

## config/

Contiene toda la configuración del proyecto.

Incluye parámetros generales, permisos y configuración de las distintas fuentes de información utilizadas por el agente.

---

## data/

Almacena toda la información utilizada durante la ejecución.

Dentro de esta carpeta se encuentran:

### documentos_prueba/

Documentación utilizada para las pruebas del agente.

Incluye archivos PDF y su correspondiente versión en texto.

Ejemplos:

- Billetes.
- Presentaciones.
- Currículums.

---

### estado/

Contiene los ficheros JSON utilizados para mantener el estado interno del agente.

Entre ellos:

- Eventos activos.
- Relación entre usuarios de Telegram y ponentes.
- Solicitudes de contacto pendientes.

Estos archivos permiten mantener contexto entre conversaciones.

---

### uploads/

Directorio reservado para documentos recibidos durante la ejecución del sistema.

---

## integrations/

Implementa todas las conexiones con servicios externos.

Actualmente incluye:

- Telegram.
- Base de datos PostgreSQL.
- Modelo de lenguaje.

---

## logs/

Contiene los registros generados durante la ejecución del agente.

Facilita el diagnóstico de errores y el seguimiento de la actividad del sistema.

---

## src/

Implementa toda la lógica del agente.

Aquí se encuentra el procesamiento de mensajes, validaciones, prompts, herramientas y la función principal del sistema.

Esta carpeta constituye el núcleo del proyecto.

---

## tests/

Incluye pruebas destinadas a verificar el correcto funcionamiento del agente y validar su comportamiento antes de desplegar nuevas versiones.

---

## servicio.py

Es el punto de entrada principal del proyecto.

Inicializa el servicio, mantiene la comunicación con Telegram y delega el procesamiento de cada mensaje al agente.

---

## README.md

Documento técnico que describe la arquitectura, funcionamiento e instalación del proyecto.

---

---

# 10. Funcionamiento interno del agente

El núcleo del sistema se encuentra dentro de la carpeta `src/`.

Aquí reside toda la lógica necesaria para interpretar los mensajes recibidos desde Telegram, consultar la información disponible y generar una respuesta para el ponente.

A diferencia de un bot basado únicamente en reglas, este agente combina información estructurada procedente de la base de datos con un modelo de lenguaje (LLM), permitiendo mantener conversaciones naturales y responder preguntas formuladas de distintas maneras.

El procesamiento siempre sigue una secuencia controlada antes de devolver una respuesta al usuario.

---

# 11. Ciclo de procesamiento de un mensaje

Cada mensaje recibido sigue el siguiente flujo:

```text
Mensaje recibido

      │

      ▼

servicio.py

      │

      ▼

Validación del mensaje

      │

      ▼

Obtención del contexto

      │

      ▼

Consulta de información

      │

      ▼

Construcción del prompt

      │

      ▼

LLM

      │

      ▼

Validación de respuesta

      │

      ▼

Respuesta por Telegram
```

Este proceso se ejecuta de forma independiente para cada mensaje recibido.

---

# 12. Punto de entrada del agente

El punto de entrada lógico del sistema es la función:

```python
ejecutar_agente(payload)
```

Esta función centraliza todo el procesamiento del mensaje.

Entre sus responsabilidades se encuentran:

- Validar la información recibida.
- Obtener el contexto del usuario.
- Consultar la base de datos.
- Localizar documentación disponible.
- Construir el contexto para el modelo LLM.
- Generar una respuesta.
- Validar el resultado.
- Devolver una respuesta estructurada.

Toda petición procesada por el agente pasa por esta función.

---

# 13. Servicio principal

El archivo `servicio.py` constituye el proceso principal del proyecto.

Entre sus funciones destacan:

- Inicializar el bot de Telegram.
- Mantener el servicio en ejecución.
- Escuchar nuevos mensajes.
- Construir el payload recibido.
- Invocar `ejecutar_agente()`.
- Enviar la respuesta al usuario.

Este componente actúa como puente entre Telegram y la lógica del agente.

---

# 14. Gestión del contexto

Para ofrecer respuestas personalizadas, el agente mantiene información contextual del usuario.

Actualmente conserva información como:

- Evento activo.
- Identificador del ponente.
- Conversación actual.
- Solicitudes pendientes.
- Estado del usuario.

Esta información evita que el usuario tenga que repetir continuamente el contexto durante una conversación.

---

# 15. Memoria del agente

La memoria del sistema se almacena mediante archivos JSON.

Su objetivo es conservar el estado necesario para mantener conversaciones coherentes.

Entre la información almacenada se encuentra:

- Asociación entre usuario de Telegram y ponente.
- Evento activo.
- Solicitudes de contacto.
- Estado interno del agente.

Esta memoria es ligera y está orientada al contexto conversacional.

---

# 16. Integración con Telegram

Telegram constituye el canal de comunicación principal del sistema.

El agente recibe mensajes desde un bot de Telegram y devuelve la respuesta utilizando el mismo canal.

Las funciones principales de esta integración son:

- Recepción de mensajes.
- Identificación del usuario.
- Envío de respuestas.
- Gestión de comandos.
- Comunicación con el servicio principal.

Toda la interacción con el usuario se realiza a través de esta integración.

---

# 17. Integración con PostgreSQL

La información del evento se obtiene desde una base de datos PostgreSQL alojada en Neon.

El agente utiliza esta información para responder consultas relacionadas con:

- Ponentes.
- Eventos.
- Hoteles.
- Transportes.
- Agenda.
- Información general.

El acceso a la base de datos es exclusivamente de lectura.

El agente nunca modifica información almacenada.

---

# 18. Gestión documental

El agente permite consultar documentación asociada a cada ponente.

Entre los documentos disponibles pueden encontrarse:

- Billetes de avión.
- Billetes de tren.
- Reservas de hotel.
- Presentaciones.
- Currículums.
- Información complementaria.

Cuando un documento existe, el agente puede localizarlo y utilizar su contenido para responder preguntas del usuario.

---

# 19. Modelo de lenguaje

El agente utiliza un modelo de lenguaje para interpretar las consultas del usuario y generar respuestas naturales.

El modelo recibe un contexto construido dinámicamente a partir de:

- Información del evento.
- Estado del usuario.
- Documentación disponible.
- Prompt del sistema.
- Pregunta realizada.

El LLM no trabaja de forma aislada.

Siempre recibe información estructurada previamente obtenida por el agente.

---

# 20. Prompts

El comportamiento del modelo se controla mediante distintos prompts especializados.

Entre ellos se encuentran:

### Prompt del sistema

Define el comportamiento general del asistente.

Establece las normas de conversación y las restricciones del agente.

---

### Prompt de análisis

Permite interpretar correctamente la intención del usuario.

Ayuda a identificar qué información debe consultarse antes de responder.

---

### Prompt de validación

Se utiliza para comprobar que la respuesta generada cumple las reglas establecidas por el sistema.

Su objetivo es reducir errores y evitar respuestas inconsistentes.

---

# 21. Configuración del proyecto

Toda la configuración del sistema se encuentra centralizada en la carpeta `config/`.

Esto permite modificar el comportamiento del agente sin alterar el código fuente.

La configuración incluye:

- Parámetros generales.
- Permisos.
- Variables de funcionamiento.
- Configuración del modelo.
- Configuración de Telegram.
- Configuración de la base de datos.

---

# 22. Permisos

El agente dispone de un sistema de permisos que controla las acciones que puede realizar.

Entre ellos destacan:

| Permiso | Descripción |
|----------|-------------|
| `ALLOW_DB_READ` | Permite consultar la base de datos |
| `ALLOW_SEND_TELEGRAM` | Permite enviar mensajes mediante Telegram |
| `ALLOW_NOTIFY_ADMIN` | Permite registrar solicitudes para la organización |

Estos permisos facilitan adaptar el comportamiento del agente a distintos entornos.

---

# 23. Variables de entorno

El proyecto utiliza un archivo `.env` para almacenar la configuración sensible.

Entre las variables habituales se encuentran:

```text
TELEGRAM_BOT_TOKEN=

OPENAI_API_KEY=

DATABASE_URL=

LOG_LEVEL=
```

Estas variables no deben almacenarse dentro del código fuente.

---

# 24. Instalación

## Clonar el proyecto

```bash
git clone <repositorio>

cd agente_telegram_ponentes
```

---

## Crear entorno virtual

```bash
python -m venv .venv
```

---

## Activar entorno

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

---

## Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Configurar variables

Copiar el archivo:

```text
.env.example
```

como

```text
.env
```

y completar todas las credenciales necesarias.

---

# 25. Ejecución

Una vez configurado el proyecto, el servicio puede iniciarse mediante:

```bash
python servicio.py
```

Al iniciarse correctamente, el sistema comenzará a escuchar nuevos mensajes enviados al bot de Telegram.

---

# 26. Flujo completo de ejecución

```text
Inicio

   │

Carga configuración

   │

Inicialización Telegram

   │

Espera mensajes

   │

Mensaje recibido

   │

ejecutar_agente()

   │

Consulta PostgreSQL

   │

Consulta documentos

   │

Construcción del prompt

   │

LLM

   │

Validación

   │

Respuesta

   │

Telegram

   │

Fin
```

---

---

# 27. Validaciones

Antes de devolver una respuesta al usuario, el agente realiza diversas comprobaciones para garantizar la coherencia de la información generada.

Entre las principales validaciones se encuentran:

- Verificación del formato del mensaje recibido.
- Validación del usuario de Telegram.
- Comprobación de la existencia del evento asociado.
- Verificación de la disponibilidad de documentación.
- Validación de la respuesta generada por el LLM.
- Comprobación de permisos antes de realizar cualquier acción.

Estas validaciones permiten reducir errores y evitar respuestas inconsistentes.

---

# 28. Gestión de errores

El agente está diseñado para continuar funcionando incluso cuando alguno de los componentes no responde correctamente.

Los errores más habituales son:

| Error | Comportamiento |
|--------|----------------|
| Usuario sin evento asociado | Se informa al usuario y se solicita contactar con la organización. |
| Documento no encontrado | Se comunica que la documentación no está disponible. |
| Error de conexión con PostgreSQL | Se registra el error y se devuelve un mensaje genérico. |
| Error del modelo LLM | Se responde indicando que la consulta no puede procesarse temporalmente. |
| Error en Telegram | El incidente queda registrado en los logs del sistema. |

Siempre que sea posible el agente devuelve una respuesta controlada evitando finalizar la ejecución de forma inesperada.

---

# 29. Registro de actividad

El proyecto incorpora un sistema de registro que permite conocer el comportamiento del agente durante su ejecución.

Los logs facilitan:

- Diagnóstico de errores.
- Seguimiento de conversaciones.
- Análisis de incidencias.
- Verificación del funcionamiento del sistema.

Dependiendo de la configuración pueden registrarse distintos niveles de información.

| Nivel | Descripción |
|--------|-------------|
| INFO | Información general del funcionamiento. |
| WARNING | Situaciones no críticas que requieren atención. |
| ERROR | Errores producidos durante la ejecución. |
| DEBUG | Información detallada para depuración. |

---

# 30. Seguridad

El agente ha sido diseñado siguiendo el principio de mínimo privilegio.

Actualmente se aplican las siguientes medidas:

- Las credenciales se almacenan mediante variables de entorno.
- No existen claves embebidas en el código fuente.
- El acceso a la base de datos es de lectura.
- Los permisos del agente son configurables.
- El acceso a Telegram requiere un Bot Token válido.
- Los documentos únicamente son accesibles para el usuario autorizado.

Estas medidas reducen el riesgo de accesos no autorizados y facilitan el despliegue en distintos entornos.

---

# 31. Contrato de entrada

Toda petición procesada por el agente se encapsula en un único objeto (`payload`) que contiene la información necesaria para generar una respuesta.

De forma simplificada, el payload incluye información como:

```json
{
  "usuario": "...",
  "mensaje": "...",
  "evento": "...",
  "contexto": {}
}
```

Este contrato permite desacoplar la lógica del agente del canal de comunicación utilizado.

---

# 32. Contrato de salida

La respuesta generada por el agente se devuelve de forma estructurada antes de ser enviada a Telegram.

Un ejemplo simplificado sería:

```json
{
  "ok": true,
  "respuesta": "Texto generado para el usuario.",
  "estado": "correcto"
}
```

Esta estructura facilita la integración con otros componentes del sistema y simplifica el tratamiento de errores.

---

# 33. Pruebas

El proyecto incorpora un conjunto de pruebas destinadas a verificar el correcto funcionamiento del agente.

Entre ellas pueden encontrarse pruebas relacionadas con:

- Procesamiento de mensajes.
- Validaciones.
- Integración con Telegram.
- Acceso a la base de datos.
- Generación de respuestas.

Se recomienda ejecutar las pruebas antes de desplegar una nueva versión del proyecto.

---

# 34. Dependencias principales

El proyecto utiliza diversas librerías de Python para implementar sus funcionalidades.

Entre las más relevantes se encuentran:

- python-telegram-bot
- OpenAI SDK
- psycopg
- python-dotenv
- pydantic
- requests

La lista completa de dependencias puede consultarse en el archivo:

```text
requirements.txt
```

---

# 35. Recomendaciones de despliegue

Para un funcionamiento estable se recomienda:

- Utilizar un entorno virtual independiente.
- Mantener actualizadas las dependencias.
- Proteger correctamente el archivo `.env`.
- Configurar copias de seguridad de la base de datos.
- Supervisar periódicamente los logs del sistema.
- Renovar periódicamente las credenciales utilizadas por el agente.

---

# 36. Limitaciones actuales

La versión 0.9 del agente presenta las siguientes limitaciones conocidas:

- Depende de la disponibilidad de Telegram.
- Depende de la conexión con PostgreSQL.
- Depende de la disponibilidad del modelo LLM.
- No modifica información almacenada.
- No gestiona reservas.
- No realiza acciones administrativas.
- No funciona sin las credenciales configuradas.

Estas limitaciones son intencionadas y forman parte del diseño del sistema.

---

# 37. Evolución prevista

Las siguientes mejoras podrán incorporarse en futuras versiones:

- Gestión de múltiples eventos simultáneos.
- Soporte para varios idiomas.
- Envío proactivo de recordatorios.
- Integración con calendarios.
- Gestión avanzada de documentos.
- Panel de administración.
- Mayor personalización del contexto conversacional.

---

# 38. Historial de versiones

| Versión | Descripción |
|----------|-------------|
| 0.1 | Primer prototipo del agente. |
| 0.5 | Integración inicial con Telegram. |
| 0.9 | Integración con PostgreSQL, gestión documental, memoria conversacional y mejoras en el procesamiento mediante LLM. |

---

# 39. Autor

Proyecto desarrollado para la plataforma **MITUMI**.

El objetivo del agente es proporcionar un canal de comunicación inteligente entre la organización de un evento y sus ponentes mediante Telegram, ofreciendo acceso inmediato a información relevante de forma segura y automatizada.

---

# 40. Conclusión

El Agente de Telegram para Ponentes constituye un asistente conversacional especializado diseñado para facilitar la comunicación entre los ponentes y la organización de un evento.

Su arquitectura modular permite integrar servicios externos como Telegram, PostgreSQL y modelos de lenguaje, manteniendo una clara separación entre la lógica del agente, la configuración y las integraciones.

La versión 0.9 representa una base sólida sobre la que continuar incorporando nuevas funcionalidades manteniendo un diseño sencillo, mantenible y fácilmente ampliable.

---

