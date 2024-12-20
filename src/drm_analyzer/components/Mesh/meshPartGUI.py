'''
This module provides the GUI components for managing mesh parts in the DRM Analyzer application.
It includes the main tab for managing mesh parts, as well as dialogs for creating, editing, and viewing mesh parts.
Classes:
    MeshPartManagerTab(QWidget): Main tab for managing mesh parts.
    MeshPartViewOptionsDialog(QDialog): Dialog for modifying view options of a MeshPart instance.
    MeshPartCreationDialog(QDialog): Dialog for creating a new mesh part.
    MeshPartEditDialog(QDialog): Dialog for editing an existing mesh part.
Functions:
    update_mesh_part_types(category): Update mesh part types based on selected category.
    open_mesh_part_creation_dialog(): Open dialog to create a new mesh part of selected type.
    open_mesh_part_view_dialog(mesh_part): Open dialog to modify view options for a mesh part.
    refresh_mesh_parts_list(): Update the mesh parts table with current mesh parts.
    open_mesh_part_edit_dialog(mesh_part): Open dialog to edit an existing mesh part.
    delete_mesh_part(user_name): Delete a mesh part from the system.
    update_opacity(value): Update mesh part opacity.
    update_edge_visibility(state): Toggle edge visibility.
    choose_color(): Open color picker dialog.
    toggle_visibility(state): Toggle mesh part visibility.
    open_element_creation_dialog(): Opens the ElementCreationDialog for creating a new element.
    create_mesh_part(): Create a new mesh part based on input.
    update_plotter(): Update the plotter with the new mesh part.
    save_mesh_part(): Save changes to the mesh part.

'''
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QGroupBox, QMessageBox, QHeaderView, QGridLayout, 
    QCheckBox, QDialogButtonBox, QColorDialog, QSlider
)
from qtpy.QtCore import Qt

from meshmaker.components.Mesh.meshPartBase import MeshPart, MeshPartRegistry
from meshmaker.components.Element.elementBase import ElementRegistry
from meshmaker.components.Element.elementGUI import ElementCreationDialog
from meshmaker.gui.plotter import PlotterManager
from meshmaker.components.Mesh.meshPartInstance import *


class MeshPartManagerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Mesh part type selection
        type_layout = QGridLayout()
        self.mesh_part_category_combo = QComboBox()
        self.mesh_part_category_combo.addItems(MeshPartRegistry.get_mesh_part_categories())
        
        # Update mesh part types when category changes
        self.mesh_part_category_combo.currentTextChanged.connect(self.update_mesh_part_types)
        
        # Mesh part type dropdown
        self.mesh_part_type_combo = QComboBox()
        
        # Initialize mesh part types for first category
        self.update_mesh_part_types(self.mesh_part_category_combo.currentText())
        
        create_mesh_part_btn = QPushButton("Create New Mesh Part")
        create_mesh_part_btn.clicked.connect(self.open_mesh_part_creation_dialog)
        
        type_layout.addWidget(QLabel("Mesh Part Category:"), 0, 0)
        type_layout.addWidget(self.mesh_part_category_combo, 0, 1)
        type_layout.addWidget(QLabel("Mesh Part Type:"), 1, 0)
        type_layout.addWidget(self.mesh_part_type_combo, 1, 1)
        type_layout.addWidget(create_mesh_part_btn, 2, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Mesh parts table
        self.mesh_parts_table = QTableWidget()
        self.mesh_parts_table.setColumnCount(6)  # Name, Category, Type, View, Edit, Delete
        self.mesh_parts_table.setHorizontalHeaderLabels(["Name", "Category", 
                                                         "Type", "View", 
                                                         "Edit", "Delete"])
        header = self.mesh_parts_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Stretch all columns
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Except for the first one
        
        layout.addWidget(self.mesh_parts_table)
        
        # Refresh mesh parts button
        refresh_btn = QPushButton("Refresh Mesh Parts List")
        refresh_btn.clicked.connect(self.refresh_mesh_parts_list)
        layout.addWidget(refresh_btn)
        
        # Initial refresh
        self.refresh_mesh_parts_list()

    def update_mesh_part_types(self, category):
        """Update mesh part types based on selected category"""
        self.mesh_part_type_combo.clear()
        self.mesh_part_type_combo.addItems(MeshPartRegistry.get_mesh_part_types(category))

    def open_mesh_part_creation_dialog(self):
        """
        Open dialog to create a new mesh part of selected type
        """
        category = self.mesh_part_category_combo.currentText()
        mesh_part_type = self.mesh_part_type_combo.currentText()
        
        dialog = MeshPartCreationDialog(category, mesh_part_type, self)
        
        # Only refresh if a mesh part was actually created
        if dialog.exec() == QDialog.Accepted and hasattr(dialog, 'created_mesh_part'):
            self.refresh_mesh_parts_list()

    def open_mesh_part_view_dialog(self, mesh_part):
        """
        Open dialog to modify view options for a mesh part
        """
        dialog = MeshPartViewOptionsDialog(mesh_part, self)
        dialog.exec()

    def refresh_mesh_parts_list(self):
        """
        Update the mesh parts table with current mesh parts
        """
        # Clear existing rows
        self.mesh_parts_table.setRowCount(0)
        
        # Get all mesh parts
        mesh_parts = MeshPart.get_mesh_parts()
        
        # Set row count
        self.mesh_parts_table.setRowCount(len(mesh_parts))
        
        # Populate table
        for row, (user_name, mesh_part) in enumerate(mesh_parts.items()):
            # Name
            name_item = QTableWidgetItem(user_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.mesh_parts_table.setItem(row, 0, name_item)
            
            # Category
            category_item = QTableWidgetItem(str(mesh_part.category))
            category_item.setFlags(category_item.flags() & ~Qt.ItemIsEditable)
            self.mesh_parts_table.setItem(row, 1, category_item)
            
            # Mesh Part Type
            type_item = QTableWidgetItem(mesh_part.mesh_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.mesh_parts_table.setItem(row, 2, type_item)
            
            # View button
            view_btn = QPushButton("View")
            view_btn.clicked.connect(lambda checked, mp=mesh_part: self.open_mesh_part_view_dialog(mp))
            self.mesh_parts_table.setCellWidget(row, 3, view_btn)

            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, mp=mesh_part: self.open_mesh_part_edit_dialog(mp))
            self.mesh_parts_table.setCellWidget(row, 4, edit_btn)

            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, un=user_name: self.delete_mesh_part(un))
            self.mesh_parts_table.setCellWidget(row, 5, delete_btn)


    def open_mesh_part_edit_dialog(self, mesh_part):
        """
        Open dialog to edit an existing mesh part
        """
        dialog = MeshPartEditDialog(mesh_part, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_mesh_parts_list()

    def delete_mesh_part(self, user_name):
        """
        Delete a mesh part from the system
        """
        # Confirm deletion
        reply = QMessageBox.question(self, 'Delete Mesh Part', 
                                     f"Are you sure you want to delete mesh part '{user_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            actor = MeshPart._mesh_parts[user_name].actor
            PlotterManager.get_plotter().remove_actor(actor)
            MeshPart.delete_mesh_part(user_name)
            self.refresh_mesh_parts_list()



class MeshPartViewOptionsDialog(QDialog):
    """
    Dialog for modifying view options of a MeshPart instance
    """
    def __init__(self, mesh_part, parent=None):
        super().__init__(parent)
        self.mesh_part = mesh_part
        self.setWindowTitle(f"View Options for {mesh_part.user_name}")
       
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create a grid layout for organized options
        options_grid = QGridLayout()
        options_grid.setSpacing(10)  # Add some spacing between grid items
        
        # Opacity slider
        opacity_label = QLabel("Opacity:")
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(int(mesh_part.actor.GetProperty().GetOpacity() * 100))
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        
        options_grid.addWidget(opacity_label, 0, 0)
        options_grid.addWidget(self.opacity_slider, 0, 1)
        
        # Visibility checkbox
        self.visibility_checkbox = QCheckBox("Visible")
        self.visibility_checkbox.setChecked(True)
        self.visibility_checkbox.stateChanged.connect(self.toggle_visibility)
        options_grid.addWidget(self.visibility_checkbox, 1, 0, 1, 2)
        
        # Show edges checkbox
        self.show_edges_checkbox = QCheckBox("Show Edges")
        self.show_edges_checkbox.setChecked(mesh_part.actor.GetProperty().GetEdgeVisibility())
        self.show_edges_checkbox.stateChanged.connect(self.update_edge_visibility)
        options_grid.addWidget(self.show_edges_checkbox, 2, 0, 1, 2)
        
        # Color selection
        color_label = QLabel("Color:")
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        
        options_grid.addWidget(color_label, 3, 0)
        options_grid.addWidget(self.color_button, 3, 1)
        
        # Add the grid layout to the main layout
        layout.addLayout(options_grid)
        
        # OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def update_opacity(self, value):
        """Update mesh part opacity"""
        self.mesh_part.actor.GetProperty().SetOpacity(value / 100.0)
    
    def update_edge_visibility(self, state):
        """Toggle edge visibility"""
        self.mesh_part.actor.GetProperty().SetEdgeVisibility(bool(state))
    
    def choose_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            # Convert QColor to VTK color (0-1 range)
            vtk_color = (
                color.redF(),
                color.greenF(),
                color.blueF()
            )
            self.mesh_part.actor.GetProperty().SetColor(vtk_color)
    
    def toggle_visibility(self, state):
        """Toggle mesh part visibility"""
        self.mesh_part.actor.visibility = bool(state)


class MeshPartCreationDialog(QDialog):
    """
    Dialog for creating a new mesh part
    """
    
    def __init__(self, category, mesh_part_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Create New {mesh_part_type} Mesh Part")
        
        # Store the created mesh part
        self.created_mesh_part = None
        self.created_element = None
        self.plotter = PlotterManager.get_plotter()

        # Main Layout
        main_layout = QVBoxLayout(self)

        # Group Box for Username and Element
        user_element_group = QGroupBox("User and Element Selection")
        user_element_layout = QGridLayout(user_element_group)

        # User Name input
        self.user_name_input = QLineEdit()
        user_element_layout.addWidget(QLabel("User Name:"), 0, 0)
        user_element_layout.addWidget(self.user_name_input, 0, 1, 1, 2)

        # Element selection
        self.create_element_btn = QPushButton("Create Element")
        self.element_combo = QComboBox()
        self.element_combo.addItems(ElementRegistry.get_element_types())
        user_element_layout.addWidget(QLabel("Element:"), 1, 0)
        user_element_layout.addWidget(self.element_combo, 1, 1)
        user_element_layout.addWidget(self.create_element_btn, 1, 2)
        self.create_element_btn.clicked.connect(self.open_element_creation_dialog)

        main_layout.addWidget(user_element_group)

        # Group Box for Dynamic Parameters
        parameters_group = QGroupBox("Mesh Part Parameters")
        parameters_layout = QGridLayout(parameters_group)

        self.parameter_inputs = {}
        self.mesh_part_class = MeshPartRegistry._mesh_part_types[category][mesh_part_type]
        for row, (param_name, param_description) in enumerate(self.mesh_part_class.get_parameters()):
            param_input = QLineEdit()
            parameters_layout.addWidget(QLabel(f"{param_name}:"), row, 0)
            parameters_layout.addWidget(param_input, row, 1)
            parameters_layout.addWidget(QLabel(f"({param_description})"), row, 2)
            self.parameter_inputs[param_name] = param_input

        main_layout.addWidget(parameters_group)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_mesh_part)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(cancel_btn)

        main_layout.addLayout(buttons_layout)


    def open_element_creation_dialog(self):
        """
        Opens the ElementCreationDialog for creating a new element.
        """
        element_type = self.element_combo.currentText()
    
        if not element_type:
            QMessageBox.warning(self, "Error", "Please select an element type before creating.")
            return
        

        comp_elements = self.mesh_part_class.get_compatible_elements()
        if element_type not in comp_elements:
            QMessageBox.warning(self, "Error", f"Element type {element_type} is not compatible with this mesh part.\n Compatible elements are: {comp_elements}")
            return


        dialog = ElementCreationDialog(element_type, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.created_element = dialog.created_element

            

    def create_mesh_part(self):
        """
        Create a new mesh part based on input
        """
        try:
            # Validate and collect parameters
            user_name = self.user_name_input.text().strip()
            if not user_name:
                raise ValueError("User name cannot be empty")

            if not self.created_element:
                raise ValueError("Please create an element first")

            # Collect and validate parameters
            params = {name: widget.text().strip() for name, widget in self.parameter_inputs.items()}

            # Get the current mesh part class
            category = self.parent().mesh_part_category_combo.currentText()
            mesh_part_type = self.parent().mesh_part_type_combo.currentText()
            mesh_part_class = MeshPartRegistry._mesh_part_types[category][mesh_part_type]

            # Validate parameters and create mesh part
            validated_params = mesh_part_class.validate_parameters(**params)
            mesh_part = mesh_part_class(user_name=user_name,
                                        element=self.created_element,
                                        **validated_params)

            # Mark as created and accept the dialog
            self.created_mesh_part = mesh_part
            self.update_plotter()
            self.accept()


        except Exception as e:
            if self.created_element:
                ElementRegistry.delete_element(self.created_element.user_name)
            QMessageBox.warning(self, "Error", str(e))


    def update_plotter(self):
        """
        Update the plotter with the new mesh part
        """
        self.created_mesh_part.generate_mesh()
        self.created_mesh_part.actor = self.plotter.add_mesh(self.created_mesh_part.mesh, 
                                                                 style= "surface",
                                                                 opacity=1.0,
                                                                 show_edges=True)


class MeshPartEditDialog(QDialog):
    """
    Dialog for editing an existing mesh part
    """
    def __init__(self, mesh_part, parent=None):
        super().__init__(parent)
        self.mesh_part = mesh_part
        self.setWindowTitle(f"Edit Mesh Part: {mesh_part.user_name}")
        
        self.plotter = PlotterManager.get_plotter()

        # Main Layout
        main_layout = QVBoxLayout(self)

        # Group Box for Read-Only Information
        info_group = QGroupBox("Mesh Part Information")
        info_layout = QGridLayout(info_group)

        # User Name (read-only)
        info_layout.addWidget(QLabel("User Name:"), 0, 0)
        user_name_label = QLabel(mesh_part.user_name)
        info_layout.addWidget(user_name_label, 0, 1)

        # Element (read-only)
        info_layout.addWidget(QLabel("Element:"), 1, 0)
        element_label = QLabel(str(mesh_part.element.element_type))
        info_layout.addWidget(element_label, 1, 1)

        # Material (read-only)
        info_layout.addWidget(QLabel("Material:"), 2, 0)
        material_label = QLabel(f"{mesh_part.element._material.user_name} ({mesh_part.element._material.material_type}-{mesh_part.element._material.material_name})")
        info_layout.addWidget(material_label, 2, 1)

        #ndof (read-only)
        info_layout.addWidget(QLabel("num dof:"), 3, 0)
        ndof_label = QLabel(str(mesh_part.element._ndof))
        info_layout.addWidget(ndof_label, 3, 1)

        main_layout.addWidget(info_group)

        # Group Box for Dynamic Parameters
        parameters_group = QGroupBox("Mesh Part Parameters")
        parameters_layout = QGridLayout(parameters_group)

        # Dynamically add parameter inputs based on mesh part type
        self.parameter_inputs = {}
        for row, (param_name, param_description) in enumerate(type(mesh_part).get_parameters()):
            current_value = mesh_part.params.get(param_name, '')
            param_input = QLineEdit(str(current_value))
            parameters_layout.addWidget(QLabel(f"{param_name}:"), row, 0)
            parameters_layout.addWidget(param_input, row, 1)
            parameters_layout.addWidget(QLabel(f"({param_description})"), row, 2)
            self.parameter_inputs[param_name] = param_input

        main_layout.addWidget(parameters_group)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_mesh_part)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        main_layout.addLayout(buttons_layout)

    def save_mesh_part(self):
        """
        Save changes to the mesh part
        """
        try:
            # Collect and validate parameters
            params = {}
            for param_name, input_widget in self.parameter_inputs.items():
                params[param_name] = input_widget.text().strip()
            
            # Validate parameters
            self.mesh_part.update_parameters(**params)

            # Regenerate mesh if needed (you might want to implement this in the MeshPart class)
            self.update_plotter()
            self.accept()
        
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def update_plotter(self):
        """
        Update the plotter with the new mesh part
        """
        self.plotter.remove_actor(self.mesh_part.actor)
        self.mesh_part.generate_mesh()
        self.mesh_part.actor = self.plotter.add_mesh(self.mesh_part.mesh, 
                                                                 style= "surface",
                                                                 opacity=1.0,
                                                                 show_edges=True)

if __name__ == "__main__":
    '''
    Test the MeshPartManagerTab GUI
    '''
    from PySide6.QtWidgets import QApplication
    from meshmaker.components.Material.materialsOpenSees import ElasticIsotropicMaterial, ElasticUniaxialMaterial
    import sys
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    ElasticIsotropicMaterial(user_name="Steel",    E=200e3, ν=0.3,  ρ=7.85e-9)
    ElasticIsotropicMaterial(user_name="Concrete", E=30e3,  ν=0.2,  ρ=24e-9)
    ElasticIsotropicMaterial(user_name="Aluminum", E=70e3,  ν=0.33, ρ=2.7e-9)
    ElasticUniaxialMaterial(user_name="Steel2",    E=200e3, eta=0.1)


    # Create and display the main window
    window = MeshPartManagerTab()
    window.show()

    
    sys.exit(app.exec())