# Visión y Alcance del ProjectAgent (ATLAS)

| Campo | Valor |
| :--- | :--- |
| **Título del Documento** | Visión y Alcance del ProjectAgent (ATLAS) |
| **ID del Documento** | DSW-ProjectAgent-001 |
| **Versión** | v1.0.0 |
| **Fecha de Creación** | 2025-11-24 |
| **Autor(es)** | Carlos Román |
| **Estado** | Revisado |

---

## 1. Historial de Revisiones

| Versión | Fecha | Autor | Descripción del Cambio | Base de Cambio (Ticket/ID) |
| :--- | :--- | :--- | :--- | :--- |
| v1.0.0 | 2025-11-24 | Carlos Román | Creación inicial de la Visión, Usuarios y Alcance funcional. | N/A |

---

## 2. Visión del Agente (Product Vision)

### 2.1. Propósito y Problema Resuelto

El propósito de ATLAS es **eliminar la fricción en la gestión diaria de tareas y proyectos** permitiendo que los usuarios interactúen con el sistema de gestión de proyectos mediante **lenguaje natural**.

* **Problema Resuelto:** La sobrecarga cognitiva y el tiempo perdido al navegar por interfaces gráficas (GUIs) para realizar acciones rutinarias (crear, actualizar, listar).
* **Valor para el Cliente:** Acelerar el flujo de trabajo de los gestores de proyectos y desarrolladores a través de una interfaz conversacional (chat).

### 2.2. Usuarios (Stakeholders)

| Rol | Descripción | Necesidades Clave |
| :--- | :--- | :--- |
| **Usuario Final (Gestor/Developer)** | Persona que usa la interfaz de chat/CLI para gestionar tareas. | Necesita comandos rápidos y precisos; respuestas claras sobre el éxito de las operaciones. |
| **Desarrollador (Equipo ATLAS)** | Equipo que mantiene y extiende las herramientas (`tools.py`). | Necesita un esquema de funciones (Pydantic) claro y una arquitectura robusta (MCP) para el *debugging*. |
| **Administrador de Sistemas** | Responsable de mantener la base de datos (PostgreSQL) y las credenciales de la API. | Necesita una configuración de entorno (`.env`) sencilla y manejo robusto de errores de conexión a DB. |

---

## 3. Alcance Funcional (Scope)

Este proyecto se enfoca en la gestión fundamental de entidades (CRUD básico).

| EN ALCANCE (In Scope) | FUERA DE ALCANCE (Out of Scope) |
| :--- | :--- |
| **Gestión de Entidades:** Crear, actualizar y eliminar Tareas y Proyectos. | **Integración de Flujos de Trabajo Complejos:** (Ej. automatizaciones basadas en fechas de vencimiento, asignación automática de tareas). |
| **Conversación a Acción:** Uso obligatorio de las herramientas proporcionadas por el LLM para manipular el sistema. | **Manipulación de Archivos Adjuntos:** No se soporta la adición o eliminación de archivos. |
| **Persistencia:** Almacenamiento de datos en PostgreSQL. | **Soporte Multi-Plataforma:** Actualmente, solo soporta una única fuente de datos (PostgreSQL), no integra JIRA, Trello, etc., simultáneamente. |
| **Manejo de Errores:** Devolver un *output* estructurado al LLM en caso de fallo de la herramienta (ej. "Error 404"). | **Interfaz Gráfica (GUI):** La interfaz de usuario es puramente de línea de comandos (CLI) / chat. |

---

## 4. Requerimientos Funcionales Detallados

Las siguientes son las funciones del agente, mapeadas a los requisitos que deben ser testeados:

| ID | Requerimiento Funcional | Mapeo a Tool (`atlas_server/tools.py`) |
| :--- | :--- | :--- |
| **RF1.1** | El agente DEBE ser capaz de crear una tarea individual en un proyecto existente. | `crear_tarea` |
| **RF1.2** | El agente DEBE ser capaz de modificar el estado de una tarea existente. | `actualizar_estado_tarea` |
| **RF1.3** | El agente DEBE ser capaz de crear un proyecto junto con una lista inicial de tareas. | `crear_proyecto_y_tareas` |
| **RF2.1** | El agente DEBE permitir buscar y listar tareas filtrando por proyecto y/o estado. | `listar_tareas` |
| **RF2.2** | El agente DEBE permitir listar todos los proyectos existentes o buscar por nombre. | `listar_proyectos` |
| **RF3.1** | El agente DEBE poder crear un recordatorio con alta prioridad en el proyecto "Recordatorios" si este no existe. | `crear_recordatorio` |
| **RF4.1** | El agente DEBE permitir eliminar una tarea específica por su ID. | `eliminar_tarea` |
| **RF4.2** | El agente DEBE permitir eliminar un proyecto específico, eliminando en cascada todas sus tareas asociadas. | `eliminar_proyecto` |

---

## 5. Requerimientos No Funcionales

| ID | Requerimiento No Funcional | Descripción |
| :--- | :--- | :--- |
| **RNF1 - Confiabilidad** | El agente DEBE poder reintentar la conexión a la base de datos hasta 5 veces si la conexión inicial falla. | Implementado en `db_connector.py`. |
| **RNF2 - Seguridad** | Las credenciales de acceso a la base de datos y la API DEBEN cargarse desde variables de entorno (`.env`) y no estar codificadas. | Implementado con `python-dotenv`. |
| **RNF3 - Trazabilidad** | El servidor MCP DEBE devolver mensajes de error claros al cliente para que el LLM pueda interpretarlos y comunicarlos al usuario. | Implementado en `run_mcp_command`. |
| **RNF4 - Estructura** | La definición de los parámetros de las herramientas DEBE usar el esquema Pydantic para garantizar la calidad de los datos enviados al servidor MCP. | Implementado con el decorador `@tool` en `tools.py`. |

---
