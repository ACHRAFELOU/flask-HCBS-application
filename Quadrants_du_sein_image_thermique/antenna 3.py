import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Paramètres de base
c = 3e8  # Vitesse de la lumière (m/s)
f = 28e9  # Fréquence (28 GHz pour 5G)
lambda_ = c / f  # Longueur d'onde (m)
spacing = lambda_ / 2  # Espacement entre les éléments (lambda/2)

# Nombre d'éléments dans l'array
N_elements = 16  # Exemple d'un réseau planaire (2D) avec 16 éléments


# Fonction pour créer un array planaire d'antennes en 3D
def create_3d_array(N_elements, spacing):
    """Crée un array planaire d'antennes en 3D (disposition en lignes et colonnes)"""
    rows = int(np.sqrt(N_elements))  # Nombre de rangées (lignes)
    cols = N_elements // rows  # Nombre de colonnes
    positions = []
    for i in range(rows):
        for j in range(cols):
            # Ajout des positions dans un plan 3D, avec un espacement entre les éléments
            positions.append([i * spacing, j * spacing, 0])  # Disposition sur un plan 2D avec une coordonnée z = 0
    return np.array(positions)


# Fonction de facteur de réseau (Array Factor)
def array_factor_3d(positions, theta, phi):
    """Calcul du facteur de réseau en 3D pour un ensemble d'antennes"""
    k = 2 * np.pi / lambda_  # Vecteur d'onde
    factor = 0
    for pos in positions:
        r = np.array([np.cos(theta) * np.cos(phi), np.cos(theta) * np.sin(phi), np.sin(theta)])  # Direction d'onde
        r_n = np.array([pos[0], pos[1], pos[2]])  # Position des éléments dans l'espace 3D
        phase_shift = np.dot(r, r_n) * k * np.linalg.norm(pos)  # Déphasage pour chaque élément
        factor += np.exp(1j * phase_shift)  # Ajouter le déphasage pour chaque élément
    return np.abs(factor)


# Fonction pour afficher le réseau d'antennes en 3D
def plot_3d_array(positions):
    """Affiche le réseau d'antennes en 3D"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Extraire les coordonnées x, y, z
    x = positions[:, 0]
    y = positions[:, 1]
    z = positions[:, 2]

    # Affichage des points du réseau d'antennes
    ax.scatter(x, y, z, color='r', s=100, label='Antennes')

    # Titre et légendes
    ax.set_title("Réseau d'antennes 3D")
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()

    plt.show()


# Fonction pour afficher le diagramme de rayonnement 3D
def plot_radiation_pattern_3d(positions, theta_range=np.linspace(0, np.pi, 100),
                              phi_range=np.linspace(0, 2 * np.pi, 100)):
    """Affiche le diagramme de rayonnement en 3D"""
    factor_values = np.zeros(
        (len(theta_range), len(phi_range)))  # Tableau 2D pour stocker les valeurs du facteur de réseau

    # Calcul du facteur de réseau pour chaque combinaison de theta et phi
    for i, theta in enumerate(theta_range):
        for j, phi in enumerate(phi_range):
            factor_values[i, j] = array_factor_3d(positions, theta, phi)

    # Normalisation et affichage du diagramme de rayonnement
    max_factor = np.max(factor_values)  # Normaliser les valeurs pour l'affichage
    theta_grid, phi_grid = np.meshgrid(theta_range, phi_range)  # Créer une grille 2D des angles

    # Conversion des coordonnées sphériques en coordonnées cartésiennes pour le tracé en 3D
    r = factor_values.flatten() / max_factor
    x = r * np.sin(theta_grid.flatten()) * np.cos(phi_grid.flatten())
    y = r * np.sin(theta_grid.flatten()) * np.sin(phi_grid.flatten())
    z = r * np.cos(theta_grid.flatten())

    # Tracer en 3D
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c=r, cmap='jet', marker='o')

    ax.set_title("Diagramme de rayonnement 3D")
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()


# Création du réseau d'antennes en 3D
positions_3d = create_3d_array(N_elements, spacing)

# Affichage du réseau d'antennes en 3D
plot_3d_array(positions_3d)

# Affichage du diagramme de rayonnement 3D
plot_radiation_pattern_3d(positions_3d)
