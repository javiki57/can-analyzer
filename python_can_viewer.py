#!/usr/bin/python
# coding: utf-8

import argparse
import can
import curses
import os
import six
import struct
import sys
import csv

from curses.ascii import ESC as KEY_ESC, SP as KEY_SPACE
from typing import Dict, List, Tuple, Union

__version__ = '0.2.0'

# CANopen function codes
CANOPEN_NMT = 0x000
CANOPEN_SYNC_EMCY = 0x080
CANOPEN_TIME = 0x100
CANOPEN_TPDO1 = 0x180
CANOPEN_RPDO1 = 0x200
CANOPEN_TPDO2 = 0x280
CANOPEN_RPDO2 = 0x300
CANOPEN_TPDO3 = 0x380
CANOPEN_RPDO3 = 0x400
CANOPEN_TPDO4 = 0x480
CANOPEN_RPDO4 = 0x500
CANOPEN_SDO_TX = 0x580
CANOPEN_SDO_RX = 0x600
CANOPEN_HEARTBEAT = 0x700
CANOPEN_LSS_TX = 0x7E4
CANOPEN_LSS_RX = 0x7E5

# Mask for extracting the CANopen function code
CANOPEN_FUNCTION_CODE_MASK = 0x780

# Mask for extracting the CANopen node ID
CANOPEN_NODE_ID_MASK = 0x07F

# CANopen function codes, all the messages except the TPDOx and RPDOx message have a fixed length according to the
# specs,  so this is checked as well in order to varify that it is indeed a CANopen message
canopen_function_codes = {
    CANOPEN_NMT:        {2: 'NMT'},        # Network management (NMT) node control. The node id should not be added to this value
    CANOPEN_SYNC_EMCY:  {0: 'SYNC',        # Synchronization (SYNC) protocol. The node id should not be added to this value
                         8: 'EMCY'},       # Emergency (EMCY) protocol
    CANOPEN_TIME:       {6: 'TIME'},       # Time (TIME) protocol. The node id should not be added to this value
    CANOPEN_TPDO1:          'TPDO1',       # 1. Transmit Process Data Object (PDO)
    CANOPEN_RPDO1:          'RPDO1',       # 1. Receive Process Data Object (PDO)
    CANOPEN_TPDO2:          'TPDO2',       # 2. Transmit Process Data Object (PDO)
    CANOPEN_RPDO2:          'RPDO2',       # 2. Receive Process Data Object (PDO)
    CANOPEN_TPDO3:          'TPDO3',       # 3. Transmit Process Data Object (PDO)
    CANOPEN_RPDO3:          'RPDO3',       # 3. Receive Process Data Object (PDO)
    CANOPEN_TPDO4:          'TPDO4',       # 4. Transmit Process Data Object (PDO)
    CANOPEN_RPDO4:          'RPDO4',       # 4. Receive Process Data Object (PDO)
    CANOPEN_SDO_TX:     {8: 'SDO_TX'},     # Synchronization Object (SYNC) transmit
    CANOPEN_SDO_RX:     {8: 'SDO_RX'},     # Synchronization Object (SYNC) receive
    CANOPEN_HEARTBEAT:  {1: 'HEARTBEAT'},  # Network management (NMT) node monitoring
    CANOPEN_LSS_TX:     {8: 'LSS_TX'},     # Layer Setting Services (LSS) transmit
    CANOPEN_LSS_RX:     {8: 'LSS_RX'},     # Layer Setting Services (LSS) receive
}


