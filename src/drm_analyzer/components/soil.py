from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QWidget, QGroupBox, 
                           QGridLayout, QTabWidget, QHBoxLayout, QLineEdit)
from drm_analyzer.utils.validator import DoubleValidator, IntValidator




class SoilBlockTab(QWidget):
    """
    Individual tab representing a soil block with its properties
    """
    def __init__(self, parent=None, block_number=1):
        super().__init__(parent)
        self.block_number = block_number
        
        # Create main layout for the tab
        layout = QVBoxLayout(self)
        
        # Create form layout for soil properties
        form_layout = QGridLayout()
        
        Double_Validator = DoubleValidator()
        Double_Validator.setBottom(0)

        Int_Validator = IntValidator()
        Int_Validator.setBottom(1)


        # Add soil properties
        # Name
        form_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_edit = QLineEdit(f"Soil Block {block_number}")
        form_layout.addWidget(self.name_edit, 0, 1)

        # X width (m)
        form_layout.addWidget(QLabel("X Width (m):"), 1, 0)
        self.x_width = QLineEdit()
        form_layout.addWidget(self.x_width, 1, 1)
        self.x_width.setValidator(Double_Validator)

        # Y length (m)
        form_layout.addWidget(QLabel("Y Length (m):"), 2, 0)
        self.y_width = QLineEdit()
        form_layout.addWidget(self.y_width, 2, 1)
        self.y_width.setValidator(Double_Validator)

        # Z depth (m)
        form_layout.addWidget(QLabel("Z Depth (m):"), 3, 0)
        self.z_depth = QLineEdit()
        form_layout.addWidget(self.z_depth, 3, 1)
        self.z_depth.setValidator(Double_Validator)


        # number of elements in x direction
        form_layout.addWidget(QLabel("Number of Elements in X direction:"), 4, 0)
        self.num_x = QLineEdit()
        form_layout.addWidget(self.num_x, 4, 1)
        self.num_x.setValidator(Int_Validator)

        # number of elements in y direction
        form_layout.addWidget(QLabel("Number of Elements in Y direction:"), 5, 0)
        self.num_y = QLineEdit()
        form_layout.addWidget(self.num_y, 5, 1)
        self.num_y.setValidator(Int_Validator)

        # number of elements in z direction
        form_layout.addWidget(QLabel("Number of Elements in Z direction:"), 6, 0)
        self.num_z = QLineEdit()
        form_layout.addWidget(self.num_z, 6, 1)
        self.num_z.setValidator(Int_Validator)



        
        # Add form layout to main layout
        layout.addLayout(form_layout)
        
        # Add spacer
        layout.addStretch()

class SoilBlocks(QWidget):
    """
    A widget that displays the soil blocks with dynamic tabs.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.block_counter = 0
        
        # Main layout for the widget
        self.main_layout = QVBoxLayout(self)
        
        # Create group box for soil blocks
        self.group_box = QGroupBox('Soil Blocks')
        self.group_box_layout = QVBoxLayout(self.group_box)
        
        # Create header with Add button
        header_layout = QHBoxLayout()
        self.soil_block_button = QPushButton('Add Soil')
        
        self.soil_block_button.clicked.connect(self.add_soil_block)
        header_layout.addWidget(self.soil_block_button)
        header_layout.addStretch()
        self.group_box_layout.addLayout(header_layout)

        # style the push button
        # self.soil_block_button.setStyleSheet(Styles.Pushbutton_style)


        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.remove_soil_block)
        self.group_box_layout.addWidget(self.tab_widget)
        
        # Add group box to main layout
        self.main_layout.addWidget(self.group_box)
        
        # Add initial soil block
        self.add_soil_block()
    

    def add_soil_block(self):
        """Add a new soil block tab"""
        self.block_counter += 1
        new_tab = SoilBlockTab(block_number=self.block_counter)
        
        # Create tab with close button
        self.tab_widget.addTab(new_tab, f"Block {self.block_counter}")
        
        # Set the new tab as current
        self.tab_widget.setCurrentWidget(new_tab)

        # rename the tabs to reflect the new order
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            tab_name = f"Block {i + 1}"
            self.tab_widget.setTabText(i, tab_name)
    


    def remove_soil_block(self, index):
        """Remove a soil block tab"""
        if self.tab_widget.count() > 1:  # Ensure at least one tab remains
            self.tab_widget.removeTab(index)

        # rename the tabs to reflect the new order
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            tab_name = f"Block {i + 1}"
            self.tab_widget.setTabText(i, tab_name)
    


    def get_soil_blocks_data(self):
        """Get data from all soil blocks"""
        data = []
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            block_data = {
                'name': tab.name_edit.text(),
                'x_width': tab.x_width.text(),
                'y_width': tab.y_width.text(),
                'z_depth': tab.z_depth.text(),
                'num_x': tab.num_x.text(),
                'num_y': tab.num_y.text(),
                'num_z': tab.num_z.text()
            }
            data.append(block_data)
        return data





        
