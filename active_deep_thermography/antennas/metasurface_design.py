"""
Metasurface-Enhanced UWB Antenna Array Design
Graphene-based tunable metasurface for adaptive beamforming
"""

import numpy as np
from scipy import signal
from scipy.constants import c, epsilon_0, mu_0
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
import json


class GrapheneMetasurface:
    """Graphene-based tunable metasurface for antenna enhancement."""

    def __init__(self,
                 chemical_potential: float = 0.4,  # eV
                 temperature: float = 300,  # K
                 scattering_rate: float = 0.1e12,  # Hz
                 unit_cell_size: float = 3e-3):  # m

        self.mu_c = chemical_potential * 1.602e-19  # Convert to Joules
        self.T = temperature
        self.Gamma = scattering_rate
        self.d = unit_cell_size

        # Physical constants
        self.e = 1.602e-19  # Electron charge
        self.hbar = 1.054e-34  # Reduced Planck constant
        self.kb = 1.3806e-23  # Boltzmann constant

    def surface_conductivity(self, frequency: float) -> complex:
        """
        Calculate graphene surface conductivity using Kubo formula.

        Parameters:
        -----------
        frequency : float
            Frequency in Hz

        Returns:
        --------
        sigma : complex
            Surface conductivity in Siemens
        """
        omega = 2 * np.pi * frequency

        # Intraband contribution (Drude model)
        sigma_intra = (1j * self.e ** 2 * self.mu_c) / \
                      (np.pi * self.hbar ** 2 * (omega + 2j * self.Gamma))

        # Interband contribution
        if self.mu_c > self.hbar * omega / 2:
            sigma_inter = 0
        else:
            sigma_inter = (self.e ** 2 / (4 * self.hbar)) * \
                          (1 + (1j / np.pi) * np.log(np.abs((self.hbar * omega - 2 * self.mu_c) /
                                                            (self.hbar * omega + 2 * self.mu_c))))

        return sigma_intra + sigma_inter

    def reflection_coefficient(self, frequency: float,
                               incidence_angle: float = 0) -> complex:
        """
        Calculate reflection coefficient for normal incidence.
        """
        sigma = self.surface_conductivity(frequency)
        eta0 = np.sqrt(mu_0 / epsilon_0)  # Free space impedance

        # For normal incidence on conductive sheet
        Gamma = -eta0 * sigma / (2 + eta0 * sigma)

        return Gamma

    def phase_shift(self, frequency: float, bias_voltage: float) -> float:
        """
        Calculate phase shift introduced by metasurface.

        Parameters:
        -----------
        bias_voltage : float
            Bias voltage applied to graphene (0-5V)

        Returns:
        --------
        phase_shift : float
            Phase shift in radians
        """
        # Update chemical potential based on bias
        self.mu_c = 0.2 * bias_voltage * 1.602e-19  # Simple linear model

        # Calculate reflection phase
        Gamma = self.reflection_coefficient(frequency)
        phase = np.angle(Gamma)

        return phase


