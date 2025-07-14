import serial, time
import csv
import pyautogui
import pyscreeze
import matplotlib as plt
import numpy as np
import cv2
from pylab import *

##ser = serial.Serial('COM3', 9600)

n = 225
pix = [[0] * n for p in range(n)]
r = [[0] * n for p in range(n)]
g = [[0] * n for p in range(n)]
b = [[0] * n for p in range(n)]

m = 8
Name = [[0] * n for p in range(m)]

minimum = 23.98
maximum = 24.50

RealPix = 12

levelGrad1 = 0.9
levelGrad2 = 0.6
levelGrad3 = 0.9

img = np.zeros((800, 800, 3), np.uint8)
img[:] = (225, 255, 225)


def rgb(minimum, maximum, value):
    minimum, maximum, value = float(minimum), float(maximum), float(value)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b1 = int(max(0, 255 * (1 - ratio)))
    r1 = int(max(0, 255 * (ratio - 1)))
    g1 = 255 - b1 - r1
    return r1, g1, b1


##def grad1(level, PixelTemperature, x1, y1):
##    PixelTemperature = float(PixelTemperature) - float(level)
##    (rg, gg, bg) = rgb(minimum, maximum, PixelTemperature)
##
##    for y in range(y1 - RealPix, y1 - RealPix + 3 * RealPix, RealPix):
##        for x in range(x1 - RealPix, x1 - RealPix + 3 * RealPix, RealPix):
##            if (x == x1 and y == y1):
##                continue
##            else:
##                cv2.rectangle(img, (x, y), (x + RealPix, y + RealPix), (bg, gg, rg), -1)


