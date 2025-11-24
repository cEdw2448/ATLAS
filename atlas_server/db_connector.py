# ATLAS/atlas_server/db_connector.py

import psycopg2
import os
import sys
from dotenv import load_dotenv
import time

load_dotenv()

DB_CONFIG = {
    "host"        :os.getenv("DB_HOST"),
    "database"    :os.getenv("DB_NAME"),
    "user"        :os.getenv("DB_USER"),
    "password"    :os.getenv("DB_PASSWORD"),
    "port"        :os.getenv("DB_PORT")
}

def get_db_connection(max_retries=5):
    print(f"DEBUG: Intentando conectar a HOST={DB_CONFIG['host']}:PORT={DB_CONFIG['port']} con USER={DB_CONFIG['user']}")

    """Establece y devuelve una conexión a la base de datos PostgreSQL con reintentos."""
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except psycopg2.OperationalError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Intento {attempt + 1} de {max_retries}: Error de conexión a la BD. Reintentando en 1 segundo...")
                time.sleep(1)
            else:
                print(f"❌ ERROR: No se pudo conectar a la base de datos después de {max_retries} intentos.")
                print(f"Asegúrese de que el servidor PostgreSQL esté corriendo en {DB_CONFIG['host']}:{DB_CONFIG['port']} con las credenciales correctas.")
                return None
    return None

