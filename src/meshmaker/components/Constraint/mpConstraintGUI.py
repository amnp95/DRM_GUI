from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout
)
from meshmaker.components.Constraint.mpConstraint import (
    mpConstraint, equalDOF, rigidLink, rigidDiaphragm, mpConstraintManager
)

class MPConstraintManagerTab(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Constraint type selection
        type_layout = QGridLayout()
        
        # Constraint type dropdown
        self.constraint_type_combo = QComboBox()
        self.constraint_type_combo.addItems(["equalDOF", "rigidLink", "rigidDiaphragm"])
        
        create_constraint_btn = QPushButton("Create New Constraint")
        create_constraint_btn.clicked.connect(self.open_constraint_creation_dialog)
        
        type_layout.addWidget(QLabel("Constraint Type:"), 0, 0)
        type_layout.addWidget(self.constraint_type_combo, 0, 1)
        type_layout.addWidget(create_constraint_btn, 1, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Constraints table
        self.constraints_table = QTableWidget()
        self.constraints_table.setColumnCount(7)  # Tag, Type, Master, Slaves, Parameters, Edit, Delete
        self.constraints_table.setHorizontalHeaderLabels(["Tag", "Type", "Master", "Slaves", "Parameters", "Edit", "Delete"])
        header = self.constraints_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.constraints_table)
        
        # Refresh constraints button
        refresh_btn = QPushButton("Refresh Constraints List")
        refresh_btn.clicked.connect(self.refresh_constraints_list)
        layout.addWidget(refresh_btn)
        
        # Initial refresh
        self.refresh_constraints_list()

    def open_constraint_creation_dialog(self):
        """Open dialog to create new constraint"""
        constraint_type = self.constraint_type_combo.currentText()
        dialog = MPConstraintCreationDialog(constraint_type, self)
        
        if dialog.exec() == QDialog.Accepted:
            self.refresh_constraints_list()

    def refresh_constraints_list(self):
        """Update constraints table with current data"""
        self.constraints_table.setRowCount(0)
        constraints = mpConstraint._constraints.values()
        
        self.constraints_table.setRowCount(len(constraints))
        
        for row, constraint in enumerate(constraints):
            # Tag
            tag_item = QTableWidgetItem(str(constraint.tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.constraints_table.setItem(row, 0, tag_item)
            
            # Type
            type_item = QTableWidgetItem(constraint.__class__.__name__)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.constraints_table.setItem(row, 1, type_item)
            
            # Master Node
            master_item = QTableWidgetItem(str(constraint.master_node))
            master_item.setFlags(master_item.flags() & ~Qt.ItemIsEditable)
            self.constraints_table.setItem(row, 2, master_item)
            
            # Slave Nodes
            slaves_str = ", ".join(map(str, constraint.slave_nodes))
            slaves_item = QTableWidgetItem(slaves_str)
            slaves_item.setFlags(slaves_item.flags() & ~Qt.ItemIsEditable)
            self.constraints_table.setItem(row, 3, slaves_item)
            
            # Parameters
            params = []
            if isinstance(constraint, equalDOF):
                params = f"DOFs: {', '.join(map(str, constraint.dofs))}"
            elif isinstance(constraint, rigidLink):
                params = f"Type: {constraint.type}"
            elif isinstance(constraint, rigidDiaphragm):
                params = f"Direction: {constraint.direction}"
            params_item = QTableWidgetItem(params)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.constraints_table.setItem(row, 4, params_item)
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, c=constraint: self.open_constraint_edit_dialog(c))
            self.constraints_table.setCellWidget(row, 5, edit_btn)

            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, tag=constraint.tag: self.delete_constraint(tag))
            self.constraints_table.setCellWidget(row, 6, delete_btn)

    def open_constraint_edit_dialog(self, constraint):
        """Open dialog to edit existing constraint"""
        dialog = MPConstraintEditDialog(constraint, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_constraints_list()

    def delete_constraint(self, tag):
        """Delete constraint from system"""
        reply = QMessageBox.question(
            self, 'Delete Constraint',
            f"Delete constraint with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            mpConstraintManager().remove_constraint(tag)
            self.refresh_constraints_list()

class MPConstraintCreationDialog(QDialog):
    def __init__(self, constraint_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Create {constraint_type} Constraint")
        self.constraint_type = constraint_type
        self.manager = mpConstraintManager()
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Common fields
        self.master_input = QLineEdit()
        self.slaves_input = QLineEdit()
        
        form_layout.addRow("Master Node:", self.master_input)
        form_layout.addRow("Slave Nodes (comma separated):", self.slaves_input)
        
        # Type-specific fields
        self.type_specific_widget = QWidget()
        type_layout = QFormLayout(self.type_specific_widget)
        
        if constraint_type == "equalDOF":
            self.dofs_input = QLineEdit()
            type_layout.addRow("DOFs (space separated):", self.dofs_input)
        elif constraint_type == "rigidLink":
            self.type_combo = QComboBox()
            self.type_combo.addItems(["bar", "beam"])
            type_layout.addRow("Link Type:", self.type_combo)
        elif constraint_type == "rigidDiaphragm":
            self.direction_input = QLineEdit()
            type_layout.addRow("Direction:", self.direction_input)
        
        form_layout.addRow(self.type_specific_widget)
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_constraint)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_constraint(self):
        try:
            master = int(self.master_input.text())
            slaves = [int(n.strip()) for n in self.slaves_input.text().split(",")]
            
            args = [master, slaves]
            
            if self.constraint_type == "equalDOF":
                dofs = list(map(int, self.dofs_input.text().split()))
                args.append(dofs)
            elif self.constraint_type == "rigidLink":
                args.insert(0, self.type_combo.currentText())
            elif self.constraint_type == "rigidDiaphragm":
                args.insert(0, int(self.direction_input.text()))
            
            self.manager.create_constraint(self.constraint_type, *args)
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {str(e)}")

class MPConstraintEditDialog(QDialog):
    def __init__(self, constraint, parent=None):
        super().__init__(parent)
        self.constraint = constraint
        self.manager = mpConstraintManager()
        self.setWindowTitle(f"Edit {type(constraint).__name__} Constraint")
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Master Node
        self.master_input = QLineEdit(str(constraint.master_node))
        form_layout.addRow("Master Node:", self.master_input)
        
        # Slave Nodes
        self.slaves_input = QLineEdit(", ".join(map(str, constraint.slave_nodes)))
        form_layout.addRow("Slave Nodes:", self.slaves_input)
        
        # Type-specific fields
        if isinstance(constraint, equalDOF):
            self.dofs_input = QLineEdit(" ".join(map(str, constraint.dofs)))
            form_layout.addRow("DOFs:", self.dofs_input)
        elif isinstance(constraint, rigidLink):
            self.type_combo = QComboBox()
            self.type_combo.addItems(["bar", "beam"])
            self.type_combo.setCurrentText(constraint.type)
            form_layout.addRow("Type:", self.type_combo)
        elif isinstance(constraint, rigidDiaphragm):
            self.direction_input = QLineEdit(str(constraint.direction))
            form_layout.addRow("Direction:", self.direction_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)

    def save_changes(self):
        try:
            # Update common properties
            new_master = int(self.master_input.text())
            new_slaves = [int(n.strip()) for n in self.slaves_input.text().split(",")]
            
            # Recreate constraint with new parameters
            self.manager.remove_constraint(self.constraint.tag)
            
            args = [new_master, new_slaves]
            if isinstance(self.constraint, equalDOF):
                new_dofs = list(map(int, self.dofs_input.text().split()))
                args.append(new_dofs)
            elif isinstance(self.constraint, rigidLink):
                args.insert(0, self.type_combo.currentText())
            elif isinstance(self.constraint, rigidDiaphragm):
                args.insert(0, int(self.direction_input.text()))
            
            self.manager.create_constraint(type(self.constraint).__name__, *args)
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {str(e)}")

if __name__ == '__main__':
    from qtpy.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    manager_tab = MPConstraintManagerTab()
    manager_tab.show()
    sys.exit(app.exec())