import serialhdl, serial
import sys
from serial import SerialException
import logging
import time

sys.path.insert(0, '/home/joe/Test')

import Serial_Test

class Removal:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()

        self.gcode = self.printer.lookup_object('gcode')
        self.gcode_move = self.printer.load_object(config, "gcode_move")

        self._serialport = config.get('serial')
        self._baud = config.getint('baud', 250000, minval=2400)
        self.serial = None

        self.error = "NULL"

        self.reader = serialhdl.SerialReader(self.reactor)

        self.bause_command_sent = False
        self.gcode.register_command("READ_SERIAL", self.cmd_READ_SERIAL,
                                    desc=self.cmd_READ_SERIAL_help)
        self.gcode.register_command("READ_ERROR", self.cmd_READ_ERROR,
                                    desc=self.cmd_READ_ERROR_help)
        self.gcode.register_command("RESET_ERROR", self.cmd_RESET_ERROR,
                                    desc=self.cmd_RESET_ERROR_help)
        self.gcode.register_command("ADJUSTMENTS", self.cmd_ADJUSTMENTS,
                                    desc=self.cmd_ADJUSTMENTS_help)
        
        #self.gcode.register_command('ADJUSTMENTS', self.cmd_ADJUSTMENTS)
        webhooks = self.printer.lookup_object('webhooks')
        webhooks.register_endpoint("read_serial", self._handle_read_serial_request)
        webhooks.register_endpoint("read_error", self._handle_read_error_request)
        webhooks.register_endpoint("reset_error", self._handle_reset_error_request)
        webhooks.register_endpoint("adjustments", self._handle_reset_error_request)

        self.reset_status()

    def reset_status(self):
        self.status = {
            'is_active': False,
            'a_position': None,
            'a_position_lower': None,
            'a_position_upper': None
        }
    def get_status(self, eventtime):
        return self.status
    
    def _handle_read_serial_request(self, web_request):
        self.gcode.run_script("READ_SERIAL")

    def _handle_read_error_request(self, web_request):
        self.gcode.run_script("READ_ERROR")

    def _handle_reset_error_request(self, web_request):
        self.gcode.run_script("RESET_ERROR")
    
    cmd_READ_SERIAL_help = ("Sending Serial Command")   
    def cmd_READ_SERIAL(self, gcmd):
        gcmd.respond_info("Connecting Serial Command")
        #reader = serialhdl.SerialReader(self,self.reactor)
        #reader.connect_uart(self,self._serialport,self._baud)
        if self.serial:
            gcmd.respond_info("Serial port is already active, disconnect first")
            return
        gcmd.respond_info(("Connecting to serial on port (%s) at (%s)" %
                     (self._serialport, self._baud)))
        com = serial.Serial(port=self._serialport, baudrate=self._baud, timeout=.1)
        #Serial is now connected
        if com.is_open == True:
            while True:
                gcmd.respond_info("Serial port connected")
                data = Serial_Test.write_read(com,"a")
                #gcmd.respond_info(str(data))

                ##TODO:ADD Emergency button. Sends 's'
                while data != b'\n1\r':
                    data = Serial_Test.read(com)
                    #if 
                    #gcmd.respond_info("1")
                if data == b'\n1\r':
                    gcmd.respond_info("Bed is Clean! Continue Printing!")
                break
    
    cmd_READ_ERROR_help = ("Sending Error Types")   
    def cmd_READ_ERROR(self, gcmd):
        #For testing only 
        gcmd.respond_info("Getting Error Types from file")
        #Open file & read it, 
        f = open("/home/joe/Test/readme.txt", "r")
        error = f.read()
        #For testing, Sends over contents of file, Could be useful for telling user error type in prompt
        gcmd.respond_info(error)
        if error != "No Errors" and error != "Ready":
            #self.gcode.run_script_from_command("UPDATE_DELAYED_GCODE ID=error_check DURATION=0")
            if error != "Detected":
                self.error = error
                file_create = open("/home/joe/Test/readme.txt", "w")
                file_create.write("Detected")
                file_create.close()
                #self.gcode.run_script_from_command("ERROR_DETECTED_PROMPT")
                self.gcode.run_script_from_command(
                    "PAUSE\n"
                    "G4 S1\n"
                    "ERROR_DETECTED_PROMPT")

            gcmd.respond_info("error")
            # self.gcode.run_script_from_command(
            #     "UPDATE_DELAYED_GCODE ID=error_check DURATION=0\n"
            #     "ERROR_DETECTED_PROMPT\n"
            #     "UPDATE_DELAYED_GCODE ID=error_check DURATION=0")
            
            #gcmd.respond_info("UPDATE_DELAYED_GCODE ID=error_check DURATION=0")

            #self.gcode.run_script_from_command("UPDATE_DELAYED_GCODE ID=error_check DURATION=0")
            #self.gcode
        # if error == "stringing":
        #     f
        # elif error == "under extrusion":
        #     f
        # elif error == "warping":
        #     f
        
        # self.gcode.run_script_from_command("ADJUSTMENTS")
        #return error
    cmd_RESET_ERROR_help = ("Reset Error Types")   
    def cmd_RESET_ERROR(self, gcmd):
        file_create = open("/home/joe/Test/readme.txt", "w")
        file_create.write("Ready")
        file_create.close()

    cmd_ADJUSTMENTS_help = ("Fix Error Types")   
    def cmd_ADJUSTMENTS(self, gcmd):
        if self.error == "spagehtti":
            self.gcode.run_script_from_command("SPAGHETTI_CHECK")
        elif self.error == "stringing":
            self.gcode.run_script_from_command("STRINGING_CHECK")
        elif self.error == "under extrusion":
            self.gcode.run_script_from_command("UNDER_EXTRUSION_CHECK")
        elif self.error == "warping":
            self.gcode.run_script_from_command("WARPING_CHECK")
        else:
            gcmd.respond_info(self.error)
            


