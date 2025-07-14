import serial
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
from collections import deque

# Port série à utiliser
serial_port = 'COM5'

# Chemin du fichier CSV de sortie sur le bureau
output_file = os.path.join(os.path.expanduser('~'), 'Desktop', 'elouerghi_sensors_Ambient.csv')

# Initialiser les listes pour les données des capteurs et l'horodatage
timestamps = deque(maxlen=100)  # Stocker les 100 derniers horodatages
sensor_data = [deque(maxlen=100) for _ in range(9)]  # Une file pour chaque capteur

# Initialiser les graphiques
plt.ion()
fig, axs = plt.subplots(3, 3, figsize=(12, 8))  # 3x3 subplots pour 9 capteurs
axs = axs.flatten()
for i, ax in enumerate(axs):
    ax.set_title(f"Sensor {i+1}")
    ax.set_xlim(0, 100)  # Affichage des 100 derniers points
    ax.set_ylim(21.2, 21.5)  # Plage fixe pour les valeurs
    ax.set_xlabel("Time (10s intervals)")
    ax.set_ylabel("Value")

lines = [ax.plot([], [])[0] for ax in axs]  # Initialiser les courbes pour chaque capteur

# Ouvrir le port série
try:
    ser = serial.Serial(serial_port, 115200, timeout=1)
except serial.SerialException as e:
    print(f"Erreur : Impossible d'ouvrir le port série {serial_port}. {e}")
    exit()

# Créer le fichier CSV et écrire l'en-tête s'il n'existe pas déjà
if not os.path.exists(output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp'] + [f'Sensor_{i+1}' for i in range(9)])

print("En attente de données...")

while True:
    try:
        # Lire une ligne depuis le port série
        line = ser.readline().decode('utf-8').strip()

        if line:
            data = line.split(",")
            print("Reçu :", data)

            # Vérifier que nous avons exactement 9 données
            if len(data) != 9:
                print(f"Erreur : Nombre inattendu de données ({len(data)})")
                continue

            # Convertir les données en float
            sensors = []
            for value in data:
                try:
                    sensors.append(float(value.strip()))
                except ValueError:
                    print(f"Valeur non valide ignorée : {value}")
                    sensors.append(None)

            # Ajouter les données dans les files et l'horodatage
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            timestamps.append(timestamp)
            for i, sensor_value in enumerate(sensors):
                sensor_data[i].append(sensor_value)

            # Écrire les données dans le fichier CSV
            with open(output_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([timestamp] + sensors)

            # Mettre à jour les graphiques toutes les 10 secondes
            if len(timestamps) % 10 == 0:
                for i, line in enumerate(lines):
                    line.set_xdata(range(len(sensor_data[i])))
                    line.set_ydata(sensor_data[i])
                    axs[i].relim()
                    axs[i].autoscale_view()

                plt.pause(0.1)  # Mettre à jour les graphiques

    except KeyboardInterrupt:
        print("Arrêt par l'utilisateur.")
        break
    except Exception as e:
        print(f"Erreur lors de la lecture ou de l'écriture : {e}")

# Fermer le port série et désactiver le mode interactif
ser.close()
plt.ioff()
plt.show()
print("Port série fermé.")
