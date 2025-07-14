import serial
import cv2

serial_port = 'COM3'
ser = serial.Serial(serial_port, 9600)

n = 225
pix = [[0] * n for p in range(n)]

if __name__ == "__main__":
    while 1:
        line = ser.readline().decode('utf-8')
        line = line.split(',')
        if len(line) >= 32:
            line = [x.strip() for x in line]
            for i in range(32):
                pix[i] = line[i]
                pix[i + 32] = line[i]
                pix[i + 64] = line[i]

        print(pix[1])
               # print(pix[32])
              #  print(pix[64])

