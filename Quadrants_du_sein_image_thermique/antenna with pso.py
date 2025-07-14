import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Dimensions du bonnet (ajustables selon les données anthropométriques)
radius_horizontal = 8.0  # Rayon horizontal (cm) - demi-grand axe de l'ellipse
radius_vertical = 6.5    # Rayon vertical (cm) - demi-petit axe de l'ellipse
projection_depth = 6.0   # Profondeur du sein (distance maximale vers l'avant, cm)

# Meshgrid pour la surface (base elliptique)
theta = np.linspace(0, 2 * np.pi, 100)  # Angle horizontal (360°)
phi = np.linspace(0, np.pi / 2, 100)    # Angle vertical (180° coupé à moitié)
theta, phi = np.meshgrid(theta, phi)

# Coordonnées en 3D pour une base elliptique
x = radius_horizontal * np.sin(phi) * np.cos(theta)  # Largeur
y = radius_vertical * np.sin(phi) * np.sin(theta)    # Hauteur
z = projection_depth * np.cos(phi)                  # Profondeur

# Visualisation
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Surface de l'ellipse 3D
ax.plot_surface(x, y, z, color='pink', edgecolor='k', alpha=0.8)

# Ajuster les axes et titres
ax.set_title("Modélisation 3D d'un bonnet elliptique", fontsize=14)
ax.set_xlabel("Largeur horizontale (cm)")
ax.set_ylabel("Hauteur verticale (cm)")
ax.set_zlabel("Profondeur (cm)")
ax.view_init(elev=20, azim=30)  # Angle de vue

plt.show()
