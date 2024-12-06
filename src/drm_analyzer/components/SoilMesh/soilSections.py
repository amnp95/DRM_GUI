from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                           QPushButton, QTabWidget, QComboBox)
from .rectangularGrid import RectangularGridTab
from .sphericalGrid import SphericalGridTab
from .customGrid import CustomGridTab

class soilSections(QWidget):
    GRID_TYPES = {
        'Rectangular Grid': RectangularGridTab,
        'Spherical Grid': SphericalGridTab,
        'Custom Grid': CustomGridTab
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.block_counter = 0
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        
        # Group box
        self.group_box = QGroupBox('Soil Sections')
        self.group_box_layout = QVBoxLayout(self.group_box)
        
        # Header with grid type selector and Add button
        header_layout = QHBoxLayout()
        
        self.grid_type_selector = QComboBox()
        self.grid_type_selector.addItems(self.GRID_TYPES.keys())
        header_layout.addWidget(self.grid_type_selector)
        
        self.soil_block_button = QPushButton('Add Section')
        self.soil_block_button.clicked.connect(self.add_soil_block)
        header_layout.addWidget(self.soil_block_button)
        
        self.group_box_layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.remove_soil_block)
        self.group_box_layout.addWidget(self.tab_widget)
        
        # Add group box to main layout
        self.main_layout.addWidget(self.group_box)
        
        # Add initial soil block
        self.add_soil_block()

    def add_soil_block(self):
        self.block_counter += 1
        grid_type = self.grid_type_selector.currentText()
        grid_class = self.GRID_TYPES[grid_type]
        
        new_tab = grid_class(block_number=self.block_counter)
        self.tab_widget.addTab(new_tab, f"Block {self.block_counter}")
        self.tab_widget.setCurrentWidget(new_tab)
        
        self.update_tab_names()

    def remove_soil_block(self, index):
        if self.tab_widget.count() > 1:
            tab = self.tab_widget.widget(index)
            if hasattr(tab, 'delete_grid'):
                tab.delete_grid()
            self.tab_widget.removeTab(index)
            self.update_tab_names()

    def update_tab_names(self):
        for i in range(self.tab_widget.count()):
            self.tab_widget.setTabText(i, f"Block {i + 1}")

    def get_soil_blocks_data(self):
        return [self.tab_widget.widget(i).get_data() 
                for i in range(self.tab_widget.count())]