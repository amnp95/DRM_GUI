# from PySide6.QtWidgets import (QFrame, QVBoxLayout, QWidget, 
#                            QTabWidget, QLabel)
from qtpy.QtWidgets import QFrame, QVBoxLayout, QWidget, QTabWidget, QLabel
from drm_analyzer.components.Material.materialGUI import MaterialManagerTab
from drm_analyzer.components.Mesh.meshPartGUI import MeshPartManagerTab
from drm_analyzer.components.Assemble.AssemblerGUI import AssemblyManagerTab

class LeftPanel(QFrame):
    '''
    Left panel of the main window containing various tabs.
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(400)
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
        self.mesh_tab = QWidget()
        self.Assemble_tab = QWidget()
        self.absorbing_tab = QWidget()
        self.analysis_tab = QWidget()

        # Add tabs to the tab widget
        self.tabs.addTab(self.material_tab, "Material")
        self.tabs.addTab(self.mesh_tab, "Mesh")
        self.tabs.addTab(self.Assemble_tab, "Assemble")
        self.tabs.addTab(self.absorbing_tab, "Absorbing")
        self.tabs.addTab(self.analysis_tab, "Analysis")

    def setup_tab_contents(self):
        # Material tab
        self.material_tab.layout = QVBoxLayout()
        self.material_tab.layout.addWidget(MaterialManagerTab())
        self.material_tab.setLayout(self.material_tab.layout)

        # Mesh tab
        self.mesh_tab.layout = QVBoxLayout()
        self.mesh_tab.layout.addWidget(MeshPartManagerTab())
        self.mesh_tab.setLayout(self.mesh_tab.layout)

        # Assemble tab
        self.Assemble_tab.layout = QVBoxLayout()
        self.Assemble_tab.layout.addWidget(AssemblyManagerTab())
        self.Assemble_tab.setLayout(self.Assemble_tab.layout)

        # Absorbing tab
        self.absorbing_tab.layout = QVBoxLayout()
        self.absorbing_tab.layout.addWidget(QLabel("Absorbing content here"))
        self.absorbing_tab.setLayout(self.absorbing_tab.layout)

        # Analysis tab
        self.analysis_tab.layout = QVBoxLayout()
        self.analysis_tab.layout.addWidget(QLabel("Analysis content here"))
        self.analysis_tab.setLayout(self.analysis_tab.layout)

