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

minimum = 18
maximum = 28

RealPix = 10
levelGrad1 = 0.9
levelGrad2 = 0.6
levelGrad3 = 0.9
img = np.zeros((800, 700, 3), np.uint8)
img[:] = (240, 180, 203)

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
        print(line)
        if len(line) >= 2:
            line = [x.strip() for x in line]
            print(line[95])
            for i in range(32):
                pix[i] = line[i]
                pix[i + 32] = line[i + 32]
                pix[i + 64] = line[i + 64]
                pix[i + 96] = line[i + 96]
            for i in range(32):
                (r[i], g[i], b[i]) = rgb(minimum, maximum, pix[i])
                (r[i + 32], g[i + 32], b[i + 32]) = rgb(minimum, maximum, pix[i + 32])
                (r[i + 64], g[i + 64], b[i + 64]) = rgb(minimum, maximum, pix[i + 64])
                (r[i + 96], g[i + 96], b[i + 96]) = rgb(minimum, maximum, pix[i + 96])

        #############################################################
        #                 Le 1er Quadrant Sup_droit                 #
        #############################################################

                                 ## 1 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (350, 350), 0, 0, -11.25, (b[2], g[2], r[2]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, -11.25, -22.5, (b[0], g[0], r[0]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, -22.5, -33.75, (b[3], g[3], r[3]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, -33.75, -45, (b[16], g[16], r[16]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, -45, -56.25, (b[29], g[29], r[29]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, -56.25, -67.5, (b[31], g[31], r[31]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, -67.5, -78.75, (b[28], g[28], r[28]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, -78.75, -90, (b[30], g[30], r[30]), -1)
                                 ## 2 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (290, 290), 0, 0, -11.25, (b[1], g[1], r[1]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, -11.25, -22.5, (b[7], g[7], r[7]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, -22.5, -33.75, (b[5], g[5], r[5]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, -33.75, -45, (b[6], g[6], r[6]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, -45, -56.25, (b[4], g[4], r[4]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, -56.25, -67.5, (b[17], g[17], r[17]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, -67.5, -78.75, (b[25], g[25], r[25]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, -78.75, -90, (b[24], g[24], r[24]), -1)
                                ## 3 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (230, 230), 0, 0, -12.85714286, (b[8], g[8], r[8]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, -12.85714286, -25.71428571, (b[10], g[10], r[10]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, -25.71428571, -38.57142857, (b[9], g[9], r[9]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, -38.57142857, -51.42857143, (b[20], g[20], r[20]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, -51.42857143, -64.28571429, (b[21], g[21], r[21]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, -64.28571429, -77.14285715, (b[22], g[22], r[22]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, -77.14285715, -90, (b[23], g[23], r[23]), -1)
                                 ## 4 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (170, 170), 0, 0, -18, (b[11], g[11], r[11]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 0, -18, -36, (b[18], g[18], r[18]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 0, -36, -54, (b[19], g[19], r[19]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 0, -54, -72, (b[15], g[15], r[15]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 0, -72, -90, (b[14], g[14], r[14]), -1)
                                ## 5 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (110, 110), 0, 0, -30, (b[27], g[27], r[27]), -1)
            cv2.ellipse(img, (350, 350), (110, 110), 0, -30, -60, (b[12], g[12], r[12]), -1)
            cv2.ellipse(img, (350, 350), (110, 110), 0, -60, -90, (b[13], g[13], r[13]), -1)
                                ## 6 Cercle rjouté  ##
            cv2.ellipse(img, (350, 350), (50, 50), 0, 0, -90, (b[26], g[26], r[26]), -1)

            #############################################################
            #                 Le 2eme Quadrant Inf_droit                #
            #############################################################

                            ## 1 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (350, 350), 0, 0, 11.25, (b[62], g[62], r[62]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, 11.25, 22.5, (b[60], g[60], r[60]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, 22.5, 33.75, (b[63], g[63], r[63]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, 33.75, 45, (b[61], g[61], r[61]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, 45, 56.25, (b[48], g[48], r[48]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, 56.25, 67.5, (b[35], g[35], r[35]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, 67.5, 78.75, (b[32], g[32], r[32]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 0, 78.75, 90, (b[34], g[34], r[34]), -1)

                            ## 2 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (290, 290), 0, 0, 11.25, (b[56], g[56], r[56]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, 11.25, 22.5, (b[57], g[57], r[57]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, 22.5, 33.75, (b[49], g[49], r[49]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, 33.75, 45, (b[36], g[36], r[36]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, 45, 56.25, (b[38], g[38], r[38]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, 56.25, 67.5, (b[37], g[37], r[37]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, 67.5, 78.75, (b[39], g[39], r[39]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 0, 78.75, 90, (b[33], g[33], r[33]), -1)
                              ## 3 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (230, 230), 0, 0, 12.85714286, (b[55], g[55], r[55]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, 12.85714286, 25.71428571, (b[54], g[54], r[54]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, 25.71428571, 38.57142857, (b[53], g[53], r[53]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, 38.57142857, 51.42857143, (b[52], g[52], r[52]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, 51.42857143, 64.28571429, (b[41], g[41], r[41]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, 64.28571429, 77.14285715, (b[42], g[42], r[42]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 0, 77.14285715, 90, (b[40], g[40], r[40]), -1)
                             ## 4 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (170, 170), 0, 0, 18, (b[46], g[46], r[46]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 0, 18, 36, (b[47], g[47], r[47]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 0, 36, 54, (b[51], g[51], r[51]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 0, 54, 72, (b[50], g[50], r[50]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 0, 72, 90, (b[43], g[43], r[43]), -1)
                              ## 5 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (110, 110), 0, 0, 30, (b[45], g[45], r[45]), -1)
            cv2.ellipse(img, (350, 350), (110, 110), 0, 30, 60, (b[44], g[44], r[44]), -1)
            cv2.ellipse(img, (350, 350), (110, 110), 0, 60, 90, (b[59], g[59], r[59]), -1)
                            ## 6 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (50, 50), 0, 0, 90, (b[58], g[58], r[58]), -1)
                        #############################################################
                        #                 Le 3eme Quadrant Sup_gauche               #
                        #############################################################

                                     ## 1 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (350, 350), -90, 0, -11.25, (b[98], g[98], r[98]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), -90, -11.25, -22.5, (b[96], g[96], r[96]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), -90, -22.5, -33.75, (b[99], g[99], r[99]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), -90, -33.75, -45, (b[112], g[112], r[112]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), -90, -45, -56.25, (b[125], g[125], r[125]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), -90, -56.25, -67.5, (b[127], g[127], r[127]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), -90, -67.5, -78.75, (b[124], g[124], r[124]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), -90, -78.75, -90, (b[126], g[126], r[126]), -1)
                                                ## 2 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (290, 290), -90, 0, -11.25, (b[97], g[97], r[97]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), -90, -11.25, -22.5, (b[103], g[103], r[103]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), -90, -22.5, -33.75, (b[101], g[101], r[101]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), -90, -33.75, -45, (b[102], g[102], r[102]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), -90, -45, -56.25, (b[100], g[100], r[100]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), -90, -56.25, -67.5, (b[113], g[113], r[113]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), -90, -67.5, -78.75, (b[121], g[121], r[121]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), -90, -78.75, -90, (b[120], g[120], r[120]), -1)

                                             ## 3 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (230, 230), -90, 0, -12.85714286, (b[104], g[104], r[104]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), -90, -12.85714286, -25.71428571, (b[106], g[106], r[106]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), -90, -25.71428571, -38.57142857, (b[105], g[105], r[105]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), -90, -38.57142857, -51.42857143, (b[116], g[116], r[116]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), -90, -51.42857143, -64.28571429, (b[117], g[117], r[117]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), -90, -64.28571429, -77.14285715, (b[118], g[118], r[118]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), -90, -77.14285715, -90, (b[119], g[119], r[119]), -1)

                                                ## 4 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (170, 170), -90, 0, -18, (b[107], g[107], r[107]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), -90, -18, -36, (b[114], g[114], r[114]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), -90, -36, -54, (b[115], g[115], r[115]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), -90, -54, -72, (b[111], g[111], r[111]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), -90, -72, -90, (b[110], g[110], r[110]), -1)

                                             ## 5 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (110, 110), -90, 0, -30, (b[123], g[123], r[123]), -1)
            cv2.ellipse(img, (350, 350), (110, 110), -90, -30, -60, (b[108], g[108], r[108]), -1)
            cv2.ellipse(img, (350, 350), (110, 110), -90, -60, -90, (b[109], g[109], r[109]), -1)

                                            ## 6 Cercle rjouté  ##
            cv2.ellipse(img, (350, 350), (50, 50), -90, 0, -90, (b[122], g[122], r[122]), -1)

                            #############################################################
                            #                  Le 4eme Quadrant Inf_gauche              #
                            #############################################################

                                             ## 1 Cercle ajouté  ##

            cv2.ellipse(img, (350, 350), (350, 350), 90, 0, 11.25, (b[94], g[94], r[94]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 90, 11.25, 22.5, (b[92], g[92], r[92]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 90, 22.5, 33.75, (b[95], g[95], r[95]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 90, 33.75, 45, (b[93], g[93], r[93]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 90, 45, 56.25, (b[80], g[80], r[80]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 90, 56.25, 67.5, (b[67], g[67], r[67]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 90, 67.5, 78.75, (b[64], g[64], r[64]), -1)
            cv2.ellipse(img, (350, 350), (350, 350), 90, 78.75, 90, (b[66], g[66], r[66]), -1)

                                                  ## 2 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (290, 290), 90, 0, 11.25, (b[88], g[88], r[88]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 90, 11.25, 22.5, (b[89], g[89], r[89]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 90, 22.5, 33.75, (b[81], g[81], r[81]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 90, 33.75, 45, (b[68], g[68], r[68]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 90, 45, 56.25, (b[70], g[70], r[70]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 90, 56.25, 67.5, (b[69], g[69], r[69]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 90, 67.5, 78.75, (b[71], g[71], r[71]), -1)
            cv2.ellipse(img, (350, 350), (290, 290), 90, 78.75, 90, (b[65], g[65], r[65]), -1)

                                                 ## 3 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (230, 230), 90, 0, 12.85714286, (b[87], g[87], r[87]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 90, 12.85714286, 25.71428571, (b[86], g[86], r[86]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 90, 25.71428571, 38.57142857, (b[85], g[85], r[85]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 90, 38.57142857, 51.42857143, (b[84], g[84], r[84]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 90, 51.42857143, 64.28571429, (b[73], g[73], r[73]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 90, 64.28571429, 77.14285715, (b[74], g[74], r[74]), -1)
            cv2.ellipse(img, (350, 350), (230, 230), 90, 77.14285715, 90, (b[72], g[72], r[72]), -1)

                                                ## 4 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (170, 170), 90, 0, 18, (b[78], g[78], r[78]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 90, 18, 36, (b[79], g[79], r[79]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 90, 36, 54, (b[83], g[83], r[83]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 90, 54, 72, (b[82], g[82], r[82]), -1)
            cv2.ellipse(img, (350, 350), (170, 170), 90, 72, 90, (b[75], g[75], r[75]), -1)

                                                 ## 5 Cercle ajouté  ##
            cv2.ellipse(img, (350, 350), (110, 110), 90, 0, 30, (b[77], g[77], r[77]), -1)
            cv2.ellipse(img, (350, 350), (110, 110), 90, 30, 60, (b[76], g[76], r[76]), -1)
            cv2.ellipse(img, (350, 350), (110, 110), 90, 60, 90, (b[91], g[91], r[91]), -1)

                                                  ## 6 Cercle rjouté  ##
            cv2.ellipse(img, (350, 350), (50, 50), 90, 0, 90, (b[90], g[90], r[90]), -1)

            #############################################################
            #                        Show image                         #
            #############################################################
            # bicubic_img = cv2.resize(img, None, fx=0.8, fy=0.8, interpolation=cv2.INTER_LINEAR)
            #
            # cv2.imshow(' Breast Phantom with LOQ Tumor -OpenCV-', bicubic_img)
            #
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            # break

            # Ajoutez les légendes souhaitées
            legend1 = "UIQ"
            legend2 = "UOQ"
            legend3 = "LIQ"
            legend4 = "LOQ"
            legend5 = "RIGHT BREAST"

            # Paramètres du texte
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            color = (0, 0, 0)  # Couleur du texte (noir dans cet exemple)
            thickness = 2  # Épaisseur du texte

            # Position des légendes
            legend1_position = (5, 100)  # Coordonnées de la légende 1
            legend2_position = (630, 100)  # Coordonnées de la légende 2
            legend3_position = (5, 630)  # Coordonnées de la légende 3
            legend4_position = (630, 630)  # Coordonnées de la légende 4
            legend5_position = (270, 750)  # Coordonnées de la légende 5
            # ...

            # Ajoutez les légendes à l'image
            cv2.putText(img, legend1, legend1_position, font, font_scale, color, thickness, cv2.LINE_AA)
            cv2.putText(img, legend2, legend2_position, font, font_scale, color, thickness, cv2.LINE_AA)
            cv2.putText(img, legend3, legend3_position, font, font_scale, color, thickness, cv2.LINE_AA)
            cv2.putText(img, legend4, legend4_position, font, font_scale, color, thickness, cv2.LINE_AA)
            cv2.putText(img, legend5, legend5_position, font, font_scale, color, 2, cv2.LINE_AA)

            # resized_img = cv2.resize(img, None, fx=0.8, fy=0.8)
            bicubic_img = cv2.resize(img, None, fx=0.8, fy=0.8, interpolation=cv2.INTER_NEAREST)

            # blurred_img = cv2.GaussianBlur(resized_img, (0, 0), sigmaX=2, sigmaY=2)
            cv2.imshow('Image thermique du Sein', bicubic_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            # cv2.imshow('Heat Sensors Image', img)
            # RGBimage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # plt.imshow(RGBimage)
            # plt.show()
            # cv2.waitKey(0)

cv2.destroyAllWindows()