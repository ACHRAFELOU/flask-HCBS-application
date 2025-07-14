import serial
import serial
import csv
import os
from datetime import datetime
serial_port = 'COM3'
ser = serial.Serial(serial_port, 9600)
if __name__ == "__main__":
 while 1:
         line = ser.readline().decode('utf-8')
         line=line.split(',')
         print(line)

         if len(line) >= 2:
             line[-1] = line[-1].strip()
             print(line[2])


