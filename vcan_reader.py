import can

def iniciar_monitorizacion():
    # Iniciar la captura de tramas desde vcan0
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    
    try:
        while True:

            trama = bus.recv()
            print(f"ID: {trama.arbitration_id}  Datos: {trama.data.hex()}")

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    iniciar_monitorizacion()
