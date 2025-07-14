import cv2
import numpy as np
import matplotlib.pyplot as plt

img = np.zeros((800, 700, 3), np.uint8)
img[:] = (240, 180, 203)

n = 225
pix = [[0] * n for _ in range(n)]
r = [[0] * n for _ in range(n)]
g = [[0] * n for _ in range(n)]
b = [[0] * n for _ in range(n)]

m = 8
Name = [[0] * n for _ in range(m)]

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
    while True:
        # Values assigned to `pix` list
        pix = [
            29, 21, 21, 28, 28, 21, 21, 28, 28, 21, 21, 27, 28, 21, 21.5, 29, 26, 20, 27.5, 29, 25, 20, 30, 30, 28, 20, 25.5, 27, 27.5, 25.5, 28, 32
        ]

        data = np.array(pix)
        min_val = np.min(data)
        max_val = np.max(data)
        print("Valeur minimale:", min_val)
        print("Valeur maximale:", max_val)
        min_indices = [i for i, val in enumerate(pix) if val == min_val]
        max_indices = [i for i, val in enumerate(pix) if val == max_val]

        for i in range(1, 33):
            (r[i], g[i], b[i]) = rgb(minimum, maximum, pix[i - 1])

        # Drawing ellipses
        cv2.ellipse(img, (350, 350), (350, 350), 0, 0, -11.25, (b[1], g[1], r[1]), -1)
        # ... (other ellipse drawing code)

        # Displaying the image
        cv2.imshow("Image", img)
        cv2.waitKey(0)

        # Saving the image
        cv2.imwrite("output_image.png", img)
