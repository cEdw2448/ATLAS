# ATLAS: Agente Inteligente de Gestión de Tareas

## 🚀 Resumen del Proyecto

**ATLAS** es una herramienta de automatización diseñada para simplificar y centralizar la gestión de tareas y proyectos a través de una base de datos dedicada en PostgreSQL.

Su objetivo principal es permitir la manipulación rápida de proyectos y tareas (creación, actualización, listado) mediante comandos eficientes o llamadas a API, mejorando la productividad del equipo de gestión.

## ⚙️ Tecnologías Clave

| Componente | Tecnología Sugerida | Notas |
| :--- | :--- | :--- |
| **Lenguaje Base** | Python (Recomendado) | Usado para lógica del agente y manejo de comandos. |
| **Cliente API** | API específica de un LLM para interpretar los prompts | Esto le permite al LLM interactuar con la base de datos y utilizar las herramientas. |
| **Persistencia** | Base de datos PostgreSQL | Para mantener toda la información disponible. Esta se puede configurar de forma local o a través de un servidor NAS. |

## 🌐 Integraciones Soportadas

* **[PostgreSQL]:** Base de datos dedicada con estructura definida en 02_Arquitectura.md
---

## 🛠️ Instalación Rápida (Para Desarrolladores)

Siga estos pasos para configurar y ejecutar el agente en su entorno local:

1.  **Clonar el Repositorio:**
    ```bash
    git clone [URL_DE_SU_REPO]
    cd ProjectAgent
    ```

2.  **Configurar Entorno Virtual (Recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/macOS
    # .\venv\Scripts\activate # En Windows
    ```

3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar Variables de Entorno:**
    Cree un archivo `.env` en la raíz con sus credenciales (consulte la **Sección 2 del Manual de Integración** (`docs/03_Manual_Integracion.md`)).

5.  **Ejecutar el Agente (Modo CLI):**
    ```bash
    python run_agent.py --help
    ```

## 📚 Documentación Completa

La documentación detallada sobre el uso de cada función (`crear_tarea`, `listar_proyectos`, etc.), arquitectura técnica y visión de negocio se encuentra en el directorio:

* **[`docs/`](/docs)**

---