class RemovalHelper:
    def __init__(self, printer, serial, gcmd, finalize_callback):
        self.serial = serial
        self.printer = printer
        self.finalize_callback = finalize_callback
        self.gcode = self.printer.lookup_object('gcode')
        self.toolhead = self.printer.lookup_object('toolhead')
        self.speed = gcmd.get_float("SPEED", 5.)
        self.report_a_status()
        

    # def move_a(self, z_pos):
    #     curpos = self.toolhead.get_position()
    #     try:
    #         z_bob_pos = z_pos + Z_BOB_MINIMUM
    #         if curpos[2] < z_bob_pos:
    #             self.toolhead.manual_move([None, None, z_bob_pos], self.speed)
    #         self.toolhead.manual_move([None, None, z_pos], self.speed)
    #     except self.printer.command_error as e:
    #         self.finalize(False)
    #         raise

def load_config(config):
    return Removal(config)


# def load_config(config):
#     return Alert(config)


# self.reader.connect_uart(self._serialport,self._baud)

        # gcmd.respond_info("Send to Serial Port")

        # self.reader.send(b"1")

        # gcmd.respond_info("Disconnecting from Serial Port")

        # self.reader.disconnect(self)
        
        # self.signal_disconnect = False

        # logging.info("Connecting to Serial on port (%s) at (%s)" %
        #              (self._serialport, self._baud))
        

                # Do non-blocking reads from serial and try to find lines
        # while True:
        #     try:
        #         raw_bytes = self.serial.read()
        #     except SerialException:
        #         logging.error("Unable to communicate with the Palette 2")
        #         self.serial.close()
        #         return 
        #     if len(raw_bytes):
        #         new_buffer = str(raw_bytes.decode(encoding='UTF-8',
        #                                           errors='ignore'))
        #         text_buffer = self.read_buffer + new_buffer
        #         while True:
        #             i = text_buffer.find("\n")
        #             if i >= 0:
        #                 line = text_buffer[0:i + 1]

        #                 text_buffer = text_buffer[i + 1:]
        #             else:
        #                 break
        #         self.read_buffer = text_buffer
        #     else:
        #         break


        # arduino = serial.Serial(port=self._serialport, baudrate=self._baud, timeout=.1)
        # arduino.write(b'1')
        # time.sleep(0.1)
        # data = arduino.readline()
        # gcmd.respond_info(str(data))
        # arduino.close()


        # #self._serialport.connect_uart(self._serialport, self._baud, rts)
        # SerialObj = serial.Serial(self._serialport) # COMxx  format on Windows
        #           # ttyUSBx format on Linux
        # SerialObj.baudrate = self._baud  # set Baud rate to 9600
        # SerialObj.bytesize = 8   # Number of data bits = 8
        # SerialObj.parity  ='N'   # No parity
        # SerialObj.stopbits = 1   # Number of Stop bits = 1
        # line = SerialObj.readline()   # read a '\n' terminated line
        # gcmd.respond_info(line)
        #print(line)
        # SerialObj.write(b'A')    #transmit 'A' (8bit) to micro/Arduino
        # SerialObj.close()      # Close the port

        
        #self.gcode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE_STATE")
        # self.is_paused = True
 
