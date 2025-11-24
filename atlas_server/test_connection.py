# test_connection.py (En la carpeta de tu Agente ATLAS)

from db_connector import get_db_connection

def test_db_read():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Intentar contar cuántos proyectos hay
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        
        print("\n✅ ¡Conexión y tablas de ATLAS OK!")
        print(f"La tabla 'projects' contiene actualmente {count} filas.")
        
        conn.close()
        return True
    
    except Exception as e:
        print("\n❌ FALLÓ LA CONEXIÓN O LA VERIFICACIÓN DE TABLAS.")
        print(f"Error detallado: {e}")
        return False

if __name__ == '__main__':
    test_db_read()