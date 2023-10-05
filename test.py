import curses
import can
import threading
import time

# Función para leer datos CAN y actualizar la tabla en segundo plano
def read_can_data(bus, data):
    while True:
        message = bus.recv()
        data.append([len(data) + 1, time.strftime("%H:%M:%S", time.localtime()), hex(message.arbitration_id), message.dlc, ' '.join(format(byte, '02x') for byte in message.data)])
        if len(data) > curses.LINES - 2:
            data.pop(0)

# Función para crear la tabla en ncurses
def create_table(stdscr, data):
    stdscr.clear()

    headers = ["Count", "Time", "ID", "DLC", "Data"]
    
    # Verificar si data no está vacío
    if data:
        col_widths = [max(len(header), max(len(str(row[i])) for row in data)) + 2 for i, header in enumerate(headers)]
    else:
        col_widths = [len(header) + 2 for header in headers]

    stdscr.addch(0, 0, curses.ACS_ULCORNER)
    stdscr.addch(0, sum(col_widths) + len(col_widths) - 1, curses.ACS_URCORNER)
    stdscr.hline(0, 1, curses.ACS_HLINE, sum(col_widths) + len(col_widths) - 1)

    for i, header in enumerate(headers):
        stdscr.addstr(0, sum(col_widths[:i]) + i + 1, header)

    for i, row in enumerate(data, start=1):
        for j, cell in enumerate(row):
            stdscr.addstr(i, sum(col_widths[:j]) + j + 1, str(cell))

    stdscr.refresh()

def main(stdscr):
    can_interface = "vcan0"  # Cambia esto al nombre de tu interfaz CAN
    bus = can.interface.Bus(channel=can_interface, bustype='socketcan')

    data = []

    # Crear un hilo para leer los datos CAN en segundo plano
    can_thread = threading.Thread(target=read_can_data, args=(bus, data))
    can_thread.daemon = True
    can_thread.start()

    try:
        while True:
            create_table(stdscr, data)
            time.sleep(0.1)  # Actualizar la pantalla cada segundo
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    curses.wrapper(main)

