from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout,
    QGroupBox, QStackedWidget, QDoubleSpinBox, QSpinBox, QCheckBox,
    QDialogButtonBox
)
from qtpy.QtCore import Qt

from meshmaker.components.Analysis.analysisBase import (
    AnalysisManager, Analysis, ConstraintHandler, Numberer, System, Test, Algorithm, Integrator
)


class AnalysisManagerTab(QWidget):
    """
    Widget for managing analyses
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analysis_manager = AnalysisManager()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create new analysis section
        create_group = QGroupBox("Create New Analysis")
        create_layout = QHBoxLayout(create_group)
        
        self.analysis_name_input = QLineEdit()
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["Static", "Transient", "VariableTransient"])
        
        create_btn = QPushButton("Create Analysis")
        create_btn.clicked.connect(self.create_analysis)
        
        create_layout.addWidget(QLabel("Name:"))
        create_layout.addWidget(self.analysis_name_input)
        create_layout.addWidget(QLabel("Type:"))
        create_layout.addWidget(self.analysis_type_combo)
        create_layout.addWidget(create_btn)
        
        layout.addWidget(create_group)
        
        # Analysis table
        self.analysis_table = QTableWidget()
        self.analysis_table.setColumnCount(4)  # Tag, Name, Type, Actions
        self.analysis_table.setHorizontalHeaderLabels(["Tag", "Name", "Type", "Actions"])
        header = self.analysis_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.analysis_table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_analyses)
        layout.addWidget(refresh_btn)
        
        # Initial refresh
        self.refresh_analyses()
    
    def create_analysis(self):
        """Create a new analysis"""
        name = self.analysis_name_input.text().strip() or None
        analysis_type = self.analysis_type_combo.currentText()
        
        try:
            analysis = self.analysis_manager.create_analysis(name=name, analysis_type=analysis_type)
            self.refresh_analyses()
            
            # Open the edit dialog for the new analysis
            self.edit_analysis(analysis)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def refresh_analyses(self):
        """Refresh the analysis table"""
        self.analysis_table.setRowCount(0)
        analyses = self.analysis_manager.get_all_analyses()
        
        self.analysis_table.setRowCount(len(analyses))
        for row, (tag, analysis) in enumerate(analyses.items()):
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.analysis_table.setItem(row, 0, tag_item)
            
            # Name
            name_item = QTableWidgetItem(analysis.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.analysis_table.setItem(row, 1, name_item)
            
            # Type
            type_item = QTableWidgetItem(analysis.analysis_type or "")
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.analysis_table.setItem(row, 2, type_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, a=analysis: self.edit_analysis(a))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, t=tag: self.delete_analysis(t))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.analysis_table.setCellWidget(row, 3, actions_widget)
    
    def edit_analysis(self, analysis):
        """Open dialog to edit an analysis"""
        dialog = AnalysisEditorDialog(analysis, self)
        dialog.exec_()
        self.refresh_analyses()
    
    def delete_analysis(self, tag):
        """Delete an analysis"""
        reply = QMessageBox.question(
            self, "Delete Analysis",
            f"Are you sure you want to delete analysis with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.analysis_manager.remove_analysis(tag)
            self.refresh_analyses()


class AnalysisEditorDialog(QDialog):
    """
    Dialog for editing an analysis configuration
    """
    def __init__(self, analysis, parent=None):
        super().__init__(parent)
        self.analysis = analysis
        self.analysis_manager = AnalysisManager()
        
        self.setWindowTitle(f"Edit Analysis '{analysis.name}' (Tag: {analysis.tag})")
        self.resize(600, 500)
        
        self.init_ui()
        self.load_current_values()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create a tab widget for different components
        self.tabs = QStackedWidget()
        
        # Create tabs
        self.create_analysis_type_tab()
        self.create_constraint_tab()
        self.create_numberer_tab()
        self.create_system_tab()
        self.create_test_tab()
        self.create_algorithm_tab()
        self.create_integrator_tab()
        self.create_summary_tab()
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_tab)
        self.prev_btn.setEnabled(False)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_tab)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setVisible(False)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.save_btn)
        nav_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(self.tabs)
        layout.addLayout(nav_layout)
        
        # Initialize tab navigation
        self.current_tab = 0
        self.update_navigation()
    
    def create_analysis_type_tab(self):
        """Create the analysis type tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        group = QGroupBox("Analysis Type")
        form = QFormLayout(group)
        
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["Static", "Transient", "VariableTransient"])
        form.addRow("Type:", self.analysis_type_combo)
        
        # Additional transient options - visible only when needed
        self.transient_options = QGroupBox("Transient Options")
        transient_form = QFormLayout(self.transient_options)
        
        self.num_sublevels_spin = QSpinBox()
        self.num_sublevels_spin.setRange(0, 100)
        transient_form.addRow("Number of Sublevels:", self.num_sublevels_spin)
        
        self.num_substeps_spin = QSpinBox()
        self.num_substeps_spin.setRange(0, 100)
        transient_form.addRow("Number of Substeps:", self.num_substeps_spin)
        
        self.transient_options.setVisible(False)
        
        # Connect analysis type change to show/hide transient options
        self.analysis_type_combo.currentTextChanged.connect(self.update_transient_options)
        
        layout.addWidget(group)
        layout.addWidget(self.transient_options)
        layout.addStretch()
        
        self.tabs.addWidget(tab)
    
    def create_constraint_tab(self):
        """Create the constraint handler tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        group = QGroupBox("Constraint Handler")
        form = QFormLayout(group)
        
        self.constraint_type_combo = QComboBox()
        self.constraint_type_combo.addItems(self.analysis_manager.get_available_constraint_handlers())
        form.addRow("Type:", self.constraint_type_combo)
        
        # Create stacked widget for different constraint handler options
        self.constraint_options = QStackedWidget()
        
        # Plain - no options
        plain_widget = QWidget()
        self.constraint_options.addWidget(plain_widget)
        
        # Transformation - no options
        transformation_widget = QWidget()
        self.constraint_options.addWidget(transformation_widget)
        
        # Penalty
        penalty_widget = QWidget()
        penalty_form = QFormLayout(penalty_widget)
        self.penalty_alpha_s = QDoubleSpinBox()
        self.penalty_alpha_s.setRange(1e-10, 1e20)
        self.penalty_alpha_s.setDecimals(10)
        self.penalty_alpha_s.setValue(1e10)
        penalty_form.addRow("Alpha S:", self.penalty_alpha_s)
        
        self.penalty_alpha_m = QDoubleSpinBox()
        self.penalty_alpha_m.setRange(1e-10, 1e20)
        self.penalty_alpha_m.setDecimals(10)
        self.penalty_alpha_m.setValue(1e10)
        penalty_form.addRow("Alpha M:", self.penalty_alpha_m)
        
        self.constraint_options.addWidget(penalty_widget)
        
        # Lagrange
        lagrange_widget = QWidget()
        lagrange_form = QFormLayout(lagrange_widget)
        self.lagrange_alpha_s = QDoubleSpinBox()
        self.lagrange_alpha_s.setRange(0.1, 10.0)
        self.lagrange_alpha_s.setValue(1.0)
        lagrange_form.addRow("Alpha S:", self.lagrange_alpha_s)
        
        self.lagrange_alpha_m = QDoubleSpinBox()
        self.lagrange_alpha_m.setRange(0.1, 10.0)
        self.lagrange_alpha_m.setValue(1.0)
        lagrange_form.addRow("Alpha M:", self.lagrange_alpha_m)
        
        self.constraint_options.addWidget(lagrange_widget)
        
        # Auto
        auto_widget = QWidget()
        auto_form = QFormLayout(auto_widget)
        self.auto_verbose = QCheckBox()
        auto_form.addRow("Verbose:", self.auto_verbose)
        
        self.auto_penalty = QDoubleSpinBox()
        self.auto_penalty.setRange(1, 10)
        self.auto_penalty.setValue(3)
        auto_form.addRow("Auto Penalty (oom):", self.auto_penalty)
        
        self.user_penalty = QDoubleSpinBox()
        self.user_penalty.setRange(1e-10, 1e20)
        self.user_penalty.setDecimals(10)
        self.user_penalty.setValue(1e10)
        auto_form.addRow("User Penalty:", self.user_penalty)
        
        self.constraint_options.addWidget(auto_widget)
        
        # Connect constraint type to options widget
        self.constraint_type_combo.currentIndexChanged.connect(self.constraint_options.setCurrentIndex)
        
        # Add the stacked widget
        form.addRow("Options:", self.constraint_options)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tabs.addWidget(tab)
    
    def create_numberer_tab(self):
        """Create the numberer tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        group = QGroupBox("Numberer")
        form = QFormLayout(group)
        
        self.numberer_type_combo = QComboBox()
        self.numberer_type_combo.addItems(self.analysis_manager.get_available_numberers())
        form.addRow("Type:", self.numberer_type_combo)
        
        # Numberers have no additional options
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tabs.addWidget(tab)
    
    def create_system_tab(self):
        """Create the system tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        group = QGroupBox("System")
        form = QFormLayout(group)
        
        self.system_type_combo = QComboBox()
        self.system_type_combo.addItems(self.analysis_manager.get_available_systems())
        form.addRow("Type:", self.system_type_combo)
        
        # Create stacked widget for different system options
        self.system_options = QStackedWidget()
        
        # Most systems have no options - create empty widgets
        for i in range(5):  # First 5 system types have no options
            self.system_options.addWidget(QWidget())
        
        # Umfpack
        umfpack_widget = QWidget()
        umfpack_form = QFormLayout(umfpack_widget)
        self.umfpack_lvalue = QDoubleSpinBox()
        self.umfpack_lvalue.setRange(1.0, 100.0)
        self.umfpack_lvalue.setValue(10.0)
        umfpack_form.addRow("LValue Factor:", self.umfpack_lvalue)
        
        self.system_options.addWidget(umfpack_widget)
        
        # Connect system type to options widget
        self.system_type_combo.currentIndexChanged.connect(self.system_options.setCurrentIndex)
        
        # Add the stacked widget
        form.addRow("Options:", self.system_options)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tabs.addWidget(tab)
    
    def create_test_tab(self):
        """Create the test tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        group = QGroupBox("Convergence Test")
        form = QFormLayout(group)
        
        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems(self.analysis_manager.get_available_tests())
        form.addRow("Type:", self.test_type_combo)
        
        # Options common to all tests
        self.test_tol = QDoubleSpinBox()
        self.test_tol.setRange(1e-12, 1e-2)
        self.test_tol.setDecimals(12)
        self.test_tol.setValue(1e-6)
        form.addRow("Tolerance:", self.test_tol)
        
        self.test_max_iter = QSpinBox()
        self.test_max_iter.setRange(1, 1000)
        self.test_max_iter.setValue(10)
        form.addRow("Max Iterations:", self.test_max_iter)
        
        self.test_print_flag = QSpinBox()
        self.test_print_flag.setRange(0, 5)
        self.test_print_flag.setValue(0)
        form.addRow("Print Flag:", self.test_print_flag)
        
        self.test_norm_type = QComboBox()
        self.test_norm_type.addItems(["0 - Max Norm", "1 - 1-Norm", "2 - 2-Norm"])
        self.test_norm_type.setCurrentIndex(2)  # 2-Norm is default
        form.addRow("Norm Type:", self.test_norm_type)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tabs.addWidget(tab)
    
    def create_algorithm_tab(self):
        """Create the algorithm tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        group = QGroupBox("Algorithm")
        form = QFormLayout(group)
        
        self.algorithm_type_combo = QComboBox()
        self.algorithm_type_combo.addItems(self.analysis_manager.get_available_algorithms())
        form.addRow("Type:", self.algorithm_type_combo)
        
        # Create stacked widget for different algorithm options
        self.algorithm_options = QStackedWidget()
        
        # Linear
        linear_widget = QWidget()
        linear_form = QFormLayout(linear_widget)
        self.linear_initial = QCheckBox()
        linear_form.addRow("Use Initial Stiffness:", self.linear_initial)
        self.linear_factor_once = QCheckBox()
        linear_form.addRow("Factor Only Once:", self.linear_factor_once)
        
        self.algorithm_options.addWidget(linear_widget)
        
        # Newton
        newton_widget = QWidget()
        newton_form = QFormLayout(newton_widget)
        self.newton_initial = QCheckBox()
        newton_form.addRow("Use Initial Stiffness:", self.newton_initial)
        self.newton_initial_then_current = QCheckBox()
        newton_form.addRow("Initial Then Current:", self.newton_initial_then_current)
        
        # Connect checkboxes to ensure they are mutually exclusive
        self.newton_initial.stateChanged.connect(
            lambda state: self.newton_initial_then_current.setChecked(False) if state else None
        )
        self.newton_initial_then_current.stateChanged.connect(
            lambda state: self.newton_initial.setChecked(False) if state else None
        )
        
        self.algorithm_options.addWidget(newton_widget)
        
        # ModifiedNewton
        modified_newton_widget = QWidget()
        modified_newton_form = QFormLayout(modified_newton_widget)
        self.modified_newton_initial = QCheckBox()
        modified_newton_form.addRow("Use Initial Stiffness:", self.modified_newton_initial)
        
        self.algorithm_options.addWidget(modified_newton_widget)
        
        # Connect algorithm type to options widget
        self.algorithm_type_combo.currentIndexChanged.connect(self.algorithm_options.setCurrentIndex)
        
        # Add the stacked widget
        form.addRow("Options:", self.algorithm_options)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tabs.addWidget(tab)
    
    def create_integrator_tab(self):
        """Create the integrator tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        group = QGroupBox("Integrator")
        form = QFormLayout(group)
        
        self.integrator_type_combo = QComboBox()
        self.integrator_type_combo.addItems(self.analysis_manager.get_available_integrators())
        form.addRow("Type:", self.integrator_type_combo)
        
        # Create stacked widget for different integrator options
        self.integrator_options = QStackedWidget()
        
        # LoadControl
        load_control_widget = QWidget()
        load_control_form = QFormLayout(load_control_widget)
        self.load_control_lambda = QDoubleSpinBox()
        self.load_control_lambda.setRange(-100.0, 100.0)
        self.load_control_lambda.setValue(1.0)
        load_control_form.addRow("Lambda:", self.load_control_lambda)
        
        self.load_control_num_iter = QSpinBox()
        self.load_control_num_iter.setRange(0, 1000)
        self.load_control_num_iter.setValue(1)
        self.load_control_num_iter.setSpecialValueText("Not specified")
        load_control_form.addRow("Num Iterations:", self.load_control_num_iter)
        
        self.load_control_min_lambda = QDoubleSpinBox()
        self.load_control_min_lambda.setRange(-100.0, 100.0)
        self.load_control_min_lambda.setValue(0.1)
        self.load_control_min_lambda.setEnabled(False)
        load_control_form.addRow("Min Lambda:", self.load_control_min_lambda)
        
        self.load_control_max_lambda = QDoubleSpinBox()
        self.load_control_max_lambda.setRange(-100.0, 100.0)
        self.load_control_max_lambda.setValue(1.0)
        self.load_control_max_lambda.setEnabled(False)
        load_control_form.addRow("Max Lambda:", self.load_control_max_lambda)
        
        # Enable min/max lambda only if num_iter is specified
        self.load_control_num_iter.valueChanged.connect(
            lambda value: (
                self.load_control_min_lambda.setEnabled(value > 0),
                self.load_control_max_lambda.setEnabled(value > 0)
            )
        )
        
        self.integrator_options.addWidget(load_control_widget)
        
        # DisplacementControl
        disp_control_widget = QWidget()
        disp_control_form = QFormLayout(disp_control_widget)
        self.disp_control_node = QSpinBox()
        self.disp_control_node.setRange(1, 100000)
        disp_control_form.addRow("Node:", self.disp_control_node)
        
        self.disp_control_dof = QSpinBox()
        self.disp_control_dof.setRange(1, 6)
        disp_control_form.addRow("DOF:", self.disp_control_dof)
        
        self.disp_control_incr = QDoubleSpinBox()
        self.disp_control_incr.setRange(-100.0, 100.0)
        self.disp_control_incr.setValue(0.1)
        disp_control_form.addRow("Increment:", self.disp_control_incr)
        
        self.disp_control_num_iter = QSpinBox()
        self.disp_control_num_iter.setRange(0, 1000)
        self.disp_control_num_iter.setValue(1)
        self.disp_control_num_iter.setSpecialValueText("Not specified")
        disp_control_form.addRow("Num Iterations:", self.disp_control_num_iter)
        
        self.disp_control_min_incr = QDoubleSpinBox()
        self.disp_control_min_incr.setRange(-100.0, 100.0)
        self.disp_control_min_incr.setValue(0.01)
        self.disp_control_min_incr.setEnabled(False)
        disp_control_form.addRow("Min Increment:", self.disp_control_min_incr)
        
        self.disp_control_max_incr = QDoubleSpinBox()
        self.disp_control_max_incr.setRange(-100.0, 100.0)
        self.disp_control_max_incr.setValue(1.0)
        self.disp_control_max_incr.setEnabled(False)
        disp_control_form.addRow("Max Increment:", self.disp_control_max_incr)
        
        # Enable min/max incr only if num_iter is specified
        self.disp_control_num_iter.valueChanged.connect(
            lambda value: (
                self.disp_control_min_incr.setEnabled(value > 0),
                self.disp_control_max_incr.setEnabled(value > 0)
            )
        )
        
        self.integrator_options.addWidget(disp_control_widget)
        
        # Newmark
        newmark_widget = QWidget()
        newmark_form = QFormLayout(newmark_widget)
        self.newmark_gamma = QDoubleSpinBox()
        self.newmark_gamma.setRange(0.0, 1.0)
        self.newmark_gamma.setValue(0.5)
        self.newmark_gamma.setDecimals(3)
        newmark_form.addRow("Gamma:", self.newmark_gamma)
        
        self.newmark_beta = QDoubleSpinBox()
        self.newmark_beta.setRange(0.0, 0.5)
        self.newmark_beta.setValue(0.25)
        self.newmark_beta.setDecimals(3)
        newmark_form.addRow("Beta:", self.newmark_beta)
        
        # Add preset buttons
        preset_layout = QHBoxLayout()
        avg_accel_btn = QPushButton("Average Acceleration")
        avg_accel_btn.clicked.connect(lambda: (
            self.newmark_gamma.setValue(0.5),
            self.newmark_beta.setValue(0.25)
        ))
        
        linear_accel_btn = QPushButton("Linear Acceleration")
        linear_accel_btn.clicked.connect(lambda: (
            self.newmark_gamma.setValue(0.5),
            self.newmark_beta.setValue(0.167)
        ))
        
        preset_layout.addWidget(avg_accel_btn)
        preset_layout.addWidget(linear_accel_btn)
        newmark_form.addRow("Presets:", preset_layout)
        
        self.integrator_options.addWidget(newmark_widget)
        
        # GeneralizedAlpha
        gen_alpha_widget = QWidget()
        gen_alpha_form = QFormLayout(gen_alpha_widget)
        self.gen_alpha_alpha_m = QDoubleSpinBox()
        self.gen_alpha_alpha_m.setRange(-1.0, 1.0)
        self.gen_alpha_alpha_m.setValue(0.0)
        self.gen_alpha_alpha_m.setDecimals(3)
        gen_alpha_form.addRow("Alpha M:", self.gen_alpha_alpha_m)
        
        self.gen_alpha_alpha_f = QDoubleSpinBox()
        self.gen_alpha_alpha_f.setRange(-1.0, 1.0)
        self.gen_alpha_alpha_f.setValue(0.0)
        self.gen_alpha_alpha_f.setDecimals(3)
        gen_alpha_form.addRow("Alpha F:", self.gen_alpha_alpha_f)
        
        self.gen_alpha_gamma = QDoubleSpinBox()
        self.gen_alpha_gamma.setRange(0.0, 1.0)
        self.gen_alpha_gamma.setValue(0.5)
        self.gen_alpha_gamma.setDecimals(3)
        self.gen_alpha_gamma.setSpecialValueText("Default")
        gen_alpha_form.addRow("Gamma (optional):", self.gen_alpha_gamma)
        
        self.gen_alpha_beta = QDoubleSpinBox()
        self.gen_alpha_beta.setRange(0.0, 0.5)
        self.gen_alpha_beta.setValue(0.25)
        self.gen_alpha_beta.setDecimals(3)
        self.gen_alpha_beta.setSpecialValueText("Default")
        gen_alpha_form.addRow("Beta (optional):", self.gen_alpha_beta)
        
        self.integrator_options.addWidget(gen_alpha_widget)
        
        # Connect integrator type to options widget
        self.integrator_type_combo.currentIndexChanged.connect(self.integrator_options.setCurrentIndex)
        
        # Add the stacked widget
        form.addRow("Options:", self.integrator_options)
        
        layout.addWidget(group)
        layout.addStretch()
        
        self.tabs.addWidget(tab)
    
    def create_summary_tab(self):
        """Create the summary tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        group = QGroupBox("Analysis Summary")
        summary_layout = QVBoxLayout(group)
        
        self.summary_text = QLabel("Please configure all analysis components to see the summary.")
        self.summary_text.setWordWrap(True)
        self.summary_text.setTextFormat(Qt.RichText)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(group)
        
        # Analysis control section
        control_group = QGroupBox("Analysis Control")
        control_layout = QFormLayout(control_group)
        
        self.num_steps_spin = QSpinBox()
        self.num_steps_spin.setRange(1, 10000)
        self.num_steps_spin.setValue(10)
        control_layout.addRow("Number of Steps:", self.num_steps_spin)
        
        self.time_step_spin = QDoubleSpinBox()
        self.time_step_spin.setRange(0.00001, 10.0)
        self.time_step_spin.setValue(0.01)
        self.time_step_spin.setDecimals(5)
        control_layout.addRow("Time Step (dt):", self.time_step_spin)
        
        # Only show time step for transient analysis
        self.time_step_spin.setVisible(self.analysis.analysis_type != "Static")
        
        # Connect analysis type change to show/hide time step
        self.analysis_type_combo.currentTextChanged.connect(
            lambda text: self.time_step_spin.setVisible(text != "Static")
        )
        
        layout.addWidget(control_group)
        layout.addStretch()
        
        self.tabs.addWidget(tab)
    
    def update_transient_options(self, text):
        """Show/hide transient options based on analysis type"""
        self.transient_options.setVisible(text != "Static")
    
    def load_current_values(self):
        """Load current analysis values into the UI"""
        # Analysis type
        if self.analysis.analysis_type:
            index = self.analysis_type_combo.findText(self.analysis.analysis_type)
            if index >= 0:
                self.analysis_type_combo.setCurrentIndex(index)
        
        # Constraint handler
        if self.analysis.constraint_handler:
            handler_type = type(self.analysis.constraint_handler).__name__
            handler_type = handler_type.replace("ConstraintHandler", "")
            index = self.constraint_type_combo.findText(handler_type, Qt.MatchContains)
            if index >= 0:
                self.constraint_type_combo.setCurrentIndex(index)
                self.constraint_options.setCurrentIndex(index)
                
                # Load constraint handler options
                if isinstance(self.analysis.constraint_handler, PenaltyConstraintHandler):
                    self.penalty_alpha_s.setValue(self.analysis.constraint_handler.alpha_s)
                    self.penalty_alpha_m.setValue(self.analysis.constraint_handler.alpha_m)
                elif isinstance(self.analysis.constraint_handler, LagrangeConstraintHandler):
                    self.lagrange_alpha_s.setValue(self.analysis.constraint_handler.alpha_s)
                    self.lagrange_alpha_m.setValue(self.analysis.constraint_handler.alpha_m)
                elif isinstance(self.analysis.constraint_handler, AutoConstraintHandler):
                    self.auto_verbose.setChecked(self.analysis.constraint_handler.verbose)
                    if self.analysis.constraint_handler.auto_penalty is not None:
                        self.auto_penalty.setValue(self.analysis.constraint_handler.auto_penalty)
                    if self.analysis.constraint_handler.user_penalty is not None:
                        self.user_penalty.setValue(self.analysis.constraint_handler.user_penalty)
        
        # Numberer
        if self.analysis.numberer:
            numberer_type = type(self.analysis.numberer).__name__
            numberer_type = numberer_type.replace("Numberer", "")
            index = self.numberer_type_combo.findText(numberer_type, Qt.MatchContains)
            if index >= 0:
                self.numberer_type_combo.setCurrentIndex(index)
        
        # System
        if self.analysis.system:
            system_type = type(self.analysis.system).__name__
            system_type = system_type.replace("System", "")
            index = self.system_type_combo.findText(system_type, Qt.MatchContains)
            if index >= 0:
                self.system_type_combo.setCurrentIndex(index)
                self.system_options.setCurrentIndex(index)
                
                # Load system options
                if isinstance(self.analysis.system, UmfpackSystem) and self.analysis.system.lvalue_fact is not None:
                    self.umfpack_lvalue.setValue(self.analysis.system.lvalue_fact)
        
        # Test
        if self.analysis.test:
            test_type = type(self.analysis.test).__name__
            test_type = test_type.replace("Test", "")
            index = self.test_type_combo.findText(test_type, Qt.MatchContains)
            if index >= 0:
                self.test_type_combo.setCurrentIndex(index)
                
                # Load test options (common to all tests)
                self.test_tol.setValue(self.analysis.test.tol)
                self.test_max_iter.setValue(self.analysis.test.max_iter)
                self.test_print_flag.setValue(self.analysis.test.print_flag)
                self.test_norm_type.setCurrentIndex(self.analysis.test.norm_type)
        
        # Algorithm
        if self.analysis.algorithm:
            algorithm_type = type(self.analysis.algorithm).__name__
            algorithm_type = algorithm_type.replace("Algorithm", "")
            index = self.algorithm_type_combo.findText(algorithm_type, Qt.MatchContains)
            if index >= 0:
                self.algorithm_type_combo.setCurrentIndex(index)
                self.algorithm_options.setCurrentIndex(index)
                
                # Load algorithm options
                if isinstance(self.analysis.algorithm, LinearAlgorithm):
                    self.linear_initial.setChecked(self.analysis.algorithm.initial)
                    self.linear_factor_once.setChecked(self.analysis.algorithm.factor_once)
                elif isinstance(self.analysis.algorithm, NewtonAlgorithm):
                    self.newton_initial.setChecked(self.analysis.algorithm.initial)
                    self.newton_initial_then_current.setChecked(self.analysis.algorithm.initial_then_current)
                elif isinstance(self.analysis.algorithm, ModifiedNewtonAlgorithm):
                    self.modified_newton_initial.setChecked(self.analysis.algorithm.initial)
        
        # Integrator
        if self.analysis.integrator:
            integrator_type = type(self.analysis.integrator).__name__
            integrator_type = integrator_type.replace("Integrator", "")
            index = self.integrator_type_combo.findText(integrator_type, Qt.MatchContains)
            if index >= 0:
                self.integrator_type_combo.setCurrentIndex(index)
                self.integrator_options.setCurrentIndex(index)
                
                # Load integrator options
                if isinstance(self.analysis.integrator, LoadControlIntegrator):
                    self.load_control_lambda.setValue(self.analysis.integrator.lambda_val)
                    if self.analysis.integrator.num_iter is not None:
                        self.load_control_num_iter.setValue(self.analysis.integrator.num_iter)
                    if self.analysis.integrator.min_lambda is not None:
                        self.load_control_min_lambda.setValue(self.analysis.integrator.min_lambda)
                    if self.analysis.integrator.max_lambda is not None:
                        self.load_control_max_lambda.setValue(self.analysis.integrator.max_lambda)
                elif isinstance(self.analysis.integrator, DisplacementControlIntegrator):
                    self.disp_control_node.setValue(self.analysis.integrator.node)
                    self.disp_control_dof.setValue(self.analysis.integrator.dof)
                    self.disp_control_incr.setValue(self.analysis.integrator.incr)
                    if self.analysis.integrator.num_iter is not None:
                        self.disp_control_num_iter.setValue(self.analysis.integrator.num_iter)
                    if self.analysis.integrator.min_incr is not None:
                        self.disp_control_min_incr.setValue(self.analysis.integrator.min_incr)
                    if self.analysis.integrator.max_incr is not None:
                        self.disp_control_max_incr.setValue(self.analysis.integrator.max_incr)
                elif isinstance(self.analysis.integrator, NewmarkIntegrator):
                    self.newmark_gamma.setValue(self.analysis.integrator.gamma)
                    self.newmark_beta.setValue(self.analysis.integrator.beta)
                elif isinstance(self.analysis.integrator, GeneralizedAlphaIntegrator):
                    self.gen_alpha_alpha_m.setValue(self.analysis.integrator.alpha_m)
                    self.gen_alpha_alpha_f.setValue(self.analysis.integrator.alpha_f)
                    if self.analysis.integrator.gamma is not None:
                        self.gen_alpha_gamma.setValue(self.analysis.integrator.gamma)
                    if self.analysis.integrator.beta is not None:
                        self.gen_alpha_beta.setValue(self.analysis.integrator.beta)
        
        # Update the summary
        self.update_summary()
    
    def prev_tab(self):
        """Go to previous tab"""
        if self.current_tab > 0:
            self.current_tab -= 1
            self.tabs.setCurrentIndex(self.current_tab)
            self.update_navigation()
    
    def next_tab(self):
        """Go to next tab"""
        if self.current_tab < self.tabs.count() - 1:
            self.current_tab += 1
            self.tabs.setCurrentIndex(self.current_tab)
            self.update_navigation()
    
    def update_navigation(self):
        """Update navigation buttons based on current tab"""
        self.prev_btn.setEnabled(self.current_tab > 0)
        self.next_btn.setVisible(self.current_tab < self.tabs.count() - 1)
        self.save_btn.setVisible(self.current_tab == self.tabs.count() - 1)
        
        # If we're on the last tab, update the summary
        if self.current_tab == self.tabs.count() - 1:
            self.update_summary()
    
    def update_summary(self):
        """Update the analysis summary"""
        summary = f"<h3>Analysis: {self.analysis.name} (Tag: {self.analysis.tag})</h3>"
        summary += f"<p><b>Type:</b> {self.analysis_type_combo.currentText()}</p>"
        
        # Constraint Handler
        constraint_type = self.constraint_type_combo.currentText()
        summary += f"<p><b>Constraint Handler:</b> {constraint_type}"
        if constraint_type.lower() == "penalty":
            summary += f" (AlphaS: {self.penalty_alpha_s.value()}, AlphaM: {self.penalty_alpha_m.value()})"
        elif constraint_type.lower() == "lagrange":
            summary += f" (AlphaS: {self.lagrange_alpha_s.value()}, AlphaM: {self.lagrange_alpha_m.value()})"
        summary += "</p>"
        
        # Numberer
        summary += f"<p><b>Numberer:</b> {self.numberer_type_combo.currentText()}</p>"
        
        # System
        system_type = self.system_type_combo.currentText()
        summary += f"<p><b>System:</b> {system_type}"
        if system_type.lower() == "umfpack":
            summary += f" (LValueFact: {self.umfpack_lvalue.value()})"
        summary += "</p>"
        
        # Test
        test_type = self.test_type_combo.currentText()
        summary += f"<p><b>Test:</b> {test_type} "
        summary += f"(Tolerance: {self.test_tol.value()}, MaxIter: {self.test_max_iter.value()}, "
        summary += f"PrintFlag: {self.test_print_flag.value()}, NormType: {self.test_norm_type.currentIndex()})</p>"
        
        # Algorithm
        algorithm_type = self.algorithm_type_combo.currentText()
        summary += f"<p><b>Algorithm:</b> {algorithm_type}"
        if algorithm_type.lower() == "linear":
            flags = []
            if self.linear_initial.isChecked():
                flags.append("-initial")
            if self.linear_factor_once.isChecked():
                flags.append("-factorOnce")
            if flags:
                summary += f" ({' '.join(flags)})"
        elif algorithm_type.lower() == "newton":
            flags = []
            if self.newton_initial.isChecked():
                flags.append("-initial")
            if self.newton_initial_then_current.isChecked():
                flags.append("-initialThenCurrent")
            if flags:
                summary += f" ({' '.join(flags)})"
        elif algorithm_type.lower() == "modifiednewton":
            if self.modified_newton_initial.isChecked():
                summary += " (-initial)"
        summary += "</p>"
        
        # Integrator
        integrator_type = self.integrator_type_combo.currentText()
        summary += f"<p><b>Integrator:</b> {integrator_type}"
        if integrator_type.lower() == "loadcontrol":
            summary += f" (Lambda: {self.load_control_lambda.value()}"
            if self.load_control_num_iter.value() > 0:
                summary += f", NumIter: {self.load_control_num_iter.value()}"
                if self.load_control_min_lambda.isEnabled():
                    summary += f", MinLambda: {self.load_control_min_lambda.value()}"
                    summary += f", MaxLambda: {self.load_control_max_lambda.value()}"
            summary += ")"
        elif integrator_type.lower() == "displacementcontrol":
            summary += f" (Node: {self.disp_control_node.value()}, DOF: {self.disp_control_dof.value()}, "
            summary += f"Increment: {self.disp_control_incr.value()}"
            if self.disp_control_num_iter.value() > 0:
                summary += f", NumIter: {self.disp_control_num_iter.value()}"
                if self.disp_control_min_incr.isEnabled():
                    summary += f", MinIncr: {self.disp_control_min_incr.value()}"
                    summary += f", MaxIncr: {self.disp_control_max_incr.value()}"
            summary += ")"
        elif integrator_type.lower() == "newmark":
            summary += f" (Gamma: {self.newmark_gamma.value()}, Beta: {self.newmark_beta.value()})"
        elif integrator_type.lower() == "generalizedalpha":
            summary += f" (AlphaM: {self.gen_alpha_alpha_m.value()}, AlphaF: {self.gen_alpha_alpha_f.value()}"
            if self.gen_alpha_gamma.value() > 0:
                summary += f", Gamma: {self.gen_alpha_gamma.value()}"
            if self.gen_alpha_beta.value() > 0:
                summary += f", Beta: {self.gen_alpha_beta.value()}"
            summary += ")"
        summary += "</p>"
        
        # Control
        summary += f"<p><b>Analysis Control:</b> {self.num_steps_spin.value()} steps"
        if self.analysis_type_combo.currentText() != "Static":
            summary += f", dt={self.time_step_spin.value()}"
        summary += "</p>"
        
        self.summary_text.setText(summary)
    
    def accept(self):
        """Save the analysis configuration"""
        try:
            # Analysis type
            self.analysis.set_type(self.analysis_type_combo.currentText())
            
            # Constraint handler
            constraint_type = self.constraint_type_combo.currentText().lower()
            if constraint_type == "plain":
                self.analysis.set_constraint_handler("plain")
            elif constraint_type == "transformation":
                self.analysis.set_constraint_handler("transformation")
            elif constraint_type == "penalty":
                self.analysis.set_constraint_handler("penalty", 
                                                   alpha_s=self.penalty_alpha_s.value(),
                                                   alpha_m=self.penalty_alpha_m.value())
            elif constraint_type == "lagrange":
                self.analysis.set_constraint_handler("lagrange", 
                                                   alpha_s=self.lagrange_alpha_s.value(),
                                                   alpha_m=self.lagrange_alpha_m.value())
            elif constraint_type == "auto":
                self.analysis.set_constraint_handler("auto", 
                                                   verbose=self.auto_verbose.isChecked(),
                                                   auto_penalty=self.auto_penalty.value(),
                                                   user_penalty=self.user_penalty.value())
            
            # Numberer
            numberer_type = self.numberer_type_combo.currentText().lower()
            self.analysis.set_numberer(numberer_type)
            
            # System
            system_type = self.system_type_combo.currentText().lower()
            if system_type == "umfpack":
                self.analysis.set_system(system_type, lvalue_fact=self.umfpack_lvalue.value())
            else:
                self.analysis.set_system(system_type)
            
            # Test
            test_type = self.test_type_combo.currentText().lower()
            self.analysis.set_test(test_type, 
                                  tol=self.test_tol.value(),
                                  max_iter=self.test_max_iter.value(),
                                  print_flag=self.test_print_flag.value(),
                                  norm_type=self.test_norm_type.currentIndex())
            
            # Algorithm
            algorithm_type = self.algorithm_type_combo.currentText().lower()
            if algorithm_type == "linear":
                self.analysis.set_algorithm(algorithm_type, 
                                           initial=self.linear_initial.isChecked(),
                                           factor_once=self.linear_factor_once.isChecked())
            elif algorithm_type == "newton":
                self.analysis.set_algorithm(algorithm_type, 
                                           initial=self.newton_initial.isChecked(),
                                           initial_then_current=self.newton_initial_then_current.isChecked())
            elif algorithm_type == "modifiednewton":
                self.analysis.set_algorithm(algorithm_type, 
                                           initial=self.modified_newton_initial.isChecked())
            
            # Integrator
            integrator_type = self.integrator_type_combo.currentText().lower()
            if integrator_type == "loadcontrol":
                kwargs = {
                    'lambda_val': self.load_control_lambda.value()
                }
                if self.load_control_num_iter.value() > 0:
                    kwargs['num_iter'] = self.load_control_num_iter.value()
                    if self.load_control_min_lambda.isEnabled():
                        kwargs['min_lambda'] = self.load_control_min_lambda.value()
                        kwargs['max_lambda'] = self.load_control_max_lambda.value()
                self.analysis.set_integrator(integrator_type, **kwargs)
            elif integrator_type == "displacementcontrol":
                kwargs = {
                    'node': self.disp_control_node.value(),
                    'dof': self.disp_control_dof.value(),
                    'incr': self.disp_control_incr.value()
                }
                if self.disp_control_num_iter.value() > 0:
                    kwargs['num_iter'] = self.disp_control_num_iter.value()
                    if self.disp_control_min_incr.isEnabled():
                        kwargs['min_incr'] = self.disp_control_min_incr.value()
                        kwargs['max_incr'] = self.disp_control_max_incr.value()
                self.analysis.set_integrator(integrator_type, **kwargs)
            elif integrator_type == "newmark":
                self.analysis.set_integrator(integrator_type, 
                                           gamma=self.newmark_gamma.value(),
                                           beta=self.newmark_beta.value())
            elif integrator_type == "generalizedalpha":
                kwargs = {
                    'alpha_m': self.gen_alpha_alpha_m.value(),
                    'alpha_f': self.gen_alpha_alpha_f.value()
                }
                if self.gen_alpha_gamma.value() > 0:
                    kwargs['gamma'] = self.gen_alpha_gamma.value()
                if self.gen_alpha_beta.value() > 0:
                    kwargs['beta'] = self.gen_alpha_beta.value()
                self.analysis.set_integrator(integrator_type, **kwargs)
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# Run tab for executing the analysis
class AnalysisRunTab(QWidget):
    """
    Widget for running an analysis
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analysis_manager = AnalysisManager()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Analysis selection
        select_group = QGroupBox("Select Analysis")
        select_layout = QHBoxLayout(select_group)
        
        self.analysis_combo = QComboBox()
        self.refresh_analysis_list()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_analysis_list)
        
        select_layout.addWidget(QLabel("Analysis:"))
        select_layout.addWidget(self.analysis_combo, stretch=1)
        select_layout.addWidget(refresh_btn)
        
        layout.addWidget(select_group)
        
        # Analysis details
        details_group = QGroupBox("Analysis Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_label = QLabel("No analysis selected")
        self.details_label.setWordWrap(True)
        self.details_label.setTextFormat(Qt.RichText)
        details_layout.addWidget(self.details_label)
        
        layout.addWidget(details_group)
        
        # Run controls
        run_group = QGroupBox("Run Controls")
        run_layout = QFormLayout(run_group)
        
        self.num_steps_spin = QSpinBox()
        self.num_steps_spin.setRange(1, 10000)
        self.num_steps_spin.setValue(10)
        run_layout.addRow("Number of Steps:", self.num_steps_spin)
        
        self.time_step_spin = QDoubleSpinBox()
        self.time_step_spin.setRange(0.00001, 10.0)
        self.time_step_spin.setValue(0.01)
        self.time_step_spin.setDecimals(5)
        run_layout.addRow("Time Step (dt):", self.time_step_spin)
        
        self.run_btn = QPushButton("Run Analysis")
        self.run_btn.clicked.connect(self.run_analysis)
        run_layout.addRow("", self.run_btn)
        
        layout.addWidget(run_group)
        
        # Connect analysis selection to update details
        self.analysis_combo.currentIndexChanged.connect(self.update_details)
        
    def refresh_analysis_list(self):
        """Refresh the analysis list"""
        self.analysis_combo.clear()
        analyses = self.analysis_manager.get_all_analyses()
        
        for tag, analysis in analyses.items():
            self.analysis_combo.addItem(f"{analysis.name} (Tag: {tag})", analysis)
        
        self.update_details()
    
    def update_details(self):
        """Update the analysis details"""
        analysis = self.analysis_combo.currentData()
        
        if analysis:
            # Enable/disable time step based on analysis type
            is_static = analysis.analysis_type == "Static"
            self.time_step_spin.setVisible(not is_static)
            self.time_step_spin.setEnabled(not is_static)
            
            # Update the details
            details = str(analysis).replace("\n", "<br>")
            self.details_label.setText(details)
            self.run_btn.setEnabled(True)
        else:
            self.details_label.setText("No analysis selected")
            self.run_btn.setEnabled(False)
    
    def run_analysis(self):
        """Run the selected analysis"""
        analysis = self.analysis_combo.currentData()
        
        if not analysis:
            return
        
        try:
            num_steps = self.num_steps_spin.value()
            dt = self.time_step_spin.value() if analysis.analysis_type != "Static" else None
            
            # Run the analysis
            result = analysis.analyze(num_steps, dt)
            
            if result:
                QMessageBox.information(self, "Success", "Analysis completed successfully!")
            else:
                QMessageBox.warning(self, "Warning", "Analysis completed with warnings. Check the console for details.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = AnalysisManagerTab()
    window.show()
    sys.exit(app.exec_())