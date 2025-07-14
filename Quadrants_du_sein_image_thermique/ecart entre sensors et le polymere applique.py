import pandas as pd
import matplotlib.pyplot as plt

# Charger le fichier CSV
file_path = 'C:/Users/a.elouerghi/Desktop/elouerghi_sensors_Ambient.csv'
data = pd.read_csv(file_path, delimiter=';')

# Convertir la colonne Timestamp en type datetime
data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y %H:%M')

# Calculer les écarts en valeur absolue
data['Diff_4_7'] = abs(data['Sensor_4'] - data['Sensor_7'])
data['Diff_5_8'] = abs(data['Sensor_5'] - data['Sensor_8'])

# Préparer la figure
plt.figure(figsize=(14, 8))

# Tracer les écarts
plt.plot(data['Timestamp'], data['Diff_4_7'], label='|Sensor 4 - Sensor 7|', color='blue', linewidth=2)
plt.plot(data['Timestamp'], data['Diff_5_8'], label='|Sensor 5 - Sensor 8|', color='green', linewidth=2)

# Ajouter une zone ombrée pour l'intervalle [0, 0.5]
plt.fill_between(data['Timestamp'], 0, 0.5, color='gray', alpha=0.2, label='Intervalle [0, 0.5]')

# Ligne de référence pour écart nul
plt.axhline(0, color='red', linestyle='--', label='Écart nul', linewidth=1.5)

# Personnalisation des graphes
plt.title('Analyse des Écarts Absolus entre les Capteurs', fontsize=16, fontweight='bold')
plt.xlabel('Temps d\'Acquisition', fontsize=14)
plt.ylabel('Écart Absolu (°C)', fontsize=14)
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=12, loc='upper right')
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# Annotation explicative pour les pics
max_diff_4_7 = data['Diff_4_7'].max()
max_time_4_7 = data['Timestamp'][data['Diff_4_7'].idxmax()]
plt.annotate(f'Pic: {max_diff_4_7:.2f} °C', xy=(max_time_4_7, max_diff_4_7),
             xytext=(max_time_4_7, max_diff_4_7 + 0.5),
             arrowprops=dict(facecolor='blue', arrowstyle='->'),
             fontsize=10, color='blue')

max_diff_5_8 = data['Diff_5_8'].max()
max_time_5_8 = data['Timestamp'][data['Diff_5_8'].idxmax()]
plt.annotate(f'Pic: {max_diff_5_8:.2f} °C', xy=(max_time_5_8, max_diff_5_8),
             xytext=(max_time_5_8, max_diff_5_8 + 0.5),
             arrowprops=dict(facecolor='green', arrowstyle='->'),
             fontsize=10, color='green')

# Ajuster les marges et afficher
plt.tight_layout()
plt.show()
