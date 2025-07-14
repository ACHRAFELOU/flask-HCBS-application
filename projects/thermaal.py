import numpy as np
import random
import json
import cv2
from datetime import datetime

# Paramètres globaux
n = 225
pix = [[0] * n for _ in range(n)]
r = [[0] * n for _ in range(n)]
g = [[0] * n for _ in range(n)]
b = [[0] * n for _ in range(n)]

minimum = 18
maximum = 28


def rgb(minimum, maximum, value):
    minimum, maximum, value = float(minimum), float(maximum), float(value)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b1 = int(max(0, 255 * (1 - ratio)))
    r1 = int(max(0, 255 * (ratio - 1)))
    g1 = 255 - b1 - r1
    return r1, g1, b1


def generate_thermal_data():
    data = []

    for i in range(32):
        temp_value = random.randint(18, 35)
        color = rgb(minimum, maximum, temp_value)
        data.append({
            "temperature": temp_value,
            "color": {
                "red": color[0],
                "green": color[1],
                "blue": color[2]
            }
        })

    return json.dumps(data)


def generate_thermal_image():
    img = np.zeros((800, 700, 3), np.uint8)
    img[:] = (240, 180, 203)

    while True:
        # Mettre à jour les pixels
        for i in range(32):
            pix[i] = random.randint(18, 35)

        # Générer l'image thermique (code omis pour la clarté)

        # Ici, vous pouvez appeler la fonction pour obtenir les données thermiques en JSON
        thermal_data_json = generate_thermal_data()
        print(thermal_data_json)  # Afficher les données JSON

        # Vous pouvez également ajouter le code pour afficher l'image ici
        # cv2.imshow('Thermal Image', img)

        # Pour sortir de la boucle, vous pouvez ajouter une condition, par exemple:
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break


# Appeler la fonction pour générer l'image thermique
generate_thermal_image()
