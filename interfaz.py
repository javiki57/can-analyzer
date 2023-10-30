import sys
import curses
import signal
import database
import subprocess
import os

def def_handler(sig, frame):
    sys.exit(1)

def stop_execution_handler(signal, frame):
    global stop_execution
    stop_execution = True

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
    atras = False
    stop_execution = False

    signal.signal(signal.SIGINT, def_handler)
    signal.signal(signal.SIGQUIT, stop_execution_handler)

    while True:
        stdscr.clear()
        stdscr.refresh()
        

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
                interfaz = "vcan0"
                filtrar_ids = False
                
                while True:
                    stdscr.clear()
                    stdscr.addstr(1, 2, "Monitorización de Tráfico CAN Bus", curses.A_BOLD)
                    stdscr.addstr(4, 2, "¿Deseas almacenar el tráfico en un archivo?", COLOR_CYAN_BLACK)
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

                        stdscr.clear()
                        stdscr.addstr(1, 2, "Monitorización de Tráfico CAN Bus", curses.A_BOLD)
                        stdscr.addstr(4, 2, "¿Qué interfaz vas a utilizar? (Por defecto vcan0):", COLOR_CYAN_BLACK)
                        stdscr.addstr(5, 2, "Interfaz:", COLOR_CYAN_BLACK)
                        curses.curs_set(1)
                        interfaz_input = ""
                        atras = False

                        while True:
                            ch = stdscr.getch()
                            if ch == 27:  # Tecla 'Esc' para volver al menú principal
                                curses.curs_set(0)  # Ocultar el cursor
                                atras = True
                                break
                
                            elif ch == 10:  # Tecla 'Enter' para confirmar la interfaz
                                interfaz = interfaz_input.strip() or "vcan0"  # Usar vcan0 si no se especifica otra interfaz
                                #stdscr.addstr(7, 2, "Interfaz seleccionada:", COLOR_YELLOW_BLACK)
                                #stdscr.addstr(8, 2, interfaz)
                                #stdscr.refresh()
                                curses.curs_set(0)  # Ocultar el cursor
                                break

                            elif ch == curses.KEY_BACKSPACE:  # Tecla 'Backspace' para borrar caracteres
                                interfaz_input = interfaz_input[:-1]
                                stdscr.move(4, 12)  # Mover el cursor a la posición correcta
                                stdscr.clrtoeol()  # Borrar la línea actual desde la posición del cursor
                                stdscr.addstr(4, 12, interfaz_input)  # Actualizar visualmente la interfaz
            
                            elif 0 <= ch <= 255:
                                interfaz_input += chr(ch)
                                stdscr.addstr(4, 12, interfaz_input)
                                stdscr.refresh()

                        if monitorizar_option == "Sí" and (atras == False):
                            stdscr.clear()
                            stdscr.addstr(1, 2, "Monitorización de Tráfico CAN Bus", curses.A_BOLD)
                            stdscr.addstr(4, 2, "Introduce el nombre del archivo CSV para guardar las tramas:", COLOR_CYAN_BLACK)
                            stdscr.addstr(6, 2, "Nombre del archivo:", COLOR_CYAN_BLACK)
                            stdscr.addstr(7, 2, ruta_archivo)
                            stdscr.refresh()
                            curses.curs_set(1)  # Mostrar el cursor para ingresar el nombre del archivo            
                            atras = False

                            while True:
                                ch = stdscr.getch()
    
                                if ch == 27:  # Tecla 'Esc' para volver al menú principal
                                    curses.curs_set(0)  # Ocultar el cursor
                                    atras = True
                                    break

                                elif ch == 10:  # Tecla 'Enter' para confirmar el nombre del archivo
                                    # Aquí se almacena el nombre del archivo y se comienza a capturar tramas
                                    nombre_archivo = ruta_archivo.strip() + ".csv"
                                    curses.curs_set(0)  # Ocultar el cursor
                                    break

                                elif ch == curses.KEY_BACKSPACE:  # Tecla 'Backspace' para borrar caracteres
                                    ruta_archivo = ruta_archivo[:-1]
                                    stdscr.move(7, 2)  # Mover el cursor a la posición correcta
                                    stdscr.clrtoeol()  # Borrar la línea actual desde la posición del cursor
                                    stdscr.addstr(7, 2, ruta_archivo)  # Actualizar visualmente la ruta

                                elif 0 <= ch <= 255:
                                    ruta_archivo += chr(ch)
                                    stdscr.addstr(7, 2, ruta_archivo)
                                    stdscr.refresh()

                        

                        if atras == False:
                            stdscr.clear()
                            stdscr.addstr(1, 2, "Monitorización de Tráfico CAN Bus", curses.A_BOLD)
                            stdscr.addstr(4, 2, "¿Deseas filtrar por IDs? ", COLOR_CYAN_BLACK)
                
                            filtrar_ids_option = "No" # Valor predeterminado
                            atras = False

                            while True:
                                if filtrar_ids_option == "Sí":
                                    stdscr.addstr(6, 4, "[X] Sí", COLOR_GREEN_BLACK)
                                    stdscr.addstr(7, 4, "[ ] No", COLOR_RED_BLACK)
                                else:
                                    stdscr.addstr(6, 4, "[ ] Sí", COLOR_GREEN_BLACK)
                                    stdscr.addstr(7, 4, "[X] No", COLOR_RED_BLACK)
                
                                stdscr.refresh()
        
                                choice = stdscr.getch()
                                if choice == curses.KEY_UP or choice == curses.KEY_DOWN:
                                    # Cambiar la selección entre "Sí" y "No"
                                    filtrar_ids_option = "No" if filtrar_ids_option == "Sí" else "Sí"
        
                                elif choice == ord('\n'):  # Confirmar la selección
                                    if filtrar_ids_option == "Sí":
                                        filtrar_ids = True
                                    break

                                elif choice == 27:  # Tecla 'Esc' para volver al menú principal
                                    atras = True
                                    break

                            if atras == False:
                                # Ejecutar python_can_viewer.py con los parámetros
                                stdscr.clear()
                                stdscr.refresh()

                                try:
                                    command = ["python3", "python_can_viewer.py"]

                                    if interfaz:
                                       command += ["-c", interfaz]
            
                                    if filtrar_ids:
                                        # Preguntar por los IDs a filtrar
                                        stdscr.clear()
                                        stdscr.addstr(1, 2, "Monitorización de Tráfico CAN Bus", curses.A_BOLD)
                                        stdscr.addstr(4, 2, "Introduce los IDs a filtrar (separados por comas):", COLOR_CYAN_BLACK)
                            
                                        curses.curs_set(1)  # Mostrar el cursor para ingresar los IDs
                                        ids_input = ""

                                        while True:
                                            ch = stdscr.getch()
                                    
                                            if ch == 27:  # Tecla 'Esc' para volver al menú principal
                                                curses.curs_set(0)  # Ocultar el cursor
                                                atras = True
                                                break

                                            elif ch == 10:  # Tecla 'Enter' para confirmar los IDs
                                                ids = ids_input.strip()
                                                ids_filter = ids.split(',')
                                                if ids:
                                                    command += ["-f"]
                                                    for id in ids_filter:
                                                        command.extend([id])
                                                
                                                stdscr.refresh()
                                                curses.curs_set(0)  # Ocultar el cursor
                                        
                                            elif ch == curses.KEY_BACKSPACE:  # Tecla 'Backspace' para borrar caracteres
                                                ids_input = ids_input[:-1]
                                                stdscr.move(6, 2)  # Mover el cursor a la posición correcta
                                                stdscr.clrtoeol()  # Borrar la línea actual desde la posición del cursor
                                                stdscr.addstr(6, 2, ids_input)  # Actualizar visualmente los IDs
                                            elif 0 <= ch <= 255:
                                                ids_input += chr(ch)
                                                stdscr.addstr(6, 2, ids_input)
                                                stdscr.refresh()
                                    
                                    try:
                                        if (monitorizar_option == "Sí"):
                                            
                                            #stdscr.refresh()
                                            #curses.curs_set(0)  # Ocultar el cursor

                                            command += ["-o", nombre_archivo]

                                            # Ejecutar el comando
                                            subprocess.run(command, check=True)

                                            #Añadir el contenido del csv a la base de datos
                                            db = ["python3", "database.py", nombre_archivo]
                                            subprocess.run(db, check=True)

                                        
                                        else:
                                            subprocess.run(command, check=True)

                                    except subprocess.CalledProcessError as e:
                                        #stdscr.addstr(10, 2, f"Error al ejecutar python_can_viewer.py: {str(e)}", COLOR_RED_BLACK)
                                        stdscr.refresh()
                                        curses.curs_set(0)  # Ocultar el cursor
                                        #exit()
                                        #curses.napms(2000)  # Esperar 2 segundos antes de volver al menú principal
                                    #break


                                except Exception as e:
                                    #stdscr.addstr(9, 2, f"Error al ingresar los IDs a filtrar: {str(e)}", COLOR_RED_BLACK)
                                    stdscr.refresh()
                                    curses.curs_set(0)  # Ocultar el cursor
                                    #exit()
                                    #curses.napms(2000)  # Esperar 2 segundos antes de volver al menú principal

                        
                    elif choice == 27:
                        break #Tecla Esc para volver atrás

            elif option == 1:

                # Ingresar en la opción "Inyectar Archivo"
                stdscr.clear()
                stdscr.addstr(1, 2, "Inyectar un archivo en la red CAN Bus", curses.A_BOLD)
                stdscr.addstr(4, 2, "Indica la ruta absoluta del archivo que deseas inyectar en la red:", COLOR_CYAN_BLACK)
                current_dir = os.path.dirname(os.path.abspath(__file__))  # Obtener la ruta del directorio actual
                stdscr.addstr(6, 2, "Ruta actual del directorio: ", COLOR_CYAN_BLACK)
                stdscr.addstr(6 ,30, f"{current_dir}", COLOR_MAGENTA_BLACK)
                stdscr.addstr(8, 2, ruta_archivo)
                stdscr.refresh()
                curses.curs_set(1)  # Mostrar el cursor para ingresar la ruta del archivo
                
                
                while True:
                    ch = stdscr.getch()

                    if ch == 27:  # Tecla 'Esc' para volver al menú principal
                        curses.curs_set(0)  # Ocultar el cursor
                        break

                    elif ch == 10:  # Tecla 'Enter' para confirmar la ruta del archivo
                        # Aquí se almacena la ruta del archivo en la variable y procesarla
                        stdscr.addstr(10, 2, "Ruta almacenada:", COLOR_YELLOW_BLACK)
                        stdscr.addstr(11, 2, ruta_archivo)
                        stdscr.refresh()
                    
                    elif ch == curses.KEY_BACKSPACE:
                        if ruta_archivo:
                            ruta_archivo = ruta_archivo[:-1]
                            stdscr.move(8, 2)  # Mover el cursor a la posición correcta
                            stdscr.clrtoeol()  # Borrar la línea actual desde la posición del cursor
                            stdscr.addstr(8, 2, ruta_archivo)  # Actualizar visualmente la ruta


                    elif 0 <= ch <= 255:
                        ruta_archivo += chr(ch)
                        stdscr.addstr(8, 2, ruta_archivo)
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

        elif key == 27:  # Tecla 'Esc' 
            break
        
        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
