import numpy as np
import matplotlib.pyplot as plt

# Paramètres de simulation
lambda_values = [1e-5, 1e-4, 1e-3]  # Différentes densités de nœuds (nœuds/m²)
Pt = 1  # Puissance d'émission de chaque nœud (W)
alpha = 2.5  # Exposant d'atténuation
area_radius = 1000  # Rayon de la zone simulée (m)
num_samples = 1000  # Nombre d'échantillons pour la simulation
noise_power = 1e-13  # Puissance du bruit thermique (W)

# Générer des interférences totales pour différentes densités
interference_data = {}

for lam in lambda_values:
    num_nodes = np.random.poisson(lam * np.pi * area_radius ** 2)  # Nombre de nœuds
    distances = np.random.uniform(1, area_radius, size=(num_nodes, num_samples))  # Distances aléatoires
    interferences = np.sum(Pt / (distances ** alpha), axis=0)  # Somme des interférences
    INR_dB = 10 * np.log10(interferences / noise_power)  # Conversion en INR (dB)
    interference_data[lam] = np.sort(INR_dB)  # Ordonner pour la CDF

# Tracer la CDF
plt.figure(figsize=(10, 6))

for lam, data in interference_data.items():
    # Filtrer les données dans l'intervalle d'intérêt [-15, -10.5]
    data_filtered = data[(data >= -15) & (data <= -10.5)]
    if len(data_filtered) > 0:  # Vérifier s'il y a des points dans l'intervalle
        cdf = np.arange(1, len(data_filtered) + 1) / len(data_filtered)  # Fonction de distribution cumulative
        plt.plot(data_filtered, cdf, label=f"λ = {lam:.0e} nœuds/m²")

# Mise en forme du graphique
plt.title("CDF of Total In-Band Interference (INR in dB)", fontsize=14)
plt.xlabel("INR (dB)", fontsize=12)
plt.ylabel("CDF of Total Interference", fontsize=12)
plt.xlim([-15, -10.5])  # Intervalle pour l'axe X
plt.ylim([0, 1])  # Intervalle pour l'axe Y
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()
