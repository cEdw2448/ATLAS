# atlas_server/server.py

import sys
import json
import asyncio
# Importamos la clase Server y el tipo Tool, pero eliminamos stdio_server
from mcp.server import Server 
from mcp.types import Tool
# Importamos todas las funciones de herramientas
from tools import crear_tarea, actualizar_estado_tarea, crear_recordatorio, crear_proyecto_y_tareas, listar_tareas, listar_proyectos 

# Lista que contiene todas las funciones de las herramientas
ALL_TOOLS = [crear_tarea, actualizar_estado_tarea, crear_recordatorio, crear_proyecto_y_tareas, listar_tareas, listar_proyectos]

# Inicialización del servidor MCP
atlas_server = Server(name="ATLAS_MCP_Server")

# --- REGISTRO DE MANEJADORES DE HERRAMIENTAS ---

@atlas_server.list_tools()
async def list_available_tools() -> list[Tool]:
    """
    Manejador para ListToolsRequest (aunque no se usa en este flujo manual).
    """
    return [
        Tool(
            name=func.tool_name, 
            description=func.tool_description, 
            inputSchema=func.input_schema
        )
        for func in ALL_TOOLS
    ]

@atlas_server.call_tool()
async def execute_tool_call(tool_name: str, arguments: dict) -> dict | str:
    """
    Ejecuta la función de herramienta solicitada.
    """
    # Buscamos la función de la herramienta por su nombre
    tool_func = next((f for f in ALL_TOOLS if f.tool_name == tool_name), None)
    
    if tool_func is None:
        # En este flujo, el cliente ya debería haber verificado el nombre.
        raise ValueError(f"Tool '{tool_name}' not found.")
    
    # Ejecutamos la función con los argumentos desempaquetados
    return await tool_func(**arguments)

if __name__ == '__main__':
    # --- MANEJO MANUAL DE I/O PARA EVITAR ERRORES DE LIBRERÍA ---
    try:
        # 1. Leer el comando JSON completo de la entrada estándar (STDIN)
        json_input = sys.stdin.read().strip()
        
        if not json_input:
            # Si no hay entrada, el proceso termina sin error (ej. inicialización o llamada vacía)
            sys.exit(0) 

        # 2. Parsear el JSON manualmente
        tool_call_data = json.loads(json_input)
        
        function_name = tool_call_data.get("function")
        arguments = tool_call_data.get("arguments", {})
        
        if not function_name:
            # Devolvemos un error claro si el JSON está malformado
            print(f"❌ Error del Servidor MCP: Comando JSON inválido: falta 'function'. Input: {json_input}")
            sys.exit(1)
            
        # 3. Ejecutar la función de herramienta de forma asíncrona
        # El cliente está esperando la salida de este script.
        result = asyncio.run(execute_tool_call(function_name, arguments))
        
        # 4. Imprimir el resultado de la herramienta para que el cliente lo capture
        if isinstance(result, str):
            print(result)
        else:
            # Asegurar que los resultados estructurados (diccionarios) también se devuelven como JSON string.
            print(json.dumps(result))
            
    except json.JSONDecodeError as e:
        # Captura si la cadena de entrada no es JSON válido
        print(f"❌ Error del Servidor MCP: No se pudo decodificar el JSON de entrada. Detalle: {e}. Input: {json_input[:100]}...")
        sys.exit(1)
    except Exception as e:
        # Captura cualquier otro error durante la ejecución (incluidos errores de la BD)
        print(f"❌ Error del Servidor MCP durante la ejecución: {type(e).__name__}: {e}")
        sys.exit(1)