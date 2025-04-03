from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QDialog, QMessageBox, QTableWidget, QTableWidgetItem, 
    QPushButton, QHeaderView, QRadioButton
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
        self.radio_buttons = []
        
        # Hide vertical header (row indices)
        self.numberers_table.verticalHeader().setVisible(False)
        
        for row, (type_name, numberer) in enumerate(numberers.items()):
            # Select radio button
            radio_btn = QRadioButton()
            # Connect radio buttons to ensure mutual exclusivity
            radio_btn.toggled.connect(lambda checked, btn=radio_btn: self.on_radio_toggled(checked, btn))
            self.radio_buttons.append(radio_btn)
            
            # If this was the previously selected numberer, check its radio button
            if selected_numberer and selected_numberer == type_name:
                radio_btn.setChecked(True)
            
            radio_cell = QWidget()
            radio_layout = QHBoxLayout(radio_cell)
            radio_layout.addWidget(radio_btn)
            radio_layout.setAlignment(Qt.AlignCenter)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            self.numberers_table.setCellWidget(row, 0, radio_cell)
            
            # Numberer Type
            type_item = QTableWidgetItem(type_name.capitalize())
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.numberers_table.setItem(row, 1, type_item)
            
            # Description
            description = self.get_numberer_description(type_name)
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.numberers_table.setItem(row, 2, desc_item)

    def on_radio_toggled(self, checked, btn):
        """Handle radio button toggling to ensure mutual exclusivity"""
        if checked:
            # Uncheck all other radio buttons
            for radio_btn in self.radio_buttons:
                if radio_btn != btn and radio_btn.isChecked():
                    radio_btn.setChecked(False)

    def get_selected_numberer_type(self):
        """Get the type of the selected numberer"""
        for row, radio_btn in enumerate(self.radio_buttons):
            if radio_btn.isChecked():
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