from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout, QTabWidget,
    QGroupBox, QWizard, QWizardPage, QSpinBox, QDoubleSpinBox, 
    QRadioButton, QCheckBox
)

from meshmaker.components.Analysis.analysis import Analysis, AnalysisManager
from meshmaker.components.Analysis.constraint_handlersGUI import ConstraintHandlerManagerTab
from meshmaker.components.Analysis.integratorsGUI import IntegratorManagerTab
from meshmaker.components.Analysis.algorithmsGUI import AlgorithmManagerTab
from meshmaker.components.Analysis.systemsGUI import SystemManagerTab
from meshmaker.components.Analysis.numberersGUI import NumbererManagerTab
from meshmaker.components.Analysis.convergenceTestsGUI import TestManagerTab

from meshmaker.components.Analysis.constraint_handlers import ConstraintHandlerManager
from meshmaker.components.Analysis.numberers import NumbererManager
from meshmaker.components.Analysis.systems import SystemManager
from meshmaker.components.Analysis.algorithms import AlgorithmManager
from meshmaker.components.Analysis.convergenceTests import TestManager
from meshmaker.components.Analysis.integrators import IntegratorManager, StaticIntegrator, TransientIntegrator


class AnalysisManagerDialog(QDialog):
    """
    Main dialog for managing analyses
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analysis Manager")
        self.resize(900, 600)
        
        # Get the analysis manager instance
        self.analysis_manager = AnalysisManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Header with title and create button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Manage Analysis Definitions"))
        create_btn = QPushButton("Create New Analysis")
        create_btn.clicked.connect(self.create_new_analysis)
        header_layout.addWidget(create_btn)
        layout.addLayout(header_layout)
        
        # Analyses table
        self.analyses_table = QTableWidget()
        self.analyses_table.setColumnCount(6)  # Select, Tag, Name, Type, Steps/Time, Components
        self.analyses_table.setHorizontalHeaderLabels([
            "Select", "Tag", "Name", "Type", "Steps/Time", "Components"
        ])
        self.analyses_table.setSelectionBehavior(QTableWidget.SelectRows)
        header = self.analyses_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.analyses_table)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_analysis)
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected_analysis)
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_analyses_list)
        
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(refresh_btn)
        layout.addLayout(buttons_layout)
        
        # Initial refresh
        self.refresh_analyses_list()
        
        # Disable edit/delete buttons initially
        self.update_button_state()

    def refresh_analyses_list(self):
        """Update the analyses table with current analyses"""
        self.analyses_table.setRowCount(0)
        analyses = self.analysis_manager.get_all_analyses()
        
        self.analyses_table.setRowCount(len(analyses))
        self.radio_buttons = []
        
        # Hide vertical header
        self.analyses_table.verticalHeader().setVisible(False)
        
        for row, (tag, analysis) in enumerate(analyses.items()):
            # Select radio button
            radio_btn = QRadioButton()
            radio_btn.toggled.connect(lambda checked, btn=radio_btn: self.on_radio_toggled(checked, btn))
            self.radio_buttons.append(radio_btn)
            
            radio_cell = QWidget()
            radio_layout = QHBoxLayout(radio_cell)
            radio_layout.addWidget(radio_btn)
            radio_layout.setAlignment(Qt.AlignCenter)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            self.analyses_table.setCellWidget(row, 0, radio_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.analyses_table.setItem(row, 1, tag_item)
            
            # Name
            name_item = QTableWidgetItem(analysis.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.analyses_table.setItem(row, 2, name_item)
            
            # Analysis Type
            type_item = QTableWidgetItem(analysis.analysis_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.analyses_table.setItem(row, 3, type_item)
            
            # Steps/Time
            if analysis.num_steps is not None:
                steps_time = f"{analysis.num_steps} steps"
            elif analysis.final_time is not None:
                steps_time = f"t={analysis.final_time}"
            else:
                steps_time = "N/A"
            steps_item = QTableWidgetItem(steps_time)
            steps_item.setFlags(steps_item.flags() & ~Qt.ItemIsEditable)
            self.analyses_table.setItem(row, 4, steps_item)
            
            # Components summary
            components = []
            if analysis.constraint_handler:
                components.append(f"CH: {analysis.constraint_handler.handler_type}")
            if analysis.integrator:
                components.append(f"Int: {analysis.integrator.integrator_type}")
            
            components_str = ", ".join(components)
            components_item = QTableWidgetItem(components_str)
            components_item.setFlags(components_item.flags() & ~Qt.ItemIsEditable)
            self.analyses_table.setItem(row, 5, components_item)
        
        self.update_button_state()
        
    def on_radio_toggled(self, checked, btn):
        """Handle radio button toggling to ensure mutual exclusivity"""
        if checked:
            # Uncheck all other radio buttons
            for radio_btn in self.radio_buttons:
                if radio_btn != btn and radio_btn.isChecked():
                    radio_btn.setChecked(False)
        self.update_button_state()

    def update_button_state(self):
        """Enable/disable edit and delete buttons based on selection"""
        enable_buttons = any(rb.isChecked() for rb in self.radio_buttons) if hasattr(self, 'radio_buttons') else False
        self.edit_btn.setEnabled(enable_buttons)
        self.delete_btn.setEnabled(enable_buttons)

    def get_selected_analysis_tag(self):
        """Get the tag of the selected analysis"""
        for row, radio_btn in enumerate(self.radio_buttons):
            if radio_btn.isChecked():
                tag_item = self.analyses_table.item(row, 1)
                return int(tag_item.text())
        return None

    def create_new_analysis(self):
        """Open wizard to create a new analysis"""
        wizard = AnalysisWizard(self)
        if wizard.exec() == QWizard.Accepted and wizard.created_analysis:
            self.refresh_analyses_list()

    def edit_selected_analysis(self):
        """Edit the selected analysis"""
        tag = self.get_selected_analysis_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select an analysis to edit")
            return
        
        try:
            analysis = self.analysis_manager.get_analysis(tag)
            wizard = AnalysisWizard(self, analysis)
            if wizard.exec() == QWizard.Accepted:
                self.refresh_analyses_list()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected_analysis(self):
        """Delete the selected analysis"""
        tag = self.get_selected_analysis_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select an analysis to delete")
            return
        
        reply = QMessageBox.question(
            self, 'Delete Analysis',
            f"Are you sure you want to delete analysis with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.analysis_manager.remove_analysis(tag)
                self.refresh_analyses_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


class AnalysisWizard(QWizard):
    """
    Simplified wizard for creating/editing an analysis
    """
    def __init__(self, parent=None, analysis=None):
        super().__init__(parent)
        
        self.analysis = analysis
        self.created_analysis = None
        
        if analysis:
            self.setWindowTitle(f"Edit Analysis: {analysis.name}")
        else:
            self.setWindowTitle("Create New Analysis")
            
        self.resize(800, 600)
        
        # Initialize manager instances
        self.analysis_manager = AnalysisManager()
        self.constraint_handler_manager = ConstraintHandlerManager()
        self.numberer_manager = NumbererManager()
        self.system_manager = SystemManager()
        self.algorithm_manager = AlgorithmManager()
        self.test_manager = TestManager()
        self.integrator_manager = IntegratorManager()
        
        # Set wizard style
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Add pages
        self.addPage(BasicInfoPage(self))
        self.addPage(ComponentsPage(self))
        self.addPage(ParametersPage(self))
        self.addPage(SummaryPage(self))
        
        # Set options
        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.HaveFinishButtonOnEarlyPages, False)
        self.setOption(QWizard.HaveNextButtonOnLastPage, False)
        self.setOption(QWizard.HaveHelpButton, False)
        
        # Connect signals
        self.finished.connect(self.on_wizard_finished)
        
    def on_wizard_finished(self, result):
        """Handle wizard completion"""
        if result == QWizard.Accepted:
            try:
                # Collect parameters
                name = self.field("name")
                analysis_type = self.field("analysis_type")
                
                # Get components 
                constraint_handler_tag = self.field("constraint_handler_tag")
                constraint_handler = self.constraint_handler_manager.get_handler(constraint_handler_tag)
                
                numberer_type = self.field("numberer_type")
                numberer = self.numberer_manager.get_numberer(numberer_type)
                
                system_tag = self.field("system_tag")
                system = self.system_manager.get_system(system_tag)
                
                algorithm_tag = self.field("algorithm_tag")
                algorithm = self.algorithm_manager.get_algorithm(algorithm_tag)
                
                test_tag = self.field("test_tag")
                test = self.test_manager.get_test(test_tag)
                
                integrator_tag = self.field("integrator_tag")
                integrator = self.integrator_manager.get_integrator(integrator_tag)
                
                # Get analysis parameters
                use_num_steps = self.field("use_num_steps")
                
                num_steps = None
                final_time = None
                
                if use_num_steps:
                    num_steps = self.field("num_steps")
                else:
                    final_time = self.field("final_time")
                
                dt = None
                dt_min = None
                dt_max = None
                jd = None
                num_sublevels = None
                num_substeps = None
                
                if analysis_type != "Static":
                    dt = self.field("dt")
                    
                    if analysis_type == "VariableTransient":
                        dt_min = self.field("dt_min")
                        dt_max = self.field("dt_max")
                        jd = self.field("jd")
                
                use_substepping = self.field("use_substepping")
                if use_substepping and analysis_type != "Static":
                    num_sublevels = self.field("num_sublevels")
                    num_substeps = self.field("num_substeps")
                
                if self.analysis:
                    # Update existing analysis
                    self.update_analysis(name, constraint_handler, numberer, system, algorithm, 
                                      test, integrator, num_steps, final_time, dt,
                                      dt_min, dt_max, jd, num_sublevels, num_substeps)
                    QMessageBox.information(self, "Success", f"Analysis '{name}' updated successfully!")
                else:
                    # Create new analysis
                    self.created_analysis = self.analysis_manager.create_analysis(
                        name=name,
                        analysis_type=analysis_type,
                        constraint_handler=constraint_handler,
                        numberer=numberer,
                        system=system,
                        algorithm=algorithm,
                        test=test,
                        integrator=integrator,
                        num_steps=num_steps,
                        final_time=final_time,
                        dt=dt,
                        dt_min=dt_min,
                        dt_max=dt_max,
                        jd=jd,
                        num_sublevels=num_sublevels,
                        num_substeps=num_substeps
                    )
                    QMessageBox.information(self, "Success", f"Analysis '{name}' created successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create/update analysis: {str(e)}")
                
    def update_analysis(self, name, constraint_handler, numberer, system, algorithm, 
                    test, integrator, num_steps, final_time, dt,
                    dt_min, dt_max, jd, num_sublevels, num_substeps):
        """Update an existing analysis"""
        # Check if name changed and is not a duplicate
        if name != self.analysis.name and name in Analysis._names:
            raise ValueError(f"Analysis name '{name}' is already in use. Names must be unique.")
        
        # Update analysis components
        self.analysis_manager.update_constraint_handler(self.analysis, constraint_handler)
        self.analysis.numberer = numberer
        self.analysis_manager.update_system(self.analysis, system)
        self.analysis_manager.update_algorithm(self.analysis, algorithm)
        self.analysis_manager.update_test(self.analysis, test)
        self.analysis_manager.update_integrator(self.analysis, integrator)
        
        # Update analysis parameters
        if name != self.analysis.name:
            Analysis._names.remove(self.analysis.name)
            self.analysis.name = name
            Analysis._names.add(name)
        
        self.analysis.num_steps = num_steps
        self.analysis.final_time = final_time
        self.analysis.dt = dt
        self.analysis.dt_min = dt_min
        self.analysis.dt_max = dt_max
        self.analysis.jd = jd
        self.analysis.num_sublevels = num_sublevels
        self.analysis.num_substeps = num_substeps


class BasicInfoPage(QWizardPage):
    """First page for basic analysis information"""
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Analysis Basic Information")
        self.setSubTitle("Enter the basic information for the analysis.")
        
        layout = QFormLayout(self)
        
        # Name field
        self.name_edit = QLineEdit()
        if parent.analysis:
            self.name_edit.setText(parent.analysis.name)
        layout.addRow("Analysis Name:", self.name_edit)
        
        # Analysis type
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["Static", "Transient", "VariableTransient"])
        if parent.analysis:
            index = self.analysis_type_combo.findText(parent.analysis.analysis_type)
            if index >= 0:
                self.analysis_type_combo.setCurrentIndex(index)
            # Disable changing analysis type in edit mode
            self.analysis_type_combo.setEnabled(False)
        layout.addRow("Analysis Type:", self.analysis_type_combo)
        
        # Description box
        self.description_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(self.description_group)
        
        self.static_desc = QLabel("Static: Used for problems where inertial and damping effects are not considered.")
        self.transient_desc = QLabel("Transient: Used for dynamic analysis where inertial and damping effects are considered.")
        self.var_trans_desc = QLabel("Variable Transient: Like Transient, but with adaptive time steps based on convergence.")
        
        desc_layout.addWidget(self.static_desc)
        desc_layout.addWidget(self.transient_desc)
        desc_layout.addWidget(self.var_trans_desc)
        
        layout.addRow(self.description_group)
        
        # Update descriptions when analysis type changes
        self.analysis_type_combo.currentTextChanged.connect(self.update_description)
        
        # Register fields
        self.registerField("name*", self.name_edit)
        self.registerField("analysis_type", self.analysis_type_combo, "currentText")
        
        # Initial update
        self.update_description(self.analysis_type_combo.currentText())
        
    def update_description(self, analysis_type):
        """Update the description based on selected analysis type"""
        self.static_desc.setVisible(analysis_type == "Static")
        self.transient_desc.setVisible(analysis_type == "Transient")
        self.var_trans_desc.setVisible(analysis_type == "VariableTransient")
        
    def validatePage(self):
        """Validate the page before proceeding"""
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a name for the analysis.")
            return False
        
        # Check for duplicate name, but allow keeping the same name in edit mode
        wizard = self.wizard()
        if name in Analysis._names and (not wizard.analysis or wizard.analysis.name != name):
            QMessageBox.warning(self, "Validation Error", f"Analysis name '{name}' is already in use. Names must be unique.")
            return False
        
        return True


class ComponentsPage(QWizardPage):
    """Page for selecting all the components of the analysis"""
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Analysis Components")
        self.setSubTitle("Select the components for the analysis.")
        
        layout = QVBoxLayout(self)
        
        # Create tabbed interface for the components
        self.tabs = QTabWidget()
        
        # Add tabs for each component
        self.tabs.addTab(self.create_constraint_handler_tab(), "Constraint Handler")
        self.tabs.addTab(self.create_numberer_tab(), "Numberer")
        self.tabs.addTab(self.create_system_tab(), "System")
        self.tabs.addTab(self.create_algorithm_tab(), "Algorithm")
        self.tabs.addTab(self.create_test_tab(), "Test")
        self.tabs.addTab(self.create_integrator_tab(), "Integrator")
        
        layout.addWidget(self.tabs)
        
    def create_constraint_handler_tab(self):
        """Create the constraint handler selection tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Use an embedded ConstraintHandlerManagerTab for selection
        self.constraint_handler_manager_tab = ConstraintHandlerManagerTab()
        layout.addWidget(self.constraint_handler_manager_tab)
        
        # Register fields
        self.registerField("constraint_handler_tag", self, "selectedHandlerTag")
        
        return tab
    
    def create_numberer_tab(self):
        """Create the numberer selection tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Use an embedded NumbererManagerTab for selection
        self.numberer_manager_tab = NumbererManagerTab()
        layout.addWidget(self.numberer_manager_tab)
        
        # Register fields
        self.registerField("numberer_type", self, "selectedNumbererType")
        
        return tab
    
    def create_system_tab(self):
        """Create the system selection tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Use an embedded SystemManagerTab for selection
        self.system_manager_tab = SystemManagerTab()
        layout.addWidget(self.system_manager_tab)
        
        # Register fields
        self.registerField("system_tag", self, "selectedSystemTag")
        
        return tab
    
    def create_algorithm_tab(self):
        """Create the algorithm selection tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Use an embedded AlgorithmManagerTab for selection
        self.algorithm_manager_tab = AlgorithmManagerTab()
        layout.addWidget(self.algorithm_manager_tab)
        
        # Register fields
        self.registerField("algorithm_tag", self, "selectedAlgorithmTag")
        
        return tab
    
    def create_test_tab(self):
        """Create the test selection tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Use an embedded TestManagerTab for selection
        self.test_manager_tab = TestManagerTab()
        layout.addWidget(self.test_manager_tab)
        
        # Register fields
        self.registerField("test_tag", self, "selectedTestTag")
        
        return tab
    
    def create_integrator_tab(self):
        """Create the integrator selection tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Use an embedded IntegratorManagerTab for selection
        self.integrator_manager_tab = IntegratorManagerTab()
        layout.addWidget(self.integrator_manager_tab)
        
        # Register fields
        self.registerField("integrator_tag", self, "selectedIntegratorTag")
        
        return tab
    
    def selectedHandlerTag(self):
        """Get selected constraint handler tag"""
        # Get the tag from constraint handler tab
        return self.constraint_handler_manager_tab.get_selected_handler_tag()
    
    def selectedNumbererType(self):
        """Get selected numberer type"""
        # Extract selection from numberer tab
        selected_btn = self.numberer_manager_tab.numberer_buttons.checkedButton()
        if selected_btn:
            return selected_btn.text().lower()
        return None
    
    def selectedSystemTag(self):
        """Get selected system tag"""
        return self.system_manager_tab.get_selected_system_tag()
    
    def selectedAlgorithmTag(self):
        """Get selected algorithm tag"""
        return self.algorithm_manager_tab.get_selected_algorithm_tag()
    
    def selectedTestTag(self):
        """Get selected test tag"""
        return self.test_manager_tab.get_selected_test_tag()
    
    def selectedIntegratorTag(self):
        """Get selected integrator tag"""
        return self.integrator_manager_tab.get_selected_integrator_tag()
    
    def validatePage(self):
        """Validate that all components are selected"""
        wizard = self.wizard()
        errors = []
        
        # Check constraint handler
        if not self.selectedHandlerTag():
            errors.append("Constraint Handler")
            
        # Check numberer
        if not self.selectedNumbererType():
            errors.append("Numberer")
            
        # Check system
        if not self.selectedSystemTag():
            errors.append("System")
            
        # Check algorithm
        if not self.selectedAlgorithmTag():
            errors.append("Algorithm")
            
        # Check test
        if not self.selectedTestTag():
            errors.append("Convergence Test")
            
        # Check integrator
        if not self.selectedIntegratorTag():
            errors.append("Integrator")
        else:
            # Check integrator compatibility with analysis type
            analysis_type = wizard.field("analysis_type")
            integrator = wizard.integrator_manager.get_integrator(self.selectedIntegratorTag())
            
            if analysis_type == "Static" and not isinstance(integrator, StaticIntegrator):
                QMessageBox.warning(self, "Validation Error", 
                                   f"Static analysis requires a static integrator. {integrator.integrator_type} is not compatible.")
                return False
                
            elif analysis_type in ["Transient", "VariableTransient"] and not isinstance(integrator, TransientIntegrator):
                QMessageBox.warning(self, "Validation Error", 
                                   f"Transient analysis requires a transient integrator. {integrator.integrator_type} is not compatible.")
                return False
        
        if errors:
            QMessageBox.warning(self, "Validation Error", 
                               f"Please select the following components: {', '.join(errors)}")
            return False
            
        return True


class ParametersPage(QWizardPage):
    """Page for analysis parameters"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setTitle("Analysis Parameters")
        self.setSubTitle("Configure the parameters for the analysis.")
        
        self.layout = QVBoxLayout(self)
        
    def initializePage(self):
        """Initialize page when it becomes active"""
        # Clear existing widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        analysis_type = self.wizard().field("analysis_type")
        
        # Time Step Control
        time_step_group = QGroupBox("Analysis Time/Steps")
        time_layout = QFormLayout(time_step_group)
        
        # Option to use number of steps or final time
        self.steps_radio = QRadioButton("Specify Number of Steps")
        self.time_radio = QRadioButton("Specify Final Time")
        
        time_option_layout = QHBoxLayout()
        time_option_layout.addWidget(self.steps_radio)
        time_option_layout.addWidget(self.time_radio)
        time_layout.addRow(time_option_layout)
        
        # Number of steps
        self.num_steps_spin = QSpinBox()
        self.num_steps_spin.setRange(1, 100000)
        self.num_steps_spin.setValue(10)
        time_layout.addRow("Number of Steps:", self.num_steps_spin)
        
        # Final time
        self.final_time_spin = QDoubleSpinBox()
        self.final_time_spin.setDecimals(6)
        self.final_time_spin.setRange(0.000001, 10000)
        self.final_time_spin.setValue(1.0)
        time_layout.addRow("Final Time:", self.final_time_spin)
        
        # Connect radio buttons to enable/disable fields
        self.steps_radio.toggled.connect(lambda checked: self.num_steps_spin.setEnabled(checked))
        self.time_radio.toggled.connect(lambda checked: self.final_time_spin.setEnabled(checked))
        
        # Default checked state
        analysis = self.wizard().analysis
        if analysis and analysis.num_steps is not None:
            self.steps_radio.setChecked(True)
            self.num_steps_spin.setValue(analysis.num_steps)
            self.final_time_spin.setEnabled(False)
        elif analysis and analysis.final_time is not None:
            self.time_radio.setChecked(True)
            self.final_time_spin.setValue(analysis.final_time)
            self.num_steps_spin.setEnabled(False)
        else:
            self.steps_radio.setChecked(True)
            self.final_time_spin.setEnabled(False)
        
        self.layout.addWidget(time_step_group)
        
        # For Transient analyses, add time step parameters
        if analysis_type in ["Transient", "VariableTransient"]:
            transient_group = QGroupBox("Time Step Parameters")
            transient_layout = QFormLayout(transient_group)
            
            # Time step
            self.dt_spin = QDoubleSpinBox()
            self.dt_spin.setDecimals(6)
            self.dt_spin.setRange(0.000001, 10000)
            self.dt_spin.setValue(0.01)
            transient_layout.addRow("Time Step (dt):", self.dt_spin)
            
            # Set value from editing analysis
            if analysis and analysis.dt is not None:
                self.dt_spin.setValue(analysis.dt)
            
            # For VariableTransient, add specific parameters
            if analysis_type == "VariableTransient":
                self.dt_min_spin = QDoubleSpinBox()
                self.dt_min_spin.setDecimals(6)
                self.dt_min_spin.setRange(0.000001, 10000)
                self.dt_min_spin.setValue(0.001)
                transient_layout.addRow("Minimum Time Step:", self.dt_min_spin)
                
                self.dt_max_spin = QDoubleSpinBox()
                self.dt_max_spin.setDecimals(6)
                self.dt_max_spin.setRange(0.000001, 10000)
                self.dt_max_spin.setValue(0.1)
                transient_layout.addRow("Maximum Time Step:", self.dt_max_spin)
                
                self.jd_spin = QSpinBox()
                self.jd_spin.setRange(1, 100)
                self.jd_spin.setValue(2)
                transient_layout.addRow("J-Steps (jd):", self.jd_spin)
                
                # Set values from editing analysis
                if analysis and analysis.dt_min is not None:
                    self.dt_min_spin.setValue(analysis.dt_min)
                if analysis and analysis.dt_max is not None:
                    self.dt_max_spin.setValue(analysis.dt_max)
                if analysis and analysis.jd is not None:
                    self.jd_spin.setValue(analysis.jd)
            
            # Sub-stepping parameters for Transient/VariableTransient
            self.substep_group = QGroupBox("Sub-stepping Options")
            self.substep_group.setCheckable(True)
            self.substep_group.setChecked(False)
            substep_layout = QFormLayout(self.substep_group)
            
            self.num_sublevels_spin = QSpinBox()
            self.num_sublevels_spin.setRange(1, 10)
            self.num_sublevels_spin.setValue(1)
            substep_layout.addRow("Number of Sub-levels:", self.num_sublevels_spin)
            
            self.num_substeps_spin = QSpinBox()
            self.num_substeps_spin.setRange(1, 100)
            self.num_substeps_spin.setValue(10)
            substep_layout.addRow("Number of Sub-steps per level:", self.num_substeps_spin)
            
            # Set values from editing analysis
            if analysis and analysis.num_sublevels is not None:
                self.substep_group.setChecked(True)
                self.num_sublevels_spin.setValue(analysis.num_sublevels)
            if analysis and analysis.num_substeps is not None:
                self.num_substeps_spin.setValue(analysis.num_substeps)
                
            transient_layout.addRow(self.substep_group)
            
            self.layout.addWidget(transient_group)
        
        # Register fields
        self.registerField("use_num_steps", self.steps_radio)
        self.registerField("num_steps", self.num_steps_spin)
        self.registerField("final_time", self.final_time_spin)
        
        if analysis_type in ["Transient", "VariableTransient"]:
            self.registerField("dt", self.dt_spin)
            
            if analysis_type == "VariableTransient":
                self.registerField("dt_min", self.dt_min_spin)
                self.registerField("dt_max", self.dt_max_spin)
                self.registerField("jd", self.jd_spin)
            
            self.registerField("use_substepping", self.substep_group, "checked")
            self.registerField("num_sublevels", self.num_sublevels_spin)
            self.registerField("num_substeps", self.num_substeps_spin)
    
    def validatePage(self):
        """Validate input parameters"""
        analysis_type = self.wizard().field("analysis_type")
        
        # Validate time step/final time
        if self.steps_radio.isChecked():
            if self.num_steps_spin.value() <= 0:
                QMessageBox.warning(self, "Validation Error", "Number of steps must be greater than 0.")
                return False
        else:  # final time selected
            if self.final_time_spin.value() <= 0:
                QMessageBox.warning(self, "Validation Error", "Final time must be greater than 0.")
                return False
        
        # Validate time step for Transient/VariableTransient
        if analysis_type in ["Transient", "VariableTransient"]:
            if self.dt_spin.value() <= 0:
                QMessageBox.warning(self, "Validation Error", "Time step (dt) must be greater than 0.")
                return False
            
            # Validate VariableTransient specific parameters
            if analysis_type == "VariableTransient":
                if self.dt_min_spin.value() <= 0:
                    QMessageBox.warning(self, "Validation Error", "Minimum time step must be greater than 0.")
                    return False
                if self.dt_max_spin.value() <= 0:
                    QMessageBox.warning(self, "Validation Error", "Maximum time step must be greater than 0.")
                    return False
                if self.dt_min_spin.value() > self.dt_max_spin.value():
                    QMessageBox.warning(self, "Validation Error", "Minimum time step cannot be greater than maximum time step.")
                    return False
                if self.dt_spin.value() < self.dt_min_spin.value() or self.dt_spin.value() > self.dt_max_spin.value():
                    QMessageBox.warning(self, "Validation Error", "Initial time step must be between minimum and maximum time step.")
                    return False
        
        return True


