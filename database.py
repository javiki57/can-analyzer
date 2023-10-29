import sqlite3
import csv

# Nombre del archivo CSV para almacenar los datos
nombre_archivo = "datos_can.csv"

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

# Función para inicializar el archivo CSV
def inicializar_archivo():
    with open(nombre_archivo, mode='w', newline='') as archivo_csv:
        escritor = csv.writer(archivo_csv)
        escritor.writerow(['ID', 'Tiempo', 'Frecuencia', 'Función', 'ID Nodo', 'Tam', 'Datos'])

# Función para agregar una nueva trama al archivo CSV
def agregar_trama(trama):
    with open(nombre_archivo, mode='a', newline='') as archivo_csv:
        escritor = csv.writer(archivo_csv)
        escritor.writerow([trama['ID'], trama['tiempo'], trama['frecuencia'], trama['funcion'], trama['id_nodo'], trama['tam'], trama['datos']])

# Función para consultar todas las tramas del archivo CSV
def consultar_tramas():
    tramas = []
    with open(nombre_archivo, mode='r', newline='') as archivo_csv:
        lector = csv.DictReader(archivo_csv)
        for fila in lector:
            tramas.append(fila)
    return tramas

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