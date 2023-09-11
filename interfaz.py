import sys
import curses
import signal

def def_handler(sig, frame):
    sys.exit(1)

def main(stdscr):
    # Configuración inicial de la terminal
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    stdscr.keypad(1)
    
    # Colores personalizados
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    COLOR_CYAN_BLACK = curses.color_pair(1)
    COLOR_YELLOW_BLACK = curses.color_pair(2)
    COLOR_GREEN_BLACK = curses.color_pair(3)
    COLOR_RED_BLACK = curses.color_pair(4)
    COLOR_MAGENTA_BLACK = curses.color_pair(5)
    
    # Opciones del menú
    menu_items = ["1. Monitorización",
                  "2. Inyectar Payload",
                  "3. Modificar Payload",
                  "4. Salir"]
    
    current_row = 3
    option = 0
    
    while True:
        stdscr.clear()
        stdscr.refresh()
        signal.signal(signal.SIGINT, def_handler)

        # Título
        stdscr.addstr(1, 2, "Herramienta de Análisis CAN Bus", curses.A_BOLD)
        
        # Imprimir el menú
        for i, item in enumerate(menu_items):
            if i == option:
                stdscr.addstr(current_row, 2, item, COLOR_CYAN_BLACK)
            else:
                stdscr.addstr(current_row, 2, item, COLOR_YELLOW_BLACK)
            current_row += 1
        
        current_row = 3  # Restablecer la posición de la fila actual
        
        # Leer entrada del usuario
        key = stdscr.getch()
        
        # Lógica del menú
        if key == curses.KEY_UP and option > 0:
            option -= 1

        elif key == curses.KEY_DOWN and option < len(menu_items) - 1:
            option += 1

        elif key == ord('\n'):  # Enter

            if option == 0:
            	# Ingresar en la opción "Monitorización"
                monitorizar_option = "Sí"  
                
                while True:
                    stdscr.clear()
                    stdscr.addstr(1, 2, "Monitorización de Tráfico CAN Bus", curses.A_BOLD)
                    stdscr.addstr(3, 2, "¿Deseas almacenar el tráfico?", COLOR_CYAN_BLACK)
                    stdscr.addstr(4, 2, "Seleccione una opción:", COLOR_CYAN_BLACK)
                    
                    if monitorizar_option == "Sí":
                        stdscr.addstr(5, 4, "[X] Sí", COLOR_GREEN_BLACK)
                        stdscr.addstr(6, 4, "[ ] No", COLOR_RED_BLACK)
                        
                    else: #monitorizar_option == "No":
                        stdscr.addstr(5, 4, "[ ] Sí", COLOR_GREEN_BLACK)
                        stdscr.addstr(6, 4, "[X] No", COLOR_RED_BLACK)
                        
                    stdscr.refresh()
                    
                    choice = stdscr.getch()
                    if choice == curses.KEY_UP or choice == curses.KEY_DOWN:
                        # Cambiar la selección entre "Sí" y "No"
                        if monitorizar_option == "Sí":
                            monitorizar_option = "No"
                        else:
                            monitorizar_option = "Sí"

                    elif choice == ord('\n'):  # Confirmar la selección
                        if monitorizar_option == "Sí":
                            # Lógica para almacenar el tráfico (implementar esta parte)
                            pass
                        elif monitorizar_option == "No":
                        	# Lógica para monitorear el tráfico (implementar esta parte)
                            pass
                            
                    elif choice == 27:
                        break #Tecla Esc para volver atrás

                # Lógica para la opción 1 (Monitorización)
                # Implementar la funcionalidad
            elif option == 1:
                # Lógica para la opción 2 (Inyectar Payload)
                pass  # Implementar la funcionalidad
            elif option == 2:
                # Lógica para la opción 3 (Modificar Payload)
                pass  # Implementar la funcionalidad
            elif option == 3:
                break  # Salir
        
        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