class MetasurfaceElement:
    """Single metasurface-enhanced antenna element."""

    def __init__(self,
                 frequency_range: Tuple[float, float] = (2.5e9, 6.5e9),
                 substrate_params: Dict = None):

        self.f_low, self.f_high = frequency_range
        self.f_center = (self.f_low + self.f_high) / 2
        self.wavelength = c / self.f_center

        # Default substrate parameters (Rogers RO4350B)
        self.substrate = substrate_params or {
            'epsilon_r': 3.66,
            'tan_delta': 0.0037,
            'height': 1.524e-3,
            'thickness': 35e-6
        }

        # Initialize metasurface
        self.metasurface = GrapheneMetasurface()

        # Antenna dimensions (optimized for UWB)
        self.dimensions = self.calculate_dimensions()

    def calculate_dimensions(self) -> Dict:
        """Calculate optimized antenna dimensions."""
        # Effective dielectric constant
        epsilon_eff = (self.substrate['epsilon_r'] + 1) / 2 + \
                      (self.substrate['epsilon_r'] - 1) / (
                                  2 * np.sqrt(1 + 12 * self.substrate['height'] / self.wavelength))

        # Patch dimensions (elliptical patch for UWB)
        W = c / (2 * self.f_center * np.sqrt((epsilon_eff + 1) / 2))
        L = W * 0.618  # Golden ratio for elliptical aspect

        # Feed position for impedance matching
        x_f = L / 2
        y_f = W / np.sqrt(epsilon_eff)

        # Ground plane dimensions
        Wg = W + 0.2 * self.wavelength
        Lg = L + 0.2 * self.wavelength

        return {
            'patch_width': W,
            'patch_length': L,
            'feed_x': x_f,
            'feed_y': y_f,
            'ground_width': Wg,
            'ground_length': Lg,
            'slot_radius': 0.15 * W,
            'u_slot_gap': 0.05 * W
        }

    def calculate_s11(self, frequency: np.ndarray) -> np.ndarray:
        """
        Calculate reflection coefficient S11.

        Parameters:
        -----------
        frequency : np.ndarray
            Frequency points in Hz

        Returns:
        --------
        s11 : np.ndarray
            Complex S11 values
        """
        # Transmission line model for microstrip patch
        s11 = np.zeros_like(frequency, dtype=complex)

        for i, f in enumerate(frequency):
            # Calculate input impedance
            Zin = self.input_impedance(f)

            # Calculate S11
            Z0 = 50  # Characteristic impedance
            s11[i] = (Zin - Z0) / (Zin + Z0)

            # Apply metasurface effect
            if self.metasurface:
                phase_shift = self.metasurface.phase_shift(f, bias_voltage=2.5)
                s11[i] *= np.exp(1j * phase_shift)

        return s11

    def input_impedance(self, frequency: float) -> complex:
        """
        Calculate input impedance using cavity model.
        """
        w = 2 * np.pi * frequency
        epsilon_r = self.substrate['epsilon_r']
        h = self.substrate['height']

        # Effective dimensions
        W_eff = self.dimensions['patch_width'] + 0.412 * h * (epsilon_r + 0.3) / (epsilon_r - 0.258)
        L_eff = self.dimensions['patch_length'] + 0.412 * h * (epsilon_r + 0.3) / (epsilon_r - 0.258)

        # Cavity model
        k = w * np.sqrt(epsilon_0 * epsilon_r * mu_0)
        Z_cavity = 1j * 377 / np.sqrt(epsilon_r) * np.tan(k * h)

        # Radiation resistance
        G = self.radiation_conductance(frequency)
        Rr = 1 / (2 * G) if G > 0 else 1e6

        # Loss resistance
        tan_d = self.substrate['tan_delta']
        Rl = 1 / (w * epsilon_0 * epsilon_r * tan_d * W_eff * L_eff / h)

        # Total input impedance
        Zin = 1 / (1 / Rr + 1 / Rl + 1 / Z_cavity)

        return Zin

    def radiation_conductance(self, frequency: float) -> float:
        """Calculate radiation conductance."""
        k0 = 2 * np.pi * frequency / c
        W = self.dimensions['patch_width']

        # For dominant TM10 mode
        G = W / (120 * self.wavelength) * (1 - (k0 * W) ** 2 / 24)

        return G

    def near_field(self,
                   x_grid: np.ndarray,
                   y_grid: np.ndarray,
                   z: float,
                   frequency: float) -> np.ndarray:
        """
        Calculate near-field distribution.
        """
        k0 = 2 * np.pi * frequency / c
        W = self.dimensions['patch_width']
        L = self.dimensions['patch_length']

        # Assuming sinusoidal current distribution
        E_field = np.zeros_like(x_grid, dtype=complex)

        for i in range(x_grid.shape[0]):
            for j in range(x_grid.shape[1]):
                x = x_grid[i, j]
                y = y_grid[i, j]

                if abs(x) <= W / 2 and abs(y) <= L / 2:
                    # Inside patch
                    E_field[i, j] = np.sin(np.pi * (x + W / 2) / W) * \
                                    np.exp(-1j * k0 * z)
                else:
                    # Outside patch - approximate decay
                    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
                    E_field[i, j] = np.exp(-1j * k0 * r) / r

        return E_field


