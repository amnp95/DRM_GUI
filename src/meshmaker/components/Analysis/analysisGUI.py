from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout,
    QGroupBox, QWizard, QWizardPage, QStackedWidget, QSpinBox,
    QDoubleSpinBox, QRadioButton, QButtonGroup
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
        
        # Setup dialog properties
        self.setWindowTitle("Analysis Manager")
        self.resize(900, 600)
        
        # Get the analysis manager instance
        self.analysis_manager = AnalysisManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Header section
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Manage Analysis Definitions"))
        
        create_btn = QPushButton("Create New Analysis")
        create_btn.clicked.connect(self.create_new_analysis)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Analyses table
        self.analyses_table = QTableWidget()
        self.analyses_table.setColumnCount(8)  # Select, Tag, Name, Type, Components, Steps, dt, Parameters
        self.analyses_table.setHorizontalHeaderLabels([
            "Select", "Tag", "Name", "Type", "Components", "Steps/Time", "Time Step", "Parameters"
        ])
        self.analyses_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.analyses_table.setSelectionMode(QTableWidget.SingleSelection)
        header = self.analyses_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.analyses_table)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_analysis)
        
        self.delete_selected_btn = QPushButton("Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_analysis)
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_analyses_list)
        
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_selected_btn)
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
        
        # Hide vertical header (row indices)
        self.analyses_table.verticalHeader().setVisible(False)
        
        for row, (tag, analysis) in enumerate(analyses.items()):
            # Select radio button
            radio_btn = QRadioButton()
            # Connect radio buttons to a common slot to ensure mutual exclusivity
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
            
            # Components summary
            components = []
            if analysis.constraint_handler:
                components.append(f"CH: {analysis.constraint_handler.handler_type}")
            if analysis.algorithm:
                components.append(f"Alg: {analysis.algorithm.algorithm_type}")
            if analysis.integrator:
                components.append(f"Int: {analysis.integrator.integrator_type}")
            
            components_str = ", ".join(components)
            components_item = QTableWidgetItem(components_str)
            components_item.setFlags(components_item.flags() & ~Qt.ItemIsEditable)
            self.analyses_table.setItem(row, 4, components_item)
            
            # Steps/Time
            if analysis.num_steps is not None:
                steps_time = f"{analysis.num_steps} steps"
            elif analysis.final_time is not None:
                steps_time = f"t={analysis.final_time}"
            else:
                steps_time = "N/A"
            steps_item = QTableWidgetItem(steps_time)
            steps_item.setFlags(steps_item.flags() & ~Qt.ItemIsEditable)
            self.analyses_table.setItem(row, 5, steps_item)
            
            # Time Step
            dt_str = str(analysis.dt) if analysis.dt is not None else "N/A"
            dt_item = QTableWidgetItem(dt_str)
            dt_item.setFlags(dt_item.flags() & ~Qt.ItemIsEditable)
            self.analyses_table.setItem(row, 6, dt_item)
            
            # Additional parameters
            params = []
            if analysis.analysis_type == "VariableTransient":
                params.append(f"dt_min={analysis.dt_min}")
                params.append(f"dt_max={analysis.dt_max}")
                params.append(f"jd={analysis.jd}")
            
            if analysis.num_sublevels is not None:
                params.append(f"sublevels={analysis.num_sublevels}")
                params.append(f"substeps={analysis.num_substeps}")
            
            params_str = ", ".join(params) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.analyses_table.setItem(row, 7, params_item)
        
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
        self.delete_selected_btn.setEnabled(enable_buttons)

    def get_selected_analysis_tag(self):
        """Get the tag of the selected analysis"""
        for row, radio_btn in enumerate(self.radio_buttons):
            if radio_btn.isChecked():
                tag_item = self.analyses_table.item(row, 1)
                return int(tag_item.text())
        return None

    def create_new_analysis(self):
        """Open wizard to create a new analysis"""
        wizard = AnalysisCreationWizard(self)
        if wizard.exec() == QWizard.Accepted:
            self.refresh_analyses_list()

    def edit_selected_analysis(self):
        """Edit the selected analysis"""
        tag = self.get_selected_analysis_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select an analysis to edit")
            return
        
        try:
            analysis = self.analysis_manager.get_analysis(tag)
            wizard = AnalysisEditWizard(analysis, self)
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


