import serial
import time
import csv
import pyautogui
import pyscreeze
import matplotlib.pyplot as plt
import numpy as np
import cv2
from pylab import *

##ser = serial.Serial('COM3', 9600)

n = 225
pix = [0] * 128
minimum = 23.98
maximum = 24.50
RealPix = 12

levelGrad1 = 0.9
levelGrad2 = 0.6
levelGrad3 = 0.9

img = np.zeros((693, 693, 3), np.uint8)
img[:] = (225, 255, 225)


def rgb(minimum, maximum, value):
    minimum, maximum, value = float(minimum), float(maximum), float(value)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b1 = int(max(0, 255 * (1 - ratio)))
    r1 = int(max(0, 255 * (ratio - 1)))
    g1 = 255 - b1 - r1
    return r1, g1, b1


def interpolate(pix_values, num_pixels):
    interpolated_values = []
    num_values = len(pix_values)

    for i in range(num_values - 1):
        start_val = pix_values[i]
        end_val = pix_values[i + 1]
        diff = (end_val - start_val) / (num_pixels + 1)

        for j in range(num_pixels):
            interpolated_values.append(start_val + (j + 1) * diff)

    interpolated_values.append(pix_values[-1])

    return interpolated_values


if __name__ == "__main__":
    while 1:
        # Assign values to pix[1] to pix[128]
        pix[20] = float(24.0)
        pix[1] = float(24.0)
        pix[11] = float(23.94)
        pix[10] = float(23.96)
        # Assign values to pix[29] to pix[128]

        #############################################################
        #                        Show image                         #
        #############################################################

        img = np.zeros((693, 693, 3), np.uint8)
        img[:] = (225, 255, 225)

        interpolated_pix = interpolate(pix, RealPix)

        for i in range(1, len(interpolated_pix) + 1):
            (r, g, b) = rgb(minimum, maximum, interpolated_pix[i - 1])
            cv2.ellipse(img, (346, 346), (346, 346), 0, 22.5, -22.5, (b, g, r), -1)
            cv2.ellipse(img, (346, 346), (346, 346), 0, -22.5, -67.5, (b, g, r), -1)
            cv2.ellipse(img, (346, 346), (346, 346), 0, -67.5, -112.5, (b, g, r), -1)
            cv2.ellipse(img, (346, 346), (346, 346), 0, -112.5, -157.5, (b, g, r), -1)
            cv2.ellipse(img, (346, 346), (346, 346), 0, -157.5, -202.5, (b, g, r), -1)
            cv2.ellipse(img, (346, 346), (346, 346), 0, -202.5, -247.5, (b, g, r), -1)
            cv2.ellipse(img, (346, 346), (346, 346), 0, -247.5, -292.5, (b, g, r), -1)
            cv2.ellipse(img, (346, 346), (346, 346), 0, -292.5, -337.5, (b, g, r), -1)

        resized_img = cv2.resize(img, None, fx=0.8, fy=0.8)
        cv2.imshow('Breast Phantom with LOQ Tumor -OpenCV-', resized_img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
