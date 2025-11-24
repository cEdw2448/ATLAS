# Manual de Uso e Integración del ProjectAgent

| Campo | Valor |
| :--- | :--- |
| **Título del Documento** | **Manual de Uso e Integración del ProjectAgent** |
| **ID del Documento** | DSW-ProjectAgent-003 |
| **Versión** | v1.0.0 |
| **Fecha de Creación** | 2025-11-24 |
| **Autor(es)** | Carlos Eduardo Román Bravo |
| **Estado** | Revisado |

---

## 1. Historial de Revisiones

| Versión | Fecha | Autor | Descripción del Cambio | Base de Cambio (Ticket/ID) |
| :--- | :--- | :--- | :--- | :--- |
| v1.0.0 | 2025-11-24 | Carlos Román | Creación inicial de las funciones de gestión. | N/A |

---

## 2. Configuración Inicial y Autenticación

Esta sección detalla los pasos requeridos para inicializar el ProjectAgent y conectarlo a su sistema de gestión de proyectos (JIRA, Trello, etc.).

### 2.1. Requisitos Previos

Asegúrese de haber completado la instalación siguiendo las instrucciones del `README.md`.

### 2.2. Autenticación y Credenciales

El Agente requiere acceso autorizado a su plataforma externa.

1.  **Obtención de Credenciales:** Obtenga su *API Key* o *Token de Acceso* tomando en cuenta la plataforma correspondiente al modelo de IA que necesite.
2.  **Configuración de Entorno:** Defina las siguientes variables de entorno para la operación del Agente:
    * `DB_HOST` : string de la ip local a la base de datos
    * `DB_PORT` : string con el número de puerto habilitado
    * `DB_NAME` : string con el nombre de la base de datos
    * `DB_USER` : string con el nombre de usuario para la base de datos
    * `DB_PASSWORD` : string de la contraseña del usuario a la base de datos
    * `GIT_TOKEN` : Su token de acceso único (obtenido de github)

---

## 3. Guía de Funciones (Comandos de Gestión)

Esta sección describe cada una de las funcionalidades del Agente y cómo utilizarlas.

### 3.1. Gestión de Tareas

| Nombre de la Función | Comando / Prompt | Descripción y Uso |
| :--- | :--- | :--- |
| **`crear_tarea`** | `Crea la tarea Investigar en el proyecto DesarrolloIA` | Crea una nueva tarea individual en el proyecto especificado. |
| **`actualizar_estado_tarea`** | `Cambia el estado de la tarea Investigar en el proyecto DesarrolloIA a In Progress` | Mueve una tarea existente a un nuevo estado de flujo de trabajo (ej. "To Do", "Done", "Review"). |
| **`eliminar_tarea`** | `Elimina la tarea Investigar del proyecto Desarrollo IA` | Elimina de forma permanente una tarea específica. |

### 3.2. Gestión de Proyectos

| Nombre de la Función | Comando / Prompt | Descripción y Uso |
| :--- | :--- | :--- |
| **`crear_proyecto_y_tareas`** | `Crea un proyecto llamado Nuevo Proyecto con la tarea Nueva Tarea` | Crea un nuevo proyecto y solicita al menos una tarea para inicializar el proyecto con sus respectivas tareas. |
| **`eliminar_proyecto`** | `Elimina el proyecto Nuevo Proyecto` | **ADVERTENCIA:** Esta acción elimina el proyecto y TODAS las tareas contenidas en él. **Irreversible.** |

### 3.3. Búsqueda, Listado y Monitoreo

| Nombre de la Función | Comando / Prompt | Descripción y Uso |
| :--- | :--- | :--- |
| **`listar_tareas`** | `Lista las tareas del proyecto DesarrolloIA` | Busca y muestra una lista de tareas. Acepta filtros por nombre de proyecto y estado. |
| **`listar_proyectos`** | `Lista todos los proyectos` | Muestra una lista de todos los proyectos administrados. |

### 3.4. Automatización de Alta Prioridad

| Nombre de la Función | Comando / Prompt | Descripción y Uso |
| :--- | :--- | :--- |
| **`crear_recordatorio`** | `Crea un recordatorio de la tarea Investigar` | Crea una tarea de alta prioridad en el proyecto dedicado "Recordatorios". Es posible que necesite especificar el proyecto dependiendo del contexto reciente. |

---

## 4. Troubleshooting y Códigos de Error

(Esta sección debe ser rellenada por los desarrolladores a medida que identifiquen fallos comunes).

| Código de Error | Descripción del Error | Posible Solución |
| :--- | :--- | :--- |
| **Error 401** | Credenciales de API inválidas o token expirado. | Revise y regenere su `GIT_TOKEN`. |
| **Error 404** | El proyecto o la tarea ID especificada no existe. | Verifique la existencia y el nombre exacto del proyecto/tarea. |
| **Error 400** | Faltan parámetros obligatorios (ej. Título al crear tarea). | Asegúrese de incluir todos los argumentos requeridos por la función. |
| **Error 403** | El modelo de IA que está utilizando alcanzó el límite de tokens. | Cambie de modelo o añada más créditos al modelo. |


---
