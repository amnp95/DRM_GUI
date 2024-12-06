from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QWidget, 
                           QTabWidget, QLabel)
from drm_analyzer.components.SoilMesh.soilSections import soilSections

class LeftPanel(QFrame):
    '''
    Left panel of the main window containing various tabs.
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(200)
        self.init_ui()
        
    def init_ui(self):
        # Add a layout for future widgets
        layout = QVBoxLayout(self)

        # Create a tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.create_tabs()
        self.setup_tab_contents()

    def create_tabs(self):
        self.material_tab = QWidget()
        self.soil_tab = QWidget()
        self.drm_tab = QWidget()
        self.absorbing_tab = QWidget()
        self.analysis_tab = QWidget()
        self.partition_tab = QWidget()

        # Add tabs to the tab widget
        self.tabs.addTab(self.material_tab, "Material")
        self.tabs.addTab(self.soil_tab, "Soil Mesh")
        self.tabs.addTab(self.drm_tab, "DRM")
        self.tabs.addTab(self.absorbing_tab, "Absorbing")
        self.tabs.addTab(self.partition_tab, "Partition")
        self.tabs.addTab(self.analysis_tab, "Analysis")

    def setup_tab_contents(self):
        # Soil tab
        self.soil_tab.layout = QVBoxLayout()
        self.soil_tab.layout.addWidget(soilSections())
        self.soil_tab.setLayout(self.soil_tab.layout)

        # DRM tab
        self.drm_tab.layout = QVBoxLayout()
        self.drm_tab.layout.addWidget(QLabel("DRM content here"))
        self.drm_tab.setLayout(self.drm_tab.layout)

        # Absorbing tab
        self.absorbing_tab.layout = QVBoxLayout()
        self.absorbing_tab.layout.addWidget(QLabel("Absorbing content here"))
        self.absorbing_tab.setLayout(self.absorbing_tab.layout)

        # Analysis tab
        self.analysis_tab.layout = QVBoxLayout()
        self.analysis_tab.layout.addWidget(QLabel("Analysis content here"))
        self.analysis_tab.setLayout(self.analysis_tab.layout)

        # Partition tab
        self.partition_tab.layout = QVBoxLayout()
        self.partition_tab.layout.addWidget(QLabel("Partition content here"))
        self.partition_tab.setLayout(self.partition_tab.layout)