import csv
import sys

def extract_id_and_data(input_file, output_file):
    with open(input_file, 'r') as csv_input, open(output_file, 'w') as csv_output:
        csv_reader = csv.reader(csv_input)
        csv_writer = csv.writer(csv_output)

        next(csv_reader, None)

        for row in csv_reader:
            if len(row) >= 4:  # Asegurarse de que haya suficientes campos en la fila
                id_value = row[3]
                data = row[5].replace(" ", "") if len(row) >= 6 else "None"
                output_row = f"{id_value}#{data}"
                csv_writer.writerow([output_row])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 extract_id_and_data.py <archivo_entrada.csv> <archivo_salida.csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    extract_id_and_data(input_file, output_file)

