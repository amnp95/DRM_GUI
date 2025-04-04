from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout,
    QCheckBox, QGroupBox, QDoubleSpinBox, QRadioButton, QSpinBox,
    QTabWidget, QStackedWidget, QScrollArea, QTextEdit
)

from meshmaker.utils.validator import DoubleValidator, IntValidator
from meshmaker.components.Analysis.integrators import (
    IntegratorManager, Integrator, StaticIntegrator, TransientIntegrator,
    LoadControlIntegrator, DisplacementControlIntegrator, ParallelDisplacementControlIntegrator,
    MinUnbalDispNormIntegrator, ArcLengthIntegrator, CentralDifferenceIntegrator,
    NewmarkIntegrator, HHTIntegrator, GeneralizedAlphaIntegrator, TRBDF2Integrator,
    ExplicitDifferenceIntegrator, PFEMIntegrator
)

class IntegratorManagerTab(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup dialog properties
        self.setWindowTitle("Integrator Manager")
        self.resize(900, 600)
        
        # Get the integrator manager instance
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create combined integrator selection section
        self.create_integrator_selection()
        layout.addWidget(self.integrator_selection_group)
        
        # Integrators table
        self.integrators_table = QTableWidget()
        self.integrators_table.setColumnCount(4)  # Select, Tag, Type, Parameters
        self.integrators_table.setHorizontalHeaderLabels(["Select", "Tag", "Type", "Parameters"])
        self.integrators_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.integrators_table.setSelectionMode(QTableWidget.SingleSelection)
        header = self.integrators_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.integrators_table)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_integrator)
        
        self.delete_selected_btn = QPushButton("Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_integrator)
        
        refresh_btn = QPushButton("Refresh Integrators List")
        refresh_btn.clicked.connect(self.refresh_integrators_list)
        
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_selected_btn)
        buttons_layout.addWidget(refresh_btn)
        
        layout.addLayout(buttons_layout)
        
        # Initial refresh
        self.refresh_integrators_list()
        
        # Disable edit/delete buttons initially
        self.update_button_state()
        
    def create_integrator_selection(self):
        """Create unified integrator selection section"""
        self.integrator_selection_group = QGroupBox("Create New Integrator")
        layout = QVBoxLayout(self.integrator_selection_group)
        
        # Create type selection layout
        type_layout = QGridLayout()
        
        # Integrator category radio buttons
        self.category_group = QGroupBox("Integrator Category")
        category_layout = QHBoxLayout(self.category_group)
        
        self.static_radio = QRadioButton("Static")
        self.transient_radio = QRadioButton("Transient")
        self.static_radio.setChecked(True)  # Default selection
        
        category_layout.addWidget(self.static_radio)
        category_layout.addWidget(self.transient_radio)
        
        # Connect radio buttons to update integrator types list
        self.static_radio.toggled.connect(self.update_integrator_types)
        
        type_layout.addWidget(self.category_group, 0, 0, 1, 2)
        
        # Integrator type combo box
        self.integrator_type_combo = QComboBox()
        self.integrator_type_combo.currentTextChanged.connect(self.update_description)
        
        type_layout.addWidget(QLabel("Integrator Type:"), 1, 0)
        type_layout.addWidget(self.integrator_type_combo, 1, 1)
        
        # Create integrator button
        self.create_btn = QPushButton("Create Integrator")
        self.create_btn.clicked.connect(self.create_new_integrator)
        type_layout.addWidget(self.create_btn, 2, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Add description text area
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(120)
        layout.addWidget(self.description_text)
        
        # Initialize with static integrators
        self.update_integrator_types()
        
    def update_integrator_types(self):
        """Update the integrator types based on selected category"""
        self.integrator_type_combo.clear()
        
        if self.static_radio.isChecked():
            self.integrator_type_combo.addItems(self.integrator_manager.get_static_types())
        else:
            self.integrator_type_combo.addItems(self.integrator_manager.get_transient_types())
        
        # Update the description for the first item
        self.update_description()
        
    def update_description(self):
        """Update the description text based on selected integrator type"""
        integrator_type = self.integrator_type_combo.currentText().lower()
        
        descriptions = {
            # Static integrators
            "loadcontrol": """
                <b>LoadControl Integrator</b><br>
                Controls load increments in static analysis. Used when you want to apply
                loads in small increments to solve a nonlinear problem. The algorithm updates
                the load factor by a fixed amount at each step.
            """,
            "displacementcontrol": """
                <b>DisplacementControl Integrator</b><br>
                Controls displacement increments at a specific degree of freedom (DOF) of a
                specific node. Useful when you want to impose a fixed displacement increment
                rather than a load increment. Often used for problems where load control might fail
                due to limit points or snap-through behavior.
            """,
            "paralleldisplacementcontrol": """
                <b>ParallelDisplacementControl Integrator</b><br>
                Similar to DisplacementControl but designed for parallel computing environments.
                It specifies a displacement increment for a specific DOF at a specific node,
                optimized for distributed memory parallel processing.
            """,
            "minunbaldispnorm": """
                <b>MinUnbalDispNorm Integrator</b><br>
                Uses minimum unbalanced displacement norm to determine the increment size.
                The algorithm searches for the minimum displacement norm among all DOFs and
                uses that to determine the next step size.
            """,
            "arclength": """
                <b>ArcLength Integrator</b><br>
                Uses the arc-length method for tracing nonlinear equilibrium paths,
                particularly useful for problems with snap-through or snap-back behavior.
                It controls both load and displacement increments simultaneously.
            """,
            # Transient integrators
            "centraldifference": """
                <b>CentralDifference Integrator</b><br>
                An explicit method for dynamic analysis that requires no iteration.
                It is conditionally stable, meaning the time step must be less than
                a critical value determined by the highest frequency in the system.
                Has no parameters to configure.
            """,
            "newmark": """
                <b>Newmark Integrator</b><br>
                An implicit time integration method for dynamic analysis with parameters gamma and beta.
                When gamma=0.5 and beta=0.25 (default), it's the constant average acceleration method
                and unconditionally stable. When gamma=0.5 and beta=0, it becomes the central difference method.
            """,
            "hht": """
                <b>HHT (Hilber-Hughes-Taylor) Integrator</b><br>
                An implicit method with numerical damping controlled by alpha parameter (typically
                between -1/3 and 0). When alpha=0, it's equivalent to Newmark method. It provides
                better high-frequency damping than Newmark while maintaining second-order accuracy.
            """,
            "generalizedalpha": """
                <b>GeneralizedAlpha Integrator</b><br>
                An extension of the HHT method with two alpha parameters (alpha_m and alpha_f)
                to provide high-frequency energy dissipation while maintaining accuracy.
                Offers better control over numerical damping properties.
            """,
            "trbdf2": """
                <b>TRBDF2 Integrator</b><br>
                A composite implicit method that alternates between trapezoidal rule and
                backward difference formula. Unconditionally stable and second-order accurate,
                particularly effective for stiff systems. Has no parameters to configure.
            """,
            "explicitdifference": """
                <b>ExplicitDifference Integrator</b><br>
                An explicit method specifically designed for uncoupled dynamic equations.
                Conditionally stable with a critical time step dependent on the highest system frequency.
                Has no parameters to configure.
            """,
            "pfem": """
                <b>PFEM (Particle Finite Element Method) Integrator</b><br>
                Used for fluid-structure interaction problems where the mesh can undergo large deformations.
                Parameters gamma and beta are similar to the Newmark method.
            """
        }
        
        if integrator_type in descriptions:
            self.description_text.setHtml(descriptions[integrator_type])
        else:
            self.description_text.setHtml("<b>No description available</b>")
    
    def create_new_integrator(self):
        """Open dialog to create a new integrator of selected type"""
        integrator_type = self.integrator_type_combo.currentText().lower()
        
        dialog = None
        # Static integrators
        if integrator_type == "loadcontrol":
            dialog = LoadControlIntegratorDialog(self)
        elif integrator_type == "displacementcontrol":
            dialog = DisplacementControlIntegratorDialog(self)
        elif integrator_type == "paralleldisplacementcontrol":
            dialog = ParallelDisplacementControlIntegratorDialog(self)
        elif integrator_type == "minunbaldispnorm":
            dialog = MinUnbalDispNormIntegratorDialog(self)
        elif integrator_type == "arclength":
            dialog = ArcLengthIntegratorDialog(self)
        # Transient integrators
        elif integrator_type == "centraldifference":
            dialog = CentralDifferenceIntegratorDialog(self)
        elif integrator_type == "newmark":
            dialog = NewmarkIntegratorDialog(self)
        elif integrator_type == "hht":
            dialog = HHTIntegratorDialog(self)
        elif integrator_type == "generalizedalpha":
            dialog = GeneralizedAlphaIntegratorDialog(self)
        elif integrator_type == "trbdf2":
            dialog = TRBDF2IntegratorDialog(self)
        elif integrator_type == "explicitdifference":
            dialog = ExplicitDifferenceIntegratorDialog(self)
        elif integrator_type == "pfem":
            dialog = PFEMIntegratorDialog(self)
        
        if dialog:
            if dialog.exec() == QDialog.Accepted:
                self.refresh_integrators_list()
        else:
            QMessageBox.warning(self, "Error", f"No creation dialog available for integrator type: {integrator_type}")

    def refresh_integrators_list(self):
        """Update the integrators table with current integrators"""
        self.integrators_table.setRowCount(0)
        integrators = self.integrator_manager.get_all_integrators()
        
        self.integrators_table.setRowCount(len(integrators))
        self.checkboxes = []
        
        # Hide vertical header (row indices)
        self.integrators_table.verticalHeader().setVisible(False)
        
        for row, (tag, integrator) in enumerate(integrators.items()):
            # Select checkbox
            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox::indicator { width: 15px; height: 15px; }")
            checkbox.toggled.connect(lambda checked, btn=checkbox: self.on_checkbox_toggled(checked, btn))
            self.checkboxes.append(checkbox)
            checkbox_cell = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_cell)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.integrators_table.setCellWidget(row, 0, checkbox_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.integrators_table.setItem(row, 1, tag_item)
            
            # Integrator Type
            type_item = QTableWidgetItem(integrator.integrator_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.integrators_table.setItem(row, 2, type_item)
            
            # Parameters
            params = integrator.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.integrators_table.setItem(row, 3, params_item)
        
        self.update_button_state()
        
    def on_checkbox_toggled(self, checked, btn):
        """Handle checkbox toggling to ensure mutual exclusivity"""
        if checked:
            for checkbox in self.checkboxes:
                if checkbox != btn and checkbox.isChecked():
                    checkbox.setChecked(False)
        self.update_button_state()

    def update_button_state(self):
        """Enable/disable edit and delete buttons based on selection"""
        enable_buttons = any(cb.isChecked() for cb in self.checkboxes) if hasattr(self, 'checkboxes') else False
        self.edit_btn.setEnabled(enable_buttons)
        self.delete_selected_btn.setEnabled(enable_buttons)

    def get_selected_integrator_tag(self):
        """Get the tag of the selected integrator"""
        if not hasattr(self, 'checkboxes'):
            return None
            
        for row, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                tag_item = self.integrators_table.item(row, 1)
                return int(tag_item.text())
        return None

    def edit_selected_integrator(self):
        """Edit the selected integrator"""
        tag = self.get_selected_integrator_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select an integrator to edit")
            return
        
        try:
            integrator = self.integrator_manager.get_integrator(tag)
            dialog = None
            
            # Create the appropriate dialog based on integrator type
            if isinstance(integrator, LoadControlIntegrator):
                dialog = LoadControlIntegratorEditDialog(integrator, self)
            elif isinstance(integrator, DisplacementControlIntegrator):
                dialog = DisplacementControlIntegratorEditDialog(integrator, self)
            elif isinstance(integrator, ParallelDisplacementControlIntegrator):
                dialog = ParallelDisplacementControlIntegratorEditDialog(integrator, self)
            elif isinstance(integrator, MinUnbalDispNormIntegrator):
                dialog = MinUnbalDispNormIntegratorEditDialog(integrator, self)
            elif isinstance(integrator, ArcLengthIntegrator):
                dialog = ArcLengthIntegratorEditDialog(integrator, self)
            elif isinstance(integrator, NewmarkIntegrator):
                dialog = NewmarkIntegratorEditDialog(integrator, self)
            elif isinstance(integrator, HHTIntegrator):
                dialog = HHTIntegratorEditDialog(integrator, self)
            elif isinstance(integrator, GeneralizedAlphaIntegrator):
                dialog = GeneralizedAlphaIntegratorEditDialog(integrator, self)
            elif isinstance(integrator, PFEMIntegrator):
                dialog = PFEMIntegratorEditDialog(integrator, self)
            elif isinstance(integrator, (CentralDifferenceIntegrator, TRBDF2Integrator, ExplicitDifferenceIntegrator)):
                QMessageBox.information(self, "Info", f"The {integrator.integrator_type} integrator has no parameters to edit")
                return
            
            if dialog:
                if dialog.exec() == QDialog.Accepted:
                    self.refresh_integrators_list()
            else:
                QMessageBox.warning(self, "Error", f"No edit dialog available for integrator type: {integrator.integrator_type}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected_integrator(self):
        """Delete the selected integrator"""
        tag = self.get_selected_integrator_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select an integrator to delete")
            return
        
        self.delete_integrator(tag)

    def delete_integrator(self, tag):
        """Delete an integrator from the system"""
        reply = QMessageBox.question(
            self, 'Delete Integrator',
            f"Are you sure you want to delete integrator with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.integrator_manager.remove_integrator(tag)
            self.refresh_integrators_list()
#------------------------------------------------------
# Static Integrators Dialog Classes
#------------------------------------------------------

class LoadControlIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Load Control Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Load increment
        self.incr_spin = QDoubleSpinBox()
        self.incr_spin.setDecimals(6)
        self.incr_spin.setRange(-1e6, 1e6)
        self.incr_spin.setValue(1.0)
        params_layout.addRow("Load Increment:", self.incr_spin)
        
        # Number of iterations
        self.num_iter_spin = QSpinBox()
        self.num_iter_spin.setRange(1, 1000)
        self.num_iter_spin.setValue(1)
        params_layout.addRow("Number of Iterations:", self.num_iter_spin)
        
        # Min increment
        self.min_incr_spin = QDoubleSpinBox()
        self.min_incr_spin.setDecimals(6)
        self.min_incr_spin.setRange(-1e6, 1e6)
        self.min_incr_spin.setValue(1.0)
        params_layout.addRow("Min Increment:", self.min_incr_spin)
        
        # Max increment
        self.max_incr_spin = QDoubleSpinBox()
        self.max_incr_spin.setDecimals(6)
        self.max_incr_spin.setRange(-1e6, 1e6)
        self.max_incr_spin.setValue(0.1)
        params_layout.addRow("Max Increment:", self.max_incr_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The LoadControl integrator is used to increment the reference load in a static analysis.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_integrator(self):
        try:
            # Get parameters
            incr = self.incr_spin.value()
            num_iter = self.num_iter_spin.value()
            min_incr = self.min_incr_spin.value()
            max_incr = self.max_incr_spin.value()
            
            # Create integrator
            self.integrator = self.integrator_manager.create_integrator(
                "loadcontrol", 
                incr=incr, 
                num_iter=num_iter, 
                min_incr=min_incr, 
                max_incr=max_incr
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class DisplacementControlIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Displacement Control Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Node tag
        self.node_tag_spin = QSpinBox()
        self.node_tag_spin.setRange(1, 999999)
        params_layout.addRow("Node Tag:", self.node_tag_spin)
        
        # DOF
        self.dof_spin = QSpinBox()
        self.dof_spin.setRange(1, 6)
        params_layout.addRow("Degree of Freedom:", self.dof_spin)
        
        # Displacement increment
        self.incr_spin = QDoubleSpinBox()
        self.incr_spin.setDecimals(6)
        self.incr_spin.setRange(-1e6, 1e6)
        self.incr_spin.setValue(0.1)
        params_layout.addRow("Displacement Increment:", self.incr_spin)
        
        # Number of iterations
        self.num_iter_spin = QSpinBox()
        self.num_iter_spin.setRange(1, 1000)
        self.num_iter_spin.setValue(1)
        params_layout.addRow("Number of Iterations:", self.num_iter_spin)
        
        # Min increment
        self.min_incr_spin = QDoubleSpinBox()
        self.min_incr_spin.setDecimals(6)
        self.min_incr_spin.setRange(-1e6, 1e6)
        self.min_incr_spin.setValue(0.1)
        params_layout.addRow("Min Increment:", self.min_incr_spin)
        
        # Max increment
        self.max_incr_spin = QDoubleSpinBox()
        self.max_incr_spin.setDecimals(6)
        self.max_incr_spin.setRange(-1e6, 1e6)
        self.max_incr_spin.setValue(0.1)
        params_layout.addRow("Max Increment:", self.max_incr_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The Displacement Control integrator is used to specify a displacement increment for a specific degree of freedom at a specific node.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_integrator(self):
        try:
            # Get parameters
            node_tag = self.node_tag_spin.value()
            dof = self.dof_spin.value()
            incr = self.incr_spin.value()
            num_iter = self.num_iter_spin.value()
            min_incr = self.min_incr_spin.value()
            max_incr = self.max_incr_spin.value()
            
            # Create integrator
            self.integrator = self.integrator_manager.create_integrator(
                "displacementcontrol", 
                node_tag=node_tag,
                dof=dof,
                incr=incr, 
                num_iter=num_iter, 
                min_incr=min_incr, 
                max_incr=max_incr
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class LoadControlIntegratorEditDialog(QDialog):
    def __init__(self, integrator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Load Control Integrator")
        self.integrator = integrator
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Load increment
        self.incr_spin = QDoubleSpinBox()
        self.incr_spin.setDecimals(6)
        self.incr_spin.setRange(-1e6, 1e6)
        self.incr_spin.setValue(integrator.incr)
        params_layout.addRow("Load Increment:", self.incr_spin)
        
        # Number of iterations
        self.num_iter_spin = QSpinBox()
        self.num_iter_spin.setRange(1, 1000)
        self.num_iter_spin.setValue(integrator.num_iter)
        params_layout.addRow("Number of Iterations:", self.num_iter_spin)
        
        # Min increment
        self.min_incr_spin = QDoubleSpinBox()
        self.min_incr_spin.setDecimals(6)
        self.min_incr_spin.setRange(-1e6, 1e6)
        self.min_incr_spin.setValue(integrator.min_incr)
        params_layout.addRow("Min Increment:", self.min_incr_spin)
        
        # Max increment
        self.max_incr_spin = QDoubleSpinBox()
        self.max_incr_spin.setDecimals(6)
        self.max_incr_spin.setRange(-1e6, 1e6)
        self.max_incr_spin.setValue(integrator.max_incr)
        params_layout.addRow("Max Increment:", self.max_incr_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The LoadControl integrator is used to increment the reference load in a static analysis.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_changes(self):
        try:
            # Get parameters
            incr = self.incr_spin.value()
            num_iter = self.num_iter_spin.value()
            min_incr = self.min_incr_spin.value()
            max_incr = self.max_incr_spin.value()
            
            # Update integrator values
            self.integrator.incr = incr
            self.integrator.num_iter = num_iter
            self.integrator.min_incr = min_incr
            self.integrator.max_incr = max_incr
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class DisplacementControlIntegratorEditDialog(QDialog):
    def __init__(self, integrator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Displacement Control Integrator")
        self.integrator = integrator
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Node tag
        self.node_tag_spin = QSpinBox()
        self.node_tag_spin.setRange(1, 999999)
        self.node_tag_spin.setValue(integrator.node_tag)
        params_layout.addRow("Node Tag:", self.node_tag_spin)
        
        # DOF
        self.dof_spin = QSpinBox()
        self.dof_spin.setRange(1, 6)
        self.dof_spin.setValue(integrator.dof)
        params_layout.addRow("Degree of Freedom:", self.dof_spin)
        
        # Displacement increment
        self.incr_spin = QDoubleSpinBox()
        self.incr_spin.setDecimals(6)
        self.incr_spin.setRange(-1e6, 1e6)
        self.incr_spin.setValue(integrator.incr)
        params_layout.addRow("Displacement Increment:", self.incr_spin)
        
        # Number of iterations
        self.num_iter_spin = QSpinBox()
        self.num_iter_spin.setRange(1, 1000)
        self.num_iter_spin.setValue(integrator.num_iter)
        params_layout.addRow("Number of Iterations:", self.num_iter_spin)
        
        # Min increment
        self.min_incr_spin = QDoubleSpinBox()
        self.min_incr_spin.setDecimals(6)
        self.min_incr_spin.setRange(-1e6, 1e6)
        self.min_incr_spin.setValue(integrator.min_incr)
        params_layout.addRow("Min Increment:", self.min_incr_spin)
        
        # Max increment
        self.max_incr_spin = QDoubleSpinBox()
        self.max_incr_spin.setDecimals(6)
        self.max_incr_spin.setRange(-1e6, 1e6)
        self.max_incr_spin.setValue(integrator.max_incr)
        params_layout.addRow("Max Increment:", self.max_incr_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The Displacement Control integrator is used to specify a displacement increment for a specific degree of freedom at a specific node.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_changes(self):
        try:
            # Get parameters
            node_tag = self.node_tag_spin.value()
            dof = self.dof_spin.value()
            incr = self.incr_spin.value()
            num_iter = self.num_iter_spin.value()
            min_incr = self.min_incr_spin.value()
            max_incr = self.max_incr_spin.value()
            
            # Update integrator values
            self.integrator.node_tag = node_tag
            self.integrator.dof = dof
            self.integrator.incr = incr
            self.integrator.num_iter = num_iter
            self.integrator.min_incr = min_incr
            self.integrator.max_incr = max_incr
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NewmarkIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Newmark Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Gamma parameter
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setDecimals(6)
        self.gamma_spin.setRange(0, 1)
        self.gamma_spin.setValue(0.5)  # Default value
        params_layout.addRow("Gamma:", self.gamma_spin)
        
        # Beta parameter
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setDecimals(6)
        self.beta_spin.setRange(0, 0.5)
        self.beta_spin.setValue(0.25)  # Default value
        params_layout.addRow("Beta:", self.beta_spin)
        
        # Form parameter
        self.form_combo = QComboBox()
        self.form_combo.addItems(["D", "V", "A"])
        params_layout.addRow("Form:", self.form_combo)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The Newmark integrator is an implicit method used for dynamic analysis with parameters gamma and beta, "
                     "where gamma controls numerical damping and beta controls stability. Common values are gamma=0.5 and beta=0.25 "
                     "for average acceleration (unconditionally stable) or gamma=0.5 and beta=0 for central difference.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_integrator(self):
        try:
            # Get parameters
            gamma = self.gamma_spin.value()
            beta = self.beta_spin.value()
            form = self.form_combo.currentText()
            
            # Create integrator
            self.integrator = self.integrator_manager.create_integrator(
                "newmark",
                gamma=gamma,
                beta=beta,
                form=form
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NewmarkIntegratorEditDialog(QDialog):
    def __init__(self, integrator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Newmark Integrator")
        self.integrator = integrator
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Gamma parameter
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setDecimals(6)
        self.gamma_spin.setRange(0, 1)
        self.gamma_spin.setValue(integrator.gamma)
        params_layout.addRow("Gamma:", self.gamma_spin)
        
        # Beta parameter
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setDecimals(6)
        self.beta_spin.setRange(0, 0.5)
        self.beta_spin.setValue(integrator.beta)
        params_layout.addRow("Beta:", self.beta_spin)
        
        # Form parameter
        self.form_combo = QComboBox()
        self.form_combo.addItems(["D", "V", "A"])
        form_index = self.form_combo.findText(integrator.form)
        self.form_combo.setCurrentIndex(form_index if form_index >= 0 else 0)
        params_layout.addRow("Form:", self.form_combo)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The Newmark integrator is an implicit method used for dynamic analysis with parameters gamma and beta, "
                     "where gamma controls numerical damping and beta controls stability. Common values are gamma=0.5 and beta=0.25 "
                     "for average acceleration (unconditionally stable) or gamma=0.5 and beta=0 for central difference.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_changes(self):
        try:
            # Get parameters
            gamma = self.gamma_spin.value()
            beta = self.beta_spin.value()
            form = self.form_combo.currentText()
            
            # Update integrator values
            self.integrator.gamma = gamma
            self.integrator.beta = beta
            self.integrator.form = form
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class CentralDifferenceIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Central Difference Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("The Central Difference integrator is an explicit method for dynamic analysis. "
                     "It has no parameters to configure and is conditionally stable with a critical "
                     "time step that depends on the highest frequency in the system.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_integrator(self):
        try:
            # Create integrator - no parameters needed
            self.integrator = self.integrator_manager.create_integrator("centraldifference")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class HHTIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create HHT Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Alpha parameter
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setDecimals(6)
        self.alpha_spin.setRange(-0.5, 0)
        self.alpha_spin.setValue(-0.1)  # Default value
        params_layout.addRow("Alpha:", self.alpha_spin)
        
        # Use default gamma and beta values checkbox
        self.use_defaults_check = QCheckBox("Use default values for Gamma and Beta")
        self.use_defaults_check.setChecked(True)
        self.use_defaults_check.toggled.connect(self.toggle_defaults)
        params_layout.addRow("", self.use_defaults_check)
        
        # Gamma parameter
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setDecimals(6)
        self.gamma_spin.setRange(0, 2)
        self.gamma_spin.setEnabled(False)  # Initially disabled
        params_layout.addRow("Gamma:", self.gamma_spin)
        
        # Beta parameter
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setDecimals(6)
        self.beta_spin.setRange(0, 1)
        self.beta_spin.setEnabled(False)  # Initially disabled
        params_layout.addRow("Beta:", self.beta_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The HHT (Hilber-Hughes-Taylor) integrator is an implicit method for dynamic analysis "
                     "with numerical damping controlled by alpha (typically between -1/3 and 0). "
                     "Alpha = 0 corresponds to the Newmark method. Default gamma = 1.5-alpha and "
                     "beta = (1-alpha)²/4 are automatically computed if not specified.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Update the default values initially
        self.update_default_values()
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def toggle_defaults(self, checked):
        """Enable/disable gamma and beta inputs based on checkbox"""
        self.gamma_spin.setEnabled(not checked)
        self.beta_spin.setEnabled(not checked)
        if checked:
            self.update_default_values()
            
    def update_default_values(self):
        """Update the default gamma and beta values based on alpha"""
        alpha = self.alpha_spin.value()
        gamma = 1.5 - alpha
        beta = ((2.0 - alpha) ** 2) / 4.0
        self.gamma_spin.setValue(gamma)
        self.beta_spin.setValue(beta)
        
    def create_integrator(self):
        try:
            # Get parameters
            alpha = self.alpha_spin.value()
            
            # Use computed values if defaults are checked
            if self.use_defaults_check.isChecked():
                self.update_default_values()
                gamma = self.gamma_spin.value()
                beta = self.beta_spin.value()
                # Create integrator with just alpha, let the class compute gamma and beta
                self.integrator = self.integrator_manager.create_integrator("hht", alpha=alpha)
            else:
                gamma = self.gamma_spin.value()
                beta = self.beta_spin.value()
                # Create integrator with all parameters
                self.integrator = self.integrator_manager.create_integrator(
                    "hht", 
                    alpha=alpha,
                    gamma=gamma,
                    beta=beta
                )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class HHTIntegratorEditDialog(QDialog):
    def __init__(self, integrator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit HHT Integrator")
        self.integrator = integrator
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Alpha parameter
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setDecimals(6)
        self.alpha_spin.setRange(-0.5, 0)
        self.alpha_spin.setValue(integrator.alpha)
        params_layout.addRow("Alpha:", self.alpha_spin)
        
        # Gamma parameter
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setDecimals(6)
        self.gamma_spin.setRange(0, 2)
        self.gamma_spin.setValue(integrator.gamma)
        params_layout.addRow("Gamma:", self.gamma_spin)
        
        # Beta parameter
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setDecimals(6)
        self.beta_spin.setRange(0, 1)
        self.beta_spin.setValue(integrator.beta)
        params_layout.addRow("Beta:", self.beta_spin)
        
        # Recalculate gamma and beta checkbox
        self.recalculate_check = QCheckBox("Recalculate gamma and beta based on alpha")
        self.recalculate_check.toggled.connect(self.toggle_recalculation)
        params_layout.addRow("", self.recalculate_check)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The HHT (Hilber-Hughes-Taylor) integrator is an implicit method for dynamic analysis "
                     "with numerical damping controlled by alpha (typically between -1/3 and 0). "
                     "Alpha = 0 corresponds to the Newmark method.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def toggle_recalculation(self, checked):
        """Enable/disable gamma and beta inputs based on checkbox"""
        self.gamma_spin.setEnabled(not checked)
        self.beta_spin.setEnabled(not checked)
        if checked:
            self.update_default_values()
    
    def update_default_values(self):
        """Update the default gamma and beta values based on alpha"""
        alpha = self.alpha_spin.value()
        gamma = 1.5 - alpha
        beta = ((2.0 - alpha) ** 2) / 4.0
        self.gamma_spin.setValue(gamma)
        self.beta_spin.setValue(beta)

    def save_changes(self):
        try:
            # Get parameters
            alpha = self.alpha_spin.value()
            
            if self.recalculate_check.isChecked():
                self.update_default_values()
            
            gamma = self.gamma_spin.value()
            beta = self.beta_spin.value()
            
            # Update integrator values
            self.integrator.alpha = alpha
            self.integrator.gamma = gamma
            self.integrator.beta = beta
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class GeneralizedAlphaIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Generalized Alpha Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Alpha_m parameter
        self.alpha_m_spin = QDoubleSpinBox()
        self.alpha_m_spin.setDecimals(6)
        self.alpha_m_spin.setRange(-0.3, 0.3)
        self.alpha_m_spin.setValue(0.0)  # Default value
        params_layout.addRow("Alpha_m:", self.alpha_m_spin)
        
        # Alpha_f parameter
        self.alpha_f_spin = QDoubleSpinBox()
        self.alpha_f_spin.setDecimals(6)
        self.alpha_f_spin.setRange(-0.3, 0.3)
        self.alpha_f_spin.setValue(0.0)  # Default value
        params_layout.addRow("Alpha_f:", self.alpha_f_spin)
        
        # Use default gamma and beta values checkbox
        self.use_defaults_check = QCheckBox("Use default values for Gamma and Beta")
        self.use_defaults_check.setChecked(True)
        self.use_defaults_check.toggled.connect(self.toggle_defaults)
        params_layout.addRow("", self.use_defaults_check)
        
        # Gamma parameter
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setDecimals(6)
        self.gamma_spin.setRange(0, 2)
        self.gamma_spin.setEnabled(False)  # Initially disabled
        params_layout.addRow("Gamma:", self.gamma_spin)
        
        # Beta parameter
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setDecimals(6)
        self.beta_spin.setRange(0, 1)
        self.beta_spin.setEnabled(False)  # Initially disabled
        params_layout.addRow("Beta:", self.beta_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The Generalized Alpha integrator is an implicit method for dynamic analysis "
                     "with high-frequency dissipation controlled by alpha_m and alpha_f. "
                     "Default gamma = 0.5 + alpha_m - alpha_f and "
                     "beta = (1 + alpha_m - alpha_f)²/4 are recommended values.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Update the default values initially
        self.update_default_values()
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def toggle_defaults(self, checked):
        """Enable/disable gamma and beta inputs based on checkbox"""
        self.gamma_spin.setEnabled(not checked)
        self.beta_spin.setEnabled(not checked)
        if checked:
            self.update_default_values()
            
    def update_default_values(self):
        """Update the default gamma and beta values based on alpha_m and alpha_f"""
        alpha_m = self.alpha_m_spin.value()
        alpha_f = self.alpha_f_spin.value()
        gamma = 0.5 + alpha_m - alpha_f
        beta = ((1.0 + alpha_m - alpha_f) ** 2) / 4.0
        self.gamma_spin.setValue(gamma)
        self.beta_spin.setValue(beta)
        
    def create_integrator(self):
        try:
            # Get parameters
            alpha_m = self.alpha_m_spin.value()
            alpha_f = self.alpha_f_spin.value()
            
            # Use computed values if defaults are checked
            if self.use_defaults_check.isChecked():
                self.update_default_values()
                # Create integrator with just alpha_m and alpha_f, let the class compute gamma and beta
                self.integrator = self.integrator_manager.create_integrator(
                    "generalizedalpha", 
                    alpha_m=alpha_m, 
                    alpha_f=alpha_f
                )
            else:
                gamma = self.gamma_spin.value()
                beta = self.beta_spin.value()
                # Create integrator with all parameters
                self.integrator = self.integrator_manager.create_integrator(
                    "generalizedalpha", 
                    alpha_m=alpha_m,
                    alpha_f=alpha_f,
                    gamma=gamma,
                    beta=beta
                )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class GeneralizedAlphaIntegratorEditDialog(QDialog):
    def __init__(self, integrator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Generalized Alpha Integrator")
        self.integrator = integrator
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Alpha_m parameter
        self.alpha_m_spin = QDoubleSpinBox()
        self.alpha_m_spin.setDecimals(6)
        self.alpha_m_spin.setRange(-0.3, 0.3)
        self.alpha_m_spin.setValue(integrator.alpha_m)
        params_layout.addRow("Alpha_m:", self.alpha_m_spin)
        
        # Alpha_f parameter
        self.alpha_f_spin = QDoubleSpinBox()
        self.alpha_f_spin.setDecimals(6)
        self.alpha_f_spin.setRange(-0.3, 0.3)
        self.alpha_f_spin.setValue(integrator.alpha_f)
        params_layout.addRow("Alpha_f:", self.alpha_f_spin)
        
        # Gamma parameter
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setDecimals(6)
        self.gamma_spin.setRange(0, 2)
        self.gamma_spin.setValue(integrator.gamma)
        params_layout.addRow("Gamma:", self.gamma_spin)
        
        # Beta parameter
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setDecimals(6)
        self.beta_spin.setRange(0, 1)
        self.beta_spin.setValue(integrator.beta)
        params_layout.addRow("Beta:", self.beta_spin)
        
        # Recalculate gamma and beta checkbox
        self.recalculate_check = QCheckBox("Recalculate gamma and beta based on alpha values")
        self.recalculate_check.toggled.connect(self.toggle_recalculation)
        params_layout.addRow("", self.recalculate_check)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The Generalized Alpha integrator is an implicit method for dynamic analysis "
                     "with high-frequency dissipation controlled by alpha_m and alpha_f.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def toggle_recalculation(self, checked):
        """Enable/disable gamma and beta inputs based on checkbox"""
        self.gamma_spin.setEnabled(not checked)
        self.beta_spin.setEnabled(not checked)
        if checked:
            self.update_default_values()
    
    def update_default_values(self):
        """Update the default gamma and beta values based on alpha_m and alpha_f"""
        alpha_m = self.alpha_m_spin.value()
        alpha_f = self.alpha_f_spin.value()
        gamma = 0.5 + alpha_m - alpha_f
        beta = ((1.0 + alpha_m - alpha_f) ** 2) / 4.0
        self.gamma_spin.setValue(gamma)
        self.beta_spin.setValue(beta)

    def save_changes(self):
        try:
            # Get parameters
            alpha_m = self.alpha_m_spin.value()
            alpha_f = self.alpha_f_spin.value()
            
            if self.recalculate_check.isChecked():
                self.update_default_values()
            
            gamma = self.gamma_spin.value()
            beta = self.beta_spin.value()
            
            # Update integrator values
            self.integrator.alpha_m = alpha_m
            self.integrator.alpha_f = alpha_f
            self.integrator.gamma = gamma
            self.integrator.beta = beta
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ExplicitDifferenceIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Explicit Difference Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("The Explicit Difference integrator is an explicit method for dynamic analysis "
                     "specifically designed for uncoupled dynamic equations. "
                     "It has no parameters to configure and is conditionally stable with a critical "
                     "time step that depends on the highest frequency in the system.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_integrator(self):
        try:
            # Create integrator - no parameters needed
            self.integrator = self.integrator_manager.create_integrator("explicitdifference")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class TRBDF2IntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create TRBDF2 Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("The TRBDF2 (TR-BDF2) integrator is an implicit composite method that combines the "
                     "trapezoidal rule and backward differentiation formula. "
                     "It has no parameters to configure and provides second-order accuracy with "
                     "unconditional stability. This method is particularly effective for "
                     "stiff systems and alternates between the trapezoidal rule and backward Euler methods.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_integrator(self):
        try:
            # Create integrator - no parameters needed
            self.integrator = self.integrator_manager.create_integrator("trbdf2")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ArcLengthIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Arc-Length Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Arc length parameter
        self.s_spin = QDoubleSpinBox()
        self.s_spin.setDecimals(6)
        self.s_spin.setRange(0.0001, 1e6)
        self.s_spin.setValue(1.0)
        params_layout.addRow("Arc Length (s):", self.s_spin)
        
        # Alpha parameter
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setDecimals(6)
        self.alpha_spin.setRange(0, 1e6)
        self.alpha_spin.setValue(1.0)
        params_layout.addRow("Alpha:", self.alpha_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The Arc-Length integrator is used for tracing nonlinear equilibrium paths in "
                     "static analysis, particularly when passing limit points. The arc-length parameter (s) "
                     "controls the step size, and alpha is a scaling factor on the reference loads.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_integrator(self):
        try:
            # Get parameters
            s = self.s_spin.value()
            alpha = self.alpha_spin.value()
            
            # Create integrator
            self.integrator = self.integrator_manager.create_integrator(
                "arclength", 
                s=s,
                alpha=alpha
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ArcLengthIntegratorEditDialog(QDialog):
    def __init__(self, integrator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Arc-Length Integrator")
        self.integrator = integrator
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Arc length parameter
        self.s_spin = QDoubleSpinBox()
        self.s_spin.setDecimals(6)
        self.s_spin.setRange(0.0001, 1e6)
        self.s_spin.setValue(integrator.s)
        params_layout.addRow("Arc Length (s):", self.s_spin)
        
        # Alpha parameter
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setDecimals(6)
        self.alpha_spin.setRange(0, 1e6)
        self.alpha_spin.setValue(integrator.alpha)
        params_layout.addRow("Alpha:", self.alpha_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The Arc-Length integrator is used for tracing nonlinear equilibrium paths in "
                     "static analysis, particularly when passing limit points. The arc-length parameter (s) "
                     "controls the step size, and alpha is a scaling factor on the reference loads.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_changes(self):
        try:
            # Get parameters
            s = self.s_spin.value()
            alpha = self.alpha_spin.value()
            
            # Update integrator values
            self.integrator.s = s
            self.integrator.alpha = alpha
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class MinUnbalDispNormIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Minimum Unbalanced Displacement Norm Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Lambda1 parameter
        self.dlambda1_spin = QDoubleSpinBox()
        self.dlambda1_spin.setDecimals(6)
        self.dlambda1_spin.setRange(0.000001, 1e6)
        self.dlambda1_spin.setValue(1.0)
        params_layout.addRow("Initial Load Factor (dlambda1):", self.dlambda1_spin)
        
        # Jd parameter
        self.jd_spin = QSpinBox()
        self.jd_spin.setRange(1, 100)
        self.jd_spin.setValue(1)
        params_layout.addRow("Jd factor:", self.jd_spin)
        
        # Min lambda parameter
        self.min_lambda_spin = QDoubleSpinBox()
        self.min_lambda_spin.setDecimals(6)
        self.min_lambda_spin.setRange(0.000001, 1e6)
        self.min_lambda_spin.setValue(1.0)
        params_layout.addRow("Min Load Factor:", self.min_lambda_spin)
        
        # Max lambda parameter
        self.max_lambda_spin = QDoubleSpinBox()
        self.max_lambda_spin.setDecimals(6)
        self.max_lambda_spin.setRange(0.000001, 1e6)
        self.max_lambda_spin.setValue(1.0)
        params_layout.addRow("Max Load Factor:", self.max_lambda_spin)
        
        # Determinant flag
        self.det_check = QCheckBox("Use determinant of tangent")
        params_layout.addRow("", self.det_check)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The MinUnbalDispNorm integrator selects the minimum unbalanced displacement "
                     "norm and corresponding displacement change. It uses an incremental factor "
                     "on the time step to determine a new load level.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_integrator(self):
        try:
            # Get parameters
            dlambda1 = self.dlambda1_spin.value()
            jd = self.jd_spin.value()
            min_lambda = self.min_lambda_spin.value()
            max_lambda = self.max_lambda_spin.value()
            det = self.det_check.isChecked()
            
            # Create integrator
            self.integrator = self.integrator_manager.create_integrator(
                "minunbaldispnorm", 
                dlambda1=dlambda1,
                jd=jd,
                min_lambda=min_lambda,
                max_lambda=max_lambda,
                det=det
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class MinUnbalDispNormIntegratorEditDialog(QDialog):
    def __init__(self, integrator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Minimum Unbalanced Displacement Norm Integrator")
        self.integrator = integrator
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Lambda1 parameter
        self.dlambda1_spin = QDoubleSpinBox()
        self.dlambda1_spin.setDecimals(6)
        self.dlambda1_spin.setRange(0.000001, 1e6)
        self.dlambda1_spin.setValue(integrator.dlambda1)
        params_layout.addRow("Initial Load Factor (dlambda1):", self.dlambda1_spin)
        
        # Jd parameter
        self.jd_spin = QSpinBox()
        self.jd_spin.setRange(1, 100)
        self.jd_spin.setValue(integrator.jd)
        params_layout.addRow("Jd factor:", self.jd_spin)
        
        # Min lambda parameter
        self.min_lambda_spin = QDoubleSpinBox()
        self.min_lambda_spin.setDecimals(6)
        self.min_lambda_spin.setRange(0.000001, 1e6)
        self.min_lambda_spin.setValue(integrator.min_lambda)
        params_layout.addRow("Min Load Factor:", self.min_lambda_spin)
        
        # Max lambda parameter
        self.max_lambda_spin = QDoubleSpinBox()
        self.max_lambda_spin.setDecimals(6)
        self.max_lambda_spin.setRange(0.000001, 1e6)
        self.max_lambda_spin.setValue(integrator.max_lambda)
        params_layout.addRow("Max Load Factor:", self.max_lambda_spin)
        
        # Determinant flag
        self.det_check = QCheckBox("Use determinant of tangent")
        self.det_check.setChecked(integrator.det)
        params_layout.addRow("", self.det_check)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The MinUnbalDispNorm integrator selects the minimum unbalanced displacement "
                     "norm and corresponding displacement change. It uses an incremental factor "
                     "on the time step to determine a new load level.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_changes(self):
        try:
            # Get parameters
            dlambda1 = self.dlambda1_spin.value()
            jd = self.jd_spin.value()
            min_lambda = self.min_lambda_spin.value()
            max_lambda = self.max_lambda_spin.value()
            det = self.det_check.isChecked()
            
            # Update integrator values
            self.integrator.dlambda1 = dlambda1
            self.integrator.jd = jd
            self.integrator.min_lambda = min_lambda
            self.integrator.max_lambda = max_lambda
            self.integrator.det = det
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ParallelDisplacementControlIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Parallel Displacement Control Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Node tag
        self.node_tag_spin = QSpinBox()
        self.node_tag_spin.setRange(1, 999999)
        params_layout.addRow("Node Tag:", self.node_tag_spin)
        
        # DOF
        self.dof_spin = QSpinBox()
        self.dof_spin.setRange(1, 6)
        params_layout.addRow("Degree of Freedom:", self.dof_spin)
        
        # Displacement increment
        self.incr_spin = QDoubleSpinBox()
        self.incr_spin.setDecimals(6)
        self.incr_spin.setRange(-1e6, 1e6)
        self.incr_spin.setValue(0.1)
        params_layout.addRow("Displacement Increment:", self.incr_spin)
        
        # Number of iterations
        self.num_iter_spin = QSpinBox()
        self.num_iter_spin.setRange(1, 1000)
        self.num_iter_spin.setValue(1)
        params_layout.addRow("Number of Iterations:", self.num_iter_spin)
        
        # Min increment
        self.min_incr_spin = QDoubleSpinBox()
        self.min_incr_spin.setDecimals(6)
        self.min_incr_spin.setRange(-1e6, 1e6)
        self.min_incr_spin.setValue(0.1)
        params_layout.addRow("Min Increment:", self.min_incr_spin)
        
        # Max increment
        self.max_incr_spin = QDoubleSpinBox()
        self.max_incr_spin.setDecimals(6)
        self.max_incr_spin.setRange(-1e6, 1e6)
        self.max_incr_spin.setValue(0.1)
        params_layout.addRow("Max Increment:", self.max_incr_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The ParallelDisplacementControl integrator is similar to DisplacementControl "
                     "but designed for parallel computing environments. It specifies a displacement "
                     "increment for a specific degree of freedom at a specific node.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_integrator(self):
        try:
            # Get parameters
            node_tag = self.node_tag_spin.value()
            dof = self.dof_spin.value()
            incr = self.incr_spin.value()
            num_iter = self.num_iter_spin.value()
            min_incr = self.min_incr_spin.value()
            max_incr = self.max_incr_spin.value()
            
            # Create integrator
            self.integrator = self.integrator_manager.create_integrator(
                "paralleldisplacementcontrol", 
                node_tag=node_tag,
                dof=dof,
                incr=incr, 
                num_iter=num_iter, 
                min_incr=min_incr, 
                max_incr=max_incr
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ParallelDisplacementControlIntegratorEditDialog(QDialog):
    def __init__(self, integrator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Parallel Displacement Control Integrator")
        self.integrator = integrator
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Node tag
        self.node_tag_spin = QSpinBox()
        self.node_tag_spin.setRange(1, 999999)
        self.node_tag_spin.setValue(integrator.node_tag)
        params_layout.addRow("Node Tag:", self.node_tag_spin)
        
        # DOF
        self.dof_spin = QSpinBox()
        self.dof_spin.setRange(1, 6)
        self.dof_spin.setValue(integrator.dof)
        params_layout.addRow("Degree of Freedom:", self.dof_spin)
        
        # Displacement increment
        self.incr_spin = QDoubleSpinBox()
        self.incr_spin.setDecimals(6)
        self.incr_spin.setRange(-1e6, 1e6)
        self.incr_spin.setValue(integrator.incr)
        params_layout.addRow("Displacement Increment:", self.incr_spin)
        
        # Number of iterations
        self.num_iter_spin = QSpinBox()
        self.num_iter_spin.setRange(1, 1000)
        self.num_iter_spin.setValue(integrator.num_iter)
        params_layout.addRow("Number of Iterations:", self.num_iter_spin)
        
        # Min increment
        self.min_incr_spin = QDoubleSpinBox()
        self.min_incr_spin.setDecimals(6)
        self.min_incr_spin.setRange(-1e6, 1e6)
        self.min_incr_spin.setValue(integrator.min_incr)
        params_layout.addRow("Min Increment:", self.min_incr_spin)
        
        # Max increment
        self.max_incr_spin = QDoubleSpinBox()
        self.max_incr_spin.setDecimals(6)
        self.max_incr_spin.setRange(-1e6, 1e6)
        self.max_incr_spin.setValue(integrator.max_incr)
        params_layout.addRow("Max Increment:", self.max_incr_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The ParallelDisplacementControl integrator is similar to DisplacementControl "
                     "but designed for parallel computing environments. It specifies a displacement "
                     "increment for a specific degree of freedom at a specific node.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_changes(self):
        try:
            # Get parameters
            node_tag = self.node_tag_spin.value()
            dof = self.dof_spin.value()
            incr = self.incr_spin.value()
            num_iter = self.num_iter_spin.value()
            min_incr = self.min_incr_spin.value()
            max_incr = self.max_incr_spin.value()
            
            # Update integrator values
            self.integrator.node_tag = node_tag
            self.integrator.dof = dof
            self.integrator.incr = incr
            self.integrator.num_iter = num_iter
            self.integrator.min_incr = min_incr
            self.integrator.max_incr = max_incr
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class PFEMIntegratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create PFEM Integrator")
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Gamma parameter
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setDecimals(6)
        self.gamma_spin.setRange(0, 1)
        self.gamma_spin.setValue(0.5)  # Default value
        params_layout.addRow("Gamma:", self.gamma_spin)
        
        # Beta parameter
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setDecimals(6)
        self.beta_spin.setRange(0, 0.5)
        self.beta_spin.setValue(0.25)  # Default value
        params_layout.addRow("Beta:", self.beta_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The PFEM (Particle Finite Element Method) integrator is used for fluid-structure "
                     "interaction problems. Parameters gamma and beta are similar to those in the "
                     "Newmark method, with default values of 0.5 and 0.25 respectively.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_integrator)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_integrator(self):
        try:
            # Get parameters
            gamma = self.gamma_spin.value()
            beta = self.beta_spin.value()
            
            # Create integrator
            self.integrator = self.integrator_manager.create_integrator(
                "pfem",
                gamma=gamma,
                beta=beta
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class PFEMIntegratorEditDialog(QDialog):
    def __init__(self, integrator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit PFEM Integrator")
        self.integrator = integrator
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Gamma parameter
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setDecimals(6)
        self.gamma_spin.setRange(0, 1)
        self.gamma_spin.setValue(integrator.gamma)
        params_layout.addRow("Gamma:", self.gamma_spin)
        
        # Beta parameter
        self.beta_spin = QDoubleSpinBox()
        self.beta_spin.setDecimals(6)
        self.beta_spin.setRange(0, 0.5)
        self.beta_spin.setValue(integrator.beta)
        params_layout.addRow("Beta:", self.beta_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("The PFEM (Particle Finite Element Method) integrator is used for fluid-structure "
                     "interaction problems. Parameters gamma and beta are similar to those in the "
                     "Newmark method, with default values of 0.5 and 0.25 respectively.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_changes(self):
        try:
            # Get parameters
            gamma = self.gamma_spin.value()
            beta = self.beta_spin.value()
            
            # Update integrator values
            self.integrator.gamma = gamma
            self.integrator.beta = beta
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == '__main__':
    from qtpy.QtWidgets import QApplication
    import sys
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    window = IntegratorManagerTab()
    window.show()
    sys.exit(app.exec_())