class CanViewer:

    def __init__(self, stdscr, bus, ignore_canopen, output_file, testing=False):
        self.stdscr = stdscr
        self.bus = bus
        self.ignore_canopen = ignore_canopen
        self.output_file = output_file
        self.data_rows = []  # Lista para almacenar las filas de datos capturados

        # Initialise the ID dictionary, start timestamp, scroll and variable for pausing the viewer
        self.ids = {}
        self.start_time = None
        self.scroll = 0
        self.paused = False

        # Get the window dimensions - used for resizing the window
        self.y, self.x = self.stdscr.getmaxyx()

        # Do not wait for key inputs and disable the cursor
        self.stdscr.nodelay(True)
        curses.curs_set(0)

        if not testing:  # pragma: no cover
            self.run()

    def run(self):
        # Clear the terminal and draw the header
        self.draw_header()

        while 1:
            # Do not read the CAN-Bus when in paused mode
            if not self.paused:
                # Read the CAN-Bus and draw it in the terminal window
                msg = self.bus.recv(timeout=0)
                if msg is not None:
                    self.draw_can_bus_message(msg)


            if self.output_file:
                self.save_data_to_file()

            # Read the terminal input
            key = self.stdscr.getch()

            # Stop program if the user presses ESC or 'q'
            if key == KEY_ESC or key == ord('q'):
                break

            # Clear by pressing 'c'
            elif key == ord('c'):
                self.ids = {}
                self.start_time = None
                self.scroll = 0
                self.draw_header()

            # Pause by pressing space
            elif key == KEY_SPACE:
                self.paused = not self.paused

            # Scroll by pressing up/down
            elif key == curses.KEY_UP:
                # Limit scrolling, so the user do not scroll passed the header
                if self.scroll > 0:
                    self.scroll -= 1
                    self.redraw_screen()
            elif key == curses.KEY_DOWN:
                # Limit scrolling, so the maximum scrolling position is one below the last line
                if self.scroll <= len(self.ids) - self.y + 1:
                    self.scroll += 1
                    self.redraw_screen()

            # Check if screen was resized
            resized = curses.is_term_resized(self.y, self.x)
            if resized is True:
                self.y, self.x = self.stdscr.getmaxyx()
                if hasattr(curses, 'resizeterm'):  # pragma: no cover
                    curses.resizeterm(self.y, self.x)
                self.redraw_screen()

        # Shutdown the CAN-Bus interface
        self.bus.shutdown()



    def save_data_to_file(self):

        with open(self.output_file, 'w') as file:
            # Escribir encabezados en el archivo
            file.write("Conteo,Tiempo,Frecuencia,ID,Tam,Datos,Funcion,IDNodo\n")

            for key in self.ids.keys():
                msg = self.ids[key]['msg']

                # Format the message data as a string
                data_string = ' '.join('{:02X}'.format(x) for x in msg.data)
        
                # Format the arbitration ID as a hexadecimal value
                arbitration_id_string = '{0:0{1}X}'.format(msg.arbitration_id, 8 if msg.is_extended_id else 3)


                # Construir la fila de datos en formato CSV
                row = f"{self.ids[key]['count']},{msg.timestamp - self.start_time:.6f},{self.ids[key]['dt']:.6f},{arbitration_id_string},{msg.dlc},{data_string},"

                canopen_function_code_string, canopen_node_id_string = self.parse_canopen_message(msg)
                row += f"{canopen_function_code_string},{canopen_node_id_string}"

                # Agregar la fila a la lista de datos
                self.data_rows.append(row)

            # Escribir todas las filas de datos en el archivo
            file.write('\n'.join(self.data_rows))



    # Convert it into raw integer values and then pack the data
    @staticmethod
    def pack_data(cmd, cmd_to_struct, *args):  # type: (int, Dict, Union[*float, *int]) -> bytes
        if not cmd_to_struct or len(args) == 0:
            # If no arguments are given, then the message does not contain a data package
            return b''

        for key in cmd_to_struct.keys():
            if cmd == key if isinstance(key, int) else cmd in key:
                value = cmd_to_struct[key]
                if isinstance(value, tuple):
                    # The struct is given as the fist argument
                    struct_t = value[0]  # type: struct.Struct

                    # The conversion from SI-units to raw values are given in the rest of the tuple
                    fmt = struct_t.format
                    if isinstance(fmt, six.string_types):  # pragma: no cover
                        # Needed for Python 3.7
                        fmt = six.b(fmt)

                    # Make sure the endian is given as the first argument
                    assert six.byte2int(fmt) == ord('<') or six.byte2int(fmt) == ord('>')

                    # Disable rounding if the format is a float
                    data = []
                    for c, arg, val in zip(six.iterbytes(fmt[1:]), args, value[1:]):
                        if c == ord('f'):
                            data.append(arg * val)
                        else:
                            data.append(round(arg * val))
                else:
                    # No conversion from SI-units is needed
                    struct_t = value  # type: struct.Struct
                    data = args

                return struct_t.pack(*data)
        else:
            raise ValueError('Unknown command: 0x{:02X}'.format(cmd))

    # Unpack the data and then convert it into SI-units
    @staticmethod
    def unpack_data(cmd, cmd_to_struct, data):  # type: (int, Dict, bytes) -> List[Union[float, int]]
        if not cmd_to_struct or len(data) == 0:
            # These messages do not contain a data package
            return []

        for key in cmd_to_struct.keys():
            if cmd == key if isinstance(key, int) else cmd in key:
                value = cmd_to_struct[key]
                if isinstance(value, tuple):
                    # The struct is given as the fist argument
                    struct_t = value[0]  # type: struct.Struct

                    # The conversion from raw values to SI-units are given in the rest of the tuple
                    values = [d // val if isinstance(val, int) else float(d) / val
                              for d, val in zip(struct_t.unpack(data), value[1:])]
                else:
                    # No conversion from SI-units is needed
                    struct_t = value  # type: struct.Struct
                    values = list(struct_t.unpack(data))

                return values
        else:
            raise ValueError('Unknown command: 0x{:02X}'.format(cmd))

    @staticmethod
    def parse_canopen_message(msg):
        canopen_function_code_string, canopen_node_id_string = None, None

        if not msg.is_extended_id:
            canopen_function_code = msg.arbitration_id & CANOPEN_FUNCTION_CODE_MASK
            if canopen_function_code in canopen_function_codes:
                canopen_node_id = msg.arbitration_id & CANOPEN_NODE_ID_MASK

            # The SYNC and EMCY uses the same function code, so determine which message it is by checking both the
            # node ID and message length
                if canopen_function_code == 0x080:
                    # Check if the length is valid
                    if msg.dlc in canopen_function_codes[canopen_function_code]:
                        # Make sure the length and node ID combination is valid
                        if (msg.dlc == 0 and canopen_node_id == 0) or (msg.dlc == 8 and 1 <= canopen_node_id <= 127):
                            canopen_function_code_string = canopen_function_codes[canopen_function_code][msg.dlc]
                elif (canopen_function_code == 0x000 or canopen_function_code == 0x100) and \
                        (canopen_node_id != 0 or msg.dlc not in canopen_function_codes[canopen_function_code]):
                    # It is not a CANopen message, as the node ID is not added to these commands
                    canopen_function_code_string = None
                else:
                    if isinstance(canopen_function_codes[canopen_function_code], dict):
                        # Make sure the message has the defined length
                        if msg.dlc in canopen_function_codes[canopen_function_code]:
                            canopen_function_code_string = canopen_function_codes[canopen_function_code][msg.dlc]
                    # These IDs do not have a fixed length
                    else:
                        # Make sure the node ID is valid
                        if 1 <= canopen_node_id <= 127:
                            canopen_function_code_string = canopen_function_codes[canopen_function_code]
    
                # Now determine set the node ID string
                if canopen_function_code_string:
                    canopen_node_id_string = str(canopen_node_id)

        return canopen_function_code_string, canopen_node_id_string

    def draw_can_bus_message(self, msg, sorting=False):
        # Use the CAN-Bus ID as the key in the dict
        key = msg.arbitration_id

        # Sort the extended IDs at the bottom by setting the 32-bit high
        if msg.is_extended_id:
            key |= (1 << 32)

        new_id_added, length_changed = False, False
        if not sorting:
            # Check if it is a new message or if the length is not the same
            if key not in self.ids:
                new_id_added = True
                # Set the start time when the first message has been received
                if not self.start_time:
                    self.start_time = msg.timestamp
            elif msg.dlc != self.ids[key]['msg'].dlc:
                length_changed = True

            if new_id_added or length_changed:
                # Increment the index if it was just added, but keep it if the length just changed
                row = len(self.ids) + 1 if new_id_added else self.ids[key]['row']

                # It's a new message ID or the length has changed, so add it to the dict
                # The first index is the row index, the second is the frame counter,
                # the third is a copy of the CAN-Bus frame
                # and the forth index is the time since the previous message
                self.ids[key] = {'row': row, 'count': 0, 'msg': msg, 'dt': 0}
            else:
                # Calculate the time since the last message and save the timestamp
                self.ids[key]['dt'] = msg.timestamp - self.ids[key]['msg'].timestamp

                # Copy the CAN-Bus frame - this is used for sorting
                self.ids[key]['msg'] = msg

            # Increment frame counter
            self.ids[key]['count'] += 1

        # Sort frames based on the CAN-Bus ID if a new frame was added
        if new_id_added:
            self.draw_header()
            for i, key in enumerate(sorted(self.ids.keys())):
                # Set the new row index, but skip the header
                self.ids[key]['row'] = i + 1

                # Do a recursive call, so the frames are repositioned
                self.draw_can_bus_message(self.ids[key]['msg'], sorting=True)
        else:
            # Format the CAN-Bus ID as a hex value
            arbitration_id_string = '{0:0{1}X}'.format(msg.arbitration_id, 8 if msg.is_extended_id else 3)

            # Generate data string
            data_string = ''
            if msg.dlc > 0:
                data_string = ' '.join('{:02X}'.format(x) for x in msg.data)

            # Check if is a CANopen message
            if self.ignore_canopen:
                canopen_function_code_string, canopen_node_id_string = None, None
            else:
                canopen_function_code_string, canopen_node_id_string = self.parse_canopen_message(msg)

            # Now draw the CAN-Bus message on the terminal window
            self.draw_line(self.ids[key]['row'], 0, str(self.ids[key]['count']))
            self.draw_line(self.ids[key]['row'], 8, '{0:.6f}'.format(self.ids[key]['msg'].timestamp - self.start_time))
            self.draw_line(self.ids[key]['row'], 23, '{0:.6f}'.format(self.ids[key]['dt']))
            self.draw_line(self.ids[key]['row'], 35, arbitration_id_string)
            self.draw_line(self.ids[key]['row'], 44, str(msg.dlc))
            self.draw_line(self.ids[key]['row'], 52, data_string)
            if canopen_function_code_string:
                self.draw_line(self.ids[key]['row'], 78, canopen_function_code_string)
            if canopen_node_id_string:
                self.draw_line(self.ids[key]['row'], 88, canopen_node_id_string)
        return self.ids[key]

    def draw_line(self, row, col, txt, *args):
        if row - self.scroll < 0:
            # Skip if we have scrolled passed the line
            return
        try:
            self.stdscr.addstr(row - self.scroll, col, txt, *args)
        except curses.error:
            # Ignore if we are trying to write outside the window
            # This happens if the terminal window is too small
            pass

    def draw_header(self):
        self.stdscr.clear()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.draw_line(0, 0, 'Conteo', curses.color_pair(1))
        self.draw_line(0, 9, 'Tiempo', curses.color_pair(1))
        self.draw_line(0, 22, 'Frecuencia', curses.color_pair(1))
        self.draw_line(0, 35, 'ID', curses.color_pair(1))
        self.draw_line(0, 43, 'Tam', curses.color_pair(1))
        self.draw_line(0, 52, 'Datos', curses.color_pair(1))
        self.draw_line(0, 77, 'Función', curses.color_pair(1))
        self.draw_line(0, 87, 'ID Nodo', curses.color_pair(1))

    def redraw_screen(self):
        # Trigger a complete redraw
        self.draw_header()
        for key in self.ids.keys():
            self.draw_can_bus_message(self.ids[key]['msg'])


