from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout,QDialogButtonBox

class DRMCreatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("DRM Load Creator")
        self.layout = QVBoxLayout(self)
        
        # Form layout for parameters
        self.form_layout = QGridLayout()
        self.layout.addLayout(self.form_layout)
        
        # Add buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
    
    def get_parameters(self):
        """Override this method in subclasses to return the parameters"""
        raise NotImplementedError
        
    def create_load(self):
        """Override this method in subclasses to create the DRM load"""
        raise NotImplementedError