class AnalysisCreationWizard(QWizard):
    """
    Wizard for creating a new analysis with multiple steps/pages
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
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
        self.addPage(AnalysisBasicInfoPage(self))
        self.addPage(ConstraintHandlerPage(self))
        self.addPage(NumbererPage(self))
        self.addPage(SystemPage(self))
        self.addPage(AlgorithmPage(self))
        self.addPage(TestPage(self))
        self.addPage(IntegratorPage(self))
        self.addPage(AnalysisParametersPage(self))
        self.addPage(AnalysisSummaryPage(self))
        
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
                # Collect all parameters from field objects
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
                
                # Create the analysis
                self.analysis = self.analysis_manager.create_analysis(
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
                QMessageBox.critical(self, "Error", f"Failed to create analysis: {str(e)}")


class AnalysisEditWizard(QWizard):
    """
    Wizard for editing an existing analysis
    """
    def __init__(self, analysis, parent=None):
        super().__init__(parent)
        
        if analysis is None:
            raise ValueError("Analysis cannot be None for AnalysisEditWizard")
            
        self.analysis = analysis
        self.setWindowTitle(f"Edit Analysis: {analysis.name}")
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
        self.addPage(AnalysisBasicInfoPage(self, self.analysis))
        self.addPage(ConstraintHandlerPage(self, self.analysis))
        self.addPage(NumbererPage(self, self.analysis))
        self.addPage(SystemPage(self, self.analysis))
        self.addPage(AlgorithmPage(self, self.analysis))
        self.addPage(TestPage(self, self.analysis))
        self.addPage(IntegratorPage(self, self.analysis))
        self.addPage(AnalysisParametersPage(self, self.analysis))
        self.addPage(AnalysisSummaryPage(self, self.analysis))
        
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
                # Collect all parameters from field objects
                name = self.field("name")
                
                # Check if name changed and is not a duplicate
                if name != self.analysis.name and name in Analysis._names:
                    raise ValueError(f"Analysis name '{name}' is already in use. Names must be unique.")
                
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
                if self.analysis.analysis_type != "Static":
                    dt = self.field("dt")
                
                dt_min = None
                dt_max = None
                jd = None
                if self.analysis.analysis_type == "VariableTransient":
                    dt_min = self.field("dt_min")
                    dt_max = self.field("dt_max")
                    jd = self.field("jd")
                
                use_substepping = self.field("use_substepping")
                num_sublevels = None
                num_substeps = None
                if use_substepping and self.analysis.analysis_type != "Static":
                    num_sublevels = self.field("num_sublevels")
                    num_substeps = self.field("num_substeps")
                
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
                
                QMessageBox.information(self, "Success", f"Analysis '{name}' updated successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update analysis: {str(e)}")


class WizardPage(QWizardPage):
    """Base class for wizard pages with common functionality"""
    def __init__(self, title, subtitle="", parent=None, analysis=None):
        super().__init__(parent)
        self.setTitle(title)
        self.setSubTitle(subtitle)
        self.analysis = analysis
        
    def initializePage(self):
        """Initialize the page when it is shown"""
        super().initializePage()
        self.updateUi()
        
    def updateUi(self):
        """Update the UI based on current data - to be overridden"""
        pass


class AnalysisBasicInfoPage(WizardPage):
    """First page of the wizard for basic information"""
    def __init__(self, parent=None, analysis=None):
        super().__init__(
            "Analysis Basic Information", 
            "Enter the basic information for the analysis.",
            parent, 
            analysis
        )
        
        # Create layout
        layout = QFormLayout(self)
        
        # Name field
        self.name_edit = QLineEdit()
        if analysis:
            self.name_edit.setText(analysis.name)
        layout.addRow("Analysis Name:", self.name_edit)
        
        # Analysis type
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["Static", "Transient", "VariableTransient"])
        if analysis:
            index = self.analysis_type_combo.findText(analysis.analysis_type)
            if index >= 0:
                self.analysis_type_combo.setCurrentIndex(index)
            # Disable changing analysis type in edit mode
            self.analysis_type_combo.setEnabled(False)
        layout.addRow("Analysis Type:", self.analysis_type_combo)
        
        # Description field
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
        if name in Analysis._names and (not self.analysis or self.analysis.name != name):
            QMessageBox.warning(self, "Validation Error", f"Analysis name '{name}' is already in use. Names must be unique.")
            return False
        
        return True


class ConstraintHandlerPage(WizardPage):
    """Page for selecting a constraint handler"""
    def __init__(self, parent=None, analysis=None):
        super().__init__(
            "Constraint Handler Selection", 
            "Select a constraint handler for the analysis.",
            parent,
            analysis
        )
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Explanation
        info = QLabel("Constraint handlers determine how the constraint equations are enforced in the system of equations.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Selection table
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Select, Tag, Type, Parameters
        self.table.setHorizontalHeaderLabels(["Select", "Tag", "Type", "Parameters"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        create_new_btn = QPushButton("Create New Constraint Handler")
        create_new_btn.clicked.connect(self.open_handler_dialog)
        btn_layout.addWidget(create_new_btn)
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.populate_table)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Register fields
        self.registerField("constraint_handler_tag", self, "selectedHandlerTag")
        
        # Selected handler tag property
        self._selected_handler_tag = None
        
    selectedHandlerTagChanged = Signal(int)
    
    def selectedHandlerTag(self):
        """Getter for selected handler tag property"""
        return self._selected_handler_tag
        
    def setSelectedHandlerTag(self, tag):
        """Setter for selected handler tag property"""
        self._selected_handler_tag = tag
        
    def initializePage(self):
        """Initialize the page when it becomes active"""
        super().initializePage()
        self.populate_table()
        
    def populate_table(self):
        """Populate the table with available constraint handlers"""
        self.table.setRowCount(0)
        
        manager = ConstraintHandlerManager()
        handlers = manager.get_all_handlers()
        
        self.table.setRowCount(len(handlers))
        self.radio_buttons = []
        
        for row, (tag, handler) in enumerate(handlers.items()):
            # Select radio button
            radio_btn = QRadioButton()
            radio_btn.toggled.connect(lambda checked, t=tag: self.on_handler_selected(checked, t))
            self.radio_buttons.append(radio_btn)
            
            # Select current handler if editing
            if self.analysis and self.analysis.constraint_handler and self.analysis.constraint_handler.tag == tag:
                radio_btn.setChecked(True)
                
            radio_cell = QWidget()
            radio_layout = QHBoxLayout(radio_cell)
            radio_layout.addWidget(radio_btn)
            radio_layout.setAlignment(Qt.AlignCenter)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, radio_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, tag_item)
            
            # Type
            type_item = QTableWidgetItem(handler.handler_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, type_item)
            
            # Parameters
            params = handler.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, params_item)
            
    def on_handler_selected(self, checked, tag):
        """Handle radio button selection"""
        if checked:
            self._selected_handler_tag = tag
            self.selectedHandlerTagChanged.emit(tag)
            # Ensure only one radio button is checked
            for btn in self.radio_buttons:
                if btn.isChecked() and btn != self.sender():
                    btn.setChecked(False)
                    
    def open_handler_dialog(self):
        """Open constraint handler manager dialog"""
        dialog = ConstraintHandlerManagerTab(self)
        if dialog.exec() == QDialog.Accepted:
            self.populate_table()
    
    def validatePage(self):
        """Validate the page before proceeding"""
        if not self._selected_handler_tag:
            QMessageBox.warning(self, "Validation Error", "Please select a constraint handler.")
            return False
        
        return True


class NumbererPage(WizardPage):
    """Page for selecting a numberer"""
    def __init__(self, parent=None, analysis=None):
        super().__init__(
            "Numberer Selection", 
            "Select a numberer for the analysis.",
            parent,
            analysis
        )
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Explanation
        info = QLabel("Numberers determine the mapping between equation numbers and degrees of freedom.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Numberer options
        self.numberer_group = QGroupBox("Available Numberers")
        numberer_layout = QVBoxLayout(self.numberer_group)
        
        # Create radio buttons for each numberer type
        self.numberer_buttons = QButtonGroup(self)
        
        # Get available numberer types
        self.numberer_manager = NumbererManager()
        self.numberers = self.numberer_manager.get_all_numberers()
        
        for numberer_type, numberer in self.numberers.items():
            radio_btn = QRadioButton(f"{numberer_type.capitalize()}")
            self.numberer_buttons.addButton(radio_btn)
            numberer_layout.addWidget(radio_btn)
            
            # Set button checked if editing and this is the current numberer
            if self.analysis and self.analysis.numberer and numberer_type == self.analysis.numberer.to_tcl().split()[1]:
                radio_btn.setChecked(True)
        
        layout.addWidget(self.numberer_group)
        
        # Description box
        self.description_group = QGroupBox("Description")
        self.description_layout = QVBoxLayout(self.description_group)
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_layout.addWidget(self.description_label)
        layout.addWidget(self.description_group)
        
        # Connect signals
        self.numberer_buttons.buttonClicked.connect(self.update_description)
        
        # Register fields
        self.registerField("numberer_type", self, "selectedNumbererType")
        
        # Selected numberer type property
        self._selected_numberer_type = None
        
    selectedNumbererTypeChanged = Signal(str)
    
    def selectedNumbererType(self):
        """Getter for selected numberer type property"""
        return self._selected_numberer_type
        
    def setSelectedNumbererType(self, type_name):
        """Setter for selected numberer type property"""
        self._selected_numberer_type = type_name
    
    def update_description(self, button):
        """Update the description based on selected numberer"""
        numberer_type = button.text().lower()
        
        descriptions = {
            "plain": "Plain numberer assigns equation numbers to DOFs based on the order in which nodes are created.",
            "rcm": "Reverse Cuthill-McKee numberer reduces the bandwidth of the system matrix.",
            "amd": "Alternate Minimum Degree numberer minimizes fill-in during matrix factorization."
        }
        
        self.description_label.setText(descriptions.get(numberer_type, "No description available."))
        self._selected_numberer_type = numberer_type
        self.selectedNumbererTypeChanged.emit(numberer_type)
        
    def validatePage(self):
        """Validate the page before proceeding"""
        if not self.numberer_buttons.checkedButton():
            QMessageBox.warning(self, "Validation Error", "Please select a numberer.")
            return False
        
        self._selected_numberer_type = self.numberer_buttons.checkedButton().text().lower()
        return True


class SystemPage(WizardPage):
    """Page for selecting a system"""
    def __init__(self, parent=None, analysis=None):
        super().__init__(
            "System Selection", 
            "Select a system for the analysis.",
            parent,
            analysis
        )
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Explanation
        info = QLabel("Systems handle the system of linear equations.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Selection table
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Select, Tag, Type, Parameters
        self.table.setHorizontalHeaderLabels(["Select", "Tag", "Type", "Parameters"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        create_new_btn = QPushButton("Create New System")
        create_new_btn.clicked.connect(self.open_system_dialog)
        btn_layout.addWidget(create_new_btn)
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.populate_table)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Register fields
        self.registerField("system_tag", self, "selectedSystemTag")
        
        # Selected system tag property
        self._selected_system_tag = None
        
    selectedSystemTagChanged = Signal(int)
    
    def selectedSystemTag(self):
        """Getter for selected system tag property"""
        return self._selected_system_tag
        
    def setSelectedSystemTag(self, tag):
        """Setter for selected system tag property"""
        self._selected_system_tag = tag
    
    def initializePage(self):
        """Initialize the page when it becomes active"""
        super().initializePage()
        self.populate_table()
        
    def populate_table(self):
        """Populate the table with available systems"""
        self.table.setRowCount(0)
        
        manager = SystemManager()
        systems = manager.get_all_systems()
        
        self.table.setRowCount(len(systems))
        self.radio_buttons = []
        
        for row, (tag, system) in enumerate(systems.items()):
            # Select radio button
            radio_btn = QRadioButton()
            radio_btn.toggled.connect(lambda checked, t=tag: self.on_system_selected(checked, t))
            self.radio_buttons.append(radio_btn)
            
            # Select current system if editing
            if self.analysis and self.analysis.system and self.analysis.system.tag == tag:
                radio_btn.setChecked(True)
                
            radio_cell = QWidget()
            radio_layout = QHBoxLayout(radio_cell)
            radio_layout.addWidget(radio_btn)
            radio_layout.setAlignment(Qt.AlignCenter)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, radio_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, tag_item)
            
            # Type
            type_item = QTableWidgetItem(system.system_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, type_item)
            
            # Parameters
            params = system.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, params_item)
            
    def on_system_selected(self, checked, tag):
        """Handle radio button selection"""
        if checked:
            self._selected_system_tag = tag
            self.selectedSystemTagChanged.emit(tag)
            # Ensure only one radio button is checked
            for btn in self.radio_buttons:
                if btn.isChecked() and btn != self.sender():
                    btn.setChecked(False)
                    
    def open_system_dialog(self):
        """Open system manager dialog"""
        dialog = SystemManagerTab(self)
        if dialog.exec() == QDialog.Accepted:
            self.populate_table()
    
    def validatePage(self):
        """Validate the page before proceeding"""
        if not self._selected_system_tag:
            QMessageBox.warning(self, "Validation Error", "Please select a system.")
            return False
        
        return True


class AlgorithmPage(WizardPage):
    """Page for selecting an algorithm"""
    def __init__(self, parent=None, analysis=None):
        super().__init__(
            "Algorithm Selection", 
            "Select an algorithm for the analysis.",
            parent,
            analysis
        )
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Explanation
        info = QLabel("Algorithms determine the solution procedure (e.g., Newton-Raphson, Linear).")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Selection table
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Select, Tag, Type, Parameters
        self.table.setHorizontalHeaderLabels(["Select", "Tag", "Type", "Parameters"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        create_new_btn = QPushButton("Create New Algorithm")
        create_new_btn.clicked.connect(self.open_algorithm_dialog)
        btn_layout.addWidget(create_new_btn)
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.populate_table)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Register fields
        self.registerField("algorithm_tag", self, "selectedAlgorithmTag")
        
        # Selected algorithm tag property
        self._selected_algorithm_tag = None
        
    selectedAlgorithmTagChanged = Signal(int)
    
    def selectedAlgorithmTag(self):
        """Getter for selected algorithm tag property"""
        return self._selected_algorithm_tag
        
    def setSelectedAlgorithmTag(self, tag):
        """Setter for selected algorithm tag property"""
        self._selected_algorithm_tag = tag
    
    def initializePage(self):
        """Initialize the page when it becomes active"""
        super().initializePage()
        self.populate_table()
        
    def populate_table(self):
        """Populate the table with available algorithms"""
        self.table.setRowCount(0)
        
        manager = AlgorithmManager()
        algorithms = manager.get_all_algorithms()
        
        self.table.setRowCount(len(algorithms))
        self.radio_buttons = []
        
        for row, (tag, algorithm) in enumerate(algorithms.items()):
            # Select radio button
            radio_btn = QRadioButton()
            radio_btn.toggled.connect(lambda checked, t=tag: self.on_algorithm_selected(checked, t))
            self.radio_buttons.append(radio_btn)
            
            # Select current algorithm if editing
            if self.analysis and self.analysis.algorithm and self.analysis.algorithm.tag == tag:
                radio_btn.setChecked(True)
                
            radio_cell = QWidget()
            radio_layout = QHBoxLayout(radio_cell)
            radio_layout.addWidget(radio_btn)
            radio_layout.setAlignment(Qt.AlignCenter)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, radio_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, tag_item)
            
            # Type
            type_item = QTableWidgetItem(algorithm.algorithm_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, type_item)
            
            # Parameters
            params = algorithm.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, params_item)
            
    def on_algorithm_selected(self, checked, tag):
        """Handle radio button selection"""
        if checked:
            self._selected_algorithm_tag = tag
            self.selectedAlgorithmTagChanged.emit(tag)
            # Ensure only one radio button is checked
            for btn in self.radio_buttons:
                if btn.isChecked() and btn != self.sender():
                    btn.setChecked(False)
                    
    def open_algorithm_dialog(self):
        """Open algorithm manager dialog"""
        dialog = AlgorithmManagerTab(self)
        if dialog.exec() == QDialog.Accepted:
            self.populate_table()
    
    def validatePage(self):
        """Validate the page before proceeding"""
        if not self._selected_algorithm_tag:
            QMessageBox.warning(self, "Validation Error", "Please select an algorithm.")
            return False
        
        return True


class TestPage(WizardPage):
    """Page for selecting a convergence test"""
    def __init__(self, parent=None, analysis=None):
        super().__init__(
            "Convergence Test Selection", 
            "Select a convergence test for the analysis.",
            parent,
            analysis
        )
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Explanation
        info = QLabel("Convergence tests determine if the solution has converged.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Selection table
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Select, Tag, Type, Parameters
        self.table.setHorizontalHeaderLabels(["Select", "Tag", "Type", "Parameters"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        create_new_btn = QPushButton("Create New Test")
        create_new_btn.clicked.connect(self.open_test_dialog)
        btn_layout.addWidget(create_new_btn)
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.populate_table)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Register fields
        self.registerField("test_tag", self, "selectedTestTag")
        
        # Selected test tag property
        self._selected_test_tag = None
        
    selectedTestTagChanged = Signal(int)
    
    def selectedTestTag(self):
        """Getter for selected test tag property"""
        return self._selected_test_tag
        
    def setSelectedTestTag(self, tag):
        """Setter for selected test tag property"""
        self._selected_test_tag = tag
    
    def initializePage(self):
        """Initialize the page when it becomes active"""
        super().initializePage()
        self.populate_table()
        
    def populate_table(self):
        """Populate the table with available convergence tests"""
        self.table.setRowCount(0)
        
        manager = TestManager()
        tests = manager.get_all_tests()
        
        self.table.setRowCount(len(tests))
        self.radio_buttons = []
        
        for row, (tag, test) in enumerate(tests.items()):
            # Select radio button
            radio_btn = QRadioButton()
            radio_btn.toggled.connect(lambda checked, t=tag: self.on_test_selected(checked, t))
            self.radio_buttons.append(radio_btn)
            
            # Select current test if editing
            if self.analysis and self.analysis.test and self.analysis.test.tag == tag:
                radio_btn.setChecked(True)
                
            radio_cell = QWidget()
            radio_layout = QHBoxLayout(radio_cell)
            radio_layout.addWidget(radio_btn)
            radio_layout.setAlignment(Qt.AlignCenter)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, radio_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, tag_item)
            
            # Type
            type_item = QTableWidgetItem(test.test_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, type_item)
            
            # Parameters
            params = test.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, params_item)
            
    def on_test_selected(self, checked, tag):
        """Handle radio button selection"""
        if checked:
            self._selected_test_tag = tag
            self.selectedTestTagChanged.emit(tag)
            # Ensure only one radio button is checked
            for btn in self.radio_buttons:
                if btn.isChecked() and btn != self.sender():
                    btn.setChecked(False)
                    
    def open_test_dialog(self):
        """Open test manager dialog"""
        dialog = TestManagerTab(self)
        if dialog.exec() == QDialog.Accepted:
            self.populate_table()
    
    def validatePage(self):
        """Validate the page before proceeding"""
        if not self._selected_test_tag:
            QMessageBox.warning(self, "Validation Error", "Please select a convergence test.")
            return False
        
        return True


class IntegratorPage(WizardPage):
    """Page for selecting an integrator"""
    def __init__(self, parent=None, analysis=None):
        super().__init__(
            "Integrator Selection", 
            "Select an integrator for the analysis.",
            parent,
            analysis
        )
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Explanation
        info = QLabel("Integrators determine how the displacement and resistance are updated during the analysis.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Selection table
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Select, Tag, Type, Parameters
        self.table.setHorizontalHeaderLabels(["Select", "Tag", "Type", "Parameters"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        
        # Compatibility warning
        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: red;")
        self.warning_label.setWordWrap(True)
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        create_new_btn = QPushButton("Create New Integrator")
        create_new_btn.clicked.connect(self.open_integrator_dialog)
        btn_layout.addWidget(create_new_btn)
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.populate_table)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Register fields
        self.registerField("integrator_tag", self, "selectedIntegratorTag")
        
        # Selected integrator tag property
        self._selected_integrator_tag = None
        
    selectedIntegratorTagChanged = Signal(int)
    
    def selectedIntegratorTag(self):
        """Getter for selected integrator tag property"""
        return self._selected_integrator_tag
        
    def setSelectedIntegratorTag(self, tag):
        """Setter for selected integrator tag property"""
        self._selected_integrator_tag = tag
    
    def initializePage(self):
        """Initialize the page when it becomes active"""
        super().initializePage()
        self.analysis_type = self.wizard().field("analysis_type")
        self.populate_table()
        
    def populate_table(self):
        """Populate the table with compatible integrators"""
        self.table.setRowCount(0)
        
        manager = IntegratorManager()
        integrators = manager.get_all_integrators()
        
        # Filter compatible integrators
        compatible_integrators = {}
        
        for tag, integrator in integrators.items():
            is_static = isinstance(integrator, StaticIntegrator)
            is_transient = isinstance(integrator, TransientIntegrator)
            
            if self.analysis_type == "Static" and is_static:
                compatible_integrators[tag] = integrator
            elif self.analysis_type in ["Transient", "VariableTransient"] and is_transient:
                compatible_integrators[tag] = integrator
        
        # Populate the table
        self.table.setRowCount(len(compatible_integrators))
        self.radio_buttons = []
        
        for row, (tag, integrator) in enumerate(compatible_integrators.items()):
            # Select radio button
            radio_btn = QRadioButton()
            radio_btn.toggled.connect(lambda checked, t=tag: self.on_integrator_selected(checked, t))
            self.radio_buttons.append(radio_btn)
            
            # Select current integrator if editing
            if self.analysis and self.analysis.integrator and self.analysis.integrator.tag == tag:
                radio_btn.setChecked(True)
                
            radio_cell = QWidget()
            radio_layout = QHBoxLayout(radio_cell)
            radio_layout.addWidget(radio_btn)
            radio_layout.setAlignment(Qt.AlignCenter)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, radio_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, tag_item)
            
            # Type
            type_item = QTableWidgetItem(integrator.integrator_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, type_item)
            
            # Parameters
            params = integrator.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, params_item)
            
        # Display warning if no compatible integrators
        if len(compatible_integrators) == 0:
            self.warning_label.setText(
                f"No compatible integrators found for {self.analysis_type} analysis. "
                f"Please create a {'static' if self.analysis_type == 'Static' else 'transient'} integrator."
            )
            self.warning_label.setVisible(True)
        else:
            self.warning_label.setVisible(False)
            
    def on_integrator_selected(self, checked, tag):
        """Handle radio button selection"""
        if checked:
            self._selected_integrator_tag = tag
            self.selectedIntegratorTagChanged.emit(tag)
            # Ensure only one radio button is checked
            for btn in self.radio_buttons:
                if btn.isChecked() and btn != self.sender():
                    btn.setChecked(False)
                    
    def open_integrator_dialog(self):
        """Open integrator manager dialog"""
        dialog = IntegratorManagerTab(self)
        if dialog.exec() == QDialog.Accepted:
            self.populate_table()
    
    def validatePage(self):
        """Validate the page before proceeding"""
        if not self._selected_integrator_tag:
            QMessageBox.warning(self, "Validation Error", "Please select an integrator.")
            return False
        
        return True


class AnalysisParametersPage(WizardPage):
    """Page for configuring analysis parameters"""
    def __init__(self, parent=None, analysis=None):
        super().__init__(
            "Analysis Parameters", 
            "Configure parameters for the analysis.",
            parent,
            analysis
        )
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Will be populated in initializePage
        
    def initializePage(self):
        """Initialize the page when it becomes active"""
        super().initializePage()
        
        # Clear existing widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Create new widgets based on analysis type
        analysis_type = self.wizard().field("analysis_type")
        
        # Create form layout for parameters
        params_group = QGroupBox("Analysis Parameters")
        form_layout = QFormLayout(params_group)
        
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
        
        self.layout.addWidget(time_step_group)
        
        # For Transient and VariableTransient, add time step parameters
        if analysis_type in ["Transient", "VariableTransient"]:
            self.dt_spin = QDoubleSpinBox()
            self.dt_spin.setDecimals(6)
            self.dt_spin.setRange(0.000001, 10000)
            self.dt_spin.setValue(0.01)
            form_layout.addRow("Time Step (dt):", self.dt_spin)
            
            # Set value from editing analysis
            if self.analysis and self.analysis.dt is not None:
                self.dt_spin.setValue(self.analysis.dt)
            
            # For VariableTransient, add specific parameters
            if analysis_type == "VariableTransient":
                self.dt_min_spin = QDoubleSpinBox()
                self.dt_min_spin.setDecimals(6)
                self.dt_min_spin.setRange(0.000001, 10000)
                self.dt_min_spin.setValue(0.001)
                form_layout.addRow("Minimum Time Step:", self.dt_min_spin)
                
                self.dt_max_spin = QDoubleSpinBox()
                self.dt_max_spin.setDecimals(6)
                self.dt_max_spin.setRange(0.000001, 10000)
                self.dt_max_spin.setValue(0.1)
                form_layout.addRow("Maximum Time Step:", self.dt_max_spin)
                
                self.jd_spin = QSpinBox()
                self.jd_spin.setRange(1, 100)
                self.jd_spin.setValue(2)
                form_layout.addRow("J-Steps (jd):", self.jd_spin)
                
                # Set values from editing analysis
                if self.analysis and self.analysis.dt_min is not None:
                    self.dt_min_spin.setValue(self.analysis.dt_min)
                if self.analysis and self.analysis.dt_max is not None:
                    self.dt_max_spin.setValue(self.analysis.dt_max)
                if self.analysis and self.analysis.jd is not None:
                    self.jd_spin.setValue(self.analysis.jd)
            
            # Sub-stepping parameters for Transient/VariableTransient
            substep_group = QGroupBox("Sub-stepping Options")
            substep_group.setCheckable(True)
            substep_group.setChecked(False)
            substep_layout = QFormLayout(substep_group)
            
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
                substep_group.setChecked(True)
                self.num_sublevels_spin.setValue(self.analysis.num_sublevels)
            if self.analysis and self.analysis.num_substeps is not None:
                self.num_substeps_spin.setValue(self.analysis.num_substeps)
                
            form_layout.addRow(substep_group)
        
        self.layout.addWidget(params_group)
        
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
            
            self.registerField("use_substepping", substep_group, "checked")
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


class AnalysisSummaryPage(WizardPage):
    """Final summary page before creating/updating the analysis"""
    def __init__(self, parent=None, analysis=None):
        super().__init__(
            "Analysis Summary",
            "Review the analysis configuration before finishing.",
            parent,
            analysis
        )
        
        self.layout = QVBoxLayout(self)
        
    def initializePage(self):
        """Initialize the page when it becomes active"""
        super().initializePage()
        
        # Clear existing widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get analysis parameters from the wizard fields
        name = self.wizard().field("name")
        analysis_type = self.wizard().field("analysis_type")
        
        # Create summary text
        summary_group = QGroupBox("Analysis Configuration Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        summary_text = f"<b>Name:</b> {name}<br>"
        summary_text += f"<b>Analysis Type:</b> {analysis_type}<br><br>"
        
        # Add component information
        constraint_handler_tag = self.wizard().field("constraint_handler_tag")
        constraint_handler = self.wizard().constraint_handler_manager.get_handler(constraint_handler_tag)
        summary_text += f"<b>Constraint Handler:</b> {constraint_handler.handler_type} (Tag: {constraint_handler_tag})<br>"
        
        numberer_type = self.wizard().field("numberer_type")
        summary_text += f"<b>Numberer:</b> {numberer_type}<br>"
        
        system_tag = self.wizard().field("system_tag")
        system = self.wizard().system_manager.get_system(system_tag)
        summary_text += f"<b>System:</b> {system.system_type} (Tag: {system_tag})<br>"
        
        algorithm_tag = self.wizard().field("algorithm_tag")
        algorithm = self.wizard().algorithm_manager.get_algorithm(algorithm_tag)
        summary_text += f"<b>Algorithm:</b> {algorithm.algorithm_type} (Tag: {algorithm_tag})<br>"
        
        test_tag = self.wizard().field("test_tag")
        test = self.wizard().test_manager.get_test(test_tag)
        summary_text += f"<b>Convergence Test:</b> {test.test_type} (Tag: {test_tag})<br>"
        
        integrator_tag = self.wizard().field("integrator_tag")
        integrator = self.wizard().integrator_manager.get_integrator(integrator_tag)
        summary_text += f"<b>Integrator:</b> {integrator.integrator_type} (Tag: {integrator_tag})<br><br>"
        
        # Add analysis parameters
        use_num_steps = self.wizard().field("use_num_steps")
        if use_num_steps:
            num_steps = self.wizard().field("num_steps")
            summary_text += f"<b>Number of Steps:</b> {num_steps}<br>"
        else:
            final_time = self.wizard().field("final_time")
            summary_text += f"<b>Final Time:</b> {final_time}<br>"
        
        # For Transient and VariableTransient
        if analysis_type in ["Transient", "VariableTransient"]:
            dt = self.wizard().field("dt")
            summary_text += f"<b>Time Step (dt):</b> {dt}<br>"
            
            # For VariableTransient
            if analysis_type == "VariableTransient":
                dt_min = self.wizard().field("dt_min")
                dt_max = self.wizard().field("dt_max")
                jd = self.wizard().field("jd")
                summary_text += f"<b>Minimum Time Step:</b> {dt_min}<br>"
                summary_text += f"<b>Maximum Time Step:</b> {dt_max}<br>"
                summary_text += f"<b>J-Steps (jd):</b> {jd}<br>"
            
            # Sub-stepping parameters
            use_substepping = self.wizard().field("use_substepping")
            if use_substepping:
                num_sublevels = self.wizard().field("num_sublevels")
                num_substeps = self.wizard().field("num_substeps")
                summary_text += f"<b>Number of Sub-levels:</b> {num_sublevels}<br>"
                summary_text += f"<b>Number of Sub-steps per level:</b> {num_substeps}<br>"
        
        # Display the summary
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_layout.addWidget(summary_label)
        
        self.layout.addWidget(summary_group)
        
        # Add note about finishing
        note = QLabel("<b>Note:</b> Click 'Finish' to create/update the analysis.")
        note.setWordWrap(True)
        self.layout.addWidget(note)

    def validatePage(self):
        """Final validation before creating/updating the analysis"""
        # All validation should have been handled in previous pages
        return True


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Use AnalysisCreationWizard instead of AnalysisEditWizard for testing
    # since it doesn't require an existing analysis object
    wizard = AnalysisManagerDialog()
    wizard.show()
    
    sys.exit(app.exec_())