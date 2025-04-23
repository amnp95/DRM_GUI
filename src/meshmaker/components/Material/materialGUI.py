from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout, QMenu
)
from qtpy.QtCore import Qt

from femora.components.Material.materialBase import Material, MaterialRegistry
from femora.components.Material.materialsOpenSees import *



class MaterialManagerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Material type selection
        type_layout = QGridLayout()
        self.material_category_combo = QComboBox()
        self.material_category_combo.addItems(MaterialRegistry.get_material_categories())
        
        # Update material types when category changes
        self.material_category_combo.currentTextChanged.connect(self.update_material_types)
        
        # Material type dropdown
        self.material_type_combo = QComboBox()
        
        # Initialize material types for first category
        self.update_material_types(self.material_category_combo.currentText())
        
        create_material_btn = QPushButton("Create New Material")
        create_material_btn.clicked.connect(self.open_material_creation_dialog)
        
        type_layout.addWidget(QLabel("Material Category:"), 0, 0)
        type_layout.addWidget(self.material_category_combo, 0, 1)
        type_layout.addWidget(QLabel("Material Type:"),1, 0)
        type_layout.addWidget(self.material_type_combo, 1, 1)
        type_layout.addWidget(create_material_btn, 2, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Materials table
        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(4)  # Tag, Category, Type, Name
        self.materials_table.setHorizontalHeaderLabels(["Tag", "Category", "Type", "Name"])
        header = self.materials_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Stretch all columns
        
        # Enable context menu (right-click menu)
        self.materials_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.materials_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Select full rows when clicking
        self.materials_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.materials_table.setSelectionMode(QTableWidget.SingleSelection)
        
        layout.addWidget(self.materials_table)
        
        # Button layout for actions
        button_layout = QHBoxLayout()
        
        # Refresh materials button
        refresh_btn = QPushButton("Refresh Materials List")
        refresh_btn.clicked.connect(self.refresh_materials_list)
        button_layout.addWidget(refresh_btn)
        
        # Clear all materials button
        clear_all_btn = QPushButton("Clear All Materials")
        clear_all_btn.clicked.connect(self.clear_all_materials)
        button_layout.addWidget(clear_all_btn)
        
        layout.addLayout(button_layout)
        
        # Initial refresh
        self.refresh_materials_list()

    def update_material_types(self, category):
        """Update material types based on selected category"""
        self.material_type_combo.clear()
        self.material_type_combo.addItems(MaterialRegistry.get_material_types(category))

    def open_material_creation_dialog(self):
        """
        Open dialog to create a new material of selected type
        """
        category = self.material_category_combo.currentText()
        material_type = self.material_type_combo.currentText()
        
        dialog = MaterialCreationDialog(category, material_type, self)
        
        # Only refresh if a material was actually created
        if dialog.exec() == QDialog.Accepted and hasattr(dialog, 'created_material'):
            self.refresh_materials_list()

    def refresh_materials_list(self):
        """
        Update the materials table with current materials
        """
        # Clear existing rows
        self.materials_table.setRowCount(0)
        
        # Get all materials
        materials = Material.get_all_materials()
        
        # Set row count
        self.materials_table.setRowCount(len(materials))
        
        # Populate table
        for row, (tag, material) in enumerate(materials.items()):
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.materials_table.setItem(row, 0, tag_item)
            
            # Material Category
            category_item = QTableWidgetItem(material.material_type.split()[0])
            category_item.setFlags(category_item.flags() & ~Qt.ItemIsEditable)
            self.materials_table.setItem(row, 1, category_item)
            
            # Material Type
            type_item = QTableWidgetItem(material.material_name)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.materials_table.setItem(row, 2, type_item)
            
            # User Name
            name_item = QTableWidgetItem(material.user_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.materials_table.setItem(row, 3, name_item)

    def show_context_menu(self, position):
        """
        Show context menu for materials table
        """
        menu = QMenu()
        edit_action = menu.addAction("Edit Material")
        delete_action = menu.addAction("Delete Material")
        action = menu.exec_(self.materials_table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            selected_row = self.materials_table.currentRow()
            if selected_row != -1:
                tag = int(self.materials_table.item(selected_row, 0).text())
                material = Material.get_material_by_tag(tag)
                self.open_material_edit_dialog(material)
        elif action == delete_action:
            selected_row = self.materials_table.currentRow()
            if selected_row != -1:
                tag = int(self.materials_table.item(selected_row, 0).text())
                self.delete_material(tag)

    def clear_all_materials(self):
        """
        Clear all materials from the system
        """
        reply = QMessageBox.question(self, 'Clear All Materials', 
                                     "Are you sure you want to delete all materials?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            Material.clear_all_materials()
            self.refresh_materials_list()

    def open_material_edit_dialog(self, material):
        """
        Open dialog to edit an existing material
        """
        dialog = MaterialEditDialog(material, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_materials_list()

    def delete_material(self, tag):
        """
        Delete a material from the system
        """
        # Confirm deletion
        reply = QMessageBox.question(self, 'Delete Material', 
                                     f"Are you sure you want to delete material with tag {tag}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            Material.delete_material(tag)
            self.refresh_materials_list()

class MaterialCreationDialog(QDialog):
    def __init__(self, material_category, material_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Create {material_category} {material_type} Material")
        self.material_category = material_category
        self.material_type = material_type

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # User-specified Name
        self.user_name_input = QLineEdit()
        form_layout.addRow("Material Name:", self.user_name_input)

        material_class = MaterialRegistry._material_types[material_category][material_type]

        # Parameter inputs
        self.param_inputs = {}
        description = material_class.get_description()

        # Create a grid layout for input fields
        grid_layout = QGridLayout()

        # Add label and input fields to the grid layout
        row = 0
        for param, desc in zip(material_class.get_parameters(), description):
            label = QLabel(param)
            input_field = QLineEdit()
            description_label = QLabel(desc)

            # Add the label and input field to the grid
            grid_layout.addWidget(label, row, 0)  # Label in column 0
            grid_layout.addWidget(input_field, row, 1)  # Input field in column 1
            grid_layout.addWidget(description_label, row, 2)  # Description in column 2

            self.param_inputs[param] = input_field
            row += 1

        # Add the grid layout to the form
        form_layout.addRow(grid_layout)
        layout.addLayout(form_layout)


        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create Material")
        create_btn.clicked.connect(self.create_material)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_material(self):
        try:
            # Validate user name
            user_name = self.user_name_input.text().strip()
            if not user_name:
                QMessageBox.warning(self, "Input Error", "Please enter a material name.")
                return
            else:
                if user_name in Material._names:
                    QMessageBox.warning(self, "Input Error", f"Material with name {user_name} already exists.")
                    return

            # Collect parameters
            params = {}
            for param, input_field in self.param_inputs.items():
                value = input_field.text().strip()
                if value:
                    params[param] = float(value)

            if not params:
                QMessageBox.warning(self, "Input Error",
                                    "Please enter at least one material parameter.")
                return

            # Create material
            self.created_material = MaterialRegistry.create_material(
                material_category=self.material_category, 
                material_type=self.material_type, 
                user_name=user_name, 
                **params
            )
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error",
                                f"Invalid input: {str(e)}\nPlease enter numeric values.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class MaterialEditDialog(QDialog):
    def __init__(self, material, parent=None):
        super().__init__(parent)
        self.material = material
        self.setWindowTitle(f"Edit {material.material_name} Material (Tag: {material.tag})")

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # User-specified Name (locked)
        self.user_name_input = QLineEdit(material.user_name)
        self.user_name_input.setReadOnly(True)
        form_layout.addRow("Material Name:", self.user_name_input)

        # Create a grid layout for parameter inputs
        grid_layout = QGridLayout()

        # Parameter inputs
        self.param_inputs = {}
        params = self.material.get_parameters()
        description = self.material.get_description()
        current_values = self.material.get_values(params)

        # Add label and input fields to the grid layout
        row = 0
        for param,desc in zip(params, description):
            label = QLabel(param)
            input_field = QLineEdit()
            
            # Set the current value if available
            if current_values.get(param) is not None:
                input_field.setText(str(current_values[param]))
            
            # Add the label and input field to the grid
            grid_layout.addWidget(label, row, 0)  # Label in column 0
            grid_layout.addWidget(input_field, row, 1)  # Input field in column 1
            grid_layout.addWidget(QLabel(desc), row, 2)  # Description in column 2
            
            # Store the input field for future reference
            self.param_inputs[param] = input_field
            row += 1

        # Add the grid layout to the form layout
        form_layout.addRow(grid_layout)

        # Add the form layout to the main layout
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit Material")
        edit_btn.clicked.connect(self.edit_material)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def edit_material(self):
        try:
            new_values = {}
            for param, input_field in self.param_inputs.items():
                value = input_field.text().strip()
                if value:
                    new_values[param] = value

            if not new_values:
                QMessageBox.warning(self, "Input Error",
                                    "Please enter at least one material parameter.")
                return

            self.material.update_values(**new_values)
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error",
                                f"Invalid input: {str(e)}\nPlease enter numeric values.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = MaterialManagerTab()
    window.show()
    sys.exit(app.exec_())