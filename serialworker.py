import serial
import time
import multiprocessing
import sys
import os

import asyncio
## Change this to match your local settings
# SERIAL_PORT = f'/dev/pts/4'

# SERIAL_PORT = f'/dev/pts/{sys.argv[1]}'
SERIAL_BAUDRATE = 115200

class SerialProcess(multiprocessing.Process):
 
    def try_init_port(self):
         while True:
            time.sleep(3)
            print("try init")
            
            SERIAL_PORT = list(filter(lambda x: x.find("3") != -1, os.listdir('/dev/pts/')))

            if len(SERIAL_PORT) > 0:
                SERIAL_PORT = "/dev/pts/" + SERIAL_PORT[0]
                self.sp = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
                self.output_queue.put({
                    "type" : "ok",
                    "name" : "init_ok",
                    "msg"  : f"найденные com порты : {','.join(SERIAL_PORT)}"
                    
                })
                self.sp.flushInput()

                break
            else:
                self.output_queue.put({
                    "type" : 'err',
                    "name" : "init_err",
                    "msg"  : "не найден com port",
                    
            })
 
 
    def __init__(self, input_queue, output_queue, bin_parser):
        self.bin_parser = bin_parser
          
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.sp = None
        # self.try_init_port()

        # self.sp = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
 
    def close(self):
        self.sp.close()
 
    def writeSerial(self, data):
        self.sp.write(data)
      
    def readSerial(self):
        return self.sp.readline()
 
    def run(self):
        
        self.try_init_port()
        # if self.sp != None:
 
        while True:
            # look for incoming tornado request
            if not self.input_queue.empty():
                data = self.input_queue.get()

                # send it to the serial device
                self.writeSerial(data)
                print ("writing to serial: " + data)

            # look for incoming serial data
            if (self.sp.inWaiting() > 0):
                data = self.readSerial()
                cmd = self.bin_parser.try_get_command(data)
                

                if (cmd != None):
                    print(cmd)
                    self.output_queue.put(cmd)
                