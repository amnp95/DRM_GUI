from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout, QTabWidget,
    QGroupBox, QSpinBox, QDoubleSpinBox, QRadioButton, QCheckBox
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


class AnalysisManagerTab(QDialog):
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
        if wizard.exec() == QDialog.Accepted and wizard.created_analysis:
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
            if wizard.exec() == QDialog.Accepted:
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


class AnalysisWizard(QDialog):
    """
    Simplified dialog for creating/editing an analysis with all options in a single level of tabs
    """
    def __init__(self, parent=None, analysis=None):
        super().__init__(parent)
        
        self.analysis = analysis
        self.created_analysis = None
        
        if analysis:
            self.setWindowTitle(f"Edit Analysis: {analysis.name}")
        else:
            self.setWindowTitle("Create New Analysis")
            
        # self.resize(900, 700)
        # make the widget larger to accommodate all tabs
        self.resize(850, 550)

        
        # Initialize manager instances
        self.analysis_manager = AnalysisManager()
        self.constraint_handler_manager = ConstraintHandlerManager()
        self.numberer_manager = NumbererManager()
        self.system_manager = SystemManager()
        self.algorithm_manager = AlgorithmManager()
        self.test_manager = TestManager()
        self.integrator_manager = IntegratorManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create tabbed interface with all tabs in a single level
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_basic_tab(), "Basic Info")
        self.tabs.addTab(self.create_constraint_handler_tab(), "Constraint Handler")
        self.tabs.addTab(self.create_numberer_tab(), "Numberer")
        self.tabs.addTab(self.create_system_tab(), "System")
        self.tabs.addTab(self.create_algorithm_tab(), "Algorithm")
        self.tabs.addTab(self.create_test_tab(), "Convergence Test")
        self.tabs.addTab(self.create_integrator_tab(), "Integrator")
        self.tabs.addTab(self.create_time_stepping_tab(), "Time Stepping")
        self.tabs.addTab(self.create_summary_tab(), "Summary")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_box = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.finish_btn = QPushButton("Finish")
        self.finish_btn.clicked.connect(self.accept_and_create)
        self.finish_btn.setDefault(True)
        
        button_box.addStretch()
        button_box.addWidget(self.cancel_btn)
        button_box.addWidget(self.finish_btn)
        
        layout.addLayout(button_box)
        
        # Connect signals
        self.tabs.currentChanged.connect(self.update_summary)
        
    def create_basic_tab(self):
        """Create basic info tab with name and analysis type"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Name field
        self.name_edit = QLineEdit()
        if self.analysis:
            self.name_edit.setText(self.analysis.name)
        layout.addRow("Analysis Name:", self.name_edit)
        
        # Analysis type
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["Static", "Transient", "VariableTransient"])
        if self.analysis:
            index = self.analysis_type_combo.findText(self.analysis.analysis_type)
            if index >= 0:
                self.analysis_type_combo.setCurrentIndex(index)
            # Disable changing analysis type in edit mode
            self.analysis_type_combo.setEnabled(False)
        layout.addRow("Analysis Type:", self.analysis_type_combo)
        
        # Description box
        description_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(description_group)
        
        self.static_desc = QLabel("Static: Used for problems where inertial and damping effects are not considered.")
        self.transient_desc = QLabel("Transient: Used for dynamic analysis where inertial and damping effects are considered.")
        self.var_trans_desc = QLabel("Variable Transient: Like Transient, but with adaptive time steps based on convergence.")
        
        desc_layout.addWidget(self.static_desc)
        desc_layout.addWidget(self.transient_desc)
        desc_layout.addWidget(self.var_trans_desc)
        
        layout.addRow(description_group)
        
        # Update descriptions when analysis type changes
        self.analysis_type_combo.currentTextChanged.connect(self.update_description)
        self.analysis_type_combo.currentTextChanged.connect(self.update_time_stepping_tab)
        
        # Initial update
        self.update_description(self.analysis_type_combo.currentText())
        
        return tab
    
    def update_description(self, analysis_type):
        """Update the description based on selected analysis type"""
        self.static_desc.setVisible(analysis_type == "Static")
        self.transient_desc.setVisible(analysis_type == "Transient")
        self.var_trans_desc.setVisible(analysis_type == "VariableTransient")
    
    def create_constraint_handler_tab(self):
        """Create constraint handler tab"""
        self.constraint_handler_tab = ConstraintHandlerManagerTab()
        
        if self.analysis and self.analysis.constraint_handler:
            self.constraint_handler_tab.select_handler(self.analysis.constraint_handler.tag)
            
        return self.constraint_handler_tab
    
    def create_numberer_tab(self):
        """Create numberer tab"""
        self.numberer_tab = NumbererManagerTab()
        
        if self.analysis and self.analysis.numberer:
            self.numberer_tab.select_numberer(self.analysis.numberer.numberer_type)
            
        return self.numberer_tab
    
    def create_system_tab(self):
        """Create system tab"""
        self.system_tab = SystemManagerTab()
        
        if self.analysis and self.analysis.system:
            self.system_tab.select_system(self.analysis.system.tag)
            
        return self.system_tab
    
    def create_algorithm_tab(self):
        """Create algorithm tab"""
        self.algorithm_tab = AlgorithmManagerTab()
        
        if self.analysis and self.analysis.algorithm:
            self.algorithm_tab.select_algorithm(self.analysis.algorithm.tag)
            
        return self.algorithm_tab
    
    def create_test_tab(self):
        """Create convergence test tab"""
        self.test_tab = TestManagerTab()
        
        if self.analysis and self.analysis.test:
            self.test_tab.select_test(self.analysis.test.tag)
            
        return self.test_tab
    
    def create_integrator_tab(self):
        """Create integrator tab"""
        self.integrator_tab = IntegratorManagerTab()
        
        if self.analysis and self.analysis.integrator:
            self.integrator_tab.select_integrator(self.analysis.integrator.tag)
            
        return self.integrator_tab
    
    def create_time_stepping_tab(self):
        """Create time stepping parameters tab"""
        self.time_stepping_tab = QWidget()
        self.time_stepping_layout = QVBoxLayout(self.time_stepping_tab)
        
        # Initialize with current analysis type
        analysis_type = self.analysis_type_combo.currentText() if hasattr(self, 'analysis_type_combo') else "Static"
        self.update_time_stepping_tab(analysis_type)
        
        return self.time_stepping_tab
    
    def update_time_stepping_tab(self, analysis_type=None):
        """Update the time stepping tab based on selected analysis type"""
        if not hasattr(self, 'time_stepping_layout'):
            return
            
        # Clear existing widgets
        while self.time_stepping_layout.count():
            item = self.time_stepping_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not analysis_type:
            analysis_type = self.analysis_type_combo.currentText()
        
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
        if self.analysis and self.analysis.num_steps is not None:
            self.steps_radio.setChecked(True)
            self.num_steps_spin.setValue(self.analysis.num_steps)
            self.final_time_spin.setEnabled(False)
        elif self.analysis and self.analysis.final_time is not None:
            self.time_radio.setChecked(True)
            self.final_time_spin.setValue(self.analysis.final_time)
            self.num_steps_spin.setEnabled(False)
        else:
            self.steps_radio.setChecked(True)
            self.final_time_spin.setEnabled(False)
        
        self.time_stepping_layout.addWidget(time_step_group)
        
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
            if self.analysis and self.analysis.dt is not None:
                self.dt_spin.setValue(self.analysis.dt)
            
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
                if self.analysis and self.analysis.dt_min is not None:
                    self.dt_min_spin.setValue(self.analysis.dt_min)
                if self.analysis and self.analysis.dt_max is not None:
                    self.dt_max_spin.setValue(self.analysis.dt_max)
                if self.analysis and self.analysis.jd is not None:
                    self.jd_spin.setValue(self.analysis.jd)
            
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
            if self.analysis and self.analysis.num_sublevels is not None:
                self.substep_group.setChecked(True)
                self.num_sublevels_spin.setValue(self.analysis.num_sublevels)
            if self.analysis and self.analysis.num_substeps is not None:
                self.num_substeps_spin.setValue(self.analysis.num_substeps)
                
            transient_layout.addRow(self.substep_group)
            
            self.time_stepping_layout.addWidget(transient_group)
    
    def create_summary_tab(self):
        """Create summary tab for reviewing settings"""
        tab = QWidget()
        self.summary_layout = QVBoxLayout(tab)
        
        # Summary content will be updated when tab is shown
        self.summary_label = QLabel("Please review your analysis configuration.")
        self.summary_label.setWordWrap(True)
        self.summary_layout.addWidget(self.summary_label)
        
        return tab
    
    def update_summary(self):
        """Update the summary tab content"""
        if self.tabs.currentWidget() != self.tabs.widget(8):  # Not on summary tab (now at index 8)
            return
        
        try:
            # Get basic info
            name = self.name_edit.text()
            analysis_type = self.analysis_type_combo.currentText()
            
            # Format summary
            summary_text = f"<b>Name:</b> {name}<br>"
            summary_text += f"<b>Analysis Type:</b> {analysis_type}<br><br>"
            
            # Add component information
            constraint_handler_tag = self.constraint_handler_tab.get_selected_handler_tag()
            if constraint_handler_tag:
                constraint_handler = self.constraint_handler_manager.get_handler(constraint_handler_tag)
                summary_text += f"<b>Constraint Handler:</b> {constraint_handler.handler_type} (Tag: {constraint_handler_tag})<br>"
            
            numberer_type = self.numberer_tab.get_selected_numberer_type()
            if numberer_type:
                summary_text += f"<b>Numberer:</b> {numberer_type.capitalize()}<br>"
            
            system_tag = self.system_tab.get_selected_system_tag()
            if system_tag:
                system = self.system_manager.get_system(system_tag)
                summary_text += f"<b>System:</b> {system.system_type} (Tag: {system_tag})<br>"
            
            algorithm_tag = self.algorithm_tab.get_selected_algorithm_tag()
            if algorithm_tag:
                algorithm = self.algorithm_manager.get_algorithm(algorithm_tag)
                summary_text += f"<b>Algorithm:</b> {algorithm.algorithm_type} (Tag: {algorithm_tag})<br>"
            
            test_tag = self.test_tab.get_selected_test_tag()
            if test_tag:
                test = self.test_manager.get_test(test_tag)
                summary_text += f"<b>Convergence Test:</b> {test.test_type} (Tag: {test_tag})<br>"
            
            integrator_tag = self.integrator_tab.get_selected_integrator_tag()
            if integrator_tag:
                integrator = self.integrator_manager.get_integrator(integrator_tag)
                summary_text += f"<b>Integrator:</b> {integrator.integrator_type} (Tag: {integrator_tag})<br><br>"
            
            # Add analysis parameters if time stepping tab has been initialized
            if hasattr(self, 'steps_radio'):
                if self.steps_radio.isChecked():
                    num_steps = self.num_steps_spin.value()
                    summary_text += f"<b>Number of Steps:</b> {num_steps}<br>"
                else:
                    final_time = self.final_time_spin.value()
                    summary_text += f"<b>Final Time:</b> {final_time}<br>"
                
                # For Transient and VariableTransient
                if analysis_type in ["Transient", "VariableTransient"] and hasattr(self, 'dt_spin'):
                    dt = self.dt_spin.value()
                    summary_text += f"<b>Time Step (dt):</b> {dt}<br>"
                    
                    # For VariableTransient
                    if analysis_type == "VariableTransient" and hasattr(self, 'dt_min_spin'):
                        dt_min = self.dt_min_spin.value()
                        dt_max = self.dt_max_spin.value()
                        jd = self.jd_spin.value()
                        summary_text += f"<b>Minimum Time Step:</b> {dt_min}<br>"
                        summary_text += f"<b>Maximum Time Step:</b> {dt_max}<br>"
                        summary_text += f"<b>J-Steps (jd):</b> {jd}<br>"
                    
                    # Sub-stepping parameters
                    if hasattr(self, 'substep_group') and self.substep_group.isChecked():
                        num_sublevels = self.num_sublevels_spin.value()
                        num_substeps = self.num_substeps_spin.value()
                        summary_text += f"<b>Number of Sub-levels:</b> {num_sublevels}<br>"
                        summary_text += f"<b>Number of Sub-steps per level:</b> {num_substeps}<br>"
            
            # Display the summary
            self.summary_label.setText(summary_text)
            
        except Exception as e:
            self.summary_label.setText(f"Error generating summary: {str(e)}")
    
    def accept_and_create(self):
        """Validate and create/update the analysis when Finish is clicked"""
        # Validate basic info
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a name for the analysis.")
            self.tabs.setCurrentIndex(0)  # Switch to basic tab
            return
        
        # Check for duplicate name, but allow keeping the same name in edit mode
        if name in Analysis._names and (not self.analysis or self.analysis.name != name):
            QMessageBox.warning(self, "Validation Error", f"Analysis name '{name}' is already in use. Names must be unique.")
            self.tabs.setCurrentIndex(0)  # Switch to basic tab
            return
        
        analysis_type = self.analysis_type_combo.currentText()
        
        # Validate components with specific tab indices for each component
        errors = []
        component_tab_indices = {}
        
        # Constraint Handler (Tab index 1)
        constraint_handler_tag = self.constraint_handler_tab.get_selected_handler_tag()
        if not constraint_handler_tag:
            errors.append("Constraint Handler")
            component_tab_indices["Constraint Handler"] = 1
        
        # Numberer (Tab index 2)
        numberer_type = self.numberer_tab.get_selected_numberer_type()
        if not numberer_type:
            errors.append("Numberer")
            component_tab_indices["Numberer"] = 2
        
        # System (Tab index 3)
        system_tag = self.system_tab.get_selected_system_tag()
        if not system_tag:
            errors.append("System")
            component_tab_indices["System"] = 3
        
        # Algorithm (Tab index 4)
        algorithm_tag = self.algorithm_tab.get_selected_algorithm_tag()
        if not algorithm_tag:
            errors.append("Algorithm")
            component_tab_indices["Algorithm"] = 4
        
        # Test (Tab index 5)
        test_tag = self.test_tab.get_selected_test_tag()
        if not test_tag:
            errors.append("Convergence Test")
            component_tab_indices["Convergence Test"] = 5
        
        # Integrator (Tab index 6)
        integrator_tag = self.integrator_tab.get_selected_integrator_tag()
        if not integrator_tag:
            errors.append("Integrator")
            component_tab_indices["Integrator"] = 6
        
        if errors:
            # Take user to the first missing component tab
            first_error = errors[0]
            self.tabs.setCurrentIndex(component_tab_indices[first_error])
            QMessageBox.warning(self, "Validation Error", 
                              f"Please select the following components: {', '.join(errors)}")
            return
        
        # Check integrator compatibility
        integrator = self.integrator_manager.get_integrator(integrator_tag)
        if analysis_type == "Static" and not isinstance(integrator, StaticIntegrator):
            QMessageBox.warning(self, "Validation Error", 
                               f"Static analysis requires a static integrator. {integrator.integrator_type} is not compatible.")
            self.tabs.setCurrentIndex(6)  # Switch to integrator tab
            return
            
        if analysis_type in ["Transient", "VariableTransient"] and not isinstance(integrator, TransientIntegrator):
            QMessageBox.warning(self, "Validation Error", 
                               f"Transient analysis requires a transient integrator. {integrator.integrator_type} is not compatible.")
            self.tabs.setCurrentIndex(6)  # Switch to integrator tab
            return
        
        # Validate time stepping parameters
        use_num_steps = self.steps_radio.isChecked()
        
        if use_num_steps:
            num_steps = self.num_steps_spin.value()
            final_time = None
            if num_steps <= 0:
                QMessageBox.warning(self, "Validation Error", "Number of steps must be greater than 0.")
                self.tabs.setCurrentIndex(7)  # Switch to time stepping tab
                return
        else:
            num_steps = None
            final_time = self.final_time_spin.value()
            if final_time <= 0:
                QMessageBox.warning(self, "Validation Error", "Final time must be greater than 0.")
                self.tabs.setCurrentIndex(7)  # Switch to time stepping tab
                return
        
        # Default values
        dt = None
        dt_min = None
        dt_max = None
        jd = None
        num_sublevels = None
        num_substeps = None
        
        # Transient specific parameters
        if analysis_type in ["Transient", "VariableTransient"]:
            dt = self.dt_spin.value()
            if dt <= 0:
                QMessageBox.warning(self, "Validation Error", "Time step (dt) must be greater than 0.")
                self.tabs.setCurrentIndex(7)  # Switch to time stepping tab
                return
            
            # VariableTransient specific parameters
            if analysis_type == "VariableTransient":
                dt_min = self.dt_min_spin.value()
                dt_max = self.dt_max_spin.value()
                jd = self.jd_spin.value()
                
                if dt_min <= 0:
                    QMessageBox.warning(self, "Validation Error", "Minimum time step must be greater than 0.")
                    self.tabs.setCurrentIndex(7)  # Switch to time stepping tab
                    return
                if dt_max <= 0:
                    QMessageBox.warning(self, "Validation Error", "Maximum time step must be greater than 0.")
                    self.tabs.setCurrentIndex(7)  # Switch to time stepping tab
                    return
                if dt_min > dt_max:
                    QMessageBox.warning(self, "Validation Error", "Minimum time step cannot be greater than maximum time step.")
                    self.tabs.setCurrentIndex(7)  # Switch to time stepping tab
                    return
                if dt < dt_min or dt > dt_max:
                    QMessageBox.warning(self, "Validation Error", "Initial time step must be between minimum and maximum time step.")
                    self.tabs.setCurrentIndex(7)  # Switch to time stepping tab
                    return
            
            # Substepping parameters
            if self.substep_group.isChecked():
                num_sublevels = self.num_sublevels_spin.value()
                num_substeps = self.num_substeps_spin.value()
        
        try:
            # Get component instances
            constraint_handler = self.constraint_handler_manager.get_handler(constraint_handler_tag)
            numberer = self.numberer_manager.get_numberer(numberer_type)
            system = self.system_manager.get_system(system_tag)
            algorithm = self.algorithm_manager.get_algorithm(algorithm_tag)
            test = self.test_manager.get_test(test_tag)
            
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
            
            # Accept dialog
            self.accept()
            
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


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = AnalysisManagerTab()
    dialog.show()
    sys.exit(app.exec_())