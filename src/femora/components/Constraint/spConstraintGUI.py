from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout, 
    QStackedWidget, QRadioButton, QButtonGroup, QGroupBox, QCheckBox, QMenu,
    QScrollArea
)
from femora.components.Constraint.spConstraint import (
    SPConstraint, FixConstraint, FixXConstraint, FixYConstraint, FixZConstraint, SPConstraintManager,
    FixMacroX_max, FixMacroX_min, FixMacroY_max, FixMacroY_min, FixMacroZ_max, FixMacroZ_min
)
from femora.utils.validator import DoubleValidator, IntValidator
from femora.gui.plotter import PlotterManager
from femora.components.MeshMaker import MeshMaker


class SPConstraintManagerTab(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        layout = QVBoxLayout(self)
        self.setWindowTitle("SP Constraints Manager")
        
        # Constraint type selection
        type_layout = QGridLayout()
        
        # Constraint type dropdown
        self.constraint_type_combo = QComboBox()
        self.constraint_type_combo.addItems([
            "fix", "fixX", "fixY", "fixZ", 
            "fixMacroXmax", "fixMacroXmin", 
            "fixMacroYmax", "fixMacroYmin", 
            "fixMacroZmax", "fixMacroZmin"
        ])
        
        create_constraint_btn = QPushButton("Create New SP Constraint")
        create_constraint_btn.clicked.connect(self.open_constraint_creation_dialog)
        
        type_layout.addWidget(QLabel("Constraint Type:"), 0, 0)
        type_layout.addWidget(self.constraint_type_combo, 0, 1)
        type_layout.addWidget(create_constraint_btn, 1, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Constraints table
        self.constraints_table = QTableWidget()
        self.constraints_table.setColumnCount(3)  # Tag, Type, Parameters
        self.constraints_table.setHorizontalHeaderLabels(["Tag", "Type", "Parameters"])
        header = self.constraints_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        # Configure double-click and context menu (right-click)
        self.constraints_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.constraints_table.customContextMenuRequested.connect(self.show_context_menu)
        self.constraints_table.cellDoubleClicked.connect(self.handle_double_click)
        
        layout.addWidget(self.constraints_table)
        
        # Refresh constraints button
        refresh_btn = QPushButton("Refresh SP Constraints List")
        refresh_btn.clicked.connect(self.refresh_constraints_list)
        layout.addWidget(refresh_btn)
        
        # Initial refresh
        self.refresh_constraints_list()

    def open_constraint_creation_dialog(self):
        """Open dialog to create new constraint"""
        constraint_type = self.constraint_type_combo.currentText()
        dialog = SPConstraintCreationDialog(constraint_type, self)
        
        if dialog.exec() == QDialog.Accepted:
            self.refresh_constraints_list()

    def refresh_constraints_list(self):
        """Update constraints table with current data"""
        self.constraints_table.setRowCount(0)
        constraints = SPConstraint._constraints.values()
        
        self.constraints_table.setRowCount(len(constraints))
        
        for row, constraint in enumerate(constraints):
            # Tag
            tag_item = QTableWidgetItem(str(constraint.tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            tag_item.setData(Qt.UserRole, constraint.tag)  # Store tag for reference
            self.constraints_table.setItem(row, 0, tag_item)
            
            # Type
            constraint_type = constraint.__class__.__name__
            type_item = QTableWidgetItem(constraint_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.constraints_table.setItem(row, 1, type_item)
            
            # Parameters
            if isinstance(constraint, FixConstraint):
                params = f"Node: {constraint.node_tag}, DOFs: {' '.join(map(str, constraint.dofs))}"
            elif isinstance(constraint, FixXConstraint):
                params = f"X: {constraint.xCoordinate}, DOFs: {' '.join(map(str, constraint.dofs))}, Tol: {constraint.tol}"
            elif isinstance(constraint, FixYConstraint):
                params = f"Y: {constraint.yCoordinate}, DOFs: {' '.join(map(str, constraint.dofs))}, Tol: {constraint.tol}"
            elif isinstance(constraint, FixZConstraint):
                params = f"Z: {constraint.zCoordinate}, DOFs: {' '.join(map(str, constraint.dofs))}, Tol: {constraint.tol}"
            elif isinstance(constraint, FixMacroX_max):
                params = f"X: $X_MAX, DOFs: {' '.join(map(str, constraint.dofs))}, Tol: {constraint.tol}"
            elif isinstance(constraint, FixMacroX_min):
                params = f"X: $X_MIN, DOFs: {' '.join(map(str, constraint.dofs))}, Tol: {constraint.tol}"
            elif isinstance(constraint, FixMacroY_max):
                params = f"Y: $Y_MAX, DOFs: {' '.join(map(str, constraint.dofs))}, Tol: {constraint.tol}"
            elif isinstance(constraint, FixMacroY_min):
                params = f"Y: $Y_MIN, DOFs: {' '.join(map(str, constraint.dofs))}, Tol: {constraint.tol}"
            elif isinstance(constraint, FixMacroZ_max):
                params = f"Z: $Z_MAX, DOFs: {' '.join(map(str, constraint.dofs))}, Tol: {constraint.tol}"
            elif isinstance(constraint, FixMacroZ_min):
                params = f"Z: $Z_MIN, DOFs: {' '.join(map(str, constraint.dofs))}, Tol: {constraint.tol}"
            else:
                params = "Unknown constraint type"
                
            params_item = QTableWidgetItem(params)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.constraints_table.setItem(row, 2, params_item)

    def handle_double_click(self, row, column):
        """Handle double-click on a table cell to edit constraint"""
        tag_item = self.constraints_table.item(row, 0)
        if tag_item:
            tag = tag_item.data(Qt.UserRole)
            constraint = SPConstraint._constraints.get(tag)
            if constraint:
                self.edit_constraint(constraint)

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
            constraint = SPConstraint._constraints.get(tag)
            if constraint:
                self.edit_constraint(constraint)
        elif action == delete_action:
            self.delete_constraint(tag)

    def edit_constraint(self, constraint):
        """Open dialog to edit an existing constraint"""
        dialog = None
        if isinstance(constraint, FixConstraint):
            dialog = SPConstraintEditDialog("fix", constraint, self)
        elif isinstance(constraint, FixXConstraint):
            dialog = SPConstraintEditDialog("fixX", constraint, self)
        elif isinstance(constraint, FixYConstraint):
            dialog = SPConstraintEditDialog("fixY", constraint, self)
        elif isinstance(constraint, FixZConstraint):
            dialog = SPConstraintEditDialog("fixZ", constraint, self)
        elif isinstance(constraint, FixMacroX_max):
            dialog = SPConstraintEditDialog("fixMacroXmax", constraint, self)
        elif isinstance(constraint, FixMacroX_min):
            dialog = SPConstraintEditDialog("fixMacroXmin", constraint, self)
        elif isinstance(constraint, FixMacroY_max):
            dialog = SPConstraintEditDialog("fixMacroYmax", constraint, self)
        elif isinstance(constraint, FixMacroY_min):
            dialog = SPConstraintEditDialog("fixMacroYmin", constraint, self)
        elif isinstance(constraint, FixMacroZ_max):
            dialog = SPConstraintEditDialog("fixMacroZmax", constraint, self)
        elif isinstance(constraint, FixMacroZ_min):
            dialog = SPConstraintEditDialog("fixMacroZmin", constraint, self)
        
        if dialog and dialog.exec() == QDialog.Accepted:
            self.refresh_constraints_list()

    def delete_constraint(self, tag):
        """Delete constraint from system"""
        reply = QMessageBox.question(
            self, 'Delete SP Constraint',
            f"Delete SP constraint with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            SPConstraintManager().remove_constraint(tag)
            self.refresh_constraints_list()


    def open_constraint_edit_dialog(self, constraint):
        """Open dialog to edit existing constraint"""
        dialog = None
        if isinstance(constraint, FixConstraint):
            dialog = SPConstraintEditDialog("fix", constraint, self)
        elif isinstance(constraint, FixXConstraint):
            dialog = SPConstraintEditDialog("fixX", constraint, self)
        elif isinstance(constraint, FixYConstraint):
            dialog = SPConstraintEditDialog("fixY", constraint, self)
        elif isinstance(constraint, FixZConstraint):
            dialog = SPConstraintEditDialog("fixZ", constraint, self)
        
        if dialog and dialog.exec() == QDialog.Accepted:
            self.refresh_constraints_list()

    def delete_constraint(self, tag):
        """Delete constraint from system"""
        reply = QMessageBox.question(
            self, 'Delete SP Constraint',
            f"Delete SP constraint with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            SPConstraintManager().remove_constraint(tag)
            self.refresh_constraints_list()


class DOFSelectionWidget(QWidget):
    """Widget for selecting constrained DOFs, with dynamic DOF count support"""
    def __init__(self, num_dofs=6, dof_values=None, parent=None):
        super().__init__(parent)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create a group box for better visual grouping
        dof_group = QGroupBox("Degrees of Freedom")
        dof_layout = QVBoxLayout(dof_group)
        
        # Add a scroll area to support large numbers of DOFs
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Create a grid layout for checkboxes
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)
        
        # Create checkboxes for each DOF
        self.dof_checkboxes = []
        
        # Calculate rows and columns for grid layout (3 columns)
        cols = 3
        rows = (num_dofs + cols - 1) // cols
        
        for i in range(num_dofs):
            checkbox = QCheckBox(f"DOF {i+1}")
            self.dof_checkboxes.append(checkbox)
            
            # Set initial values if provided
            if dof_values and i < len(dof_values):
                checkbox.setChecked(dof_values[i] == 1)
                
            # Add to grid layout in a 3-column grid
            row = i // cols
            col = i % cols
            grid_layout.addWidget(checkbox, row, col)
        
        scroll_layout.addLayout(grid_layout)
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        dof_layout.addWidget(scroll_area)
        
        # Add buttons for common DOF patterns
        patterns_layout = QHBoxLayout()
        
        all_btn = QPushButton("Select All")
        all_btn.clicked.connect(lambda: self.set_all_dofs(True))
        
        none_btn = QPushButton("Clear All")
        none_btn.clicked.connect(lambda: self.set_all_dofs(False))
        
        # Add common patterns like fix translations only or rotations only
        # Only show these if we have at least 6 DOFs (typical 3D model)
        trans_btn = QPushButton("Translations Only")
        trans_btn.clicked.connect(self.set_translations_only)
        
        rot_btn = QPushButton("Rotations Only")
        rot_btn.clicked.connect(self.set_rotations_only)
        
        patterns_layout.addWidget(trans_btn)
        patterns_layout.addWidget(rot_btn)
        
        patterns_layout.addWidget(all_btn)
        patterns_layout.addWidget(none_btn)
        dof_layout.addLayout(patterns_layout)
        
        main_layout.addWidget(dof_group)
    
    def set_all_dofs(self, state):
        """Set all DOFs to specified state"""
        for checkbox in self.dof_checkboxes:
            checkbox.setChecked(state)
    
    def set_translations_only(self):
        """Select translation DOFs only (first 3)"""
        for i, checkbox in enumerate(self.dof_checkboxes):
            checkbox.setChecked(i < 3)
    
    def set_rotations_only(self):
        """Select rotation DOFs only (4-6 in typical 3D model)"""
        for i, checkbox in enumerate(self.dof_checkboxes):
            checkbox.setChecked(3 <= i < 6)
    
    def get_dof_values(self):
        """Get DOF values as a list of 0s and 1s"""
        return [1 if cb.isChecked() else 0 for cb in self.dof_checkboxes]
    
    def set_dof_values(self, values):
        """Set DOF values from a list of 0s and 1s"""
        for i, value in enumerate(values):
            if i < len(self.dof_checkboxes):
                self.dof_checkboxes[i].setChecked(value == 1)


class SPConstraintCreationDialog(QDialog):
    def __init__(self, constraint_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Create {constraint_type} SP Constraint")
        self.constraint_type = constraint_type
        self.manager = SPConstraintManager()
        self.double_validator = DoubleValidator()
        self.int_validator = IntValidator()
        
        # Get access to the mesh
        self.meshmaker = MeshMaker.get_instance()
        
        layout = QVBoxLayout(self)
        
        # Stack for different constraint types
        self.stack = QStackedWidget()
        
        # Add pages for each constraint type
        self.setup_fix_page()
        self.setup_fix_x_page()
        self.setup_fix_y_page()
        self.setup_fix_z_page()
        self.setup_fix_macro_x_max_page()
        self.setup_fix_macro_x_min_page()
        self.setup_fix_macro_y_max_page()
        self.setup_fix_macro_y_min_page()
        self.setup_fix_macro_z_max_page()
        self.setup_fix_macro_z_min_page()
        
        # Set the current page based on the constraint type
        if constraint_type == "fix":
            self.stack.setCurrentIndex(0)
        elif constraint_type == "fixX":
            self.stack.setCurrentIndex(1)
        elif constraint_type == "fixY":
            self.stack.setCurrentIndex(2)
        elif constraint_type == "fixZ":
            self.stack.setCurrentIndex(3)
        elif constraint_type == "fixMacroXmax":
            self.stack.setCurrentIndex(4)
        elif constraint_type == "fixMacroXmin":
            self.stack.setCurrentIndex(5)
        elif constraint_type == "fixMacroYmax":
            self.stack.setCurrentIndex(6)
        elif constraint_type == "fixMacroYmin":
            self.stack.setCurrentIndex(7)
        elif constraint_type == "fixMacroZmax":
            self.stack.setCurrentIndex(8)
        elif constraint_type == "fixMacroZmin":
            self.stack.setCurrentIndex(9)
        
        layout.addWidget(self.stack)
        
        # DOF count selection
        dof_count_layout = QHBoxLayout()
        dof_count_layout.addWidget(QLabel("Number of DOFs:"))

        # Direct text input for DOF count
        self.dof_count_input = QLineEdit()
        self.dof_count_input.setValidator(self.int_validator)
        self.dof_count_input.setText("6")  # Default to 6 DOFs
        self.dof_count_input.textChanged.connect(self.update_dof_widget)
        dof_count_layout.addWidget(self.dof_count_input)

        layout.addLayout(dof_count_layout)
        
        # Create placeholder for DOF selection widget that will be updated dynamically
        self.dof_widget_container = QVBoxLayout()
        layout.addLayout(self.dof_widget_container)
        
        # Initialize DOF widget with default selection
        self.update_dof_widget()
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_constraint)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def handle_dof_count_change(self, index):
        """Handle change in DOF count selection"""
        custom_selected = self.dof_count_combo.currentText() == "Other"
        self.custom_dof_count.setVisible(custom_selected)
        
        if not custom_selected:
            self.update_dof_widget()

    def update_dof_widget(self):
        """Update DOF selection widget based on selected DOF count"""
        # Clear existing widget if it exists
        if hasattr(self, 'dof_widget'):
            # Remove the old widget from layout
            self.dof_widget.setParent(None)
            self.dof_widget.deleteLater()
        
        # Get the DOF count
        try:
            dof_count = int(self.dof_count_input.text())
            if dof_count <= 0:
                dof_count = 6  # Default
        except ValueError:
            dof_count = 6  # Default
        
        # Create new DOF widget
        self.dof_widget = DOFSelectionWidget(num_dofs=dof_count)
        self.dof_widget_container.addWidget(self.dof_widget)

    def setup_fix_page(self):
        """Setup the page for fix constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        self.node_tag_input = QLineEdit()
        self.node_tag_input.setValidator(self.int_validator)
        
        node_query_layout = QHBoxLayout()
        node_query_layout.addWidget(self.node_tag_input)
        
        # Add a button to query node DOF
        query_btn = QPushButton("Query DOF")
        query_btn.clicked.connect(self.query_node_dof)
        node_query_layout.addWidget(query_btn)
        
        fix_layout.addRow("Node Tag:", node_query_layout)
        
        self.stack.addWidget(fix_page)

    def query_node_dof(self):
        """Query the DOF of a node in the assembled mesh"""
        try:
            node_tag = int(self.node_tag_input.text())
            
            # Check if mesh is assembled
            if not self.meshmaker.assembler.AssembeledMesh:
                QMessageBox.warning(self, "Error", "No assembled mesh found. Please assemble the mesh first.")
                return
            
            # Node tags in GUI are 1-based, but in the internal model are 0-based
            node_idx = node_tag - 1
            
            if node_idx < 0 or node_idx >= self.meshmaker.assembler.AssembeledMesh.n_points:
                QMessageBox.warning(self, "Error", f"Node {node_tag} is out of range.")
                return
            
            # Get the DOF from the mesh
            ndf = self.meshmaker.assembler.AssembeledMesh.point_data["ndf"][node_idx]
            
            # # Update DOF selection
            # self.dof_count_input.setText(str(ndf))
            
            QMessageBox.information(self, "Node DOF", f"Node {node_tag} has {ndf} degrees of freedom.")
            
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid node tag.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def setup_fix_x_page(self):
        """Setup the page for fixX constraint"""
        fix_x_page = QWidget()
        fix_x_layout = QFormLayout(fix_x_page)
        
        self.x_coordinate_input = QLineEdit()
        self.x_coordinate_input.setValidator(self.double_validator)
        fix_x_layout.addRow("X Coordinate:", self.x_coordinate_input)
        
        self.x_tolerance_input = QLineEdit()
        self.x_tolerance_input.setValidator(self.double_validator)
        self.x_tolerance_input.setText("1e-10")
        fix_x_layout.addRow("Tolerance:", self.x_tolerance_input)
        
        self.stack.addWidget(fix_x_page)

    def setup_fix_y_page(self):
        """Setup the page for fixY constraint"""
        fix_y_page = QWidget()
        fix_y_layout = QFormLayout(fix_y_page)
        
        self.y_coordinate_input = QLineEdit()
        self.y_coordinate_input.setValidator(self.double_validator)
        fix_y_layout.addRow("Y Coordinate:", self.y_coordinate_input)
        
        self.y_tolerance_input = QLineEdit()
        self.y_tolerance_input.setValidator(self.double_validator)
        self.y_tolerance_input.setText("1e-10")
        fix_y_layout.addRow("Tolerance:", self.y_tolerance_input)
        
        self.stack.addWidget(fix_y_page)

    def setup_fix_z_page(self):
        """Setup the page for fixZ constraint"""
        fix_z_page = QWidget()
        fix_z_layout = QFormLayout(fix_z_page)
        
        self.z_coordinate_input = QLineEdit()
        self.z_coordinate_input.setValidator(self.double_validator)
        fix_z_layout.addRow("Z Coordinate:", self.z_coordinate_input)
        
        self.z_tolerance_input = QLineEdit()
        self.z_tolerance_input.setValidator(self.double_validator)
        self.z_tolerance_input.setText("1e-10")
        fix_z_layout.addRow("Tolerance:", self.z_tolerance_input)
        
        self.stack.addWidget(fix_z_page)

    def setup_fix_macro_x_max_page(self):
        """Setup the page for fixMacroXmax constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with X coordinate = $X_MAX")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.x_max_tolerance_input = QLineEdit()
        self.x_max_tolerance_input.setValidator(self.double_validator)
        self.x_max_tolerance_input.setText("1e-10")
        fix_layout.addRow("Tolerance:", self.x_max_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def setup_fix_macro_x_min_page(self):
        """Setup the page for fixMacroXmin constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with X coordinate = $X_MIN")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.x_min_tolerance_input = QLineEdit()
        self.x_min_tolerance_input.setValidator(self.double_validator)
        self.x_min_tolerance_input.setText("1e-10")
        fix_layout.addRow("Tolerance:", self.x_min_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def setup_fix_macro_y_max_page(self):
        """Setup the page for fixMacroYmax constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with Y coordinate = $Y_MAX")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.y_max_tolerance_input = QLineEdit()
        self.y_max_tolerance_input.setValidator(self.double_validator)
        self.y_max_tolerance_input.setText("1e-10")
        fix_layout.addRow("Tolerance:", self.y_max_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def setup_fix_macro_y_min_page(self):
        """Setup the page for fixMacroYmin constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with Y coordinate = $Y_MIN")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.y_min_tolerance_input = QLineEdit()
        self.y_min_tolerance_input.setValidator(self.double_validator)
        self.y_min_tolerance_input.setText("1e-10")
        fix_layout.addRow("Tolerance:", self.y_min_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def setup_fix_macro_z_max_page(self):
        """Setup the page for fixMacroZmax constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with Z coordinate = $Z_MAX")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.z_max_tolerance_input = QLineEdit()
        self.z_max_tolerance_input.setValidator(self.double_validator)
        self.z_max_tolerance_input.setText("1e-10")
        fix_layout.addRow("Tolerance:", self.z_max_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def setup_fix_macro_z_min_page(self):
        """Setup the page for fixMacroZmin constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with Z coordinate = $Z_MIN")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.z_min_tolerance_input = QLineEdit()
        self.z_min_tolerance_input.setValidator(self.double_validator)
        self.z_min_tolerance_input.setText("1e-10")
        fix_layout.addRow("Tolerance:", self.z_min_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def create_constraint(self):
        try:
            dofs = self.dof_widget.get_dof_values()
            
            if not any(dofs):
                QMessageBox.warning(self, "Input Error", "Please select at least one DOF to constrain")
                return
            
            args = []
            if self.constraint_type == "fix":
                try:
                    node_tag = int(self.node_tag_input.text())
                    args = [node_tag, dofs]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Node tag must be an integer")
                    return
            elif self.constraint_type == "fixX":
                try:
                    x_coordinate = float(self.x_coordinate_input.text())
                    tolerance = float(self.x_tolerance_input.text())
                    args = [x_coordinate, dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "X coordinate and tolerance must be valid numbers")
                    return
            elif self.constraint_type == "fixY":
                try:
                    y_coordinate = float(self.y_coordinate_input.text())
                    tolerance = float(self.y_tolerance_input.text())
                    args = [y_coordinate, dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Y coordinate and tolerance must be valid numbers")
                    return
            elif self.constraint_type == "fixZ":
                try:
                    z_coordinate = float(self.z_coordinate_input.text())
                    tolerance = float(self.z_tolerance_input.text())
                    args = [z_coordinate, dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Z coordinate and tolerance must be valid numbers")
                    return
            elif self.constraint_type == "fixMacroXmax":
                try:
                    tolerance = float(self.x_max_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            elif self.constraint_type == "fixMacroXmin":
                try:
                    tolerance = float(self.x_min_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            elif self.constraint_type == "fixMacroYmax":
                try:
                    tolerance = float(self.y_max_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            elif self.constraint_type == "fixMacroYmin":
                try:
                    tolerance = float(self.y_min_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            elif self.constraint_type == "fixMacroZmax":
                try:
                    tolerance = float(self.z_max_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            elif self.constraint_type == "fixMacroZmin":
                try:
                    tolerance = float(self.z_min_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            
            self.manager.create_constraint(self.constraint_type, *args)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class SPConstraintEditDialog(QDialog):
    def __init__(self, constraint_type, constraint, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit {constraint_type} SP Constraint")
        self.constraint_type = constraint_type
        self.constraint = constraint
        self.manager = SPConstraintManager()
        self.double_validator = DoubleValidator()
        self.int_validator = IntValidator()
        
        # Get access to the mesh
        self.meshmaker = MeshMaker.get_instance()
        
        layout = QVBoxLayout(self)
        
        # Stack for different constraint types
        self.stack = QStackedWidget()
        
        # Add pages for each constraint type
        self.setup_fix_page()
        self.setup_fix_x_page()
        self.setup_fix_y_page()
        self.setup_fix_z_page()
        self.setup_fix_macro_x_max_page()
        self.setup_fix_macro_x_min_page()
        self.setup_fix_macro_y_max_page()
        self.setup_fix_macro_y_min_page()
        self.setup_fix_macro_z_max_page()
        self.setup_fix_macro_z_min_page()
        
        # Set the current page based on the constraint type and populate fields
        if constraint_type == "fix":
            self.stack.setCurrentIndex(0)
            self.node_tag_input.setText(str(constraint.node_tag))
        elif constraint_type == "fixX":
            self.stack.setCurrentIndex(1)
            self.x_coordinate_input.setText(str(constraint.xCoordinate))
            self.x_tolerance_input.setText(str(constraint.tol))
        elif constraint_type == "fixY":
            self.stack.setCurrentIndex(2)
            self.y_coordinate_input.setText(str(constraint.yCoordinate))
            self.y_tolerance_input.setText(str(constraint.tol))
        elif constraint_type == "fixZ":
            self.stack.setCurrentIndex(3)
            self.z_coordinate_input.setText(str(constraint.zCoordinate))
            self.z_tolerance_input.setText(str(constraint.tol))
        elif constraint_type == "fixMacroXmax":
            self.stack.setCurrentIndex(4)
            self.x_max_tolerance_input.setText(str(constraint.tol))
        elif constraint_type == "fixMacroXmin":
            self.stack.setCurrentIndex(5)
            self.x_min_tolerance_input.setText(str(constraint.tol))
        elif constraint_type == "fixMacroYmax":
            self.stack.setCurrentIndex(6)
            self.y_max_tolerance_input.setText(str(constraint.tol))
        elif constraint_type == "fixMacroYmin":
            self.stack.setCurrentIndex(7)
            self.y_min_tolerance_input.setText(str(constraint.tol))
        elif constraint_type == "fixMacroZmax":
            self.stack.setCurrentIndex(8)
            self.z_max_tolerance_input.setText(str(constraint.tol))
        elif constraint_type == "fixMacroZmin":
            self.stack.setCurrentIndex(9)
            self.z_min_tolerance_input.setText(str(constraint.tol))
        
        layout.addWidget(self.stack)
        
        # Create DOF selection widget based on constraint's DOF count
        dof_count = len(constraint.dofs)
        self.dof_widget = DOFSelectionWidget(num_dofs=dof_count, dof_values=constraint.dofs)
        layout.addWidget(self.dof_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_constraint)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def setup_fix_page(self):
        """Setup the page for fix constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        self.node_tag_input = QLineEdit()
        self.node_tag_input.setValidator(self.int_validator)
        
        node_query_layout = QHBoxLayout()
        node_query_layout.addWidget(self.node_tag_input)
        
        # Add a button to query node DOF
        query_btn = QPushButton("Query DOF")
        query_btn.clicked.connect(self.query_node_dof)
        node_query_layout.addWidget(query_btn)
        
        fix_layout.addRow("Node Tag:", node_query_layout)
        
        self.stack.addWidget(fix_page)

    def query_node_dof(self):
        """Query the DOF of a node in the assembled mesh"""
        try:
            node_tag = int(self.node_tag_input.text())
            
            # Check if mesh is assembled
            if not self.meshmaker.assembler.AssembeledMesh:
                QMessageBox.warning(self, "Error", "No assembled mesh found. Please assemble the mesh first.")
                return
            
            # Node tags in GUI are 1-based, but in the internal model are 0-based
            node_idx = node_tag - 1
            
            if node_idx < 0 or node_idx >= self.meshmaker.assembler.AssembeledMesh.n_points:
                QMessageBox.warning(self, "Error", f"Node {node_tag} is out of range.")
                return
            
            # Get the DOF from the mesh
            ndf = self.meshmaker.assembler.AssembeledMesh.point_data["ndf"][node_idx]
            
            # Recreate DOF widget with new DOF count
            old_layout = self.layout()
            old_widget = self.dof_widget
            
            # Remove old widget
            old_layout.removeWidget(old_widget)
            old_widget.deleteLater()
            
            # Create new widget with the correct DOF count
            self.dof_widget = DOFSelectionWidget(num_dofs=ndf)
            
            # Insert the new widget at the same position
            old_layout.insertWidget(1, self.dof_widget)
            
            QMessageBox.information(self, "Node DOF", f"Node {node_tag} has {ndf} degrees of freedom.")
            
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid node tag.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def setup_fix_x_page(self):
        """Setup the page for fixX constraint"""
        fix_x_page = QWidget()
        fix_x_layout = QFormLayout(fix_x_page)
        
        self.x_coordinate_input = QLineEdit()
        self.x_coordinate_input.setValidator(self.double_validator)
        fix_x_layout.addRow("X Coordinate:", self.x_coordinate_input)
        
        self.x_tolerance_input = QLineEdit()
        self.x_tolerance_input.setValidator(self.double_validator)
        fix_x_layout.addRow("Tolerance:", self.x_tolerance_input)
        
        self.stack.addWidget(fix_x_page)

    def setup_fix_y_page(self):
        """Setup the page for fixY constraint"""
        fix_y_page = QWidget()
        fix_y_layout = QFormLayout(fix_y_page)
        
        self.y_coordinate_input = QLineEdit()
        self.y_coordinate_input.setValidator(self.double_validator)
        fix_y_layout.addRow("Y Coordinate:", self.y_coordinate_input)
        
        self.y_tolerance_input = QLineEdit()
        self.y_tolerance_input.setValidator(self.double_validator)
        fix_y_layout.addRow("Tolerance:", self.y_tolerance_input)
        
        self.stack.addWidget(fix_y_page)

    def setup_fix_z_page(self):
        """Setup the page for fixZ constraint"""
        fix_z_page = QWidget()
        fix_z_layout = QFormLayout(fix_z_page)
        
        self.z_coordinate_input = QLineEdit()
        self.z_coordinate_input.setValidator(self.double_validator)
        fix_z_layout.addRow("Z Coordinate:", self.z_coordinate_input)
        
        self.z_tolerance_input = QLineEdit()
        self.z_tolerance_input.setValidator(self.double_validator)
        fix_z_layout.addRow("Tolerance:", self.z_tolerance_input)
        
        self.stack.addWidget(fix_z_page)

    def setup_fix_macro_x_max_page(self):
        """Setup the page for fixMacroXmax constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with X coordinate = $X_MAX")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.x_max_tolerance_input = QLineEdit()
        self.x_max_tolerance_input.setValidator(self.double_validator)
        fix_layout.addRow("Tolerance:", self.x_max_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def setup_fix_macro_x_min_page(self):
        """Setup the page for fixMacroXmin constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with X coordinate = $X_MIN")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.x_min_tolerance_input = QLineEdit()
        self.x_min_tolerance_input.setValidator(self.double_validator)
        fix_layout.addRow("Tolerance:", self.x_min_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def setup_fix_macro_y_max_page(self):
        """Setup the page for fixMacroYmax constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with Y coordinate = $Y_MAX")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.y_max_tolerance_input = QLineEdit()
        self.y_max_tolerance_input.setValidator(self.double_validator)
        fix_layout.addRow("Tolerance:", self.y_max_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def setup_fix_macro_y_min_page(self):
        """Setup the page for fixMacroYmin constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with Y coordinate = $Y_MIN")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.y_min_tolerance_input = QLineEdit()
        self.y_min_tolerance_input.setValidator(self.double_validator)
        fix_layout.addRow("Tolerance:", self.y_min_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def setup_fix_macro_z_max_page(self):
        """Setup the page for fixMacroZmax constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with Z coordinate = $Z_MAX")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.z_max_tolerance_input = QLineEdit()
        self.z_max_tolerance_input.setValidator(self.double_validator)
        fix_layout.addRow("Tolerance:", self.z_max_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def setup_fix_macro_z_min_page(self):
        """Setup the page for fixMacroZmin constraint"""
        fix_page = QWidget()
        fix_layout = QFormLayout(fix_page)
        
        info_label = QLabel("This constraint will apply to all nodes with Z coordinate = $Z_MIN")
        info_label.setWordWrap(True)
        fix_layout.addRow(info_label)
        
        self.z_min_tolerance_input = QLineEdit()
        self.z_min_tolerance_input.setValidator(self.double_validator)
        fix_layout.addRow("Tolerance:", self.z_min_tolerance_input)
        
        self.stack.addWidget(fix_page)

    def save_constraint(self):
        try:
            dofs = self.dof_widget.get_dof_values()
            
            if not any(dofs):
                QMessageBox.warning(self, "Input Error", "Please select at least one DOF to constrain")
                return
            
            # Remove the old constraint
            old_tag = self.constraint.tag
            self.manager.remove_constraint(old_tag)
            
            # Create a new constraint with updated values
            args = []
            if self.constraint_type == "fix":
                try:
                    node_tag = int(self.node_tag_input.text())
                    args = [node_tag, dofs]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Node tag must be an integer")
                    return
            elif self.constraint_type == "fixX":
                try:
                    x_coordinate = float(self.x_coordinate_input.text())
                    tolerance = float(self.x_tolerance_input.text())
                    args = [x_coordinate, dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "X coordinate and tolerance must be valid numbers")
                    return
            elif self.constraint_type == "fixY":
                try:
                    y_coordinate = float(self.y_coordinate_input.text())
                    tolerance = float(self.y_tolerance_input.text())
                    args = [y_coordinate, dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Y coordinate and tolerance must be valid numbers")
                    return
            elif self.constraint_type == "fixZ":
                try:
                    z_coordinate = float(self.z_coordinate_input.text())
                    tolerance = float(self.z_tolerance_input.text())
                    args = [z_coordinate, dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Z coordinate and tolerance must be valid numbers")
                    return
            elif self.constraint_type == "fixMacroXmax":
                try:
                    tolerance = float(self.x_max_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            elif self.constraint_type == "fixMacroXmin":
                try:
                    tolerance = float(self.x_min_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            elif self.constraint_type == "fixMacroYmax":
                try:
                    tolerance = float(self.y_max_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            elif self.constraint_type == "fixMacroYmin":
                try:
                    tolerance = float(self.y_min_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            elif self.constraint_type == "fixMacroZmax":
                try:
                    tolerance = float(self.z_max_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            elif self.constraint_type == "fixMacroZmin":
                try:
                    tolerance = float(self.z_min_tolerance_input.text())
                    args = [dofs, tolerance]
                except ValueError:
                    QMessageBox.warning(self, "Input Error", "Tolerance must be a valid number")
                    return
            
            self.manager.create_constraint(self.constraint_type, *args)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class FixConstraintView(QWidget):
    """Widget to visualize fix constraints in the 3D scene"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plotter = PlotterManager.get_plotter()
        self.meshmaker = MeshMaker.get_instance()
        self.constraint_actors = {}
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        show_btn = QPushButton("Show Constraints")
        show_btn.clicked.connect(self.show_constraints)
        
        hide_btn = QPushButton("Hide Constraints")
        hide_btn.clicked.connect(self.hide_constraints)
        
        refresh_btn = QPushButton("Refresh Constraints")
        refresh_btn.clicked.connect(self.refresh_constraints)
        
        btn_layout.addWidget(show_btn)
        btn_layout.addWidget(hide_btn)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Options
        options_group = QGroupBox("Display Options")
        options_layout = QVBoxLayout(options_group)
        
        # Scale slider for constraint visual size
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Size:"))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(1)
        self.scale_slider.setMaximum(50)
        self.scale_slider.setValue(10)
        self.scale_slider.valueChanged.connect(self.update_constraint_scale)
        scale_layout.addWidget(self.scale_slider)
        options_layout.addLayout(scale_layout)
        
        # Color options
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color by Type:"))
        self.color_by_type_check = QCheckBox()
        self.color_by_type_check.setChecked(True)
        self.color_by_type_check.stateChanged.connect(self.refresh_constraints)
        color_layout.addWidget(self.color_by_type_check)
        options_layout.addLayout(color_layout)
        
        layout.addWidget(options_group)
        layout.addStretch()

    def show_constraints(self):
        """Show all constraints in the 3D view"""
        # Get all constraints
        constraints = SPConstraint._constraints.values()
        
        # Clear existing constraint actors
        self.hide_constraints()
        
        if not self.meshmaker.assembler.AssembeledMesh:
            QMessageBox.warning(self, "Error", "No assembled mesh found. Please assemble the mesh first.")
            return
        
        mesh = self.meshmaker.assembler.AssembeledMesh
        scale = self.scale_slider.value() / 10.0
        
        # Define colors for different constraint types
        colors = {
            FixConstraint: [1.0, 0.0, 0.0],      # Red for fix
            FixXConstraint: [0.0, 1.0, 0.0],     # Green for fixX
            FixYConstraint: [0.0, 0.0, 1.0],     # Blue for fixY
            FixZConstraint: [1.0, 1.0, 0.0],     # Yellow for fixZ
            FixMacroX_max: [1.0, 0.5, 0.0],      # Orange for fixMacroXmax
            FixMacroX_min: [0.5, 1.0, 0.0],      # Light green for fixMacroXmin
            FixMacroY_max: [0.0, 1.0, 0.5],      # Cyan for fixMacroYmax
            FixMacroY_min: [0.5, 0.0, 1.0],      # Purple for fixMacroYmin
            FixMacroZ_max: [1.0, 0.0, 0.5],      # Pink for fixMacroZmax
            FixMacroZ_min: [0.0, 0.5, 1.0]       # Light blue for fixMacroZmin
        }
        
        for constraint in constraints:
            if isinstance(constraint, FixConstraint):
                # For FixConstraint: Create a sphere at the node location
                node_idx = constraint.node_tag - 1  # Adjust for 0-based indexing
                
                if node_idx >= 0 and node_idx < mesh.n_points:
                    point = mesh.points[node_idx]
                    
                    # Create sphere glyph
                    sphere = pv.Sphere(radius=scale, center=point)
                    
                    # Set color based on type if enabled, otherwise use red
                    color = colors[type(constraint)] if self.color_by_type_check.isChecked() else [1.0, 0.0, 0.0]
                    
                    # Add to scene
                    actor = self.plotter.add_mesh(sphere, color=color)
                    self.constraint_actors[constraint.tag] = actor
            
            elif isinstance(constraint, (FixXConstraint, FixYConstraint, FixZConstraint)):
                # For coordinate constraints: Create a plane at the boundary
                if isinstance(constraint, FixXConstraint):
                    coord = constraint.xCoordinate
                    normal = [1, 0, 0]
                    idx = 0
                elif isinstance(constraint, FixYConstraint):
                    coord = constraint.yCoordinate
                    normal = [0, 1, 0]
                    idx = 1
                else:  # FixZConstraint
                    coord = constraint.zCoordinate
                    normal = [0, 0, 1]
                    idx = 2
                
                # Create a plane at the specified coordinate
                bounds = mesh.bounds
                dimensions = [bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]]
                
                # Compute center point and size based on bounds
                center = list(mesh.center)
                center[idx] = coord
                
                plane = pv.Plane(center=center, direction=normal, i_size=dimensions[0] * 1.2, 
                                j_size=dimensions[1] * 1.2)
                
                # Set color based on type if enabled
                color = colors[type(constraint)] if self.color_by_type_check.isChecked() else [0.0, 0.0, 1.0]
                
                # Add to scene with transparency
                actor = self.plotter.add_mesh(plane, color=color, opacity=0.3)
                self.constraint_actors[constraint.tag] = actor
        
        self.plotter.update()

    def hide_constraints(self):
        """Hide all constraint visuals"""
        for tag, actor in self.constraint_actors.items():
            self.plotter.remove_actor(actor)
        
        self.constraint_actors.clear()
        self.plotter.update()

    def refresh_constraints(self):
        """Refresh all constraint visuals"""
        self.show_constraints()

    def update_constraint_scale(self):
        """Update the scale of constraint visuals"""
        # Simply refresh constraints to apply new scale
        self.refresh_constraints()


if __name__ == '__main__':
    from qtpy.QtWidgets import QApplication
    import sys
    
    # Create some sample constraints for testing
    sp_manager = SPConstraintManager()
    sp_manager.fix(1, [1, 1, 1, 0, 0, 0])
    sp_manager.fix(2, [0, 1, 0, 0, 1, 0])
    sp_manager.fixX(0.0, [1, 1, 1, 0, 0, 0])
    sp_manager.fixY(0.0, [0, 1, 0, 0, 0, 0])
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    window = SPConstraintManagerTab()
    window.show()
    sys.exit(app.exec_())


