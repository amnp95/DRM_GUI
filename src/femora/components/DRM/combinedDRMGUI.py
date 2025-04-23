from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QApplication, QScrollArea
)
from qtpy.QtCore import Qt

from femora.components.DRM.drmAbsorbingGUI import AbsorbingGUI
from femora.components.DRM.drmPatternGUI import DRMGUI
from femora.components.DRM.drmProcessGUI import DRMProcessGUI

class CombinedDRMGUI(QWidget):
    """
    A unified GUI that combines all DRM-related interfaces:
    - Pattern loading interface for H5DRM files
    - Absorbing layer management
    - DRM process configuration
    """
    def __init__(self, parent=None):
        """
        Initialize the combined DRM GUI.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Create tab widget to organize different DRM components
        self.tabWidget = QTabWidget()
        
        # Create individual DRM component widgets
        self.drmGUI = DRMGUI()
        self.absorbingGUI = AbsorbingGUI()
        self.processGUI = DRMProcessGUI()
        
        # Create scroll areas for each component to ensure they can be viewed
        # even in limited screen space
        
        # DRM Pattern tab
        drmPatternScroll = QScrollArea()
        drmPatternScroll.setWidgetResizable(True)
        drmPatternScroll.setWidget(self.drmGUI)
        
        # Absorbing Layer tab
        absorbingScroll = QScrollArea()
        absorbingScroll.setWidgetResizable(True)
        absorbingScroll.setWidget(self.absorbingGUI)
        
        # Process tab
        processScroll = QScrollArea()
        processScroll.setWidgetResizable(True)
        processScroll.setWidget(self.processGUI)
        
        # Add tabs with scroll areas
        self.tabWidget.addTab(drmPatternScroll, "DRM Pattern")
        self.tabWidget.addTab(absorbingScroll, "Absorbing Layer")
        self.tabWidget.addTab(processScroll, "DRM Process")
        
        # Add tab widget to the main layout
        layout.addWidget(self.tabWidget)
    
    def set_active_tab(self, tab_name):
        """
        Set the active tab based on name
        
        Args:
            tab_name (str): Name of tab to activate ("DRM Pattern", "Absorbing Layer", or "DRM Process")
        """
        tab_map = {
            "DRM Pattern": 0,
            "Absorbing Layer": 1,
            "DRM Process": 2
        }
        
        if tab_name in tab_map:
            self.tabWidget.setCurrentIndex(tab_map[tab_name])
    
    # Convenience methods to directly access underlying components
    
    def get_drm_gui(self):
        """Get the DRM pattern GUI component"""
        return self.drmGUI
    
    def get_absorbing_gui(self):
        """Get the absorbing layer GUI component"""
        return self.absorbingGUI
    
    def get_process_gui(self):
        """Get the DRM process GUI component"""
        return self.processGUI


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = CombinedDRMGUI()
    window.show()
    sys.exit(app.exec_())
