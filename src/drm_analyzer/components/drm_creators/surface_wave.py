from PyQt5.QtWidgets import QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QLabel
from .base_creator import DRMCreatorDialog


class SurfaceWaveCreator(DRMCreatorDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Surface Wave")
        self.setup_form()
        
    def setup_form(self):
        # Add your surface wave specific parameters here
        self.wave_type = QComboBox()
        self.wave_type.addItems(['Rayleigh', 'Love'])
        self.form_layout.addRow("Wave Type:", self.wave_type)
        
        self.frequency = QDoubleSpinBox()
        self.frequency.setRange(0.1, 100.0)
        self.frequency.setValue(1.0)
        self.form_layout.addRow("Frequency (Hz):", self.frequency)
        
        self.wavelength = QDoubleSpinBox()
        self.wavelength.setRange(1.0, 1000.0)
        self.wavelength.setValue(100.0)
        self.form_layout.addRow("Wavelength (m):", self.wavelength)
    
    def get_parameters(self):
        return {
            'wave_type': self.wave_type.currentText(),
            'frequency': self.frequency.value(),
            'wavelength': self.wavelength.value()
        }
    
    def create_load(self):
        params = self.get_parameters()
        # Implement your surface wave creation logic here
        print(f"Creating surface wave with parameters: {params}")
        # Return the created wave or None if failed
        return params