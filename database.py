import sqlite3

# Conectar a la base de datos (creará un nuevo archivo si no existe)
conn = sqlite3.connect('can_traffic.db')

# Crear un cursor para ejecutar comandos SQL
cursor = conn.cursor()

# Crear una tabla para almacenar el tráfico CAN
cursor.execute('''
    CREATE TABLE IF NOT EXISTS can_data (
        conteo INTEGER,
        tiempo REAL,
        frecuencia REAL,
        id TEXT PRIMARY KEY,
        tam INTEGER,
        datos TEXT,
        funcion TEXT,
        id_nodo INTEGER
    )
''')

def insertar_trama(conteo, tiempo, frecuencia, id, tam, datos, funcion, id_nodo):
    cursor.execute('''
        INSERT INTO can_data (conteo, tiempo, frecuencia, id, tam, datos, funcion, id_nodo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (conteo, tiempo, frecuencia, id, tam, datos, funcion, id_nodo))
    conn.commit()


# Función para consultar todas las tramas almacenadas
def consultar_tramas():
    cursor.execute('SELECT * FROM can_data')
    return cursor.fetchall()


# Función para cerrar la conexión con la base de datos
def cerrar_base_de_datos():
    conn.close()