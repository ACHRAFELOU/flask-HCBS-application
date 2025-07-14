import pandas as pd
import matplotlib.pyplot as plt

# Lire les données à partir du fichier Excel
df = pd.read_excel('Sensitivity Detecto.xlsx')  # Assurez-vous de remplacer 'votre_fichier.xlsx' par le chemin de votre fichier.

# Extrait les colonnes X et Y
x = df['Input Power (dBm)']
y = df['Output Voltage(V)']

# Créer le tracé
plt.plot(x, y)

# Ajouter les étiquettes et le titre
plt.xlabel('Input Power (dBm)')
plt.ylabel('Output Voltage(V)')
plt.title('Données à partir d\'un fichier Excel')

# Afficher le tracé
plt.show()
