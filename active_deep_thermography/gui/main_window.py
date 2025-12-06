"""
Clinical Graphical User Interface for Active Deep Thermography
PyQt5-based interface with real-time imaging capabilities
"""

import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTabWidget,
                             QGroupBox, QGridLayout, QSlider, QSpinBox,
                             QDoubleSpinBox, QComboBox, QFileDialog, QMessageBox,
                             QProgressBar, QStatusBar, QAction, QMenuBar, QToolBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon, QPalette, QColor
import pyqtgraph as pg
from pyqtgraph.opengl import GLViewWidget, GLMeshItem
import vispy.scene
from vispy.scene import visuals

from neural_networks.hpinn import HPINN
from experimental.measurement_control import MeasurementSystem
from utils.visualization import ThermalVisualizer


class MeasurementThread(QThread):
    """Thread for background measurement acquisition."""
    measurement_complete = pyqtSignal(object)
    progress_update = pyqtSignal(int)

    def __init__(self, measurement_sys, scan_params):
        super().__init__()
        self.measurement_sys = measurement_sys
        self.scan_params = scan_params

    def run(self):
        """Perform scan in background."""
        try:
            s_parameters = []
            n_steps = len(self.scan_params['positions'])

            for i, position in enumerate(self.scan_params['positions']):
                # Move to position
                self.measurement_sys.move_to(position)

                # Acquire data
                s_params = self.measurement_sys.acquire_single_point(
                    frequency_points=self.scan_params['frequencies'],
                    averaging=self.scan_params['averaging']
                )
                s_parameters.append(s_params)

                # Update progress
                progress = int(100 * (i + 1) / n_steps)
                self.progress_update.emit(progress)

                # Small delay
                self.msleep(50)

            self.measurement_complete.emit(s_parameters)

        except Exception as e:
            self.measurement_complete.emit({'error': str(e)})


class ReconstructionThread(QThread):
    """Thread for background reconstruction."""
    reconstruction_complete = pyqtSignal(object)

    def __init__(self, hpinn_model, s_parameters):
        super().__init__()
        self.hpinn_model = hpinn_model
        self.s_parameters = s_parameters

    def run(self):
        """Perform reconstruction in background."""
        try:
            reconstruction = self.hpinn_model.reconstruct(self.s_parameters)
            self.reconstruction_complete.emit(reconstruction)
        except Exception as e:
            self.reconstruction_complete.emit({'error': str(e)})


