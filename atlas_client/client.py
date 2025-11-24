# ATLAS/atlas_client/client.py
import os
import json
import subprocess
import sys
import asyncio
from typing import Any

from openai import OpenAI
from dotenv import load_dotenv
from atlas_server.tools import initialize_db_schema # <--- Importar la función

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from atlas_server.tools import crear_tarea, actualizar_estado_tarea, crear_recordatorio, crear_proyecto_y_tareas, listar_tareas, listar_proyectos   
TOOLS_LIST = [
    {
        "type": "function", 
        "function": {
            # Los nombres de las propiedades ahora son los que definimos en el decorador
            "name": func.tool_name, 
            "description": func.tool_description, 
            # ACCESO CRÍTICO: Leer el esquema directamente de la función
            "parameters": func.input_schema 
        }
    }
    for func in [crear_tarea, actualizar_estado_tarea, crear_recordatorio, crear_proyecto_y_tareas, listar_tareas, listar_proyectos]
]

load_dotenv()

# Configuración del LLM
token = os.getenv("GIT_TOKEN")
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4.1-nano"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

# --- 1. Definición de la Función de Ejecución del Servidor MCP ---
def run_mcp_command(command: str) -> str:
    """
    Ejecuta el servidor MCP de ATLAS como un subprocesso 
    para procesar una llamada a herramienta y devuelve el resultado.
    """
    try:
        
        server_dir = os.path.join(os.path.dirname(__file__), '..', 'atlas_server')
        server_path = os.path.join(server_dir, 'server.py')

        print(f"   [COMANDO MCP ENVIADO]: {command[:80]}...") 

        env = os.environ.copy()
        env['PYTHONPATH'] = server_dir + os.pathsep + env.get('PYTHONPATH', '')

        process = subprocess.run(
            ['python', server_path],
            input=command,
            capture_output=True,
            text=True,
            timeout=10,
            env=env 
        )
        
        if   process.stderr:
            return f"Error del Servidor MCP (código {process.returncode}): \n{process.stderr.strip()}"
        
        # El Servidor MCP devolverá la respuesta de la herramienta
        return process.stdout.strip()
        
    except subprocess.TimeoutExpired:
        return "Error: La ejecución del comando MCP ha agotado el tiempo de espera (10s)."
    except FileNotFoundError:
        return f"Error: No se encontró el servidor en la ruta: {server_path}"
    except Exception as e:
        return f"Error desconocido al ejecutar MCP: {e}"


# --- 2. Instrucciones para ATLAS (System Prompt) ---
SYSTEM_PROMPT = """
Eres ATLAS, un Agente de Gestión de Proyectos experto. Tu función es gestionar tareas y proyectos.
**REGLA CRÍTICA DE EJECUCIÓN:** Para cualquier acción relacionada con proyectos o tareas (crear, listar, actualizar), **DEBES OBLIGATORIAMENTE** usar una de las herramientas proporcionadas.
No respondas con texto conversacional sobre el estado o la creación si la solicitud requiere una herramienta; en su lugar, **DEBES** hacer la llamada a la herramienta.
**INSTRUCCIÓN ESPECÍFICA:** Para "Listar proyectos", "Ver proyectos" o "Mostrar todos los proyectos", **DEBES USAR LA HERRAMIENTA 'listar_proyectos' sin excepción**.
"""

# --- 3. Bucle de Conversación Principal ---
async def chat_with_atlas():
    initialize_db_schema()
    print("🤖 ATLAS: ¡Hola! Soy ATLAS, tu gestor de proyectos. ¿Cómo puedo ayudarte hoy?")
    messages : list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("\nTú: ")
        if user_input.lower() in ["salir", "adios", "exit", "q"]:
            print("🤖 ATLAS: ¡Hasta pronto!")
            break

        messages.append({"role": "user", "content": user_input})
        
        print("Procesando...")

        # Llamada a la API de OpenAI
        try:
            response = client.chat.completions.create(
                model=model_name, 
                messages=messages,
                tools=TOOLS_LIST,
                tool_choice="auto",
            )
        except Exception as e:
            print(f"❌ ERROR: Falló la llamada a la API de OpenAI. Error: {e}")
            messages.pop() # Eliminar el último mensaje del usuario para que pueda reintentar
            continue

        response_message = response.choices[0].message
        
        # --- 4. Procesamiento de Llamada a Herramienta ---
        if response_message.tool_calls:
            messages.append(response_message)
            print("Llamada  a herramienta...\n")

            tool_output=""
            
            # Recorrer todas las llamadas que el modelo sugiere
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    error = f"❌ Error al decodificar argumentos JSON para {function_name}: {tool_call.function.arguments}"
                    print(error)
                    tool_output = error
                    function_args = {}

                # El Servidor MCP necesita el comando en formato JSON string
                mcp_command = json.dumps({
                    "function": function_name,
                    "arguments": function_args
                })
                
                # Ejecutar el comando en el Servidor MCP
                if not tool_output.startswith("❌ Error al decodificar"):
                    tool_output = run_mcp_command(mcp_command)   

                if not tool_output.startswith("❌ Error Crítico"):
                    print(f"🛠️ Resultado de la Herramienta ({function_name}): {tool_output}")

                # Añadir la respuesta de la herramienta al historial de mensajes
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_output,
                    }
                )
            
            # 5. Volver a llamar al LLM con la respuesta de la herramienta para obtener la respuesta final
            #print("🤖 ATLAS: Generando respuesta final...")
            final_response = client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            print("🤖 ATLAS:", final_response.choices[0].message.content)
            messages.append(final_response.choices[0].message)
        
        else:
            # Respuesta simple del modelo sin usar herramientas
            print("⚠️ ADVERTENCIA: El LLM no generó una llamada a herramienta. Respondió con texto conversacional.")
            print("🤖 ATLAS:", response_message.content)
            messages.append(response_message)

if __name__ == '__main__':
    try:
        asyncio.run(chat_with_atlas())
    except KeyboardInterrupt:
        print("\nSaliendo...")
    except Exception as e:
        print(f"Error fatal al iniciar el cliente: {e}")