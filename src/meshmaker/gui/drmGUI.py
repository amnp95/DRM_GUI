from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QSpinBox, QLabel, QDialogButtonBox, QColorDialog,
    QComboBox, QPushButton, QGridLayout, QMessageBox, QProgressDialog, QApplication,
    QSlider, QDialog, QDoubleSpinBox, QCheckBox, QFileDialog, QHBoxLayout, QLineEdit, 
    QRadioButton, QButtonGroup
)
from qtpy.QtCore import Qt
from meshmaker.gui.plotter import PlotterManager
from meshmaker.components.MeshMaker import MeshMaker
from qtpy.QtWidgets import QSizePolicy
from meshmaker.components.Pattern.patternBase import H5DRMPattern, PatternManager
import numpy as np
import os
import csv

class DRMGUI(QWidget):
    def __init__(self, parent=None):
        """
        Initialize the DRMGUI.
       
        Args:
            main_window: Reference to the MainWindow instance
        """
        super().__init__(parent)

        self.meshmaker = MeshMaker.get_instance()
        self.pattern_manager = PatternManager()
        
        # Set size policy for the main widget
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # make the alignment of the layout to be top left
        layout.setAlignment(Qt.AlignTop)
        
        # Add H5DRM Pattern box FIRST
        h5drmPatternBox = QGroupBox("H5DRM Load Pattern")
        h5drmPatternBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        h5drmLayout = QGridLayout(h5drmPatternBox)
        
        # H5DRM File path
        h5drmLayout.addWidget(QLabel("H5DRM File"), 0, 0)
        self.h5drmFilePath = QLineEdit()
        self.h5drmFilePath.setReadOnly(True)
        self.h5drmFilePath.setPlaceholderText("Select H5DRM file...")
        
        fileLayout = QHBoxLayout()
        fileLayout.addWidget(self.h5drmFilePath)
        
        self.browseButton = QPushButton("Browse")
        self.browseButton.clicked.connect(self.browse_h5drm_file)
        fileLayout.addWidget(self.browseButton)
        
        h5drmLayout.addLayout(fileLayout, 0, 1)
        
        # Scale factor
        h5drmLayout.addWidget(QLabel("Scale Factor"), 1, 0)
        self.factorSpinBox = QDoubleSpinBox()
        self.factorSpinBox.setMinimum(0.01)
        self.factorSpinBox.setMaximum(10.0)
        self.factorSpinBox.setSingleStep(0.1)
        self.factorSpinBox.setValue(1.0)
        h5drmLayout.addWidget(self.factorSpinBox, 1, 1)
        
        # Coordinate scale
        h5drmLayout.addWidget(QLabel("Coordinate Scale"), 2, 0)
        self.coordScaleSpinBox = QDoubleSpinBox()
        self.coordScaleSpinBox.setMinimum(0.001)
        self.coordScaleSpinBox.setMaximum(1000.0)
        self.coordScaleSpinBox.setSingleStep(0.1)
        self.coordScaleSpinBox.setValue(1.0)
        h5drmLayout.addWidget(self.coordScaleSpinBox, 2, 1)
        
        # Distance tolerance
        h5drmLayout.addWidget(QLabel("Distance Tolerance"), 3, 0)
        self.distToleranceSpinBox = QDoubleSpinBox()
        self.distToleranceSpinBox.setMinimum(0.0001)
        self.distToleranceSpinBox.setMaximum(1.0)
        self.distToleranceSpinBox.setSingleStep(0.001)
        self.distToleranceSpinBox.setValue(0.001)
        self.distToleranceSpinBox.setDecimals(4)
        h5drmLayout.addWidget(self.distToleranceSpinBox, 3, 1)
        
        # Auto set from mesh and Use center from mesh
        self.useFromMeshCheckbox = QCheckBox("Auto set transform from mesh")
        self.useFromMeshCheckbox.setChecked(True)
        h5drmLayout.addWidget(self.useFromMeshCheckbox, 4, 0, 1, 2)
        
        # Matrix transformation button
        self.transformButton = QPushButton("Configure Transformation Matrix...")
        self.transformButton.clicked.connect(self.configure_transformation)
        h5drmLayout.addWidget(self.transformButton, 5, 0, 1, 2)
        
        # DRM Points Visualization
        pointsGroup = QGroupBox("DRM Points Visualization")
        pointsLayout = QGridLayout(pointsGroup)
        
        # Radio buttons for point source
        self.showPointsCheckbox = QCheckBox("Show DRM points in visualization")
        pointsLayout.addWidget(self.showPointsCheckbox, 0, 0, 1, 2)
        
        sourceGroup = QGroupBox("Points Source")
        sourceLayout = QVBoxLayout(sourceGroup)
        
        self.pointsSourceGroup = QButtonGroup()
        self.h5drmFileRadio = QRadioButton("From H5DRM file")
        self.h5drmFileRadio.setChecked(True)
        self.csvFileRadio = QRadioButton("From CSV file")
        
        self.pointsSourceGroup.addButton(self.h5drmFileRadio)
        self.pointsSourceGroup.addButton(self.csvFileRadio)
        
        sourceLayout.addWidget(self.h5drmFileRadio)
        sourceLayout.addWidget(self.csvFileRadio)
        
        # CSV file selection
        csvFileLayout = QHBoxLayout()
        self.csvFilePath = QLineEdit()
        self.csvFilePath.setReadOnly(True)
        self.csvFilePath.setEnabled(False)
        self.csvFilePath.setPlaceholderText("Select CSV file with DRM points...")
        
        self.browseCsvButton = QPushButton("Browse")
        self.browseCsvButton.setEnabled(False)
        self.browseCsvButton.clicked.connect(self.browse_csv_file)
        
        csvFileLayout.addWidget(self.csvFilePath)
        csvFileLayout.addWidget(self.browseCsvButton)
        
        # Connect radio buttons to enable/disable CSV controls
        self.h5drmFileRadio.toggled.connect(self.toggle_csv_controls)
        self.csvFileRadio.toggled.connect(self.toggle_csv_controls)
        
        sourceLayout.addLayout(csvFileLayout)
        pointsLayout.addWidget(sourceGroup, 1, 0, 1, 2)
        
        # Point visualization customization
        visualGroup = QGroupBox("Point Visualization")
        visualLayout = QGridLayout(visualGroup)
        
        visualLayout.addWidget(QLabel("Point Size:"), 0, 0)
        self.pointSizeSpinBox = QDoubleSpinBox()
        self.pointSizeSpinBox.setRange(1, 20)
        self.pointSizeSpinBox.setValue(5)
        self.pointSizeSpinBox.setSingleStep(1)
        visualLayout.addWidget(self.pointSizeSpinBox, 0, 1)
        
        visualLayout.addWidget(QLabel("Color:"), 1, 0)
        self.pointColorButton = QPushButton("Choose Color...")
        self.pointColorButton.clicked.connect(self.choose_point_color)
        visualLayout.addWidget(self.pointColorButton, 1, 1)
        
        # Initialize point color
        self.pointColor = (1.0, 0.0, 0.0)  # Default red
        
        pointsLayout.addWidget(visualGroup, 2, 0, 1, 2)
        
        h5drmLayout.addWidget(pointsGroup, 6, 0, 1, 2)
        
        # Show DRM Points Button
        self.showDRMPointsButton = QPushButton("Show DRM Points")
        self.showDRMPointsButton.clicked.connect(self.show_drm_points)
        h5drmLayout.addWidget(self.showDRMPointsButton, 7, 0, 1, 2)
        
        # Add H5DRM Pattern button
        self.addH5DRMButton = QPushButton("Add H5DRM Pattern")
        self.addH5DRMButton.setStyleSheet("background-color: blue; color: white")
        self.addH5DRMButton.clicked.connect(self.add_h5drm_pattern)
        h5drmLayout.addWidget(self.addH5DRMButton, 8, 0, 1, 2)
        
        h5drmLayout.setContentsMargins(10, 10, 10, 10)
        h5drmLayout.setSpacing(10)
        
        layout.addWidget(h5drmPatternBox)
        
        # Absorbing Layer (SECOND)
        AbsorbingLayerbox = QGroupBox("Absorbing Layer")
        # Set size policy for the GroupBox
        AbsorbingLayerbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        AbsorbingLayerlayout = QGridLayout(AbsorbingLayerbox)
        
        # Add widgets
        AbsorbingLayerlayout.addWidget(QLabel("Geometry"), 0, 0)
        self.absorbingLayerCombox = QComboBox()
        self.absorbingLayerCombox.addItem("Rectangular")
        AbsorbingLayerlayout.addWidget(self.absorbingLayerCombox, 0, 1)
        
        AbsorbingLayerlayout.addWidget(QLabel("Type"), 1, 0)
        self.absorbingLayerTypeCombox = QComboBox()
        self.absorbingLayerTypeCombox.addItem("Rayleigh")
        self.absorbingLayerTypeCombox.addItem("PML")
        AbsorbingLayerlayout.addWidget(self.absorbingLayerTypeCombox, 1, 1)
        
        AbsorbingLayerlayout.addWidget(QLabel("Partition Algorithm"), 2, 0)
        self.absorbingLayerPartitionCombox = QComboBox()
        self.absorbingLayerPartitionCombox.addItem("kd-tree")
        AbsorbingLayerlayout.addWidget(self.absorbingLayerPartitionCombox, 2, 1)
        
        AbsorbingLayerlayout.addWidget(QLabel("Number of Partitions"), 3, 0)
        self.absorbingLayerPartitionLineEdit = QSpinBox()
        self.absorbingLayerPartitionLineEdit.setMinimum(0)
        self.absorbingLayerPartitionLineEdit.setMaximum(1000)
        AbsorbingLayerlayout.addWidget(self.absorbingLayerPartitionLineEdit, 3, 1)
        
        AbsorbingLayerlayout.addWidget(QLabel("Number of Layers"), 4, 0)
        self.absorbingLayerNumLayersLineEdit = QSpinBox()
        self.absorbingLayerNumLayersLineEdit.setMinimum(1)
        self.absorbingLayerNumLayersLineEdit.setMaximum(50)
        self.absorbingLayerNumLayersLineEdit.setValue(5)
        AbsorbingLayerlayout.addWidget(self.absorbingLayerNumLayersLineEdit, 4, 1)

        AbsorbingLayerlayout.addWidget(QLabel("Damping Factor"), 5, 0)
        self.dampingFactorSpinBox = QDoubleSpinBox()
        self.dampingFactorSpinBox.setMinimum(0.0)
        self.dampingFactorSpinBox.setMaximum(1.0)
        self.dampingFactorSpinBox.setSingleStep(0.01)
        self.dampingFactorSpinBox.setValue(0.95)
        AbsorbingLayerlayout.addWidget(self.dampingFactorSpinBox, 5, 1)

        # Add match damping checkbox
        self.matchDampingCheckbox = QCheckBox("Match Damping with Regular Domain")
        AbsorbingLayerlayout.addWidget(self.matchDampingCheckbox, 6, 0, 1, 2)

        # Add a button to add the absorbing layer
        self.addAbsorbingLayerButton = QPushButton("Add Absorbing Layer")
        self.addAbsorbingLayerButton.setStyleSheet("background-color: green")
        AbsorbingLayerlayout.addWidget(self.addAbsorbingLayerButton, 7, 0, 1, 2)
        self.addAbsorbingLayerButton.clicked.connect(self.add_absorbing_layer)

        # Add view options button
        self.viewOptionsButton = QPushButton("View Options")
        AbsorbingLayerlayout.addWidget(self.viewOptionsButton, 8, 0, 1, 2)
        self.viewOptionsButton.clicked.connect(self.show_view_options_dialog)

        AbsorbingLayerlayout.setContentsMargins(10, 10, 10, 10)
        AbsorbingLayerlayout.setSpacing(10)
        
        layout.addWidget(AbsorbingLayerbox)
        
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Initialize transformation matrix with identity matrix and zero origin
        self.transform_matrix = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        self.origin = [0.0, 0.0, 0.0]
        
        # Initialize DRM points visualization attributes
        self.drm_points_actor = None

    def browse_h5drm_file(self):
        """Open file dialog to select H5DRM file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select H5DRM File", "", "H5DRM Files (*.h5drm);;All Files (*)"
        )
        if file_path:
            self.h5drmFilePath.setText(file_path)
    
    def browse_csv_file(self):
        """Open file dialog to select CSV file with DRM points"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File with DRM Points", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.csvFilePath.setText(file_path)
    
    def toggle_csv_controls(self):
        """Enable/disable CSV controls based on selected source"""
        enable_csv = self.csvFileRadio.isChecked()
        self.csvFilePath.setEnabled(enable_csv)
        self.browseCsvButton.setEnabled(enable_csv)
    
    def choose_point_color(self):
        """Open color picker for DRM points"""
        color = QColorDialog.getColor()
        if color.isValid():
            # Convert QColor to RGB tuple (0-1 range)
            self.pointColor = (color.redF(), color.greenF(), color.blueF())
            
            # Update button background color as visual feedback
            style = f"background-color: rgb({color.red()}, {color.green()}, {color.blue()})"
            self.pointColorButton.setStyleSheet(style)
    
    def configure_transformation(self):
        """Open dialog to configure transformation matrix and origin"""
        # If auto set from mesh is checked and mesh is available, calculate from mesh first
        if self.useFromMeshCheckbox.isChecked() and self.meshmaker.assembler.AssembeledMesh is not None:
            self.set_transform_from_mesh()

        dialog = TransformationDialog(self.transform_matrix, self.origin, self)
        if dialog.exec_() == QDialog.Accepted:
            self.transform_matrix = dialog.get_transform_matrix()
            self.origin = dialog.get_origin()
    
    def set_transform_from_mesh(self):
        """Calculate transformation matrix and origin from assembled mesh bounds"""
        if self.meshmaker.assembler.AssembeledMesh is None:
            QMessageBox.warning(self, "Warning", "No assembled mesh available. Please assemble a mesh first.")
            return False
        
        # Get mesh bounds
        bounds = self.meshmaker.assembler.AssembeledMesh.bounds
        xmin, xmax, ymin, ymax, zmin, zmax = bounds
        
        # Calculate center for x and y, but use zmax for z
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        center_z = zmax  # As requested, use zmax for z-coordinate
        
        # Set origin
        self.origin = [center_x, center_y, center_z]
        
        # Keep identity transform matrix
        self.transform_matrix = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        
        return True
    
    def show_drm_points(self):
        """Visualize DRM points on the plotter"""
        if not self.showPointsCheckbox.isChecked():
            QMessageBox.warning(self, "Warning", "Please check 'Show DRM points in visualization' first.")
            return
        
        # Get the plotter
        try:
            plotter = PlotterManager.get_plotter()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not get plotter: {str(e)}")
            return
        
        # Remove existing DRM points actor if any
        if self.drm_points_actor is not None:
            plotter.remove_actor(self.drm_points_actor)
            self.drm_points_actor = None
        
        points = None
        
        # Get points based on selected source
        if self.h5drmFileRadio.isChecked():
            # From H5DRM file
            h5drm_path = self.h5drmFilePath.text()
            if not h5drm_path:
                QMessageBox.warning(self, "Warning", "Please select an H5DRM file first.")
                return
            
            try:
                import h5py
                with h5py.File(h5drm_path, 'r') as h5_file:
                    # Get the points from the "xyz" dataset in the DRM_Data group
                    points = h5_file['DRM_Data']["xyz"][()]
                    points = np.array(points)
                    
                    # Get the origin from the DRM_Metadata/drmbox_x0 dataset
                    xyz0 = h5_file['DRM_Metadata']['drmbox_x0'][()]
                    xyz0 = np.array(xyz0)
                    
                    # Adjust points relative to the DRM box origin
                    points = points - xyz0
                    
                    # Apply coordinate scale from GUI
                    coord_scale = self.coordScaleSpinBox.value()
                    points = points * coord_scale
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read H5DRM file: {str(e)}")
                return
        else:
            # From CSV file
            csv_path = self.csvFilePath.text()
            if not csv_path:
                QMessageBox.warning(self, "Warning", "Please select a CSV file with DRM points.")
                return
            
            try:
                # Read points from CSV file
                points = []
                with open(csv_path, 'r') as file:
                    csv_reader = csv.reader(file)
                    header = next(csv_reader, None)  # Skip header if exists
                    
                    # Check if first row is header or data
                    if header and all(not is_number(val) for val in header):
                        # First row is header, continue with data
                        pass
                    else:
                        # First row is data, add it to points
                        try:
                            points.append([float(val) for val in header[:3]])
                        except ValueError:
                            # Not numeric data, must be header
                            pass
                    
                    # Read remaining rows
                    for row in csv_reader:
                        if len(row) >= 3:  # Ensure we have at least x,y,z coordinates
                            try:
                                x, y, z = float(row[0]), float(row[1]), float(row[2])
                                points.append([x, y, z])
                            except ValueError:
                                # Skip non-numeric rows
                                continue
                
                points = np.array(points)
                if len(points) == 0:
                    raise ValueError("No valid points found in CSV file")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read CSV file: {str(e)}")
                return
        
        if points is None or len(points) == 0:
            QMessageBox.warning(self, "Error", "No points loaded.")
            return
        
        # Always apply coordinate transformation as requested
        # Create transformation matrix
        T = np.array(self.transform_matrix).reshape(3, 3)
        
        # Apply transformation and add origin
        points_transformed = np.dot(points, T.T)
        points_transformed += np.array(self.origin)
        points = points_transformed
        
        try:
            # Create and visualize points
            point_size = self.pointSizeSpinBox.value()
            
            import pyvista as pv
            point_cloud = pv.PolyData(points)
            self.drm_points_actor = plotter.add_mesh(
                point_cloud, 
                color=self.pointColor,
                point_size=point_size,
                render_points_as_spheres=True
            )
            
            plotter.update()
            plotter.render()
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Visualized {len(points)} DRM points"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to visualize points: {str(e)}")
    
    def add_h5drm_pattern(self):
        """Add H5DRM pattern to the model"""
        # Check if file path is provided
        filepath = self.h5drmFilePath.text()
        if not filepath:
            QMessageBox.warning(self, "Missing File", "Please select a H5DRM file.")
            return
        
        # If auto set from mesh is checked, calculate from mesh
        if self.useFromMeshCheckbox.isChecked():
            if not self.set_transform_from_mesh():
                # set_transform_from_mesh will show its own warning
                return
        
        try:
            # Get parameters
            factor = self.factorSpinBox.value()
            crd_scale = self.coordScaleSpinBox.value()
            distance_tolerance = self.distToleranceSpinBox.value()
            do_transform = 1  # Always enable transformation
            
            # Create the H5DRM pattern
            pattern = self.pattern_manager.create_pattern(
                "h5drm",
                filepath=filepath,
                factor=factor,
                crd_scale=crd_scale,
                distance_tolerance=distance_tolerance,
                do_coordinate_transformation=do_transform,
                transform_matrix=self.transform_matrix,
                origin=self.origin
            )
            
            QMessageBox.information(
                self,
                "Success",
                f"H5DRM pattern created successfully with tag: {pattern.tag}"
            )
            
            # Show DRM points if checkbox is checked
            if self.showPointsCheckbox.isChecked():
                self.show_drm_points()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create H5DRM pattern: {str(e)}")
    
    def show_view_options_dialog(self):
        """Show the view options dialog for the absorbing mesh"""
        dialog = AbsorbingMeshViewOptionsDialog(self)
        dialog.exec_()

    def show_view_options_dialog(self):
        """Show the view options dialog for the absorbing mesh"""
        dialog = AbsorbingMeshViewOptionsDialog(self)
        dialog.exec_()

    def add_absorbing_layer(self):
        response = QMessageBox.warning(
            self,
            "Warning",
            "Adding an absorbing layer will modify the mesh. Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if response == QMessageBox.No:
            return

        self.plotter = PlotterManager.get_plotter()

        if self.meshmaker.assembler.AssembeledActor is not None:
            PlotterManager.get_plotter().renderer.remove_actor(self.meshmaker.assembler.AssembeledActor)
            self.meshmaker.assembler.AssembeledActor = None

        # Get parameters from UI
        geometry = self.absorbingLayerCombox.currentText()
        absorbing_layer_type = self.absorbingLayerTypeCombox.currentText()
        partition_algorithm = self.absorbingLayerPartitionCombox.currentText()
        num_partitions = self.absorbingLayerPartitionLineEdit.value()
        num_layers = self.absorbingLayerNumLayersLineEdit.value()
        damping_factor = self.dampingFactorSpinBox.value()
        match_damping = self.matchDampingCheckbox.isChecked()

        # Create and configure progress dialog
        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setWindowTitle("Processing")
        self.progress_dialog.setLabelText("Creating absorbing layer...")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setRange(0, 100)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        
        # Show the dialog
        self.progress_dialog.show()
        QApplication.processEvents()

        try:
            # Start the mesh operation
            self.meshmaker.addAbsorbingLayer(
                num_layers,
                num_partitions,
                partition_algorithm,
                geometry,
                damping=damping_factor,
                matchDamping=match_damping,
                progress_callback=self.update_progress,
                type=absorbing_layer_type,
            )

            self.plotter.clear()
            self.meshmaker.assembler.AssembeledActor = self.plotter.add_mesh(
                self.meshmaker.assembler.AssembeledMesh,
                opacity=1.0,
                show_edges=True,
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e), QMessageBox.Ok)
        finally:
            self.progress_dialog.close()

    def update_progress(self, value):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(int(value))
            QApplication.processEvents()


