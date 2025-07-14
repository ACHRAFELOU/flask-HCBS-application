import serial, time
import csv
import pyautogui
import pyscreeze
import matplotlib as plt
import numpy as np
import cv2
from pylab import *
serial_port = 'COM3'
ser = serial.Serial(serial_port, 9600)

n = 225
pix = [[0] * n for p in range(n)]
r = [[0] * n for p in range(n)]
g = [[0] * n for p in range(n)]
b = [[0] * n for p in range(n)]

m = 8
Name = [[0] * n for p in range(m)]

minimum = 27
maximum = 30

RealPix = 10
levelGrad1 = 0.9
levelGrad2 = 0.6
levelGrad3 = 0.9

img = np.zeros((800, 800, 3), np.uint8)
img[:] = (240, 90, 250)


def rgb(minimum, maximum, value):
    minimum, maximum, value = float(minimum), float(maximum), float(value)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b1 = int(max(0, 255 * (1 - ratio)))
    r1 = int(max(0, 255 * (ratio - 1)))
    g1 = 255 - b1 - r1
    return r1, g1, b1
if __name__ == "__main__":
   while 1:
       line = ser.readline().decode('utf-8')
       line = line.split(',')
       if len(line) >= 2:
        line[-1] = line[-1].strip()
      ## 1 Cercle rajoutés  ##
        pix[1] = float(line[0])
        pix[2] = float(line[1])
        pix[3] = float(line[2])
        pix[4] = float(line[3])
        pix[5] = float(line[4])
        pix[6] = float(line[5])
        pix[7] = float(line[6])
        pix[8] = float(line[7])
        pix[9] = float(line[8])
        pix[10] = float(line[9])
        pix[11] = float(line[10])
        pix[12] = float(line[11])
        pix[13] = float(line[12])
        pix[14] = float(line[13])
        pix[15] = float(line[14])
        pix[16] = float(line[15])
        pix[17] = float(line[16])
        pix[18] = float(line[17])
        pix[19] = float(line[18])
        pix[20] = float(line[19])
        pix[21] = float(line[20])
        pix[22] = float(line[21])
        pix[23] = float(line[22])
        pix[24] = float(line[23])
        pix[25] = float(line[24])
        pix[26] = float(line[25])
        pix[27] = float(line[26])
        pix[28] = float(line[27])
        pix[29] = float(line[28])
        pix[30] = float(line[29])
        pix[31] = float(line[30])
        pix[32] = float(line[31])


        (r[1], g[1], b[1]) = rgb(minimum, maximum, pix[1])
        (r[2], g[2], b[2]) = rgb(minimum, maximum, pix[2])
        (r[3], g[3], b[3]) = rgb(minimum, maximum, pix[3])
        (r[4], g[4], b[4]) = rgb(minimum, maximum, pix[4])
        (r[5], g[5], b[5]) = rgb(minimum, maximum, pix[5])
        (r[6], g[6], b[6]) = rgb(minimum, maximum, pix[6])
        (r[7], g[7], b[7]) = rgb(minimum, maximum, pix[7])
        (r[8], g[8], b[8]) = rgb(minimum, maximum, pix[8])
        (r[9], g[9], b[9]) = rgb(minimum, maximum, pix[9])
        (r[10], g[10], b[10]) = rgb(minimum, maximum, pix[10])
        (r[11], g[11], b[11]) = rgb(minimum, maximum, pix[11])
        (r[12], g[12], b[12]) = rgb(minimum, maximum, pix[12])
        (r[13], g[13], b[13]) = rgb(minimum, maximum, pix[13])
        (r[14], g[14], b[14]) = rgb(minimum, maximum, pix[14])
        (r[15], g[15], b[15]) = rgb(minimum, maximum, pix[15])
        (r[16], g[16], b[16]) = rgb(minimum, maximum, pix[16])
        (r[17], g[17], b[17]) = rgb(minimum, maximum, pix[17])
        (r[18], g[18], b[18]) = rgb(minimum, maximum, pix[18])
        (r[19], g[19], b[19]) = rgb(minimum, maximum, pix[19])
        (r[20], g[20], b[20]) = rgb(minimum, maximum, pix[20])
        (r[21], g[21], b[21]) = rgb(minimum, maximum, pix[21])
        (r[22], g[22], b[22]) = rgb(minimum, maximum, pix[22])
        (r[23], g[23], b[23]) = rgb(minimum, maximum, pix[23])
        (r[24], g[24], b[24]) = rgb(minimum, maximum, pix[24])
        (r[25], g[25], b[25]) = rgb(minimum, maximum, pix[25])
        (r[26], g[26], b[26]) = rgb(minimum, maximum, pix[26])
        (r[27], g[27], b[27]) = rgb(minimum, maximum, pix[27])
        (r[28], g[28], b[28]) = rgb(minimum, maximum, pix[28])
        (r[29], g[29], b[29]) = rgb(minimum, maximum, pix[29])
        (r[30], g[30], b[30]) = rgb(minimum, maximum, pix[30])
        (r[31], g[31], b[31]) = rgb(minimum, maximum, pix[31])
        (r[32], g[32], b[32]) = rgb(minimum, maximum, pix[32])

        #############################################################
        #                 Le 1er Quadrant Sup_droit                 #
        #############################################################

        ## 1 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (350, 350), 0, 0, -11.25, (b[3], g[3], r[3]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -11.25, -22.5, (b[1], g[1], r[1]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -22.5, -33.75, (b[4], g[4], r[4]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -33.75, -45, (b[17], g[17], r[17]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -45, -56.25, (b[30], g[30], r[30]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -56.25, -67.5, (b[32], g[32], r[32]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -67.5, -78.75, (b[29], g[29], r[29]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -78.75, -90, (b[31], g[31], r[31]), -1)

        ## 2 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (290, 290), 0, 0, -11.25, (b[2], g[2], r[2]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -11.25, -22.5, (b[8], g[8], r[8]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -22.5, -33.75, (b[6], g[6], r[6]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -33.75, -45, (b[7], g[7], r[7]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -45, -56.25, (b[5], g[5], r[5]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -56.25, -67.5, (b[18], g[18], r[18]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -67.5, -78.75, (b[26], g[26], r[26]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -78.75, -90, (b[25], g[25], r[25]), -1)

        ## 3 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (230, 230), 0, 0, -12.85714286, (b[9], g[9], r[9]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -12.85714286, -25.71428571, (b[11], g[11], r[11]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -25.71428571, -38.57142857, (b[10], g[10], r[10]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -38.57142857, -51.42857143, (b[21], g[21], r[21]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -51.42857143, -64.28571429, (b[22], g[22], r[22]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -64.28571429, -77.14285715, (b[23], g[23], r[23]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -77.14285715, -90, (b[29], g[24], r[24]), -1)

        ## 4 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (170, 170), 0, 0, -18, (b[12], g[12], r[12]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, -18, -36, (b[19], g[19], r[19]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, -36, -54, (b[20], g[20], r[20]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, -54, -72, (b[16], g[16], r[16]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, -72, -90, (b[15], g[15], r[15]), -1)

        ## 5 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (110, 110), 0, 0, -30, (b[28], g[28], r[28]), -1)
        cv2.ellipse(img, (350, 350), (110, 110), 0, -30, -60, (b[13], g[13], r[13]), -1)
        cv2.ellipse(img, (350, 350), (110, 110), 0, -60, -90, (b[14], g[14], r[14]), -1)

        ## 6 Cercle rjouté  ##
        cv2.ellipse(img, (350, 350), (50, 50), 0, 0, -90, (b[27], g[27], r[27]), -1)




    #############################################################
        #                        Show image                         #
        #############################################################
        bicubic_img = cv2.resize(img, None, fx=0.8, fy=0.8, interpolation=cv2.INTER_NEAREST)

        cv2.imshow(' Breast Phantom with LOQ Tumor -OpenCV-', bicubic_img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
# cv2.imshow('Heat Sensors Image', img)
# RGBimage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# plt.imshow(RGBimage)
# plt.show()
# cv2.waitKey(0)

cv2.destroyAllWindows()