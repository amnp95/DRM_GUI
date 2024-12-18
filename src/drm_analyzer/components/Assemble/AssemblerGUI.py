import sys
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QPushButton, QVBoxLayout, QHBoxLayout, 
    QWidget, QDialog, QCheckBox, QLabel, QListWidget, QListWidgetItem, 
    QSpinBox, QComboBox, QMessageBox,QHeaderView, QTableWidget, QTableWidgetItem, QDialogButtonBox
)

from drm_analyzer.components.Mesh.meshPartBase import MeshPart
from drm_analyzer.components.Assemble.Assembler import Assembler

class AssemblyManagerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create Assembly Section button
        create_section_btn = QPushButton("Create New Assembly Section")
        create_section_btn.clicked.connect(self.open_assembly_section_creation_dialog)
        layout.addWidget(create_section_btn)
        
        # Assembly sections table
        self.assembly_sections_table = QTableWidget()
        self.assembly_sections_table.setColumnCount(5)  # Tag, Mesh Parts, Partitions, View, Delete
        self.assembly_sections_table.setHorizontalHeaderLabels([
            "Name", "Mesh Parts", "Partitions", "View", "Delete"
        ])
        header = self.assembly_sections_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.assembly_sections_table)
        
        # Refresh assembly sections button
        refresh_btn = QPushButton("Refresh Assembly Sections List")
        refresh_btn.clicked.connect(self.refresh_assembly_sections_list)
        layout.addWidget(refresh_btn)
        
        # Initial refresh
        self.refresh_assembly_sections_list()
    
    def open_assembly_section_creation_dialog(self):
        """
        Open dialog to create a new assembly section
        """
        from drm_analyzer.components.Assemble.AssemblerGUI import AssemblySectionCreationDialog
        
        dialog = AssemblySectionCreationDialog(self)
        
        # Refresh the list if a new section was created
        if dialog.exec() == QDialog.Accepted:
            self.refresh_assembly_sections_list()
    
    def refresh_assembly_sections_list(self):
        """
        Update the assembly sections table with current sections
        """
        # Get the Assembler instance
        assembler = Assembler.get_instance()
        
        # Clear existing rows
        self.assembly_sections_table.setRowCount(0)
        
        # Get all assembly sections
        assembly_sections = assembler.get_sections()
        
        # Set row count
        self.assembly_sections_table.setRowCount(len(assembly_sections))
        
        # Populate table
        for row, (tag, section) in enumerate(assembly_sections.items()):
            # Name (Section{tag})
            name_item = QTableWidgetItem(f"Section{tag}")
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.assembly_sections_table.setItem(row, 0, name_item)
            
            # Mesh Parts
            mesh_parts_str = ", ".join(section.meshparts)
            mesh_parts_item = QTableWidgetItem(mesh_parts_str)
            mesh_parts_item.setFlags(mesh_parts_item.flags() & ~Qt.ItemIsEditable)
            self.assembly_sections_table.setItem(row, 1, mesh_parts_item)
            
            # Partitions
            partitions_item = QTableWidgetItem(str(section.num_partitions))
            partitions_item.setFlags(partitions_item.flags() & ~Qt.ItemIsEditable)
            self.assembly_sections_table.setItem(row, 2, partitions_item)
            
            # View button
            view_btn = QPushButton("View")
            view_btn.clicked.connect(lambda checked, s=section: self.open_section_view_dialog(s))
            self.assembly_sections_table.setCellWidget(row, 3, view_btn)
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, t=tag: self.delete_assembly_section(t))
            self.assembly_sections_table.setCellWidget(row, 4, delete_btn)
    
    def open_section_view_dialog(self, section):
        """
        Open a dialog to view assembly section details
        """
        dialog = AssemblySectionViewDialog(section, self)
        dialog.exec()
    
    def delete_assembly_section(self, tag):
        """
        Delete an assembly section
        """
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            'Delete Assembly Section', 
            f"Are you sure you want to delete assembly section with tag '{tag}'?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            assembler = Assembler.get_instance()
            assembler.delete_section(tag)
            self.refresh_assembly_sections_list()


class AssemblySectionViewDialog(QDialog):
    """
    Dialog for viewing details of an assembly section
    """
    def __init__(self, section, parent=None):
        super().__init__(parent)
        self.section = section
        self.setWindowTitle(f"Assembly Section Details")
        
        # Main Layout
        layout = QVBoxLayout(self)
        
        # Section Details Group
        details_layout = QVBoxLayout()
        
        # Mesh Parts
        mesh_parts_label = QLabel(f"Mesh Parts: {', '.join(section.meshparts)}")
        details_layout.addWidget(mesh_parts_label)
        
        # Partitions
        partitions_label = QLabel(f"Number of Partitions: {section.num_partitions}")
        details_layout.addWidget(partitions_label)
        
        # Partition Algorithm
        algo_label = QLabel(f"Partition Algorithm: {section.partition_algorithm}")
        details_layout.addWidget(algo_label)
        
        # Merge Points
        merge_label = QLabel(f"Merge Points: {'Yes' if section.merging_points else 'No'}")
        details_layout.addWidget(merge_label)
        
        layout.addLayout(details_layout)
        
        # OK Button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)





class AssemblySectionCreationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Assembly Section")
        self.setModal(True)
        self.Assembler = Assembler.get_instance()
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Mesh Parts Selection
        mesh_parts_label = QLabel("Select Mesh Parts:")
        main_layout.addWidget(mesh_parts_label)
        
        # List of Mesh Parts
        self.mesh_parts_list = QListWidget()
        self.mesh_parts_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Populate the list with available mesh parts
        self._populate_mesh_parts()
        
        main_layout.addWidget(self.mesh_parts_list)
        
        # Partitioning Options Layout
        options_layout = QVBoxLayout()
        
        # Number of Partitions
        num_partitions_layout = QHBoxLayout()
        num_partitions_label = QLabel("Number of Partitions:")
        self.num_partitions_spinbox = QSpinBox()
        self.num_partitions_spinbox.setMinimum(0)
        self.num_partitions_spinbox.setMaximum(100)
        self.num_partitions_spinbox.setValue(0)
        
        num_partitions_layout.addWidget(num_partitions_label)
        num_partitions_layout.addWidget(self.num_partitions_spinbox)
        options_layout.addLayout(num_partitions_layout)
        
        # Partition Algorithm
        partition_algo_layout = QHBoxLayout()
        partition_algo_label = QLabel("Partition Algorithm:")
        self.partition_algo_combobox = QComboBox()
        self.partition_algo_combobox.addItems([
            "kd-tree", 
            # "metis", 
            # "scotch"  # Add more algorithms if available
        ])
        
        partition_algo_layout.addWidget(partition_algo_label)
        partition_algo_layout.addWidget(self.partition_algo_combobox)
        options_layout.addLayout(partition_algo_layout)
        
        main_layout.addLayout(options_layout)
        
        # Merge Points Checkbox
        self.merge_points_checkbox = QCheckBox("Merge Points")
        self.merge_points_checkbox.setChecked(True)
        main_layout.addWidget(self.merge_points_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("Add Section")
        ok_button.clicked.connect(self.create_section)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def _populate_mesh_parts(self):
        """
        Populate the list with available mesh parts.
        
        Uses the class method from MeshPart to retrieve existing mesh parts.
        """
        # Retrieve existing mesh parts
        existing_mesh_parts = list(MeshPart._mesh_parts.keys())
        
        # Add to the list widget
        for mesh_part in existing_mesh_parts:
            self.mesh_parts_list.addItem(QListWidgetItem(mesh_part))
    
    def get_selected_mesh_parts(self) -> List[str]:
        """
        Retrieve selected mesh part names.
        
        Returns:
            List[str]: List of selected mesh part names
        """
        return [item.text() for item in self.mesh_parts_list.selectedItems()]
    
    def get_partition_settings(self):
        """
        Retrieve partition settings from the dialog.
        
        Returns:
            Tuple containing number of partitions, algorithm, and merge points flag
        """
        return (
            self.num_partitions_spinbox.value(),
            self.partition_algo_combobox.currentText(),
            self.merge_points_checkbox.isChecked()
        )
    
    def create_section(self):
        """
        Create the assembly section based on the selected mesh parts and settings.
        """
        try:
            self.Assembler.create_section( 
                meshparts=self.get_selected_mesh_parts(),
                num_partitions=self.num_partitions_spinbox.value(),
                partition_algorithm=self.partition_algo_combobox.currentText(),
                merging_points=self.merge_points_checkbox.isChecked()
            )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Input Error",
                                f"Invalid input: {str(e)}\nPlease enter appropriate values.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        

        

if __name__ == "__main__":
    '''
    Test the AssemblyManagerTab GUI
    '''
    from PySide6.QtWidgets import QApplication
    import sys

    # Preliminary setup of mesh parts for testing
    from drm_analyzer.components.Material.materialsOpenSees import ElasticIsotropicMaterial
    from drm_analyzer.components.Element.elementsOpenSees import stdBrickElement
    from drm_analyzer.components.Mesh.meshPartInstance import StructuredRectangular3D

    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Create some test materials and elements
    elastic = ElasticIsotropicMaterial(user_name="Steel", E=200e3, ν=0.3, ρ=7.85e-9)
    stdbrik1 = stdBrickElement(ndof=3, material=elastic, b1=0, b2=0, b3=-10)
    
    # Create some test mesh parts
    StructuredRectangular3D(user_name="base", element=stdbrik1, 
                            **{'X Min': -50, 'X Max': 50, 'Y Min': -50, 'Y Max': 50, 
                               'Z Min': -30, 'Z Max': -20, 'Nx Cells': 10, 'Ny Cells': 10, 'Nz Cells': 10})
    StructuredRectangular3D(user_name="middle", element=stdbrik1,
                            **{'X Min': -50, 'X Max': 50, 'Y Min': -50, 'Y Max': 50, 
                               'Z Min': -20, 'Z Max': -10, 'Nx Cells': 10, 'Ny Cells': 10, 'Nz Cells': 10})
    StructuredRectangular3D(user_name="top", element=stdbrik1,
                            **{'X Min': -50, 'X Max': 50, 'Y Min': -50, 'Y Max': 50, 
                               'Z Min': -10, 'Z Max': 0, 'Nx Cells': 10, 'Ny Cells': 10, 'Nz Cells': 10})

    # Create and display the main window
    window = AssemblyManagerTab()
    window.show()
    
    sys.exit(app.exec())