class MetasurfaceArray:
    """8x8 reconfigurable metasurface antenna array."""

    def __init__(self,
                 n_elements: Tuple[int, int] = (8, 8),
                 frequency_range: Tuple[float, float] = (2.5e9, 6.5e9),
                 substrate_params: Dict = None):

        self.nx, self.ny = n_elements
        self.n_elements = n_elements[0] * n_elements[1]

        # Non-uniform spacing optimized by genetic algorithm
        self.positions = self.optimize_element_positions()

        # Create antenna elements
        self.elements = []
        for i in range(self.n_elements):
            element = MetasurfaceElement(
                frequency_range=frequency_range,
                substrate_params=substrate_params
            )
            self.elements.append(element)

        # Feed network
        self.feed_network = CorporateFeedNetwork(self.n_elements)

        # Mutual coupling matrix
        self.coupling_matrix = None

    def optimize_element_positions(self) -> np.ndarray:
        """
        Optimize element positions using genetic algorithm
        to minimize mutual coupling and grating lobes.
        """
        # Genetic algorithm parameters
        pop_size = 100
        n_generations = 50

        # Initial random population
        population = []
        for _ in range(pop_size):
            # Start with uniform spacing
            positions = np.zeros((self.n_elements, 2))

            # Add random perturbations
            for i in range(self.n_elements):
                xi = (i % self.nx) * 0.025  # 25mm nominal
                yi = (i // self.nx) * 0.025

                # Add perturbation (±3mm)
                positions[i, 0] = xi + np.random.uniform(-0.003, 0.003)
                positions[i, 1] = yi + np.random.uniform(-0.003, 0.003)

            population.append(positions)

        # Genetic algorithm main loop (simplified)
        best_positions = population[0]
        best_fitness = -np.inf

        for generation in range(n_generations):
            fitness_scores = []

            for positions in population:
                fitness = self.evaluate_positions(positions)
                fitness_scores.append(fitness)

                if fitness > best_fitness:
                    best_fitness = fitness
                    best_positions = positions

            # Selection, crossover, mutation
            population = self.evolve_population(population, fitness_scores)

        return best_positions

    def evaluate_positions(self, positions: np.ndarray) -> float:
        """Evaluate fitness of element positions."""
        # Calculate minimum distance
        min_dist = np.inf
        for i in range(self.n_elements):
            for j in range(i + 1, self.n_elements):
                dist = np.linalg.norm(positions[i] - positions[j])
                min_dist = min(min_dist, dist)

        # Calculate grating lobe condition
        max_spacing = np.max(np.std(positions, axis=0))

        # Fitness function
        fitness = min_dist - 10 * max_spacing

        return fitness

    def evolve_population(self, population: List, fitness_scores: List) -> List:
        """Evolve population using genetic operators."""
        # Tournament selection
        new_population = []
        n_pop = len(population)

        for _ in range(n_pop):
            # Select two parents
            idx1 = np.random.choice(n_pop, size=2, p=softmax(fitness_scores))
            parent1 = population[idx1[0]]
            parent2 = population[idx1[1]]

            # Crossover
            child = self.crossover(parent1, parent2)

            # Mutation
            if np.random.random() < 0.1:
                child = self.mutate(child)

            new_population.append(child)

        return new_population

    def calculate_s_parameters(self,
                               frequency: np.ndarray,
                               include_coupling: bool = True) -> np.ndarray:
        """
        Calculate full S-parameter matrix for the array.

        Returns:
        --------
        S : np.ndarray
            Shape: (n_elements, n_elements, n_frequencies)
        """
        n_freq = len(frequency)
        S = np.zeros((self.n_elements, self.n_elements, n_freq), dtype=complex)

        # Calculate self-impedances
        for i in range(self.n_elements):
            S[i, i, :] = self.elements[i].calculate_s11(frequency)

        if include_coupling:
            # Calculate mutual coupling
            for i in range(self.n_elements):
                for j in range(i + 1, self.n_elements):
                    # Calculate coupling based on distance
                    dist = np.linalg.norm(self.positions[i] - self.positions[j])

                    # Friis transmission equation for coupling
                    lambda_f = c / frequency
                    coupling = (lambda_f / (4 * np.pi * dist)) * \
                               np.exp(-1j * 2 * np.pi * dist / lambda_f)

                    S[i, j, :] = coupling
                    S[j, i, :] = coupling

        self.coupling_matrix = np.mean(np.abs(S), axis=2)

        return S

    def beamforming(self,
                    target_direction: Tuple[float, float],
                    frequency: float) -> np.ndarray:
        """
        Calculate beamforming weights for target direction.

        Parameters:
        -----------
        target_direction : Tuple[float, float]
            (theta, phi) in radians

        Returns:
        --------
        weights : np.ndarray
            Complex weights for each element
        """
        theta, phi = target_direction
        k = 2 * np.pi * frequency / c

        weights = np.zeros(self.n_elements, dtype=complex)

        for i in range(self.n_elements):
            # Phase shift for beam steering
            r = self.positions[i]
            phase_shift = k * (r[0] * np.sin(theta) * np.cos(phi) +
                               r[1] * np.sin(theta) * np.sin(phi))

            weights[i] = np.exp(-1j * phase_shift)

        # Apply window for sidelobe reduction
        window = np.hanning(self.n_elements).reshape(self.nx, self.ny).flatten()
        weights *= window

        return weights

    def adaptive_focusing(self,
                          target_point: Tuple[float, float, float],
                          frequency: float) -> np.ndarray:
        """
        Calculate weights for near-field focusing.
        """
        tx, ty, tz = target_point
        k = 2 * np.pi * frequency / c

        weights = np.zeros(self.n_elements, dtype=complex)

        for i in range(self.n_elements):
            x, y = self.positions[i]
            dist = np.sqrt((x - tx) ** 2 + (y - ty) ** 2 + tz ** 2)

            # Time reversal focusing
            weights[i] = np.exp(1j * k * dist)

        # Normalize
        weights /= np.linalg.norm(weights)

        return weights


class CorporateFeedNetwork:
    """Stripline corporate feed network with phase shifters."""

    def __init__(self, n_elements: int):
        self.n_elements = n_elements
        self.phase_shifters = np.zeros(n_elements)
        self.amplitude_weights = np.ones(n_elements)

    def set_phase_shifts(self, phases: np.ndarray):
        """Set phase shifts for beam steering."""
        self.phase_shifters = phases % (2 * np.pi)

    def set_amplitude_weights(self, weights: np.ndarray):
        """Set amplitude tapering."""
        self.amplitude_weights = weights

    def calculate_s_matrix(self, frequency: float) -> np.ndarray:
        """Calculate S-parameters of feed network."""
        # T-junction model for corporate feed
        S = np.zeros((self.n_elements + 1, self.n_elements + 1), dtype=complex)

        # Input port
        S[0, 0] = 0  # Well matched

        # Output ports with phase shifts
        for i in range(self.n_elements):
            phase = self.phase_shifters[i]
            amplitude = self.amplitude_weights[i]

            # Equal power division with phase shift
            S[0, i + 1] = amplitude * np.exp(1j * phase) / np.sqrt(self.n_elements)
            S[i + 1, 0] = S[0, i + 1]

            # Output port matching
            S[i + 1, i + 1] = 0

        return S


def softmax(x):
    """Softmax function for selection probabilities."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()