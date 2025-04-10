from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QSpinBox, QLabel, 
    QPushButton, QGridLayout, QMessageBox, QDoubleSpinBox,
    QHBoxLayout
)
from qtpy.QtCore import Qt
from meshmaker.components.MeshMaker import MeshMaker
from qtpy.QtWidgets import QSizePolicy
from meshmaker.components.Process.processGUI import ProcessGUI

class DRMProcessGUI(QWidget):
    def __init__(self, parent=None):
        """
        Initialize the DRM Process GUI.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.meshmaker = MeshMaker.get_instance()
        
        # Set size policy for the main widget
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
        
        # DRM Process Box
        drmProcessBox = QGroupBox("DRM Analysis Process")
        drmProcessBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        drmProcessLayout = QGridLayout(drmProcessBox)
        
        # Time step
        drmProcessLayout.addWidget(QLabel("Time Step (dT):"), 0, 0)
        self.timeStepSpinBox = QDoubleSpinBox()
        self.timeStepSpinBox.setMinimum(0.0001)
        self.timeStepSpinBox.setMaximum(1.0)
        self.timeStepSpinBox.setSingleStep(0.001)
        self.timeStepSpinBox.setValue(0.01)
        self.timeStepSpinBox.setDecimals(4)
        drmProcessLayout.addWidget(self.timeStepSpinBox, 0, 1)
        
        # Final Time
        drmProcessLayout.addWidget(QLabel("Final Time:"), 1, 0)
        self.finalTimeSpinBox = QDoubleSpinBox()
        self.finalTimeSpinBox.setMinimum(0.01)
        self.finalTimeSpinBox.setMaximum(10000.0)
        self.finalTimeSpinBox.setSingleStep(1.0)
        self.finalTimeSpinBox.setValue(10.0)
        self.finalTimeSpinBox.setDecimals(2)
        drmProcessLayout.addWidget(self.finalTimeSpinBox, 1, 1)
        
        # Create process button
        buttonLayout = QHBoxLayout()
        self.createProcessButton = QPushButton("Create Default DRM Process")
        self.createProcessButton.setStyleSheet("background-color: green; color: white;")
        self.createProcessButton.clicked.connect(self.create_default_drm_process)
        buttonLayout.addWidget(self.createProcessButton)
        
        # View process button
        self.viewProcessButton = QPushButton("View Process Steps")
        self.viewProcessButton.clicked.connect(self.view_process_steps)
        buttonLayout.addWidget(self.viewProcessButton)
        
        drmProcessLayout.addLayout(buttonLayout, 2, 0, 1, 2)
        
        drmProcessLayout.setContentsMargins(10, 10, 10, 10)
        drmProcessLayout.setSpacing(10)
        
        layout.addWidget(drmProcessBox)
        layout.setContentsMargins(10, 10, 10, 10)
        
    def create_default_drm_process(self):
        """Create the default DRM process with specified parameters"""
        try:
            dT = self.timeStepSpinBox.value()
            finalTime = self.finalTimeSpinBox.value()
            
            if not hasattr(self.meshmaker, 'drm'):
                QMessageBox.critical(self, "Error", "DRM module not initialized", QMessageBox.Ok)
                return
                
            # Call the createDefaultProcess method
            self.meshmaker.drm.createDefaultProcess(dT, finalTime)
            
            QMessageBox.information(
                self, 
                "Success", 
                "Default DRM process created successfully. Process includes:\n"
                "• Fixing boundary conditions\n"
                "• Gravity analysis (elastic & plastic phases)\n"
                "• VTKHDF recorder configuration\n"
                "• Dynamic analysis configuration"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create DRM process: {str(e)}", QMessageBox.Ok)
    
    def view_process_steps(self):
        """Open the process GUI to display and manage process steps"""
        if not hasattr(self.meshmaker, 'process') or not hasattr(self.meshmaker.process, 'steps'):
            QMessageBox.warning(self, "No Process", "No process steps defined yet.", QMessageBox.Ok)
            return
            
        steps = self.meshmaker.process.steps
        if not steps:
            QMessageBox.warning(self, "Empty Process", "The process contains no steps.", QMessageBox.Ok)
            return
        
        # Open the process GUI dialog
        process_dialog = ProcessGUI(self)
        process_dialog.show()


if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = DRMProcessGUI()
    window.show()
    sys.exit(app.exec_())
