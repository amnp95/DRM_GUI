from PySide6.QtWidgets import (QLabel, QLineEdit, QComboBox, QPushButton, 
                           QGridLayout, QWidget, QDialog, QVBoxLayout,
                           QHBoxLayout, QDialogButtonBox)
import numpy as np
import pyvista as pv
from .baseGrid import BaseGridTab
from meshmaker.utils.validator import DoubleValidator, IntValidator

class SpacingSettingsDialog(QDialog):
    """Popup dialog for spacing method settings"""
    def __init__(self, parent=None, direction="X"):
        super().__init__(parent)
        self.setWindowTitle(f"{direction} Direction Spacing Settings")
        self.layout = QVBoxLayout(self)
        
        # Method selection
        method_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            'Linear', 'Geometric', 'Log', 'Power', 'Custom'
        ])
        method_layout.addWidget(QLabel("Method:"))
        method_layout.addWidget(self.method_combo)
        self.layout.addLayout(method_layout)
        
        # Parameters
        params_layout = QGridLayout()
        self.start = QLineEdit()
        self.end = QLineEdit()
        self.num_elements = QLineEdit()
        self.param1 = QLineEdit()
        self.param1_label = QLabel("Base:")
        
        params_layout.addWidget(QLabel("Start:"), 0, 0)
        params_layout.addWidget(self.start, 0, 1)
        params_layout.addWidget(QLabel("End:"), 1, 0)
        params_layout.addWidget(self.end, 1, 1)
        params_layout.addWidget(QLabel("Elements:"), 2, 0)
        params_layout.addWidget(self.num_elements, 2, 1)
        params_layout.addWidget(self.param1_label, 3, 0)
        params_layout.addWidget(self.param1, 3, 1)
        
        self.layout.addLayout(params_layout)
        
        # Add validators
        double_validator = DoubleValidator()
        int_validator = IntValidator()
        
        if double_validator:
            self.start.setValidator(double_validator)
            self.end.setValidator(double_validator)
            self.param1.setValidator(double_validator)
        if int_validator:
            self.num_elements.setValidator(int_validator)
        
        # Connect method change to UI update
        self.method_combo.currentTextChanged.connect(self.update_fields)
        
        # Add OK/Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)
        
        self.update_fields()
        
    def update_fields(self):
        """Show/hide fields based on spacing method"""
        method = self.method_combo.currentText()
        self.param1.hide()
        self.param1_label.hide()
        
        if method == 'Geometric':
            self.param1.show()
            self.param1_label.show()
            self.param1_label.setText("Growth Rate:")
        elif method == 'Log':
            self.param1.show()
            self.param1_label.show()
            self.param1_label.setText("Base:")

class DirectionModule(QWidget):
    """Compact widget showing current spacing method with edit button"""
    def __init__(self, direction, parent=None):
        super().__init__(parent)
        self.direction = direction
        self.parent = parent
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.method_label = QLabel("Linear")
        self.edit_button = QPushButton("Settings")
        self.edit_button.clicked.connect(self.show_settings)
        
        layout.addWidget(QLabel(f"{direction}:"))
        layout.addWidget(self.method_label)
        layout.addWidget(self.edit_button)
        
        # Store current settings
        self.current_settings = {
            'method': 'Linear',
            'start': '0',
            'end': '1',
            'num_elements': '10',
            'param1': '10'
        }
        
    def show_settings(self):
        dialog = SpacingSettingsDialog(self.parent, self.direction)
        
        # Set current values
        dialog.method_combo.setCurrentText(self.current_settings['method'])
        dialog.start.setText(self.current_settings['start'])
        dialog.end.setText(self.current_settings['end'])
        dialog.num_elements.setText(self.current_settings['num_elements'])
        dialog.param1.setText(self.current_settings['param1'])
        
        if dialog.exec_() == QDialog.Accepted:
            # Store new settings
            self.current_settings.update({
                'method': dialog.method_combo.currentText(),
                'start': dialog.start.text(),
                'end': dialog.end.text(),
                'num_elements': dialog.num_elements.text(),
                'param1': dialog.param1.text()
            })
            self.method_label.setText(self.current_settings['method'])
    
    def get_spacing_array(self):
        """Generate spacing array based on current settings"""
        try:
            start = float(self.current_settings['start'] or 0)
            end = float(self.current_settings['end'] or 0)
            num = int(self.current_settings['num_elements'] or 0)
            
            if any(v == 0 for v in [num]) or start == end:
                return None
                
            method = self.current_settings['method']
            
            if method == 'Linear':
                return np.linspace(start, end, num)
            elif method == 'Geometric':
                growth = float(self.current_settings['param1'] or 1.1)
                return np.geomspace(start, end, num)
            elif method == 'Log':
                base = float(self.current_settings['param1'] or 10)
                return np.logspace(start, end, num, base=base)
            elif method == 'Power':
                return np.power(np.linspace(start**(1/2), end**(1/2), num), 2)
            elif method == 'Custom':
                return np.linspace(start, end, num)
                
        except ValueError:
            return None

class RectangularGridTab(BaseGridTab):
    def setup_specific_fields(self):
        # Create direction modules
        self.x_module = DirectionModule("X", self)
        self.y_module = DirectionModule("Y", self)
        self.z_module = DirectionModule("Z", self)
        
        # Add modules to layout
        self.form_layout.addWidget(self.x_module, 1, 0, 1, 2)
        self.form_layout.addWidget(self.y_module, 2, 0, 1, 2)
        self.form_layout.addWidget(self.z_module, 3, 0, 1, 2)

    def create_grid(self):
        try:
            # Get spacing arrays for each direction
            x_spacing = self.x_module.get_spacing_array()
            y_spacing = self.y_module.get_spacing_array()
            z_spacing = self.z_module.get_spacing_array()
            
            if any(spacing is None for spacing in [x_spacing, y_spacing, z_spacing]):
                return None
            
            X, Y, Z = np.meshgrid(x_spacing, y_spacing, z_spacing, indexing='ij')
            grid = pv.StructuredGrid(X, Y, Z)
            return grid
            
        except ValueError:
            return None

    def get_data(self):
        data = super().get_data()
        data.update({
            'type': 'rectangular',
            'x_settings': self.x_module.current_settings,
            'y_settings': self.y_module.current_settings,
            'z_settings': self.z_module.current_settings
        })
        return data