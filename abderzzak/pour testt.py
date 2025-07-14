import numpy as np
import matplotlib.pyplot as plt

class AdaptiveFilter:
    def __init__(self, order, step_size):
        self.order = order
        self.step_size = step_size
        self.weights = np.zeros(order)

    def update(self, input_signal, desired_signal):
        input_signal = np.pad(input_signal, (self.order-1, 0), mode='constant')
        desired_signal = desired_signal[:len(input_signal)]  # Ajuster la longueur de desired_signal
        error = desired_signal - np.convolve(input_signal, self.weights, mode='valid')
        update_term = self.step_size * np.convolve(input_signal, error, mode='valid')
        self.weights += update_term
        return error

def generate_test_signal(freq, amplitude, num_samples):
    t = np.linspace(0, 1, num_samples)
    signal = amplitude * np.sin(2 * np.pi * freq * t)
    return signal

def main():
    # Paramètres du signal de test
    frequency = 10  # Fréquence du signal sinusoïdal en Hz
    amplitude = 1.5  # Amplitude du signal sinusoïdal
    num_samples = 300000  # Nombre d'échantillons

    # Générer le signal de test
    test_signal = generate_test_signal(frequency, amplitude, num_samples)

    # Paramètres du filtre adaptatif
    filter_order = 50
    step_size = 0.001

    # Créer le filtre adaptatif
    adaptive_filter = AdaptiveFilter(order=filter_order, step_size=step_size)

    # Signal désiré (dans ce cas, le même que le signal de test)
    desired_signal = test_signal

    # Filtrage adaptatif
    filtered_signal = adaptive_filter.update(np.zeros_like(test_signal), desired_signal)

    # Affichage des résultats
    plt.figure(figsize=(10, 6))
    plt.plot(test_signal[:1000], label='Signal de Test (Original)')
    plt.plot(filtered_signal[:1000], label='Signal Filtré')
    plt.title('Filtrage Adaptatif d\'un Signal Sinusoïdal')
    plt.xlabel('Échantillons')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
