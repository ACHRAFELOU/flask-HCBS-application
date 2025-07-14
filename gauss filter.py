import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Paramètres
sigma = 1.0
size = 5  # taille du filtre (impair)

# Création des coordonnées x et y centrées
ax = np.arange(-size//2 + 1, size//2 + 1, 1)
x, y = np.meshgrid(ax, ax)

# Fonction gaussienne
G = (1/(2 * np.pi * sigma**2)) * np.exp(-(x**2 + y**2) / (2 * sigma**2))

# Tracé 3D
fig = plt.figure(figsize=(8,6))
ax3d = fig.add_subplot(111, projection='3d')
ax3d.plot_surface(x, y, G, cmap='viridis')

ax3d.set_title('Filtre Gaussien 2D')
ax3d.set_xlabel('x')
ax3d.set_ylabel('y')
ax3d.set_zlabel('G(x,y)')

plt.show()
