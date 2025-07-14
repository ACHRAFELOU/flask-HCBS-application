import numpy as np
import matplotlib.pyplot as plt

# Paramètres
R = 10  # Rayon du sein (en cm)
nb_sensors = 32
n_agents = 20
iterations = 100

# Fonction de fitness : maximiser la dispersion des capteurs
def fitness_function(positions):
    positions = positions.reshape((nb_sensors, 2))
    total_distance = 0
    for i in range(nb_sensors):
        for j in range(i + 1, nb_sensors):
            total_distance += np.linalg.norm(positions[i] - positions[j])
    return -total_distance  # On minimise le négatif

# Initialisation aléatoire
def initialize_population(n_agents):
    return np.random.uniform(-R, R, size=(n_agents, nb_sensors * 2))

# Algorithme WOA avec courbe de convergence
def woa_optimize(iterations=100, n_agents=20):
    pop = initialize_population(n_agents)
    fitness = np.array([fitness_function(ind) for ind in pop])
    best_pos = pop[np.argmin(fitness)]
    best_fitness = [fitness.min()]

    for t in range(iterations):
        a = 2 - t * (2 / iterations)
        for i in range(n_agents):
            r = np.random.rand()
            A = 2 * a * r - a
            C = 2 * np.random.rand()
            D = abs(C * best_pos - pop[i])
            pop[i] = best_pos - A * D
        fitness = np.array([fitness_function(ind) for ind in pop])
        best_pos = pop[np.argmin(fitness)]
        best_fitness.append(fitness.min())

    return best_pos.reshape((nb_sensors, 2)), best_fitness

# Générer une configuration initiale pour comparaison
initial_positions = initialize_population(1).reshape((nb_sensors, 2))

# Optimisation WOA
optimized_positions, convergence_curve = woa_optimize(iterations, n_agents)

# --- Affichage des figures ---

# Figure 1 : Placement initial vs optimisé
fig, axs = plt.subplots(1, 2, figsize=(12, 6))
titles = ["Initial Placement", "WOA Optimized Placement"]

for ax, positions, title in zip(axs, [initial_positions, optimized_positions], titles):
    circle = plt.Circle((0, 0), R, color='lightblue', fill=False)
    ax.add_artist(circle)
    ax.scatter(positions[:, 0], positions[:, 1], color='red')
    ax.set_xlim(-R-2, R+2)
    ax.set_ylim(-R-2, R+2)
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.grid(True)

plt.tight_layout()
plt.show()

# Figure 2 : Courbe de convergence
plt.figure(figsize=(8, 5))
plt.plot(convergence_curve, marker='o')
plt.title("WOA Convergence Curve")
plt.xlabel("Iteration")
plt.ylabel("Best Fitness Value")
plt.grid(True)
plt.tight_layout()
plt.show()
