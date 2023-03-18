import serial
import time
import random 
import sys
import os


bin_file_path = "./logs/output.txt"
bin_f = open(bin_file_path, "rb").read()
FILE_BYTES = os.stat(bin_file_path).st_size
print("FILE_BYTES : ", FILE_BYTES)


SERIAL_PORT = f'/dev/pts/{sys.argv[1]}'
SPEED = int(sys.argv[2])


SERIAL_BAUDRATE = 115200
sp = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)


gen_count_byte = lambda : random.randrange(10, 100)

if __name__ == "__main__":
    point = 0
    while True:
        time.sleep(1 / SPEED)
        count_byte = gen_count_byte()
        print("count_byte_read", count_byte)
        print("curr_point", point)

        gets_byte = bin_f[point : point + count_byte]
        # print(gets_byte.hex())
        sp.write(gets_byte)
        point += count_byte
        if point >= FILE_BYTES:
            point = point - FILE_BYTES
        
    
        
        