class TransformationDialog(QDialog):
    """Dialog for configuring transformation matrix and origin"""
    def __init__(self, transform_matrix, origin, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Transformation")
        self.setMinimumWidth(500)
        
        # Store initial values
        self.transform_matrix = transform_matrix.copy()
        self.origin = origin.copy()
        
        layout = QVBoxLayout(self)
        
        # Matrix group
        matrix_group = QGroupBox("Transformation Matrix (3x3)")
        matrix_layout = QGridLayout()
        
        self.matrix_inputs = []
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                input_field = QDoubleSpinBox()
                input_field.setRange(-1000, 1000)
                input_field.setDecimals(6)
                input_field.setSingleStep(0.1)
                input_field.setValue(transform_matrix[idx])
                matrix_layout.addWidget(input_field, i, j)
                self.matrix_inputs.append(input_field)
        
        matrix_group.setLayout(matrix_layout)
        layout.addWidget(matrix_group)
        
        # Origin group
        origin_group = QGroupBox("Origin Location")
        origin_layout = QHBoxLayout()
        
        self.origin_inputs = []
        for i, label in enumerate(["X:", "Y:", "Z:"]):
            origin_layout.addWidget(QLabel(label))
            input_field = QDoubleSpinBox()
            input_field.setRange(-1000, 1000)
            input_field.setDecimals(6)
            input_field.setSingleStep(0.1)
            input_field.setValue(origin[i])
            origin_layout.addWidget(input_field)
            self.origin_inputs.append(input_field)
        
        origin_group.setLayout(origin_layout)
        layout.addWidget(origin_group)
        
        # Preset buttons
        preset_group = QGroupBox("Matrix Presets")
        preset_layout = QHBoxLayout()
        
        identity_btn = QPushButton("Identity Matrix")
        identity_btn.clicked.connect(self.set_identity_matrix)
        preset_layout.addWidget(identity_btn)
        
        # Add more presets if needed
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def set_identity_matrix(self):
        """Set the transformation matrix to identity"""
        identity = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        for i, value in enumerate(identity):
            self.matrix_inputs[i].setValue(value)
    
    def get_transform_matrix(self):
        """Get the current transformation matrix values"""
        return [input_field.value() for input_field in self.matrix_inputs]
    
    def get_origin(self):
        """Get the current origin values"""
        return [input_field.value() for input_field in self.origin_inputs]


def is_number(s):
    """Check if a string can be converted to a float"""
    try:
        float(s)
        return True
    except ValueError:
        return False


class AbsorbingMeshViewOptionsDialog(QDialog):
    """
    Dialog for modifying view options of the absorbing mesh
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("View Options for Absorbing Mesh")
        self.plotter = PlotterManager.get_plotter()
        self.meshmaker = MeshMaker.get_instance()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create a grid layout for organized options
        options_grid = QGridLayout()
        options_grid.setSpacing(10)
        
        row = 0
        
        # Scalars dropdown
        scalar_label = QLabel("Scalars:")
        self.scalar_combobox = QComboBox()
        self.scalar_combobox.addItems(self.meshmaker.assembler.AssembeledMesh.array_names)
        active_scalar = self.meshmaker.assembler.AssembeledMesh.active_scalars_name
        current_index = self.scalar_combobox.findText(active_scalar)
        self.scalar_combobox.setCurrentIndex(current_index)
        self.scalar_combobox.currentIndexChanged.connect(self.update_scalars)

        options_grid.addWidget(scalar_label, row, 0)
        options_grid.addWidget(self.scalar_combobox, row, 1)
        row += 1

        # Opacity slider
        opacity_label = QLabel("Opacity:")
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(int(self.meshmaker.assembler.AssembeledActor.GetProperty().GetOpacity() * 100))
        self.opacity_slider.valueChanged.connect(self.update_opacity)

        options_grid.addWidget(opacity_label, row, 0)
        options_grid.addWidget(self.opacity_slider, row, 1)
        row += 1

        # Visibility checkbox
        self.visibility_checkbox = QCheckBox("Visible")
        self.visibility_checkbox.setChecked(self.meshmaker.assembler.AssembeledActor.GetVisibility())
        self.visibility_checkbox.stateChanged.connect(self.toggle_visibility)
        options_grid.addWidget(self.visibility_checkbox, row, 0, 1, 2)
        row += 1

        # Show edges checkbox
        self.show_edges_checkbox = QCheckBox("Show Edges")
        self.show_edges_checkbox.setChecked(self.meshmaker.assembler.AssembeledActor.GetProperty().GetEdgeVisibility())
        self.show_edges_checkbox.stateChanged.connect(self.update_edge_visibility)
        options_grid.addWidget(self.show_edges_checkbox, row, 0, 1, 2)
        row += 1

        # Color selection
        color_label = QLabel("Color:")
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)

        options_grid.addWidget(color_label, row, 0)
        options_grid.addWidget(self.color_button, row, 1)

        # Add the grid layout to the main layout
        layout.addLayout(options_grid)

        # OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def update_scalars(self):
        """Update the scalars for the absorbing mesh"""
        scalars_name = self.scalar_combobox.currentText()
        self.meshmaker.assembler.AssembeledMesh.active_scalars_name = scalars_name
        self.meshmaker.assembler.AssembeledActor.mapper.array_name = scalars_name
        self.meshmaker.assembler.AssembeledActor.mapper.scalar_range = (
            self.meshmaker.assembler.AssembeledMesh.get_data_range(scalars_name)
        )

        self.plotter.update_scalar_bar_range(
            self.meshmaker.assembler.AssembeledMesh.get_data_range(scalars_name)
        )
        self.plotter.update()
        self.plotter.render()
    
    def update_opacity(self, value):
        """Update absorbing mesh opacity"""
        self.meshmaker.assembler.AssembeledActor.GetProperty().SetOpacity(value / 100.0)
        self.plotter.render()

    def update_edge_visibility(self, state):
        """Toggle edge visibility"""
        self.meshmaker.assembler.AssembeledActor.GetProperty().SetEdgeVisibility(bool(state))
        self.plotter.render()

    def choose_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            # Convert QColor to VTK color (0-1 range)
            vtk_color = (
                color.redF(),
                color.greenF(),
                color.blueF()
            )
            self.meshmaker.assembler.AssembeledActor.GetProperty().SetColor(vtk_color)
            self.plotter.render()

    def toggle_visibility(self, state):
        """Toggle absorbing mesh visibility"""
        self.meshmaker.assembler.AssembeledActor.SetVisibility(bool(state))
        self.plotter.render()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = DRMGUI()
    window.show()
    sys.exit(app.exec_())