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
                  "2. Inyectar archivo",
                  "3. Inyectar trama",
                  "4. Modificar archivo",
                  "5. Modificar trama",
                  "6. Salir"]
    
    current_row = 4
    option = 0
    ruta_archivo = ""
    
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
            current_row += 2
        
        current_row = 4  # Restablecer la posición de la fila actual
        
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
                    stdscr.addstr(4, 2, "¿Deseas almacenar el tráfico?", COLOR_CYAN_BLACK)
                    stdscr.addstr(6, 2, "Seleccione una opción:", COLOR_CYAN_BLACK)
                    
                    if monitorizar_option == "Sí":
                        stdscr.addstr(8, 4, "[X] Sí", COLOR_GREEN_BLACK)
                        stdscr.addstr(9, 4, "[ ] No", COLOR_RED_BLACK)
                        
                    else: #monitorizar_option == "No":
                        stdscr.addstr(8, 4, "[ ] Sí", COLOR_GREEN_BLACK)
                        stdscr.addstr(9, 4, "[X] No", COLOR_RED_BLACK)
                        
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

                # Ingresar en la opción "Inyectar Payload"
                stdscr.clear()
                stdscr.addstr(1, 2, "Inyectar Payload en la red CAN Bus", curses.A_BOLD)
                stdscr.addstr(4, 2, "Indica la ruta absoluta del archivo que deseas inyectar en la red:", COLOR_CYAN_BLACK)
                stdscr.addstr(6, 2, "Ruta del archivo:", COLOR_CYAN_BLACK)
                stdscr.addstr(7, 2, ruta_archivo)
                stdscr.refresh()
                curses.curs_set(1)  # Mostrar el cursor para ingresar la ruta del archivo
                
                
                while True:
                    ch = stdscr.getch()

                    if ch == 27:  # Tecla 'Esc' para volver al menú principal
                        curses.curs_set(0)  # Ocultar el cursor
                        break

                    elif ch == 10:  # Tecla 'Enter' para confirmar la ruta del archivo
                        # Aquí se almacena la ruta del archivo en la variable y procesarla
                        stdscr.addstr(9, 2, "Ruta almacenada:", COLOR_YELLOW_BLACK)
                        stdscr.addstr(10, 2, ruta_archivo)
                        stdscr.refresh()

                    elif ch == 8:  # Tecla 'Backspace' para borrar caracteres
                        ruta_archivo = ruta_archivo[:-1]

                    elif ch == curses.KEY_BACKSPACE:
                        if ruta_archivo:
                            ruta_archivo = ruta_archivo[:-1]
                            stdscr.move(7, 2)  # Mover el cursor a la posición correcta
                            stdscr.clrtoeol()  # Borrar la línea actual desde la posición del cursor
                            stdscr.addstr(7, 2, ruta_archivo)  # Actualizar visualmente la ruta


                    elif 0 <= ch <= 255:
                        ruta_archivo += chr(ch)
                        stdscr.addstr(7, 2, ruta_archivo)
                        stdscr.refresh()

                # Lógica para la opción 2 (Inyectar Payload)
                # pass   Implementar la funcionalidad
            elif option == 2:
                # Lógica para la opción 3 (Modificar Payload)
                pass  # Implementar la funcionalidad

            elif option == 3:
            	pass # Implementar funcionalidad

            elif option == 4:
                pass

            elif option == 5:
            	break
        
        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
