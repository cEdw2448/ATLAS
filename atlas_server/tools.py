# ATLAS/atlas_server/tools.py

from atlas_server.db_connector import get_db_connection
from pydantic import BaseModel, Field
import json, datetime

def tool(name, description, pydantic_class):
    """
    Decorador personalizado que adjunta el esquema JSON de Pydantic
    a la función para que el cliente lo lea directamente.
    """
    def decorator(func):
        # Almacenar los metadatos y el esquema en la propia función
        func.tool_name = name
        func.tool_description = description
        
        # Almacenar el esquema Pydantic v2 para que el cliente lo lea
        func.input_schema = pydantic_class.model_json_schema(by_alias=True)
        return func
    return decorator
# ----------------------------------------------------

# ----------------------------------------------------
# 0. INICIALIZACIÓN DE LA BASE DE DATOS 
# ----------------------------------------------------

def initialize_db_schema():
    """Crea las tablas 'projects' y 'tasks' con el esquema simplificado si no existen."""
    conn = get_db_connection()
    if conn is None:
        print("❌ ERROR: La inicialización de la base de datos falló al obtener la conexión.")
        return
        
    cursor = None
    
    try:
        cursor = conn.cursor()
        
        # Tabla de proyectos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabla de tareas (ESQUEMA SIMPLIFICADO: SIN assigned_to ni due_date)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                description VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'Pendiente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        print("✅ Esquema de base de datos inicializado (tablas projects y tasks creadas/verificadas con esquema simplificado).")
        
    except Exception as e:
        print(f"❌ ADVERTENCIA: No se pudo inicializar el esquema de la base de datos. Las herramientas podrían fallar. Error: {e}")
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# --- CLASES PYDANTIC ---
class CrearTareaInput(BaseModel):
    project_id: int = Field(..., description="El ID numérico del proyecto al que se debe asignar la tarea.")
    description: str = Field(..., description="El título conciso de la nueva tarea a crear.")

class ActualizarEstadoInput(BaseModel):
    tarea_id: int = Field(..., description="El ID numérico de la tarea que se va a modificar.")
    nuevo_estado: str = Field(..., description="El nuevo estado de la tarea, ej.: 'En Progreso', 'Hecha', 'Bloqueada'.")

class CrearRecordatorioInput(BaseModel):
    description: str = Field(..., description="El título o descripción concisa del recordatorio.")

class CrearProyectoYTareasInput(BaseModel):
    nombre_proyecto: str = Field(..., description="El nombre que se le dará al nuevo proyecto.")
    lista_tareas: str = Field(..., description="Cadena de texto con todas las tareas separadas por comas, saltos de línea o guiones.")

class ListarTareasInput(BaseModel):
    project_name: str = Field(None, description="Filtra por nombre del proyecto (búsqueda parcial).")
    status: str = Field(None, description="Filtra por estado de la tarea (ej. 'Pendiente', 'Hecha').")

class ListarProyectosInput(BaseModel):
    nombre: str = Field(None, description="Filtra proyectos por nombre (búsqueda parcial).")

# --- HERRAMIENTAS ATLAS ---

@tool(
    name="crear_tarea",
    description="Crea una tarea individual con un título en un proyecto específico. Requiere el ID del proyecto. (Omite asignación y vencimiento).",
    pydantic_class=CrearTareaInput
)
async def crear_tarea(project_id: int, description: str) -> str:
    """Inserta una nueva tarea en la tabla 'tasks' asociada a un proyecto (esquema simplificado)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Consulta SQL simplificada: Solo project_id y description
        cursor.execute(
            "INSERT INTO tasks (project_id, description) VALUES (%s, %s) RETURNING id",
            (project_id, description)
        )
        task_id = cursor.fetchone()[0]
        conn.commit()
        return f"Tarea '{description}' creada exitosamente en el proyecto ID {project_id}. ID de Tarea: {task_id}."
    except Exception as e:
        conn.rollback()
        return f"❌ Error al crear la tarea. Asegúrate de que el Project ID {project_id} existe. Error: {e}"
    finally:
        conn.close()

@tool(
    name="actualizar_estado_tarea",
    description="Actualiza el estado de una tarea existente. Los estados válidos comunes son 'Pendiente', 'En Progreso', 'Bloqueada', o 'Hecha'.",
    pydantic_class=ActualizarEstadoInput
)
async def actualizar_estado_tarea(tarea_id: int, nuevo_estado: str) -> str:
    """Actualiza el campo 'status' de una tarea específica."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE tasks SET status = %s WHERE id = %s RETURNING id",
            (nuevo_estado, tarea_id)
        )
        if cursor.rowcount == 0:
            return f"❌ Error: No se encontró la tarea con ID {tarea_id}."
        conn.commit()
        return f"✅ Tarea ID {tarea_id} actualizada. Nuevo estado: {nuevo_estado}."
    except Exception as e:
        conn.rollback()
        return f"❌ Error al actualizar el estado de la tarea {tarea_id}. Error: {e}"
    finally:
        conn.close()

