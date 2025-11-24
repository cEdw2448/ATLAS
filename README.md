# ATLAS: Agente de Gestión de Proyectos experto (Tool-Calling)

## 🚀 Resumen del Proyecto

**ATLAS** (Agent-Based Task and Log Automation System) es un Agente de Gestión de Proyectos avanzado que utiliza la arquitectura de **Tool-Calling** (llamada a herramientas) de modelos de lenguaje grandes (LLM) para interactuar con una base de datos PostgreSQL.

Su función principal es interpretar instrucciones en lenguaje natural (chat) y convertirlas en acciones estructuradas (crear tareas, listar proyectos, actualizar estados) a través de un servidor de proceso de comandos (MCP).

## ⚙️ Arquitectura y Tecnologías Clave

| Componente | Descripción | Dependencia Clave |
| :--- | :--- | :--- |
| **Cliente (`atlas_client/client.py`)** | Maneja el bucle de conversación, la comunicación con la API de GitHub/OpenAI, y ejecuta el Servidor MCP como un subproceso. | `OpenAI`, `asyncio`, `subprocess` |
| **Servidor MCP (`atlas_server/server.py`)** | Servidor de Proceso de Comandos. Recibe peticiones JSON del cliente y ejecuta la lógica de la herramienta correspondiente. | `mcp.server`, `mcp.types` |
| **Herramientas (`atlas_server/tools.py`)** | Define las funciones de gestión de proyectos (`crear_tarea`, `listar_proyectos`) y maneja la conexión con la base de datos. | `pydantic`, `psycopg2` |
| **Persistencia** | Base de datos relacional para almacenar proyectos y tareas. | **PostgreSQL** |

---

## 🛠️ Instalación y Configuración Rápida

La configuración de ATLAS requiere inicializar la base de datos y configurar las credenciales de la API.

### Paso 1: Dependencias de Python

Asegúrese de tener un entorno virtual activo e instale las bibliotecas necesarias:

```bash
pip install openai python-dotenv psycopg2-binary pydantic
# Nota: La librería 'mcp' se asume disponible en el entorno o es código local.
```

--- 

### Paso 2: Configuración de la Base de Datos (PostgreSQL)

ATLAS utiliza una base de datos PostgreSQL.

1. Asegúrese de que un servidor PostgreSQL esté en ejecución.
2. Cree una base de datos vacía (ej. `atlas_db`).

---

### Paso 3: Configuración de Credenciales (.env)

Cree el archivo `.env` en el directorio raíz (`ATLAS/`) con las siguientes variables:
| Variable | Uso | Ejemplo |
| :--- | :--- | :--- |
| **GIT_TOKEN** | Token de la API de GitHub AI (OpenAI/Modelo). Necesario para el LLM. | `GIT_TOKEN=ghu_xxxxxxxxxxxxxxxxxx` |
| **DB_HOST** | Host de su servidor PostgreSQL. | `DB_HOST=localhost` |
| **DB_NAME** | Nombre de la base de datos creada en el Paso 2. | `DB_NAME=atlas_db` |
| **DB_USER** | Usuario de la base de datos. | `DB_USER=atlas_user` |
| **DB_PASSWORD** | Contraseña del usuario. | `DB_PASSWORD=secret_password` |
| **DB_PORT** | Puerto de PostgreSQL (generalmente 5432). | `DB_PORT=5432` |

---

### Paso 4: Ejecución del Agente

Ejecute el cliente principal para iniciar la conversación. La primera ejecución inicializará el esquema de la base de datos (projects y tasks).
Bash

#### Desde el directorio raíz (ATLAS/)
`python atlas_client/client.py`

Una vez iniciado, el agente le saludará.

🌐 ATLAS: ¡Hola! Soy ATLAS, tu gestor de proyectos. ¿Cómo puedo ayudarte hoy?

---


## 📚 Documentación y Uso de Comandos

Las instrucciones detalladas sobre las funciones y la lógica de cada comando se encuentran en:

- [**Manual de Integración**](./docs/03_Manual_Integración.md): Guía de uso de las funciones (`crear_tarea`, `listar_proyectos`, etc.).
- [**Visión y Alcance**](./docs/01_Vision_Alcance.md): Requerimientos de negocio y casos de uso.
- [**Arquitectura**](./docs/02_Arquitectura.md): Flujo de datos Cliente/Servidor MCP y detalle de la conexión DB.

  