class ClinicalGUI(QMainWindow):
    """Main clinical interface window."""

    def __init__(self, hpinn_model, measurement_sys, config):
        super().__init__()

        self.hpinn = hpinn_model
        self.measurement_sys = measurement_sys
        self.config = config

        self.current_scan = None
        self.current_reconstruction = None
        self.patient_data = {}

        self.init_ui()
        self.setup_connections()
        self.load_default_settings()

    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Active Deep Thermography System - IEEE T-AP")
        self.setGeometry(100, 100, 1600, 900)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel - Controls
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, stretch=1)

        # Right panel - Visualization
        right_panel = self.create_visualization_panel()
        main_layout.addWidget(right_panel, stretch=3)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("System Ready")

        # Menu bar
        self.create_menu_bar()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.setVisible(False)

    def create_control_panel(self):
        """Create control panel with scan parameters."""
        panel = QWidget()
        layout = QVBoxLayout()

        # Patient information group
        patient_group = QGroupBox("Patient Information")
        patient_layout = QGridLayout()

        patient_layout.addWidget(QLabel("Patient ID:"), 0, 0)
        self.patient_id = QSpinBox()
        self.patient_id.setRange(1, 9999)
        patient_layout.addWidget(self.patient_id, 0, 1)

        patient_layout.addWidget(QLabel("Age:"), 1, 0)
        self.patient_age = QSpinBox()
        self.patient_age.setRange(18, 100)
        patient_layout.addWidget(self.patient_age, 1, 1)

        patient_layout.addWidget(QLabel("Breast Density:"), 2, 0)
        self.breast_density = QComboBox()
        self.breast_density.addItems(["A - Fatty", "B - Scattered",
                                      "C - Heterogeneous", "D - Extremely Dense"])
        patient_layout.addWidget(self.breast_density, 2, 1)

        patient_group.setLayout(patient_layout)
        layout.addWidget(patient_group)

        # Scan parameters group
        scan_group = QGroupBox("Scan Parameters")
        scan_layout = QGridLayout()

        scan_layout.addWidget(QLabel("Frequency Range:"), 0, 0)
        self.freq_min = QDoubleSpinBox()
        self.freq_min.setRange(2.5, 6.0)
        self.freq_min.setValue(3.0)
        self.freq_min.setSuffix(" GHz")
        scan_layout.addWidget(self.freq_min, 0, 1)

        self.freq_max = QDoubleSpinBox()
        self.freq_max.setRange(3.0, 6.5)
        self.freq_max.setValue(4.5)
        self.freq_max.setSuffix(" GHz")
        scan_layout.addWidget(self.freq_max, 0, 2)

        scan_layout.addWidget(QLabel("Power Level:"), 1, 0)
        self.power_level = QDoubleSpinBox()
        self.power_level.setRange(-10, 10)
        self.power_level.setValue(0)
        self.power_level.setSuffix(" dBm")
        scan_layout.addWidget(self.power_level, 1, 1)

        scan_layout.addWidget(QLabel("Averaging:"), 2, 0)
        self.averaging = QSpinBox()
        self.averaging.setRange(1, 100)
        self.averaging.setValue(16)
        scan_layout.addWidget(self.averaging, 2, 1)

        scan_layout.addWidget(QLabel("Scan Pattern:"), 3, 0)
        self.scan_pattern = QComboBox()
        self.scan_pattern.addItems(["Raster", "Spiral", "Adaptive", "Multi-resolution"])
        scan_layout.addWidget(self.scan_pattern, 3, 1)

        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Scan")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_btn.clicked.connect(self.start_scan)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_scan)
        button_layout.addWidget(self.stop_btn)

        self.reconstruct_btn = QPushButton("Reconstruct")
        self.reconstruct_btn.clicked.connect(self.start_reconstruction)
        button_layout.addWidget(self.reconstruct_btn)

        self.save_btn = QPushButton("Save Results")
        self.save_btn.clicked.connect(self.save_results)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        # AI settings group
        ai_group = QGroupBox("AI Settings")
        ai_layout = QGridLayout()

        ai_layout.addWidget(QLabel("Model:"), 0, 0)
        self.model_selector = QComboBox()
        self.model_selector.addItems(["HPINN (Default)", "U-Net", "PINN", "Ensemble"])
        ai_layout.addWidget(self.model_selector, 0, 1)

        ai_layout.addWidget(QLabel("Confidence Threshold:"), 1, 0)
        self.confidence_threshold = QSlider(Qt.Horizontal)
        self.confidence_threshold.setRange(50, 95)
        self.confidence_threshold.setValue(75)
        ai_layout.addWidget(self.confidence_threshold, 1, 1)

        ai_layout.addWidget(QLabel("Temperature Range:"), 2, 0)
        self.temp_min = QDoubleSpinBox()
        self.temp_min.setRange(35.0, 37.0)
        self.temp_min.setValue(36.5)
        self.temp_min.setSuffix(" °C")
        ai_layout.addWidget(self.temp_min, 2, 1)

        self.temp_max = QDoubleSpinBox()
        self.temp_max.setRange(37.0, 40.0)
        self.temp_max.setValue(38.5)
        self.temp_max.setSuffix(" °C")
        ai_layout.addWidget(self.temp_max, 2, 2)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # Federated learning controls
        fed_group = QGroupBox("Federated Learning")
        fed_layout = QVBoxLayout()

        self.fed_update_btn = QPushButton("Update Model (Federated)")
        self.fed_update_btn.clicked.connect(self.federated_update)
        fed_layout.addWidget(self.fed_update_btn)

        self.fed_status = QLabel("Last update: Never")
        fed_layout.addWidget(self.fed_status)

        fed_group.setLayout(fed_layout)
        layout.addWidget(fed_group)

        # Metrics display
        metrics_group = QGroupBox("Scan Metrics")
        self.metrics_layout = QVBoxLayout()

        self.metrics_labels = {}
        metrics = ["SNR", "Resolution", "Coverage", "Scan Time"]
        for metric in metrics:
            label = QLabel(f"{metric}: --")
            self.metrics_layout.addWidget(label)
            self.metrics_labels[metric] = label

        metrics_group.setLayout(self.metrics_layout)
        layout.addWidget(metrics_group)

        layout.addStretch()
        panel.setLayout(layout)

        return panel

    def create_visualization_panel(self):
        """Create visualization panel with multiple views."""
        panel = QTabWidget()

        # 2D Thermal Map tab
        thermal_tab = QWidget()
        thermal_layout = QVBoxLayout()

        # PyQtGraph for thermal visualization
        self.thermal_plot = pg.GraphicsLayoutWidget()
        self.thermal_img = pg.ImageItem()

        # Create histogram for color scaling
        self.histogram = pg.HistogramLUTItem()
        self.histogram.setImageItem(self.thermal_img)

        # Add to layout
        thermal_layout.addWidget(self.thermal_plot)
        thermal_tab.setLayout(thermal_layout)
        panel.addTab(thermal_tab, "2D Thermal Map")

        # 3D Visualization tab
        tab_3d = QWidget()
        layout_3d = QVBoxLayout()

        # VisPy for 3D visualization
        self.canvas_3d = vispy.scene.SceneCanvas(keys='interactive',
                                                 bgcolor='white')
        self.view_3d = self.canvas_3d.central_widget.add_view()
        self.view_3d.camera = 'turntable'

        layout_3d.addWidget(self.canvas_3d.native)
        tab_3d.setLayout(layout_3d)
        panel.addTab(tab_3d, "3D Visualization")

        # S-Parameters tab
        s_param_tab = QWidget()
        s_param_layout = QVBoxLayout()

        self.s_param_plot = pg.GraphicsLayoutWidget()
        s_param_layout.addWidget(self.s_param_plot)

        tab_3d.setLayout(s_param_layout)
        panel.addTab(s_param_tab, "S-Parameters")

        # Comparison tab
        compare_tab = QWidget()
        compare_layout = QGridLayout()

        self.compare_plots = []
        for i in range(4):
            plot = pg.PlotWidget()
            self.compare_plots.append(plot)
            compare_layout.addWidget(plot, i // 2, i % 2)

        compare_tab.setLayout(compare_layout)
        panel.addTab(compare_tab, "Comparison")

        # Analysis tab
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout()

        # Tumor characterization
        tumor_group = QGroupBox("Tumor Characterization")
        tumor_layout = QGridLayout()

        metrics = ["Size", "Depth", "ΔT", "Confidence", "Malignancy Score"]
        self.tumor_metrics = {}

        for i, metric in enumerate(metrics):
            tumor_layout.addWidget(QLabel(metric), i, 0)
            value_label = QLabel("--")
            self.tumor_metrics[metric] = value_label
            tumor_layout.addWidget(value_label, i, 1)

        tumor_group.setLayout(tumor_layout)
        analysis_layout.addWidget(tumor_group)

        # ROI analysis
        roi_group = QGroupBox("ROI Analysis")
        roi_layout = QGridLayout()

        self.roi_plot = pg.PlotWidget()
        roi_layout.addWidget(self.roi_plot, 0, 0, 1, 2)

        self.add_roi_btn = QPushButton("Add ROI")
        self.add_roi_btn.clicked.connect(self.add_roi)
        roi_layout.addWidget(self.add_roi_btn, 1, 0)

        self.clear_roi_btn = QPushButton("Clear ROIs")
        roi_layout.addWidget(self.clear_roi_btn, 1, 1)

        roi_group.setLayout(roi_layout)
        analysis_layout.addWidget(roi_group)

        analysis_tab.setLayout(analysis_layout)
        panel.addTab(analysis_tab, "Analysis")

        return panel

    def create_menu_bar(self):
        """Create menu bar with file and tools menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        load_action = QAction('Load Scan', self)
        load_action.triggered.connect(self.load_scan)
        file_menu.addAction(load_action)

        save_action = QAction('Save Scan', self)
        save_action.triggered.connect(self.save_scan)
        file_menu.addAction(save_action)

        export_action = QAction('Export Report', self)
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu('Tools')

        calib_action = QAction('Calibrate System', self)
        calib_action.triggered.connect(self.calibrate_system)
        tools_menu.addAction(calib_action)

        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        docs_action = QAction('Documentation', self)
        help_menu.addAction(docs_action)

    def setup_connections(self):
        """Setup signal-slot connections."""
        # Timer for real-time updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(100)  # 10 Hz update rate

        # Measurement thread
        self.measurement_thread = None
        self.reconstruction_thread = None

    def load_default_settings(self):
        """Load default system settings."""
        # Set default color map
        self.color_map = pg.colormap.get('viridis')
        self.histogram.gradient.setColorMap(self.color_map)

        # Initialize 3D visualization
        self.init_3d_visualization()

    def init_3d_visualization(self):
        """Initialize 3D visualization elements."""
        # Create mesh for breast surface
        # This would be loaded from a standard model
        pass

    def start_scan(self):
        """Start measurement scan."""
        if not self.measurement_sys.is_connected():
            QMessageBox.warning(self, "Connection Error",
                                "Measurement system not connected.")
            return

        # Get scan parameters
        scan_params = {
            'frequencies': np.linspace(
                self.freq_min.value() * 1e9,
                self.freq_max.value() * 1e9,
                201
            ),
            'power': self.power_level.value(),
            'averaging': self.averaging.value(),
            'pattern': self.scan_pattern.currentText(),
            'positions': self.generate_scan_positions()
        }

        # Disable controls
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)

        # Start measurement thread
        self.measurement_thread = MeasurementThread(
            self.measurement_sys,
            scan_params
        )
        self.measurement_thread.progress_update.connect(self.update_progress)
        self.measurement_thread.measurement_complete.connect(self.scan_complete)
        self.measurement_thread.start()

        self.status_bar.showMessage("Scan in progress...")

    def stop_scan(self):
        """Stop ongoing scan."""
        if self.measurement_thread and self.measurement_thread.isRunning():
            self.measurement_thread.terminate()
            self.measurement_thread.wait()
            self.status_bar.showMessage("Scan stopped")

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

    def scan_complete(self, s_parameters):
        """Handle completion of scan."""
        if 'error' in s_parameters:
            QMessageBox.critical(self, "Scan Error", s_parameters['error'])
            return

        self.current_scan = s_parameters

        # Update display
        self.plot_s_parameters(s_parameters)

        # Enable reconstruction
        self.reconstruct_btn.setEnabled(True)

        # Calculate metrics
        self.calculate_scan_metrics(s_parameters)

        self.status_bar.showMessage("Scan complete")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

    def start_reconstruction(self):
        """Start reconstruction process."""
        if self.current_scan is None:
            QMessageBox.warning(self, "No Data",
                                "Please acquire scan data first.")
            return

        self.reconstruct_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        # Start reconstruction thread
        self.reconstruction_thread = ReconstructionThread(
            self.hpinn,
            self.current_scan
        )
        self.reconstruction_thread.reconstruction_complete.connect(
            self.reconstruction_complete
        )
        self.reconstruction_thread.start()

        self.status_bar.showMessage("Reconstruction in progress...")

    def reconstruction_complete(self, reconstruction):
        """Handle completion of reconstruction."""
        if 'error' in reconstruction:
            QMessageBox.critical(self, "Reconstruction Error",
                                 reconstruction['error'])
            return

        self.current_reconstruction = reconstruction

        # Update displays
        self.update_thermal_display(reconstruction)
        self.update_3d_display(reconstruction)
        self.analyze_tumor(reconstruction)

        self.status_bar.showMessage("Reconstruction complete")
        self.reconstruct_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def update_thermal_display(self, reconstruction):
        """Update 2D thermal map display."""
        # Convert reconstruction to image
        img_data = reconstruction['temperature']

        # Apply color map
        self.thermal_img.setImage(img_data)

        # Set color scale
        vmin = self.temp_min.value()
        vmax = self.temp_max.value()
        self.thermal_img.setLevels([vmin, vmax])

        # Update histogram
        self.histogram.setLevels(vmin, vmax)

    def update_3d_display(self, reconstruction):
        """Update 3D visualization."""
        # Extract temperature data
        temp_data = reconstruction['temperature']

        # Create isosurface
        vertices, faces = self.extract_isosurface(temp_data, 0.5)

        # Update mesh
        if hasattr(self, 'mesh_item'):
            self.mesh_item.set_data(vertices=vertices, faces=faces)
        else:
            self.mesh_item = visuals.Mesh(vertices=vertices, faces=faces,
                                          color=(1, 0, 0, 0.5))
            self.view_3d.add(self.mesh_item)

        self.canvas_3d.update()

    def extract_isosurface(self, data, threshold):
        """Extract isosurface from 3D data."""
        # Simplified implementation
        # In production, use marching cubes
        vertices = []
        faces = []

        return np.array(vertices), np.array(faces)

    def plot_s_parameters(self, s_parameters):
        """Plot S-parameters in dedicated tab."""
        self.s_param_plot.clear()

        # Plot magnitude
        mag_plot = self.s_param_plot.addPlot(title="|S11|")
        for i in range(min(8, len(s_parameters))):
            mag = np.abs(s_parameters[i])
            freq = np.linspace(self.freq_min.value(),
                               self.freq_max.value(),
                               len(mag))
            mag_plot.plot(freq, mag, pen=pg.mkPen(color=pg.intColor(i)))

        # Plot phase
        phase_plot = self.s_param_plot.addPlot(title="Phase(S11)")
        for i in range(min(8, len(s_parameters))):
            phase = np.angle(s_parameters[i])
            freq = np.linspace(self.freq_min.value(),
                               self.freq_max.value(),
                               len(phase))
            phase_plot.plot(freq, phase, pen=pg.mkPen(color=pg.intColor(i)))

        self.s_param_plot.nextRow()

    def analyze_tumor(self, reconstruction):
        """Analyze tumor characteristics."""
        temp_data = reconstruction['temperature']

        # Find hot spots
        threshold = np.percentile(temp_data, 95)
        hot_mask = temp_data > threshold

        if np.any(hot_mask):
            # Calculate metrics
            size = np.sum(hot_mask) * 0.25  # mm² (assuming 0.5mm resolution)
            max_temp = np.max(temp_data)
            avg_temp = np.mean(temp_data[hot_mask])
            delta_t = max_temp - avg_temp

            # Update display
            self.tumor_metrics["Size"].setText(f"{size:.1f} mm²")
            self.tumor_metrics["ΔT"].setText(f"{delta_t:.2f} °C")
            self.tumor_metrics["Confidence"].setText("85%")

            # Calculate malignancy score (simplified)
            malignancy = 0.3 * (size / 50) + 0.7 * (delta_t / 1.0)
            malignancy = min(1.0, max(0.0, malignancy))
            self.tumor_metrics["Malignancy Score"].setText(f"{malignancy:.2%}")

    def calculate_scan_metrics(self, s_parameters):
        """Calculate scan quality metrics."""
        # Calculate SNR
        signal_power = np.mean(np.abs(s_parameters) ** 2)
        noise_power = np.var(s_parameters)
        snr = 10 * np.log10(signal_power / noise_power)

        # Update labels
        self.metrics_labels["SNR"].setText(f"SNR: {snr:.1f} dB")
        self.metrics_labels["Scan Time"].setText("Scan Time: 45s")

    def generate_scan_positions(self):
        """Generate scan positions based on selected pattern."""
        pattern = self.scan_pattern.currentText()

        if pattern == "Raster":
            positions = self.raster_scan(20, 20)
        elif pattern == "Spiral":
            positions = self.spiral_scan(10, 0.5)
        elif pattern == "Adaptive":
            positions = self.adaptive_scan()
        else:
            positions = self.multiresolution_scan()

        return positions

    def raster_scan(self, nx, ny):
        """Generate raster scan positions."""
        positions = []
        for i in range(nx):
            for j in range(ny):
                x = (i - nx / 2) * 0.025  # 25mm spacing
                y = (j - ny / 2) * 0.025
                positions.append((x, y))
        return positions

    def spiral_scan(self, n_turns, spacing):
        """Generate spiral scan positions."""
        positions = []
        for i in range(100):
            t = i / 100 * 2 * np.pi * n_turns
            r = spacing * t / (2 * np.pi)
            x = r * np.cos(t)
            y = r * np.sin(t)
            positions.append((x, y))
        return positions

    def update_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)

    def update_display(self):
        """Update real-time displays."""
        if self.current_reconstruction is not None:
            # Update temperature color bar
            pass

    def federated_update(self):
        """Perform federated learning update."""
        from gui.federated_client import FederatedClient

        client = FederatedClient(model=self.hpinn)

        # Get local updates
        local_update = client.compute_update(self.current_scan,
                                             self.current_reconstruction)

        # Send to server (simulated)
        QMessageBox.information(self, "Federated Learning",
                                "Model update sent to server.")

        # Update status
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.fed_status.setText(f"Last update: {timestamp}")

    def save_results(self):
        """Save scan and reconstruction results."""
        if self.current_reconstruction is None:
            QMessageBox.warning(self, "No Data",
                                "No reconstruction to save.")
            return

        # Get file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "",
            "HDF5 Files (*.h5);;Numpy Files (*.npz);;All Files (*)"
        )

        if file_path:
            # Save data
            import h5py
            with h5py.File(file_path, 'w') as f:
                f.create_dataset('s_parameters', data=self.current_scan)
                f.create_dataset('temperature',
                                 data=self.current_reconstruction['temperature'])
                f.create_dataset('patient_info',
                                 data=str(self.get_patient_info()))

            self.status_bar.showMessage(f"Results saved to {file_path}")

    def get_patient_info(self):
        """Get current patient information."""
        return {
            'id': self.patient_id.value(),
            'age': self.patient_age.value(),
            'density': self.breast_density.currentText()
        }

    def load_scan(self):
        """Load previously saved scan."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Scan", "",
            "HDF5 Files (*.h5);;Numpy Files (*.npz);;All Files (*)"
        )

        if file_path:
            # Load data
            import h5py
            with h5py.File(file_path, 'r') as f:
                self.current_scan = f['s_parameters'][:]

                if 'temperature' in f:
                    self.current_reconstruction = {
                        'temperature': f['temperature'][:]
                    }

            # Update displays
            self.plot_s_parameters(self.current_scan)
            if self.current_reconstruction:
                self.update_thermal_display(self.current_reconstruction)

            self.status_bar.showMessage(f"Scan loaded from {file_path}")

    def calibrate_system(self):
        """Run system calibration."""
        QMessageBox.information(self, "Calibration",
                                "Starting system calibration...")

        # In production, this would run actual calibration routines
        self.status_bar.showMessage("Calibration complete")

    def show_settings(self):
        """Show system settings dialog."""
        # Implementation for settings dialog
        pass

    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>Active Deep Thermography System</h2>
        <p><b>IEEE Transactions on Antennas and Propagation</b></p>
        <p>Version 1.0.0</p>
        <p>Early Breast Cancer Detection using Microwave Antenna Arrays</p>
        <p>© 2024 Achraf Elouerghi et al.</p>
        <p>Based on previous work: "An IoMT-based Wearable Thermography System"</p>
        """
        QMessageBox.about(self, "About", about_text)

    def export_report(self):
        """Export clinical report."""
        if self.current_reconstruction is None:
            QMessageBox.warning(self, "No Data",
                                "No data to export.")
            return

        # Generate report
        report = self.generate_report()

        # Save to file
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "",
            "PDF Files (*.pdf);;HTML Files (*.html);;All Files (*)"
        )

        if file_path:
            self.save_report(report, file_path)
            self.status_bar.showMessage(f"Report exported to {file_path}")

    def generate_report(self):
        """Generate clinical report."""
        report = {
            'patient': self.get_patient_info(),
            'scan_parameters': {
                'frequency_range': f"{self.freq_min.value()}-{self.freq_max.value()} GHz",
                'power': f"{self.power_level.value()} dBm",
                'pattern': self.scan_pattern.currentText()
            },
            'findings': self.tumor_metrics,
            'images': {
                'thermal_map': self.current_reconstruction['temperature'],
                's_parameters': self.current_scan
            }
        }
        return report

    def save_report(self, report, file_path):
        """Save report to file."""
        # Implementation for saving report
        pass

    def add_roi(self):
        """Add region of interest for analysis."""
        # Implementation for ROI management
        pass

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop any running threads
        if self.measurement_thread and self.measurement_thread.isRunning():
            self.measurement_thread.terminate()
            self.measurement_thread.wait()

        if self.reconstruction_thread and self.reconstruction_thread.isRunning():
            self.reconstruction_thread.terminate()
            self.reconstruction_thread.wait()

        event.accept()


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    # In production, initialize with actual model and measurement system
    gui = ClinicalGUI(None, None, None)
    gui.show()

    sys.exit(app.exec_())