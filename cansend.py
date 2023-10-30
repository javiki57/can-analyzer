import sys
import struct
import socket
import can

def send_can_frame(device, can_frame):
    try:
        can_id, data = can_frame.split('#')
        can_id = int(can_id, 16)  # Convierte el identificador CAN a entero
        data = bytes.fromhex(data)
    except ValueError:
        print("Error: Formato de marco CAN incorrecto")
        return

    try:
        s = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        s.bind((device,))
        s.send(struct.pack("=IB3x8s", can_id, len(data), data))
        s.close()
        print(f"Marco CAN enviado en {device}: {can_frame}")
    except OSError as e:
        print(f"Error al enviar el marco CAN: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 send.py <device> <can_frame>")
        sys.exit(1)

    device = sys.argv[1]
    can_frame = sys.argv[2]

    send_can_frame(device, can_frame)
