"""
Coupled Electromagnetic-Thermal Solver
Integration of Maxwell's equations with Pennes bioheat equation
"""

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.constants import c, epsilon_0, mu_0
import numba
from typing import Dict, Tuple, Callable


class CoupledEMThermalSolver:
    """
    Solves coupled electromagnetic-thermal equations for breast tissue.
    """

    def __init__(self,
                 grid_shape: Tuple[int, int, int],
                 grid_spacing: float = 1e-3,
                 tissue_properties: Dict = None):

        self.nx, self.ny, self.nz = grid_shape
        self.dx = grid_spacing
        self.N = self.nx * self.ny * self.nz

        # Default tissue properties
        self.tissue = tissue_properties or self.default_tissue_properties()

        # Initialize fields
        self.E_field = np.zeros((self.nx, self.ny, self.nz, 3), dtype=complex)
        self.H_field = np.zeros((self.nx, self.ny, self.nz, 3), dtype=complex)
        self.T_field = np.ones((self.nx, self.nz, self.nz)) * 37.0  # °C
        self.sigma_field = np.zeros((self.nx, self.ny, self.nz))

        # Precompute operators
        self.laplacian = self.build_laplacian()
        self.gradient = self.build_gradient()

    def default_tissue_properties(self) -> Dict:
        """Default dielectric and thermal properties."""
        return {
            'skin': {
                'epsilon_r': 38.0,
                'sigma': 1.45,
                'rho': 1100,
                'cp': 3500,
                'k': 0.37,
                'w_b': 0.001,
                'q_m': 700
            },
            'fat': {
                'epsilon_r': 5.3,
                'sigma': 0.11,
                'rho': 920,
                'cp': 2500,
                'k': 0.21,
                'w_b': 0.0003,
                'q_m': 400
            },
            'glandular': {
                'epsilon_r': 21.0,
                'sigma': 1.23,
                'rho': 1050,
                'cp': 3800,
                'k': 0.48,
                'w_b': 0.0008,
                'q_m': 900
            },
            'tumor': {
                'epsilon_r': 50.0,
                'sigma': 1.8,
                'rho': 1080,
                'cp': 3900,
                'k': 0.52,
                'w_b': 0.008,
                'q_m': 25000
            }
        }

    def temperature_dependent_sigma(self, T: float, tissue_type: str) -> float:
        """
        Calculate temperature-dependent conductivity.

        sigma(T) = sigma_37 * [1 + α(T-37) + β(T-37)²]
        """
        sigma_37 = self.tissue[tissue_type]['sigma']
        alpha = 0.015  # °C⁻¹
        beta = 0.0003  # °C⁻²

        delta_T = T - 37.0
        sigma = sigma_37 * (1 + alpha * delta_T + beta * delta_T ** 2)

        return sigma

    def build_laplacian(self) -> sparse.csr_matrix:
        """Build 3D Laplacian operator."""
        # 7-point stencil for 3D Laplacian
        diag = -6 * np.ones(self.N)
        off_diag = np.ones(self.N - 1)

        # x-direction neighbors
        for i in range(self.N):
            if i % self.nx != self.nx - 1:
                off_diag[i] = 1

        # Create sparse matrix
        L = sparse.diags([diag, off_diag, off_diag,
                          off_diag, off_diag, off_diag, off_diag],
                         [0, 1, -1, self.nx, -self.nx,
                          self.nx * self.ny, -self.nx * self.ny])

        return L.tocsr() / (self.dx ** 2)

    def build_gradient(self) -> Tuple[sparse.csr_matrix, ...]:
        """Build gradient operators."""
        # Forward differences
        Dx = sparse.diags([-1, 1], [0, 1], shape=(self.N, self.N))
        Dy = sparse.diags([-1, 1], [0, self.nx], shape=(self.N, self.N))
        Dz = sparse.diags([-1, 1], [0, self.nx * self.ny], shape=(self.N, self.N))

        # Apply boundary conditions
        for i in range(self.N):
            if i % self.nx == self.nx - 1:
                Dx[i, i] = 0
            if i // self.nx % self.ny == self.ny - 1:
                Dy[i, i] = 0
            if i // (self.nx * self.ny) == self.nz - 1:
                Dz[i, i] = 0

        return Dx.tocsr() / self.dx, Dy.tocsr() / self.dx, Dz.tocsr() / self.dx

    def solve_maxwell(self,
                      frequency: float,
                      source: np.ndarray,
                      max_iter: int = 100,
                      tolerance: float = 1e-6) -> np.ndarray:
        """
        Solve Maxwell's equations using FDFD method.

        Parameters:
        -----------
        frequency : float
            Source frequency in Hz
        source : np.ndarray
            Source current distribution (N × 3)

        Returns:
        --------
        E_field : np.ndarray
            Electric field distribution
        """
        omega = 2 * np.pi * frequency
        k0 = omega / c

        # Build Maxwell operator: ∇×(∇×) - k0²ε
        curl_curl = self.build_curl_curl()

        # Complex permittivity including conductivity
        epsilon = self.build_permittivity_matrix(omega)

        # Combined operator
        A = curl_curl - k0 ** 2 * epsilon

        # Solve for each polarization
        E = np.zeros((self.N, 3), dtype=complex)

        for pol in range(3):
            b = source[:, pol]

            # Solve linear system
            E[:, pol] = spsolve(A, b)

        # Reshape to 3D grid
        E_field = E.reshape((self.nx, self.ny, self.nz, 3))

        return E_field

    def build_curl_curl(self) -> sparse.csr_matrix:
        """Build curl-curl operator for Maxwell's equations."""
        # This is a simplified implementation
        # Full implementation would use Yee grid

        Dx, Dy, Dz = self.gradient

        # Build curl operator
        curl = sparse.bmat([
            [None, -Dz, Dy],
            [Dz, None, -Dx],
            [-Dy, Dx, None]
        ])

        # Curl-curl = ∇×(∇×) = -∇² + ∇(∇·)
        laplacian_3d = sparse.kron(sparse.eye(3), self.laplacian)

        # Gradient of divergence term
        grad_div = sparse.bmat([
            [Dx @ Dx, Dx @ Dy, Dx @ Dz],
            [Dy @ Dx, Dy @ Dy, Dy @ Dz],
            [Dz @ Dx, Dz @ Dy, Dz @ Dz]
        ])

        curl_curl = -laplacian_3d + grad_div

        return curl_curl

    def build_permittivity_matrix(self, omega: float) -> sparse.dia_matrix:
        """Build complex permittivity matrix."""
        epsilon_r = np.ones(self.N)
        sigma = np.ones(self.N)

        # Assign tissue properties
        # This would be filled based on tissue segmentation

        # Complex permittivity: ε = ε' - jσ/ωε₀
        epsilon_complex = epsilon_0 * epsilon_r - 1j * sigma / omega

        return sparse.diags(epsilon_complex)

    def calculate_sar(self, E_field: np.ndarray, sigma: np.ndarray) -> np.ndarray:
        """
        Calculate Specific Absorption Rate.

        SAR = σ|E|² / (2ρ)
        """
        # Reshape fields
        E_mag = np.sqrt(np.sum(np.abs(E_field) ** 2, axis=-1))

        # Calculate SAR (W/kg)
        SAR = sigma * E_mag ** 2 / (2 * self.tissue_density())

        return SAR

    def tissue_density(self) -> np.ndarray:
        """Get tissue density distribution."""
        rho = np.ones((self.nx, self.ny, self.nz))
        # Assign based on tissue type
        return rho * 1000  # kg/m³

    def solve_bioheat(self,
                      SAR: np.ndarray,
                      time_step: float = 1.0,
                      n_steps: int = 100) -> np.ndarray:
        """
        Solve Pennes bioheat equation.

        ρc_p ∂T/∂t = ∇·(k∇T) + ρ_b c_{p,b} ω_b (T_a - T) + q_m + q_r
        """
        # Discretization
        dt = time_step
        T = self.T_field.flatten()

        # Thermal properties
        rho = self.tissue_density().flatten()
        cp = self.tissue_heat_capacity().flatten()
        k = self.tissue_thermal_conductivity().flatten()

        # Blood perfusion parameters
        rho_b = 1050  # kg/m³
        cp_b = 3600  # J/kg·K
        w_b = self.tissue_perfusion_rate().flatten()
        T_a = 37.0  # Arterial temperature

        # Metabolic heat
        q_m = self.tissue_metabolic_heat().flatten()

        # Build matrices
        A_conduct = self.build_thermal_conduction(k)
        A_perf = sparse.diags(rho_b * cp_b * w_b)
        M = sparse.diags(rho * cp / dt)

        # Time stepping
        for step in range(n_steps):
            # Right-hand side
            b = (M @ T +
                 q_m +
                 rho_b * cp_b * w_b * T_a +
                 SAR.flatten() * rho)

            # Left-hand side matrix
            A = M + A_conduct + A_perf

            # Solve
            T = spsolve(A, b)

            # Update conductivity based on temperature
            self.update_conductivity(T.reshape(self.T_field.shape))

        self.T_field = T.reshape(self.T_field.shape)
        return self.T_field

    def build_thermal_conduction(self, k: np.ndarray) -> sparse.csr_matrix:
        """Build thermal conduction operator."""
        # Diffusion operator: ∇·(k∇)
        Dx, Dy, Dz = self.gradient

        # Anisotropic diffusion
        Kx = sparse.diags(k) @ Dx
        Ky = sparse.diags(k) @ Dy
        Kz = sparse.diags(k) @ Dz

        A = Dx.T @ Kx + Dy.T @ Ky + Dz.T @ Kz

        return A

    def tissue_heat_capacity(self) -> np.ndarray:
        """Get tissue heat capacity distribution."""
        cp = np.ones((self.nx, self.ny, self.nz))
        # Assign based on tissue type
        return cp * 3500  # J/kg·K

    def tissue_thermal_conductivity(self) -> np.ndarray:
        """Get tissue thermal conductivity."""
        k = np.ones((self.nx, self.ny, self.nz))
        # Assign based on tissue type
        return k * 0.5  # W/m·K

    def tissue_perfusion_rate(self) -> np.ndarray:
        """Get blood perfusion rate."""
        w_b = np.ones((self.nx, self.ny, self.nz)) * 0.0005
        # Higher in tumor regions
        return w_b

    def tissue_metabolic_heat(self) -> np.ndarray:
        """Get metabolic heat generation."""
        q_m = np.ones((self.nx, self.ny, self.nz)) * 700
        # Higher in tumor regions
        return q_m

    def update_conductivity(self, T: np.ndarray):
        """Update conductivity based on temperature."""
        # Update sigma_field based on local temperature and tissue type
        for i in range(self.nx):
            for j in range(self.ny):
                for k in range(self.nz):
                    tissue_type = self.get_tissue_type(i, j, k)
                    self.sigma_field[i, j, k] = \
                        self.temperature_dependent_sigma(T[i, j, k], tissue_type)

    def get_tissue_type(self, i: int, j: int, k: int) -> str:
        """Determine tissue type at grid point."""
        # Simplified - would use segmentation in real implementation
        if k < 2:  # Skin layer
            return 'skin'
        elif k < 20:  # Fat layer
            return 'fat'
        else:  # Glandular tissue
            return 'glandular'

    def coupled_simulation(self,
                           frequency: float,
                           source: np.ndarray,
                           n_iterations: int = 5) -> Dict:
        """
        Perform coupled EM-thermal simulation.

        Returns:
        --------
        results : Dict
            Contains E_field, T_field, SAR, etc.
        """
        results = {}

        for iter in range(n_iterations):
            print(f"Iteration {iter + 1}/{n_iterations}")

            # 1. Solve Maxwell's equations
            E_field = self.solve_maxwell(frequency, source)

            # 2. Calculate SAR
            SAR = self.calculate_sar(E_field, self.sigma_field)

            # 3. Solve bioheat equation
            T_field = self.solve_bioheat(SAR)

            # 4. Update conductivity
            self.update_conductivity(T_field)

        results['E_field'] = E_field
        results['T_field'] = T_field
        results['SAR'] = SAR
        results['sigma_field'] = self.sigma_field

        return results


@numba.jit(nopython=True, parallel=True)
def compute_s_parameters_parallel(E_fields, positions, frequency):
    """
    Compute S-parameters in parallel using Numba.
    """
    n_elements = len(positions)
    n_freq = len(frequency)
    S = np.zeros((n_elements, n_elements, n_freq), dtype=np.complex128)

    k = 2 * np.pi * frequency / c

    for i in numba.prange(n_elements):
        for j in range(n_elements):
            if i == j:
                # Self-impedance
                for f_idx in range(n_freq):
                    S[i, j, f_idx] = compute_reflection(E_fields[i], f_idx)
            else:
                # Mutual coupling
                dist = np.linalg.norm(positions[i] - positions[j])
                for f_idx in range(n_freq):
                    coupling = np.exp(-1j * k[f_idx] * dist) / (4 * np.pi * dist)
                    S[i, j, f_idx] = coupling
                    S[j, i, f_idx] = coupling

    return S


def compute_reflection(E_field, freq_idx):
    """Compute reflection coefficient from E-field."""
    # Simplified implementation
    return -0.1 * np.exp(1j * freq_idx * 0.1)