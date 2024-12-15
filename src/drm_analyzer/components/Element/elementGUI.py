from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                               QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout)
from drm_analyzer.components.Element.elementBase import Element, ElementRegistry
from drm_analyzer.components.Element.elementsOpenSees import *
from drm_analyzer.components.Material.materialBase import Material


class ElementManagerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Element type selection
        type_layout = QGridLayout()
        
        # Element type dropdown
        self.element_type_combo = QComboBox()
        self.element_type_combo.addItems(ElementRegistry.get_element_types())
        
        create_element_btn = QPushButton("Create New Element")
        create_element_btn.clicked.connect(self.open_element_creation_dialog)
        
        type_layout.addWidget(QLabel("Element Type:"), 0, 0)
        type_layout.addWidget(self.element_type_combo, 0, 1)
        type_layout.addWidget(create_element_btn, 1, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Elements table
        self.elements_table = QTableWidget()
        self.elements_table.setColumnCount(6)  # Tag, Type, Material, Parameters, Edit, Delete
        self.elements_table.setHorizontalHeaderLabels(["Tag", "Type", "Material", "Parameters", "Edit", "Delete"])
        header = self.elements_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Stretch all columns
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Except for the first one
        
        layout.addWidget(self.elements_table)
        
        # Refresh elements button
        refresh_btn = QPushButton("Refresh Elements List")
        refresh_btn.clicked.connect(self.refresh_elements_list)
        layout.addWidget(refresh_btn)
        
        # Initial refresh
        self.refresh_elements_list()

    def open_element_creation_dialog(self):
        """
        Open dialog to create a new element of selected type
        """
        element_type = self.element_type_combo.currentText()
        
        dialog = ElementCreationDialog(element_type, self)
        
        # Only refresh if an element was actually created
        if dialog.exec() == QDialog.Accepted and hasattr(dialog, 'created_element'):
            self.refresh_elements_list()

    def refresh_elements_list(self):
        """
        Update the elements table with current elements
        """
        # Clear existing rows
        self.elements_table.setRowCount(0)
        
        # Get all elements
        elements = Element.get_all_elements()
        
        # Set row count
        self.elements_table.setRowCount(len(elements))
        
        # Populate table
        for row, (tag, element) in enumerate(elements.items()):
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.elements_table.setItem(row, 0, tag_item)
            
            # Element Type
            type_item = QTableWidgetItem(element.element_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.elements_table.setItem(row, 1, type_item)
            
            # Material
            material = element.get_material()
            material_item = QTableWidgetItem(material.user_name if material else "No Material")
            material_item.setFlags(material_item.flags() & ~Qt.ItemIsEditable)
            self.elements_table.setItem(row, 2, material_item)
            
            # Parameters 
            params_str = ", ".join([f"{k}: {v}" for k, v in element.get_values(element.get_parameters()).items()])
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.elements_table.setItem(row, 3, params_item)
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, elem=element: self.open_element_edit_dialog(elem))
            self.elements_table.setCellWidget(row, 4, edit_btn)

            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, tag=tag: self.delete_element(tag))
            self.elements_table.setCellWidget(row, 5, delete_btn)

    def open_element_edit_dialog(self, element):
        """
        Open dialog to edit an existing element
        """
        dialog = ElementEditDialog(element, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_elements_list()

    def delete_element(self, tag):
        """
        Delete an element from the system
        """
        # Confirm deletion
        reply = QMessageBox.question(self, 'Delete Element', 
                                     f"Are you sure you want to delete element with tag {tag}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            Element.delete_element(tag)
            self.refresh_elements_list()


class ElementCreationDialog(QDialog):
    def __init__(self, element_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Create {element_type} Element")
        self.element_type = element_type

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Get the element class
        self.element_class = ElementRegistry._element_types[element_type]

        # Parameter inputs
        self.param_inputs = {}
        parameters = self.element_class.get_parameters()

        # Create a grid layout for input fields
        grid_layout = QGridLayout()

        # Material selection
        self.material_combo = QComboBox()
        self.materials = list(Material.get_all_materials().values())
        self.material_combo.addItem("No Material")
        for material in self.materials:
            self.material_combo.addItem(f"{material.user_name} (Category: {material.material_type} Type: {material.material_name})")
        form_layout.addRow("Assign Material:", self.material_combo)


        # dof selection
        self.dof_combo = QComboBox()
        dofs = self.element_class.get_possible_dofs()
        self.dof_combo.addItems(dofs)
        form_layout.addRow("Assign DOF:", self.dof_combo)


        # Add label and input fields to the grid layout
        row = 0
        description = self.element_class.get_description()
        for param,desc in zip(parameters,description):
            input_field = QLineEdit()

            # Add the label and input field to the grid
            grid_layout.addWidget(QLabel(param), row, 0)  # Label in column 0
            grid_layout.addWidget(input_field, row, 1)  # Input field in column 1
            grid_layout.addWidget(QLabel(desc), row, 2)  # Description in column 2

            self.param_inputs[param] = input_field
            row += 1

        # Add the grid layout to the form
        form_layout.addRow(grid_layout)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create Element")
        create_btn.clicked.connect(self.create_element)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_element(self):
        try:
            # Assign material if selected
            material_index = self.material_combo.currentIndex()
            if material_index > 0:
                material = self.materials[material_index - 1]
                if not self.element_class._is_material_compatible(material):
                    raise ValueError("Selected material is not compatible with element type")
            else:
                raise ValueError("Please select a material for the element")
            
            # Assign DOF if selected
            dof = self.dof_combo.currentText()
            if dof:
                dof = int(dof)
            else:
                raise ValueError("Invalid number of DOFs returned")
            

            # Collect parameters
            params = {}
            for param, input_field in self.param_inputs.items():
                value = input_field.text().strip()
                if value:
                    params[param] = value


            params = self.element_class.validate_element_parameters(**params)
            # Create element
            self.created_element = ElementRegistry.create_element(
                element_type=self.element_type, 
                ndof=dof,
                material=material,
                **params
            )

            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error",
                                f"Invalid input: {str(e)}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ElementEditDialog(QDialog):
    def __init__(self, element, parent=None):
        super().__init__(parent)
        self.element = element
        self.setWindowTitle(f"Edit {element.element_type} Element (Tag: {element.tag})")

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Material selection
        self.material_combo = QComboBox()
        self.materials = list(Material.get_all_materials().values())
        self.material_combo.addItem("No Material")
        
        current_material = element.get_material()
        selected_index = 0
        for i, material in enumerate(self.materials):
            self.material_combo.addItem(f"{material.user_name} (Category: {material.material_type} Type: {material.material_name})")
            if current_material and current_material.user_name == material.user_name:
                selected_index = i
        
        self.material_combo.setCurrentIndex(selected_index)
        form_layout.addRow("Assign Material:", self.material_combo)


        # dof selection
        self.dof_combo = QComboBox()
        dofs = self.element.get_possible_dofs()
        self.dof_combo.addItems(dofs)
        if str(self.element._ndof) in dofs:
            self.dof_combo.setCurrentText(str(self.element._ndof))
        else:
            raise ValueError("Invalid number of DOFs returned")
        form_layout.addRow("Assign DOF:", self.dof_combo)


        # Create a grid layout for parameter inputs
        grid_layout = QGridLayout()

        # Parameter inputs
        self.param_inputs = {}
        params = element.get_parameters()
        current_values = element.get_values(params)

        # Add label and input fields to the grid layout
        row = 0
        description = element.get_description()
        for param,desc in zip(params,description):
            
            input_field = QLineEdit()
            
            # Set the current value if available
            if current_values.get(param) is not None:
                input_field.setText(str(current_values[param]))
            
            # Add the label and input field to the grid
            grid_layout.addWidget(QLabel(param), row, 0)  # Label in column 0
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
        edit_btn = QPushButton("Edit Element")
        edit_btn.clicked.connect(self.edit_element)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def edit_element(self):
        try:
            # Assign material if selected
            material_index = self.material_combo.currentIndex()
            if material_index > 0:
                material = self.materials[material_index - 1]
            else:
                raise ValueError("Please select a material for the element")
            
            self.element.assign_material(material)

            # assign DOF if selected
            dof = self.dof_combo.currentText()
            if dof:
                dof = int(dof)
            else:
                raise ValueError("Invalid number of DOFs returned")
            self.element.assign_ndof(dof)

            # Update parameters
            new_values = {}
            for param, input_field in self.param_inputs.items():
                value = input_field.text().strip()
                if value:
                    new_values[param] = value

            new_values = self.element.validate_element_parameters(**new_values)
            # Update element values
            self.element.update_values(new_values)

            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error",
                                f"Invalid input: {str(e)}\nPlease enter appropriate values.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    from drm_analyzer.components.Material.materialsOpenSees import ElasticIsotropicMaterial, ElasticUniaxialMaterial
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    ElasticIsotropicMaterial(user_name="Steel", E=200e3, ν=0.3, ρ=7.85e-9)
    ElasticIsotropicMaterial(user_name="Concrete", E=30e3, ν=0.2, ρ=24e-9)
    ElasticIsotropicMaterial(user_name="Aluminum", E=70e3, ν=0.33, ρ=2.7e-9)
    ElasticUniaxialMaterial(user_name="Steel", E=200e3, eta=0.1)
    # Create and show the ElementManagerTab directly
    element_manager_tab = ElementManagerTab()
    element_manager_tab.show()

    sys.exit(app.exec())
