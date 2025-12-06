"""
Active Deep Thermography - Main Pipeline
IEEE Transactions on Antennas and Propagation
Breast Cancer Detection System
"""

import argparse
import logging
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from antennas.metasurface_design import MetasurfaceArray
from forward_model.dataset_generator import DatasetGenerator
from neural_networks.hpinn import HPINN
from gui.main_window import ClinicalGUI
from experimental.measurement_control import MeasurementSystem
from utils.metrics import PerformanceEvaluator

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ActiveDeepThermography:
    """Main class orchestrating the complete system."""

    def __init__(self, config_path="config/parameters.py"):
        self.config = self.load_config(config_path)
        self.initialize_system()

    def load_config(self, config_path):
        """Load configuration parameters."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config

    def initialize_system(self):
        """Initialize all system components."""
        logger.info("Initializing Active Deep Thermography System...")

        # Initialize antenna array
        self.array = MetasurfaceArray(
            n_elements=self.config.N_ELEMENTS,
            frequency_range=self.config.FREQUENCY_RANGE,
            substrate_params=self.config.SUBSTRATE_PARAMS
        )

        # Initialize forward model
        self.forward_model = DatasetGenerator(
            array=self.array,
            phantom_params=self.config.PHANTOM_PARAMS
        )

        # Initialize neural networks
        self.hpinn = HPINN(
            input_shape=self.config.INPUT_SHAPE,
            output_shape=self.config.OUTPUT_SHAPE,
            physics_constraints=True
        )

        # Initialize measurement system
        self.measurement_sys = MeasurementSystem(
            vna_address=self.config.VNA_ADDRESS,
            thermal_camera_id=self.config.CAMERA_ID
        )

        logger.info("System initialization complete.")

    def generate_training_data(self, n_samples=50000):
        """Generate synthetic training data using multi-physics simulations."""
        logger.info(f"Generating {n_samples} training samples...")

        dataset = self.forward_model.generate_dataset(
            n_samples=n_samples,
            tumor_params=self.config.TUMOR_PARAMS_RANGE,
            noise_level=self.config.NOISE_LEVEL
        )

        # Save dataset
        self.save_dataset(dataset, "training_data.h5")
        return dataset

    def train_hpinn(self, dataset_path="training_data.h5"):
        """Train the hierarchical physics-informed neural network."""
        logger.info("Training HPINN...")

        self.hpinn.build_model()

        history = self.hpinn.train(
            dataset_path=dataset_path,
            epochs=self.config.EPOCHS,
            batch_size=self.config.BATCH_SIZE,
            validation_split=0.1
        )

        # Save trained model
        self.hpinn.save_model("models/hpinn_model.h5")

        # Plot training history
        self.plot_training_history(history)

        return history

    def experimental_validation(self, phantom_path):
        """Perform experimental validation with physical phantom."""
        logger.info("Starting experimental validation...")

        # Load phantom
        phantom_data = self.load_phantom(phantom_path)

        # Configure measurement system
        self.measurement_sys.configure(
            frequency_points=self.config.FREQUENCY_POINTS,
            power_level=self.config.POWER_LEVEL,
            averaging=self.config.AVERAGING
        )

        # Perform scan
        s_parameters = self.measurement_sys.scan_phantom(
            phantom=phantom_data,
            scan_pattern=self.config.SCAN_PATTERN
        )

        # Reconstruct using trained HPINN
        reconstruction = self.hpinn.reconstruct(s_parameters)

        # Compare with ground truth
        evaluator = PerformanceEvaluator()
        metrics = evaluator.evaluate(
            reconstruction=reconstruction,
            ground_truth=phantom_data['temperature']
        )

        logger.info(f"Validation metrics: {metrics}")

        return reconstruction, metrics

    def clinical_interface(self):
        """Launch clinical GUI for real-time imaging."""
        logger.info("Launching clinical interface...")

        app = QApplication(sys.argv)
        gui = ClinicalGUI(
            hpinn_model=self.hpinn,
            measurement_sys=self.measurement_sys,
            config=self.config
        )
        gui.show()
        sys.exit(app.exec_())

    def federated_learning_update(self, clients_data):
        """Perform federated learning update from multiple institutions."""
        logger.info("Performing federated learning update...")

        from gui.federated_server import FederatedServer
        server = FederatedServer(model=self.hpinn)

        # Aggregate updates from clients
        global_update = server.aggregate_updates(clients_data)

        # Update global model
        self.hpinn.apply_federated_update(global_update)

        # Save updated model
        self.hpinn.save_model("models/hpinn_federated.h5")

        logger.info("Federated learning complete.")

    def save_dataset(self, dataset, filename):
        """Save dataset to HDF5 file."""
        import h5py

        with h5py.File(filename, 'w') as f:
            f.create_dataset('s_parameters', data=dataset['s_parameters'])
            f.create_dataset('permittivity', data=dataset['permittivity'])
            f.create_dataset('temperature', data=dataset['temperature'])
            f.create_dataset('metadata', data=str(dataset['metadata']))

    def plot_training_history(self, history):
        """Plot training and validation metrics."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        # Loss curves
        axes[0, 0].plot(history['loss'], label='Training')
        axes[0, 0].plot(history['val_loss'], label='Validation')
        axes[0, 0].set_title('Loss Evolution')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        # Physics constraint loss
        axes[0, 1].plot(history['physics_loss'], label='Physics')
        axes[0, 1].set_title('Physics Constraint Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].grid(True)

        # Temperature RMSE
        axes[1, 0].plot(history['temp_rmse'], label='Training')
        axes[1, 0].plot(history['val_temp_rmse'], label='Validation')
        axes[1, 0].set_title('Temperature RMSE')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('RMSE (°C)')
        axes[1, 0].legend()
        axes[1, 0].grid(True)

        # Localization error
        axes[1, 1].plot(history['loc_error'], label='Training')
        axes[1, 1].plot(history['val_loc_error'], label='Validation')
        axes[1, 1].set_title('Localization Error')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Error (mm)')
        axes[1, 1].legend()
        axes[1, 1].grid(True)

        plt.tight_layout()
        plt.savefig('training_history.png', dpi=300)
        plt.close()


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Active Deep Thermography System')
    parser.add_argument('--mode', type=str, choices=['train', 'validate', 'gui', 'federated'],
                        default='gui', help='Operation mode')
    parser.add_argument('--data_path', type=str, help='Path to data')
    parser.add_argument('--phantom_path', type=str, help='Path to phantom data')
    parser.add_argument('--n_samples', type=int, default=50000, help='Number of training samples')

    args = parser.parse_args()

    # Initialize system
    system = ActiveDeepThermography()

    if args.mode == 'train':
        # Generate data and train
        system.generate_training_data(n_samples=args.n_samples)
        system.train_hpinn()

    elif args.mode == 'validate':
        # Experimental validation
        if args.phantom_path:
            reconstruction, metrics = system.experimental_validation(args.phantom_path)
            print(f"Validation Results: {metrics}")
        else:
            logger.error("Phantom path required for validation mode")

    elif args.mode == 'gui':
        # Launch clinical interface
        system.clinical_interface()

    elif args.mode == 'federated':
        # Federated learning
        clients_data = load_clients_data(args.data_path)
        system.federated_learning_update(clients_data)


if __name__ == "__main__":
    main()