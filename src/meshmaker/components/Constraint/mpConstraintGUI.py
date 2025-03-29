from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout, QMenu,
    QSizePolicy
)
from meshmaker.components.Constraint.mpConstraint import (
    mpConstraint, equalDOF, rigidLink, rigidDiaphragm, mpConstraintManager
)

class MPConstraintManagerTab(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configure dialog size and properties
        self.setWindowTitle("MP Constraints Manager")
        self.resize(800, 600)  # Set initial size to be large enough
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
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
        self.constraints_table.setColumnCount(5)  # Tag, Type, Master, Slaves, Parameters
        self.constraints_table.setHorizontalHeaderLabels(["Tag", "Type", "Master", "Slaves", "Parameters"])
        
        # Configure table appearance
        self.constraints_table.verticalHeader().setVisible(False)  # Hide row numbers/index
        self.constraints_table.setMinimumWidth(750)  # Set minimum width for the table
        self.constraints_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set horizontal header to resize properly
        header = self.constraints_table.horizontalHeader()
        header.setStretchLastSection(True)  # Last section fills remaining space
        header.setSectionResizeMode(QHeaderView.Interactive)  # Allow manual resizing
        
        # Set default column widths
        self.constraints_table.setColumnWidth(0, 60)   # Tag column
        self.constraints_table.setColumnWidth(1, 120)  # Type column
        self.constraints_table.setColumnWidth(2, 100)  # Master column
        self.constraints_table.setColumnWidth(3, 200)  # Slaves column
        self.constraints_table.setColumnWidth(4, 250)  # Parameters column
        
        # Configure double-click and context menu (right-click)
        self.constraints_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.constraints_table.customContextMenuRequested.connect(self.show_context_menu)
        self.constraints_table.cellDoubleClicked.connect(self.handle_double_click)
        
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
            tag_item.setData(Qt.UserRole, constraint.tag)  # Store tag for reference
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

    def handle_double_click(self, row, column):
        """Handle double-click on a table cell to edit constraint"""
        tag_item = self.constraints_table.item(row, 0)
        if tag_item:
            tag = tag_item.data(Qt.UserRole)
            constraint = mpConstraint._constraints.get(tag)
            if constraint:
                self.open_constraint_edit_dialog(constraint)

    def show_context_menu(self, position):
        """Show context menu for right-clicked table cell"""
        # Get the row under the mouse
        row = self.constraints_table.rowAt(position.y())
        if row < 0:
            return
        
        # Get the constraint tag
        tag_item = self.constraints_table.item(row, 0)
        if not tag_item:
            return
        
        tag = tag_item.data(Qt.UserRole)
        
        # Create context menu
        menu = QMenu(self)
        edit_action = menu.addAction("Edit Constraint")
        delete_action = menu.addAction("Delete Constraint")
        
        # Connect actions
        action = menu.exec_(self.constraints_table.mapToGlobal(position))
        if action == edit_action:
            constraint = mpConstraint._constraints.get(tag)
            if constraint:
                self.open_constraint_edit_dialog(constraint)
        elif action == delete_action:
            self.delete_constraint(tag)

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
    
    # Create some sample constraints for testing
    mp_manager = mpConstraintManager()
    
    # Create equalDOF constraints
    mp_manager.create_equal_dof(master_node=1, slave_nodes=[2, 3], dofs=[1, 2, 3])
    mp_manager.create_equal_dof(master_node=5, slave_nodes=[6], dofs=[4, 5, 6])
    
    # Create rigidLink constraints
    mp_manager.create_rigid_link(type_str="bar", master_node=10, slave_nodes=[11, 12, 13])
    mp_manager.create_rigid_link(type_str="beam", master_node=20, slave_nodes=[21, 22])
    
    # Create rigidDiaphragm constraints
    mp_manager.create_rigid_diaphragm(direction=3, master_node=30, slave_nodes=[31, 32, 33, 34])
    mp_manager.create_rigid_diaphragm(direction=2, master_node=40, slave_nodes=[41, 42, 43])
    
    # Start the application
    app = QApplication(sys.argv)
    manager_tab = MPConstraintManagerTab()
    manager_tab.show()
    sys.exit(app.exec())