# noinspection PyUnresolvedReferences,PyProtectedMember,PyMethodMayBeStatic,PyUnusedLocal
class SmartFormatter(argparse.HelpFormatter):  # pragma: no cover

    def _get_default_metavar_for_optional(self, action):
        return action.dest.upper()

    def _format_usage(self, usage, actions, groups, prefix):
        # Use uppercase for "Usage:" text
        return argparse.HelpFormatter._format_usage(self, usage, actions, groups, 'Usage: ')

    def _format_args(self, action, default_metavar):
        if action.nargs != argparse.REMAINDER and action.nargs != argparse.ONE_OR_MORE:
            return argparse.HelpFormatter._format_args(self, action, default_metavar)

        # Use the metavar if "REMAINDER" or "ONE_OR_MORE" is set
        get_metavar = self._metavar_formatter(action, default_metavar)
        return '%s' % get_metavar(1)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return argparse.HelpFormatter._format_action_invocation(self, action)

        # Modified so "-s ARGS, --long ARGS" is replaced with "-s, --long ARGS"
        else:
            parts = []
            default = self._get_default_metavar_for_optional(action)
            args_string = self._format_args(action, default)
            for i, option_string in enumerate(action.option_strings):
                if i == len(action.option_strings) - 1:
                    parts.append('%s %s' % (option_string, args_string))
                else:
                    parts.append('%s' % option_string)
            return ', '.join(parts)

    def _split_lines(self, text, width):
        # Allow to manually split the lines
        if text.startswith('R|'):
            return text[2:].splitlines()
        return argparse.HelpFormatter._split_lines(self, text, width)