@tool(
    name="crear_recordatorio",
    description="Crea una tarea de alta prioridad con un título en el proyecto 'Recordatorios'. (No admite fecha/hora límite ni asignado en este esquema).",
    pydantic_class=CrearRecordatorioInput
)
async def crear_recordatorio(description: str) -> str:
    """Crea una tarea de alta prioridad en el proyecto 'Recordatorios'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Asegurar que el proyecto 'Recordatorios' existe
        cursor.execute("INSERT INTO projects (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id", ('Recordatorios',))
        project_id = cursor.fetchone()[0]
        
        # 2. Insertar la tarea de recordatorio (Solo project_id, description, status)
        cursor.execute(
            "INSERT INTO tasks (project_id, description, status) VALUES (%s, %s, %s) RETURNING id",
            (project_id, description, 'Recordatorio')
        )
        task_id = cursor.fetchone()[0]
        conn.commit()
        return f"✅ Recordatorio '{description}' creado (ID: {task_id})."
    except Exception as e:
        conn.rollback()
        return f"❌ Error al crear el recordatorio. Error: {e}"
    finally:
        conn.close()

@tool(
    name="crear_proyecto_y_tareas",
    description="Crea un proyecto y un conjunto de tareas iniciales. La lista de tareas debe ser una cadena separada por comas, saltos de línea o guiones.",
    pydantic_class=CrearProyectoYTareasInput
)
async def crear_proyecto_y_tareas(nombre_proyecto: str, lista_tareas: str) -> str:
    """Crea un proyecto principal y luego inserta múltiples tareas asociadas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Crear el proyecto principal y obtener su ID
        cursor.execute("INSERT INTO projects (name) VALUES (%s) RETURNING id", (nombre_proyecto,))
        project_id = cursor.fetchone()[0]
        
        # 2. Procesar la lista de tareas del texto
        tareas_raw = lista_tareas.replace('\n', ',').replace('-', ',').replace(';', ',')
        tareas = [t.strip() for t in tareas_raw.split(',') if t.strip()]
        
        if not tareas:
            conn.commit()
            return f"Proyecto '{nombre_proyecto}' creado (ID: {project_id}), pero no se encontraron tareas válidas en la lista."

        # 3. Insertar cada tarea (solo project_id, description, status)
        tareas_creadas = 0
        for tarea_description in tareas:
            cursor.execute(
                "INSERT INTO tasks (project_id, description, status) VALUES (%s, %s, %s)",
                (project_id, tarea_description, 'Pendiente')
            )
            tareas_creadas += 1
            
        conn.commit()
        return f"✅ Proyecto '{nombre_proyecto}' creado (ID: {project_id}) con {tareas_creadas} tareas iniciales."
    except Exception as e:
        conn.rollback()
        if "unique constraint" in str(e):
                return f"❌ Error: El proyecto '{nombre_proyecto}' ya existe. Por favor, usa un nombre diferente."
        return f"❌ Error al crear el proyecto y las tareas. Error: {e}"
    finally:
        conn.close()

@tool(
    name="listar_tareas",
    description="Busca y lista tareas filtradas por nombre de proyecto o estado. Devuelve un resumen formateado de las tareas encontradas (no incluye asignado ni vencimiento).",
    pydantic_class=ListarTareasInput
)
async def listar_tareas(project_name: str = None, status: str = None) -> str:
    """Busca tareas en la base de datos aplicando filtros opcionales (esquema simplificado)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Consulta SQL simplificada: solo selecciona id, description, status, project_name
        sql_query = """
            SELECT
                t.id, t.description, t.status, p.name AS project_name
            FROM 
                tasks t
            JOIN 
                projects p ON t.project_id = p.id
            WHERE 
                1 = 1
        """
        params = []
        if project_name:
            sql_query += " AND p.name ILIKE %s"
            params.append(f'%{project_name}%')
        if status:
            sql_query += " AND t.status ILIKE %s"
            params.append(f'%{status}%')
        
        # Se omite el ORDER BY due_date
        sql_query += " ORDER BY t.id ASC LIMIT 10" 
        
        cursor.execute(sql_query, params)
        resultados = cursor.fetchall()
        
        if not resultados:
            return "✅ No se encontraron tareas que coincidan con los filtros especificados."

        output = [f"--- {len(resultados)} Tareas Encontradas ---"]
        
        for row in resultados:
            # Orden de los resultados (solo las columnas existentes): id, description, status, project_name
            task_id, description, task_status, project = row
            output.append(
                f"ID: {task_id} | Proyecto: {project} | Título: {description} | Estado: {task_status}"
            )
            
        return "\n".join(output)

    except Exception as e:
        return f"❌ Error al listar tareas: {e}"
    finally:
        conn.close()

@tool(
    name="listar_proyectos",
    description="Lista todos los proyectos existentes o filtra por nombre para obtener sus IDs y nombres.",
    pydantic_class=ListarProyectosInput
)
async def listar_proyectos(nombre: str = None) -> str:
    
    """Lista todos los proyectos en la tabla 'projects'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql_query = "SELECT id, name, created_at FROM projects WHERE 1=1"
        params = []
        if nombre:
            sql_query += " AND name ILIKE %s"
            params.append(f'%{nombre}%')
        
        sql_query += " ORDER BY id ASC" 
        
        cursor.execute(sql_query, params)
        resultados = cursor.fetchall()
        
        if not resultados:
            return "✅ No se encontraron proyectos."

        output = [f"--- {len(resultados)} Proyectos Encontrados ---"]
        
        for row in resultados:
            # Asumiendo created_at es un objeto datetime. datetime.strftime()
            project_id, name, created_at = row
            # La conversión a string puede ser necesaria si el tipo de columna es TIMESTAMP
            try:
                created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
            except AttributeError:
                created_at_str = str(created_at) # Fallback si no es un datetime object
                
            output.append(
                f"ID: {project_id} | Nombre: {name} | Creado: {created_at_str}"
            )
            
        return "\n".join(output)

    except Exception as e:
        return f"❌ Error al listar proyectos: {e}"
    finally:
        conn.close()