if __name__ == "__main__":
    while 1:
        ##        for i in range(0, 4, 1):
        ##            serial_line = ser.readline()
        ##
        ##        liste = serial_line.split(','.encode())
        ##        liste[-1] = liste[-1].strip()
        ## 1 Cercle rajoutés  ##

        # liste[25]
        pix[20] = float(24.0)
        # liste[23]
        pix[1] = float(24.0)
        # liste[24]
        pix[11] = float(23.94)
        # liste[20]
        pix[10] = float(23.96)

        ## 2 Cercle rajoutés  ##

        # liste[3]
        pix[19] = float(24.17)
        # liste[21]
        pix[24] = float(24.45)
        # liste[17]
        pix[2] = float(24.17)
        # liste[27]
        pix[22] = float(24)
        # liste[4]
        pix[12] = float(23.996)
        # liste[22]
        pix[26] = float(23.996)
        # liste[12]
        pix[9] = float(24)
        # liste[26]
        pix[28] = float(24)

        ## 3 Cercle rajoutés  ##

        # liste[2]
        pix[18] = float(24.18)
        # liste[16]
        pix[23] = float(24.516)
        # liste[18]
        pix[3] = float(24.18)
        # liste[7]
        pix[21] = float(24)
        # liste[6]
        pix[13] = float(23.954)
        # liste[14]
        pix[25] = float(24)
        # liste[13]
        pix[8] = float(24)
        # liste[0]
        pix[27] = float(24)

        ## 4 Cercle rajoutés  #

        # liste[1]
        pix[17] = float(24.35)
        # liste[19]
        pix[4] = float(24.18)
        # liste[5]
        pix[14] = float(24)
        # liste[15]
        pix[7] = float(24)

        ## 5 Cercle rajoutés  ##

        # liste[10]
        pix[16] = float(24.22)
        # liste[8]
        pix[5] = float(24.182)
        # liste[11]
        pix[15] = float(24)
        # liste[9]
        pix[6] = float(24)

        # COLORS#
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

        ## 1 Cercle rajoutés  ##

        cv2.ellipse(img, (346, 346), (346, 346), 0, 22.5, -22.5, (b[20], g[20], r[20]), -1)
        cv2.ellipse(img, (346, 346), (346, 346), 0, -22.5, -67.5, (b[20], g[20], r[20]), -1)
        cv2.ellipse(img, (346, 346), (346, 346), 0, -67.5, -112.5, (b[1], g[1], r[1]), -1)
        cv2.ellipse(img, (346, 346), (346, 346), 0, -112.5, -157.5, (b[1], g[1], r[1]), -1)
        cv2.ellipse(img, (346, 346), (346, 346), 0, -157.5, -202.5, (b[11], g[11], r[11]), -1)
        cv2.ellipse(img, (346, 346), (346, 346), 0, -202.5, -247.5, (b[11], g[11], r[11]), -1)
        cv2.ellipse(img, (346, 346), (346, 346), 0, -247.5, -292.5, (b[10], g[10], r[10]), -1)
        cv2.ellipse(img, (346, 346), (346, 346), 0, -292.5, -337.5, (b[10], g[10], r[10]), -1)

        ## 2 Cercle rajoutés  ##
        cv2.ellipse(img, (346, 346), (266, 266), 0, 22.5, -22.5, (b[19], g[19], r[19]), -1)
        cv2.ellipse(img, (346, 346), (266, 266), 0, -22.5, -67.5, (b[24], g[24], r[24]), -1)
        cv2.ellipse(img, (346, 346), (266, 266), 0, -67.5, -112.5, (b[2], g[2], r[2]), -1)
        cv2.ellipse(img, (346, 346), (266, 266), 0, -112.5, -157.5, (b[22], g[22], r[22]), -1)
        cv2.ellipse(img, (346, 346), (266, 266), 0, -157.5, -202.5, (b[12], g[12], r[12]), -1)
        cv2.ellipse(img, (346, 346), (266, 266), 0, -202.5, -247.5, (b[26], g[26], r[26]), -1)
        cv2.ellipse(img, (346, 346), (266, 266), 0, -247.5, -292.5, (b[9], g[9], r[9]), -1)
        cv2.ellipse(img, (346, 346), (266, 266), 0, -292.5, -337.5, (b[28], g[28], r[28]), -1)

        ## 3 Cercle rajoutés  ##

        cv2.ellipse(img, (346, 346), (186, 186), 0, 22.5, -22.5, (b[18], g[18], r[18]), -1)
        cv2.ellipse(img, (346, 346), (186, 186), 0, -22.5, -67.5, (b[23], g[23], r[23]), -1)
        cv2.ellipse(img, (346, 346), (186, 186), 0, -67.5, -112.5, (b[3], g[3], r[3]), -1)
        cv2.ellipse(img, (346, 346), (186, 186), 0, -112.5, -157.5, (b[21], g[21], r[21]), -1)
        cv2.ellipse(img, (346, 346), (186, 186), 0, -157.5, -202.5, (b[13], g[13], r[13]), -1)
        cv2.ellipse(img, (346, 346), (186, 186), 0, -202.5, -247.5, (b[25], g[25], r[25]), -1)
        cv2.ellipse(img, (346, 346), (186, 186), 0, -247.5, -292.5, (b[8], g[8], r[8]), -1)
        cv2.ellipse(img, (346, 346), (186, 186), 0, -292.5, -337.5, (b[27], g[27], r[27]), -1)

        ## 4 Cercle rajoutés  ##

        cv2.ellipse(img, (346, 346), (106, 106), 0, 22.5, -22.5, (b[4], g[4], r[4]), -1)
        cv2.ellipse(img, (346, 346), (106, 106), 0, -22.5, -67.5, (b[17], g[17], r[17]), -1)
        cv2.ellipse(img, (346, 346), (106, 106), 0, -67.5, -112.5, (b[4], g[4], r[4]), -1)
        cv2.ellipse(img, (346, 346), (106, 106), 0, -112.5, -157.5, (b[14], g[14], r[14]), -1)
        cv2.ellipse(img, (346, 346), (106, 106), 0, -157.5, -202.5, (b[14], g[14], r[14]), -1)
        cv2.ellipse(img, (346, 346), (106, 106), 0, -202.5, -247.5, (b[14], g[14], r[14]), -1)
        cv2.ellipse(img, (346, 346), (106, 106), 0, -247.5, -292.5, (b[7], g[7], r[7]), -1)
        cv2.ellipse(img, (346, 346), (106, 106), 0, -292.5, -337.5, (b[7], g[7], r[7]), -1)

        ## 5 Cercle rajoutés  ##

        cv2.ellipse(img, (346, 346), (50, 50), 0, 22.5, -22.5, (b[4], g[4], r[4]), -1)
        cv2.ellipse(img, (346, 346), (50, 50), 0, -22.5, -67.5, (b[16], g[16], r[16]), -1)
        cv2.ellipse(img, (346, 346), (50, 50), 0, -67.5, -112.5, (b[5], g[5], r[5]), -1)
        cv2.ellipse(img, (346, 346), (50, 50), 0, -112.5, -157.5, (b[15], g[15], r[15]), -1)
        cv2.ellipse(img, (346, 346), (50, 50), 0, -157.5, -202.5, (b[15], g[15], r[15]), -1)
        cv2.ellipse(img, (346, 346), (50, 50), 0, -202.5, -247.5, (b[15], g[15], r[15]), -1)
        cv2.ellipse(img, (346, 346), (50, 50), 0, -247.5, -292.5, (b[6], g[6], r[6]), -1)
        cv2.ellipse(img, (346, 346), (50, 50), 0, -292.5, -337.5, (b[6], g[6], r[6]), -1)

        #############################################################
        #                        Show image                         #
        #############################################################
        bicubic_img = cv2.resize(img, None, fx=0.8, fy=0.8, interpolation=cv2.INTER_NEAREST)

        cv2.imshow(' Breast Phantom with LOQ Tumor -OpenCV-', bicubic_img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        cmap = plt.cm.jet
        norm = plt.Normalize(minimum, maximum)

        # Create a ScalarMappable object for the color bar
        scm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        scm.set_array([])

        # Create a color bar axis
        cbar_ax = plt.gcf().add_axes([0.05, 0.05, 0.3, 0.8])  # You can adjust the position and size of the color bar here

        # Plot the color bar
        plt.colorbar(scm, cax=cbar_ax)

        # Show the image and color bar
        plt.imshow(img)
        plt.show()
cv2.destroyAllWindows()
