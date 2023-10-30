import sys
import struct
import socket
import csv

def send_can_frame(device, can_frame):
    try:
        can_id, data = can_frame.split('#')
        can_id = int(can_id, 16)
        data = bytes.fromhex(data)
    except ValueError:
        print(f"Error: Formato de marco CAN incorrecto: {can_frame}")
        return

    try:
        s = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        s.bind((device,))
        s.send(struct.pack("=IB3x8s", can_id, len(data), data))
        #print(f"Marco CAN enviado en {device}: {can_frame}")
    except OSError as e:
        print(f"Error al enviar el marco CAN: {e}")

def send_can_frames_from_file(device, file_path):
    try:
        with open(file_path, newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if len(row) > 0:
                    send_can_frame(device, row[0])
    except FileNotFoundError:
        print(f"Error: No se puede encontrar el archivo {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 send.py <device> <file_path>")
        sys.exit(1)

    device = sys.argv[1]
    file_path = sys.argv[2]

    send_can_frames_from_file(device, file_path)
