from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QDialog, QMessageBox, QTableWidget, QTableWidgetItem, 
    QPushButton, QHeaderView, QCheckBox
)

from meshmaker.components.Analysis.numberers import NumbererManager, Numberer


class NumbererManagerTab(QDialog):
    """
    Dialog for managing and selecting numberers
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup dialog properties
        self.setWindowTitle("Numberer Manager")
        self.resize(600, 400)
        
        # Get the numberer manager instance
        self.numberer_manager = NumbererManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Description label
        description = QLabel(
            "Numberers determine the mapping between equation numbers and DOFs. "
            "Only one numberer can be active at a time."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Table showing available numberers
        self.numberers_table = QTableWidget()
        self.numberers_table.setColumnCount(3)  # Select, Type, Description
        self.numberers_table.setHorizontalHeaderLabels(["Select", "Type", "Description"])
        self.numberers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.numberers_table.setSelectionMode(QTableWidget.SingleSelection)
        header = self.numberers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.numberers_table)
        
        # Initialize the table with available numberers
        self.initialize_numberers_table()
        
        # Add OK button at the bottom
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_btn)
        layout.addLayout(buttons_layout)

    def initialize_numberers_table(self):
        """Initialize the numberers table with available numberers"""
        numberers = self.numberer_manager.get_all_numberers()
        
        selected_numberer = self.get_selected_numberer()
        
        self.numberers_table.setRowCount(len(numberers))
        self.checkboxes = []  # Changed from radio_buttons to checkboxes
        
        # Hide vertical header (row indices)
        self.numberers_table.verticalHeader().setVisible(False)
        
        for row, (type_name, numberer) in enumerate(numberers.items()):
            # Select checkbox
            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox::indicator { width: 15px; height: 15px; }")
            # Connect checkboxes to ensure mutual exclusivity
            checkbox.toggled.connect(lambda checked, btn=checkbox: self.on_checkbox_toggled(checked, btn))
            self.checkboxes.append(checkbox)
            
            # If this was the previously selected numberer, check its checkbox
            if selected_numberer and selected_numberer == type_name:
                checkbox.setChecked(True)
            
            checkbox_cell = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_cell)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.numberers_table.setCellWidget(row, 0, checkbox_cell)
            
            # Numberer Type
            type_item = QTableWidgetItem(type_name.capitalize())
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.numberers_table.setItem(row, 1, type_item)
            
            # Description
            description = self.get_numberer_description(type_name)
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.numberers_table.setItem(row, 2, desc_item)

    def on_checkbox_toggled(self, checked, btn):
        """Handle checkbox toggling to ensure mutual exclusivity"""
        if checked:
            # Uncheck all other checkboxes
            for checkbox in self.checkboxes:
                if checkbox != btn and checkbox.isChecked():
                    checkbox.setChecked(False)

    def get_selected_numberer_type(self):
        """Get the type of the selected numberer"""
        for row, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                type_item = self.numberers_table.item(row, 1)
                return type_item.text().lower()
        return None

    def get_selected_numberer(self):
        """
        Get the currently selected numberer type from program state
        This is a placeholder - in the actual implementation, you would
        track which numberer is currently selected in the model
        """
        # For this implementation, we'll just return the first numberer
        numberers = list(self.numberer_manager.get_all_numberers().keys())
        if numberers:
            return numberers[0]
        return None

    def select_numberer(self, numberer_type):
        """Select the numberer with the given type"""
        if numberer_type is None:
            return
            
        # Handle case when passed an actual numberer object
        if hasattr(numberer_type, "__class__"):
            # Get the class name and extract the type from it
            class_name = numberer_type.__class__.__name__
            # Remove "Numberer" from the end and convert to lowercase
            if class_name.endswith("Numberer"):
                numberer_type = class_name[:-8].lower()
            
        for row, checkbox in enumerate(self.checkboxes):
            type_item = self.numberers_table.item(row, 1)
            if type_item and type_item.text().lower() == numberer_type.lower():
                checkbox.setChecked(True)
                return

    def get_numberer_description(self, numberer_type):
        """Return description text for each numberer type"""
        descriptions = {
            "plain": "Assigns equation numbers to DOFs based on the order in which nodes are created.",
            "rcm": "Reverse Cuthill-McKee algorithm, reduces the bandwidth of the system matrix.",
            "amd": "Alternate Minimum Degree algorithm, minimizes fill-in during matrix factorization."
        }
        return descriptions.get(numberer_type.lower(), "No description available.")


if __name__ == '__main__':
    from qtpy.QtWidgets import QApplication
    import sys
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    window = NumbererManagerTab()
    window.show()
    sys.exit(app.exec_())