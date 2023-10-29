import sqlite3
import csv
import os
import sys

def create_database_and_table(csv_filename):
    if not os.path.exists(csv_filename):
        print(f"El archivo CSV '{csv_filename}' no existe.")
        return

    # Obtener el nombre del archivo sin la extensión
    table_name = os.path.splitext(os.path.basename(csv_filename))[0]

    # Crear una base de datos SQLite
    conn = sqlite3.connect('can_traffic.db')
    cursor = conn.cursor()

    # Leer la primera línea del archivo CSV para obtener los nombres de las columnas
    with open(csv_filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        columns = next(reader)

    # Crear la tabla con las columnas correspondientes
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
    cursor.execute(create_table_sql)
    conn.commit()

    # Leer el archivo CSV y agregar los datos a la tabla
    with open(csv_filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Saltar la primera fila, ya que son los nombres de las columnas
        for row in reader:
            # Generar una cadena de marcadores de posición para los valores
            placeholders = ', '.join(['?'] * len(columns))
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            cursor.execute(insert_sql, row)

    conn.commit()
    conn.close()
    print(f"Se ha creado la base de datos 'can_traffic.db' y se ha importado el archivo '{csv_filename}' en la tabla '{table_name}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python database.py <nombre_archivo_csv>")
        sys.exit(1)

    csv_filename = sys.argv[1]
    create_database_and_table(csv_filename)
