import matplotlib.pyplot as plt

# Données
Types_of_textile_fibers = ["Nylon", "Cotton", "Polyester", "Wool"]
Tmax_With_Textile_Fiber = [36.985,37.191 ,36.985 ,37.014]
Tmin_With_Textile_Fiber = [35.369, 35.354, 35.369, 35.366]
Delta_T = [1.616, 1.837, 1.616, 1.648]
Information_loss = [0.436, 0.23, 0.436, 0.407]
Tmax_Without_Textile_Fiber = [37.421, 37.421, 37.421, 37.421]
# Création du graphique
fig, ax1 = plt.subplots(figsize=(10, 6))

# Barres pour Tmax et Tmin
ax1.bar(Types_of_textile_fibers, Tmax_Without_Textile_Fiber, alpha=0.9, color='c', label='Tmax_Without_Textile_fiber (°C)', width=0.3)
ax1.bar(Types_of_textile_fibers, Tmax_With_Textile_Fiber, alpha=0.8, color='m', label='Tmax_With_Textile_Fiber (°C)',width=0.3)
ax1.bar(Types_of_textile_fibers, Tmin_With_Textile_Fiber, alpha=0.6, color='b', label='Tmin_With_Textile_Fiber (°C)',width=0.3)

# Configuration de l'axe des y pour Tmax et Tmin
ax1.set_ylabel('Temperature (°C)', fontweight='bold',fontsize=12)
ax1.set_xlabel('Textile Fiber', fontweight='bold',fontsize=12)
ax1.set_ylim(0, 39)

# Ajout des valeurs sur les barres
for i, value in enumerate(Tmax_With_Textile_Fiber):
    ax1.text(i, value - 1.4, f'{value:.3f}', ha='center', alpha=1, va='bottom', color='r')
for i, value in enumerate(Tmin_With_Textile_Fiber):
    ax1.text(i, value - 1.2, f'{value:.3f}', ha='center', va='bottom', color='w')
for i, value in enumerate(Tmax_Without_Textile_Fiber):
    ax1.text(i, value - 0.12, f'{value:.3f}', ha='center', va='bottom', color='c')
# Création d'un deuxième axe des y pour Delta_T
ax2 = ax1.twinx()
ax2.plot(Types_of_textile_fibers, Delta_T, 'r-o', label='Delta_T (°C)')
ax2.set_ylabel('Delta_T (°C)', fontweight='bold',fontsize=10)
ax2.set_ylim(0, 4)  # Ajustement de la limite y

# Création d'un troisième axe des y pour Perte d'information
ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 120))  # Ajustement de la position
ax3.plot(Types_of_textile_fibers, Information_loss, 'y-s', label='Information_loss (°C)')
ax3.set_ylabel('Information_loss (°C)', fontweight='bold',fontsize=10)
ax3.set_ylim(0, 0.6)  # Ajustement de la limite y

# Ajout des valeurs sur les courbes
for i, value in enumerate(Delta_T):
    ax2.text(i, value + 0.05, f'{value:.3f}', ha='center', va='bottom', color='r')
for i, value in enumerate(Information_loss):
    ax3.text(i, value - 0.045, f'{value:.3f}', ha='center', va='bottom', color='y')

# Configuration du titre et de la légende
##plt.title('Comparaison des propriétés thermiques par type de couche', fontweight='bold',fontsize=16)
fig.tight_layout()
fig.legend(loc="lower right")
ax1.set_xticklabels(Types_of_textile_fibers, fontweight='bold')

plt.show()