def parse_args(args):
    # Python versions >= 3.5
    kwargs = {}
    if sys.version_info[0] * 10 + sys.version_info[1] >= 35:  # pragma: no cover
        kwargs = {'allow_abbrev': False}

    # Parse command line arguments
    parser = argparse.ArgumentParser('python -m python_can_viewer',
                                     description='A simple CAN viewer terminal application written in Python',
                                     formatter_class=SmartFormatter, add_help=False, **kwargs)

    optional = parser.add_argument_group('Optional arguments')


    optional.add_argument('-c', '--channel', help='''Most backend interfaces require some sort of channel.
                          for example with the serial interface the channel might be a rfcomm device: "/dev/rfcomm0"
                          with the socketcan interfaces valid channel examples include: "can0", "vcan0".
                          (default: use default for the specified interface)''', default=None)


    optional.add_argument('-f', '--filter', help='''R|Comma separated CAN filters for the given CAN interface: \
                          ''',
                          metavar='{<can_id>,<can_id>', nargs=argparse.ONE_OR_MORE, default='')

    optional.add_argument('-i', '--interface', dest='interface',
                          help='''R|Specify the backend CAN interface to use. (default: "socketcan")''',
                          choices=sorted(can.VALID_INTERFACES), default='socketcan')
    
    optional.add_argument('-o', '--output', help='Specify the output CSV file for storing data.', default=None)

    parsed_args = parser.parse_args(args)

    can_filters = []
    if len(parsed_args.filter) > 0:
        for flt in parsed_args.filter:
            can_id = int(flt, base=16)
            can_mask = 0x7FF  # Máscara fija en 0x7FF
            can_filters.append({'can_id': can_id, 'can_mask': can_mask})

    return parsed_args, can_filters


def main():  # pragma: no cover
    parsed_args, can_filters = parse_args(sys.argv[1:])
    
    output_file = parsed_args.output
    
    config = {}
    if can_filters:
        config['can_filters'] = can_filters
    if parsed_args.interface:
        config['interface'] = parsed_args.interface

    # Create a CAN-Bus interface
    bus = can.interface.Bus(parsed_args.channel, **config)
    # print('Connected to {}: {}'.format(bus.__class__.__name__, bus.channel_info))

    curses.wrapper(CanViewer, bus, ignore_canopen=None, output_file=parsed_args.output)


if __name__ == '__main__':  # pragma: no cover
    # Catch ctrl+c
    try:
        main()
    except KeyboardInterrupt:
        pass