class SummaryPage(QWizardPage):
    """Final summary page for the analysis"""
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("Analysis Summary")
        self.setSubTitle("Review your analysis configuration before creating/updating it.")
        
        self.layout = QVBoxLayout(self)
        
    def initializePage(self):
        """Initialize page when it becomes active"""
        # Clear existing widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get all parameters from wizard fields
        wizard = self.wizard()
        name = wizard.field("name")
        analysis_type = wizard.field("analysis_type")
        
        # Create summary group
        summary_group = QGroupBox("Analysis Configuration")
        summary_layout = QVBoxLayout(summary_group)
        
        # Format summary
        summary_text = f"<b>Name:</b> {name}<br>"
        summary_text += f"<b>Analysis Type:</b> {analysis_type}<br><br>"
        
        # Add component information 
        constraint_handler_tag = wizard.field("constraint_handler_tag")
        constraint_handler = wizard.constraint_handler_manager.get_handler(constraint_handler_tag)
        summary_text += f"<b>Constraint Handler:</b> {constraint_handler.handler_type} (Tag: {constraint_handler_tag})<br>"
        
        numberer_type = wizard.field("numberer_type")
        summary_text += f"<b>Numberer:</b> {numberer_type.capitalize()}<br>"
        
        system_tag = wizard.field("system_tag")
        system = wizard.system_manager.get_system(system_tag)
        summary_text += f"<b>System:</b> {system.system_type} (Tag: {system_tag})<br>"
        
        algorithm_tag = wizard.field("algorithm_tag")
        algorithm = wizard.algorithm_manager.get_algorithm(algorithm_tag)
        summary_text += f"<b>Algorithm:</b> {algorithm.algorithm_type} (Tag: {algorithm_tag})<br>"
        
        test_tag = wizard.field("test_tag")
        test = wizard.test_manager.get_test(test_tag)
        summary_text += f"<b>Convergence Test:</b> {test.test_type} (Tag: {test_tag})<br>"
        
        integrator_tag = wizard.field("integrator_tag")
        integrator = wizard.integrator_manager.get_integrator(integrator_tag)
        summary_text += f"<b>Integrator:</b> {integrator.integrator_type} (Tag: {integrator_tag})<br><br>"
        
        # Add analysis parameters
        use_num_steps = wizard.field("use_num_steps")
        if use_num_steps:
            num_steps = wizard.field("num_steps")
            summary_text += f"<b>Number of Steps:</b> {num_steps}<br>"
        else:
            final_time = wizard.field("final_time")
            summary_text += f"<b>Final Time:</b> {final_time}<br>"
        
        # For Transient and VariableTransient
        if analysis_type in ["Transient", "VariableTransient"]:
            dt = wizard.field("dt")
            summary_text += f"<b>Time Step (dt):</b> {dt}<br>"
            
            # For VariableTransient
            if analysis_type == "VariableTransient":
                dt_min = wizard.field("dt_min")
                dt_max = wizard.field("dt_max")
                jd = wizard.field("jd")
                summary_text += f"<b>Minimum Time Step:</b> {dt_min}<br>"
                summary_text += f"<b>Maximum Time Step:</b> {dt_max}<br>"
                summary_text += f"<b>J-Steps (jd):</b> {jd}<br>"
            
            # Sub-stepping parameters
            use_substepping = wizard.field("use_substepping")
            if use_substepping:
                num_sublevels = wizard.field("num_sublevels")
                num_substeps = wizard.field("num_substeps")
                summary_text += f"<b>Number of Sub-levels:</b> {num_sublevels}<br>"
                summary_text += f"<b>Number of Sub-steps per level:</b> {num_substeps}<br>"
        
        # Display the summary
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_layout.addWidget(summary_label)
        
        self.layout.addWidget(summary_group)
        
        # Add note about finishing
        note = QLabel("<b>Note:</b> Click 'Finish' to create or update the analysis.")
        note.setWordWrap(True)
        self.layout.addWidget(note)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = AnalysisManagerDialog()
    dialog.show()
    sys.exit(app.exec_())