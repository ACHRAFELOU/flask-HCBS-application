"""
Configuration parameters for Active Deep Thermography System
IEEE Transactions on Antennas and Propagation
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, List


@dataclass
class SystemConfig:
    """Main system configuration."""

    # Antenna array parameters
    N_ELEMENTS: Tuple[int, int] = (8, 8)
    FREQUENCY_RANGE: Tuple[float, float] = (2.5e9, 6.5e9)  # Hz
    FREQUENCY_POINTS: int = 201

    SUBSTRATE_PARAMS: Dict = None

    # Breast phantom parameters
    PHANTOM_PARAMS: Dict = None

    # Tumor parameters range
    TUMOR_PARAMS_RANGE: Dict = None

    # Neural network parameters
    INPUT_SHAPE: Tuple[int, int, int] = (64, 64, 102)  # S-parameters
    OUTPUT_SHAPE: Tuple[int, int] = (128, 128)  # Temperature map

    # Training parameters
    EPOCHS: int = 100
    BATCH_SIZE: int = 16
    LEARNING_RATE: float = 1e-4
    VALIDATION_SPLIT: float = 0.1

    # Measurement system
    VNA_ADDRESS: str = "TCPIP0::192.168.1.100::INSTR"
    CAMERA_ID: int = 0
    POWER_LEVEL: float = 0.0  # dBm
    AVERAGING: int = 16

    # Scan parameters
    SCAN_PATTERN: str = "Spiral"
    SCAN_RESOLUTION: float = 1.0  # mm
    SCAN_SPEED: float = 10.0  # mm/s

    # Safety limits
    MAX_SAR: float = 2.0  # W/kg
    MAX_TEMPERATURE: float = 41.0  # °C

    # GUI parameters
    GUI_REFRESH_RATE: float = 10.0  # Hz
    COLOR_MAP: str = "viridis"

    # Federated learning
    FEDERATED_ROUNDS: int = 100
    MIN_CLIENTS: int = 3
    PRIVACY_EPSILON: float = 0.5

    def __post_init__(self):
        """Initialize default values."""
        if self.SUBSTRATE_PARAMS is None:
            self.SUBSTRATE_PARAMS = {
                'epsilon_r': 3.66,
                'tan_delta': 0.0037,
                'height': 1.524e-3,
                'conductivity': 5.8e7
            }

        if self.PHANTOM_PARAMS is None:
            self.PHANTOM_PARAMS = {
                'radius': 80e-3,
                'skin_thickness': 2e-3,
                'layers': ['skin', 'fat', 'glandular'],
                'dielectric_properties': {
                    'skin': {'epsilon_r': 38.0, 'sigma': 1.45},
                    'fat': {'epsilon_r': 5.3, 'sigma': 0.11},
                    'glandular': {'epsilon_r': 21.0, 'sigma': 1.23},
                    'tumor': {'epsilon_r': 50.0, 'sigma': 1.8}
                }
            }

        if self.TUMOR_PARAMS_RANGE is None:
            self.TUMOR_PARAMS_RANGE = {
                'diameter': (2e-3, 15e-3),  # m
                'depth': (5e-3, 40e-3),  # m
                'delta_t': (0.05, 1.5),  # °C
                'position_x': (-0.04, 0.04),  # m
                'position_y': (-0.04, 0.04)  # m
            }


@dataclass
class PhysicsConstants:
    """Physical constants for simulations."""

    # Fundamental constants
    c: float = 299792458.0  # Speed of light, m/s
    epsilon_0: float = 8.854187817e-12  # Vacuum permittivity, F/m
    mu_0: float = 4 * np.pi * 1e-7  # Vacuum permeability, H/m

    # Thermal properties
    rho_blood: float = 1050.0  # Blood density, kg/m³
    cp_blood: float = 3600.0  # Blood specific heat, J/kg·K
    k_tissue: float = 0.5  # Tissue thermal conductivity, W/m·K

    # Metabolic rates (W/m³)
    qm_healthy: float = 700.0
    qm_tumor: float = 25000.0

    # Perfusion rates (1/s)
    wb_healthy: float = 0.0005
    wb_tumor: float = 0.008

    # Temperature coefficients
    alpha_sigma: float = 0.015  # °C⁻¹
    beta_sigma: float = 0.0003  # °C⁻²


@dataclass
class NeuralNetworkConfig:
    """Neural network architecture configuration."""

    # EMINet (Stage 1) parameters
    EMINET_FILTERS: int = 64
    EMINET_BLOCKS: int = 4
    EMINET_ATTENTION: bool = True

    # ThermoNet (Stage 2) parameters
    THERMONET_LSTM_LAYERS: int = 2
    THERMONET_CONVLSTM: bool = True
    THERMONET_UNET_DEPTH: int = 4

    # Training parameters
    LOSS_WEIGHTS: Dict = None
    OPTIMIZER: str = "AdamW"
    SCHEDULER: str = "cosine"

    def __post_init__(self):
        if self.LOSS_WEIGHTS is None:
            self.LOSS_WEIGHTS = {
                'data_loss': 1.0,
                'physics_loss': 0.1,
                'tv_loss': 0.01,
                'boundary_loss': 0.05
            }


@dataclass
class PerformanceTargets:
    """Performance targets for the system."""

    # Detection performance
    MIN_TUMOR_SIZE: float = 3e-3  # m
    MIN_TEMPERATURE_RESOLUTION: float = 0.05  # °C
    MAX_LOCALIZATION_ERROR: float = 1e-3  # m

    # Imaging performance
    SPATIAL_RESOLUTION: float = 2e-3  # m
    DEPTH_RESOLUTION: float = 5e-3  # m
    TEMPORAL_RESOLUTION: float = 1.0  # s

    # Clinical performance
    TARGET_SENSITIVITY: float = 0.95
    TARGET_SPECIFICITY: float = 0.90
    ROC_AUC_TARGET: float = 0.97


# Create configuration instances
SYSTEM_CONFIG = SystemConfig()
PHYSICS_CONSTANTS = PhysicsConstants()
NN_CONFIG = NeuralNetworkConfig()
PERFORMANCE_TARGETS = PerformanceTargets()

# Export all configurations
__all__ = [
    'SYSTEM_CONFIG',
    'PHYSICS_CONSTANTS',
    'NN_CONFIG',
    'PERFORMANCE_TARGETS'
]