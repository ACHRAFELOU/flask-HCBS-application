import serial
import time
import csv
import pyautogui
import pyscreeze
import matplotlib.pyplot as plt
import numpy as np
import cv2
from mpl_toolkits.mplot3d import Axes3D

img = np.zeros((800, 700, 3), np.uint8)
img[:] = (240, 180, 203)

n = 225
pix = [[0] * n for p in range(n)]
r = [[0] * n for p in range(n)]
g = [[0] * n for p in range(n)]
b = [[0] * n for p in range(n)]

m = 8
Name = [[0] * n for p in range(m)]

minimum = 22.5
maximum = 44

RealPix = 10
levelGrad1 = 0.9
levelGrad2 = 0.6
levelGrad3 = 0.9

def rgb(minimum, maximum, value):
    minimum, maximum, value = float(minimum), float(maximum), float(value)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b1 = int(max(0, 255 * (1 - ratio)))
    r1 = int(max(0, 255 * (ratio - 1)))
    g1 = 255 - b1 - r1
    return r1, g1, b1

if __name__ == "__main__":
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    while True:
        # 1 Cercle rajoutés
        pix[1] = float(29.0)
        pix[2] = float(21.0)
        pix[3] = float(21.94)
        pix[4] = float(28.96)
        pix[5] = float(28.17)
        pix[6] = float(21.45)
        pix[7] = float(21.17)
        pix[8] = float(28)
        pix[9] = float(28.996)
        pix[10] = float(21.996)
        pix[11] = float(21)
        pix[12] = float(27)
        pix[13] = float(28)
        pix[14] = float(21)
        pix[15] = float(21.5)
        pix[16] = float(29)
        pix[17] = float(26)
        pix[18] = float(20)
        pix[19] = float(27.5)
        pix[20] = float(29)
        pix[21] = float(25)
        pix[22] = float(20)
        pix[23] = float(30)
        pix[24] = float(30)
        pix[25] = float(28)
        pix[26] = float(20)

        for x in range(len(pix)):
            for y in range(len(pix[x])):
                (r[x][y], g[x][y], b[x][y]) = rgb(minimum, maximum, pix[x][y])

        pyautogui.screenshot('Screenshot.png')
        img = cv2.imread('Screenshot.png')

        for i in range(0, 800, 20):
            for j in range(0, 700, 20):
                x = i // 20
                y = j // 20

                if x <= 32 and y <= 7:
                    cv2.circle(img, (i + 10, j + 10), 10, (b[x][y], g[x][y], r[x][y]), -1)
                    ax.scatter(x, y, (b[x][y], g[x][y], r[x][y]))

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.show()

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()
