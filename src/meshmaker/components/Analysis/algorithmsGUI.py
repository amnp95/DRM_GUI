from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout,
    QCheckBox, QGroupBox, QDoubleSpinBox, QSpinBox, QRadioButton
)

from meshmaker.utils.validator import DoubleValidator, IntValidator
from meshmaker.components.Analysis.algorithms import (
    Algorithm, AlgorithmManager, 
    LinearAlgorithm, NewtonAlgorithm, ModifiedNewtonAlgorithm,
    NewtonLineSearchAlgorithm, KrylovNewtonAlgorithm, SecantNewtonAlgorithm,
    BFGSAlgorithm, BroydenAlgorithm, ExpressNewtonAlgorithm
)

class AlgorithmManagerTab(QDialog):
    """Main dialog for managing algorithms"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup dialog properties
        self.setWindowTitle("Algorithm Manager")
        self.resize(800, 500)
        
        # Get the algorithm manager instance
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Algorithm type selection
        type_layout = QGridLayout()
        
        # Algorithm type dropdown
        self.algorithm_type_combo = QComboBox()
        self.algorithm_type_combo.addItems(self.algorithm_manager.get_available_types())
        
        create_algorithm_btn = QPushButton("Create New Algorithm")
        create_algorithm_btn.clicked.connect(self.open_algorithm_creation_dialog)
        
        type_layout.addWidget(QLabel("Algorithm Type:"), 0, 0)
        type_layout.addWidget(self.algorithm_type_combo, 0, 1)
        type_layout.addWidget(create_algorithm_btn, 1, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Algorithms table
        self.algorithms_table = QTableWidget()
        self.algorithms_table.setColumnCount(4)  # Select, Tag, Type, Parameters
        self.algorithms_table.setHorizontalHeaderLabels(["Select", "Tag", "Type", "Parameters"])
        self.algorithms_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.algorithms_table.setSelectionMode(QTableWidget.SingleSelection)
        header = self.algorithms_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.algorithms_table)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_algorithm)
        
        self.delete_selected_btn = QPushButton("Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_algorithm)
        
        refresh_btn = QPushButton("Refresh Algorithms List")
        refresh_btn.clicked.connect(self.refresh_algorithms_list)
        
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_selected_btn)
        buttons_layout.addWidget(refresh_btn)
        
        layout.addLayout(buttons_layout)
        
        # Initial refresh
        self.refresh_algorithms_list()
        
        # Disable edit/delete buttons initially
        self.update_button_state()

    def refresh_algorithms_list(self):
        """Update the algorithms table with current algorithms"""
        self.algorithms_table.setRowCount(0)
        algorithms = self.algorithm_manager.get_all_algorithms()
        
        self.algorithms_table.setRowCount(len(algorithms))
        self.radio_buttons = []
        
        # Hide vertical header (row indices)
        self.algorithms_table.verticalHeader().setVisible(False)
        
        for row, (tag, algorithm) in enumerate(algorithms.items()):
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
            self.algorithms_table.setCellWidget(row, 0, radio_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.algorithms_table.setItem(row, 1, tag_item)
            
            # Algorithm Type
            type_item = QTableWidgetItem(algorithm.algorithm_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.algorithms_table.setItem(row, 2, type_item)
            
            # Parameters
            params = algorithm.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items() if v])
            if not params_str:
                params_str = "No parameters"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.algorithms_table.setItem(row, 3, params_item)
        
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
        enable_buttons = any(rb.isChecked() for rb in self.radio_buttons)
        self.edit_btn.setEnabled(enable_buttons)
        self.delete_selected_btn.setEnabled(enable_buttons)

    def get_selected_algorithm_tag(self):
        """Get the tag of the selected algorithm"""
        for row, radio_btn in enumerate(self.radio_buttons):
            if radio_btn.isChecked():
                tag_item = self.algorithms_table.item(row, 1)
                return int(tag_item.text())
        return None

    def open_algorithm_creation_dialog(self):
        """Open dialog to create a new algorithm of selected type"""
        algorithm_type = self.algorithm_type_combo.currentText()
        
        dialog = None
        if algorithm_type.lower() == "linear":
            dialog = LinearAlgorithmDialog(self)
        elif algorithm_type.lower() == "newton":
            dialog = NewtonAlgorithmDialog(self)
        elif algorithm_type.lower() == "modifiednewton":
            dialog = ModifiedNewtonAlgorithmDialog(self)
        elif algorithm_type.lower() == "newtonlinesearch":
            dialog = NewtonLineSearchAlgorithmDialog(self)
        elif algorithm_type.lower() == "krylovnewton":
            dialog = KrylovNewtonAlgorithmDialog(self)
        elif algorithm_type.lower() == "secantnewton":
            dialog = SecantNewtonAlgorithmDialog(self)
        elif algorithm_type.lower() == "bfgs":
            dialog = BFGSAlgorithmDialog(self)
        elif algorithm_type.lower() == "broyden":
            dialog = BroydenAlgorithmDialog(self)
        elif algorithm_type.lower() == "expressnewton":
            dialog = ExpressNewtonAlgorithmDialog(self)
        else:
            QMessageBox.warning(self, "Error", f"No creation dialog available for algorithm type: {algorithm_type}")
            return
        
        if dialog.exec() == QDialog.Accepted:
            self.refresh_algorithms_list()

    def edit_selected_algorithm(self):
        """Edit the selected algorithm"""
        tag = self.get_selected_algorithm_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select an algorithm to edit")
            return
        
        try:
            algorithm = self.algorithm_manager.get_algorithm(tag)
            
            dialog = None
            if algorithm.algorithm_type.lower() == "linear":
                dialog = LinearAlgorithmEditDialog(algorithm, self)
            elif algorithm.algorithm_type.lower() == "newton":
                dialog = NewtonAlgorithmEditDialog(algorithm, self)
            elif algorithm.algorithm_type.lower() == "modifiednewton":
                dialog = ModifiedNewtonAlgorithmEditDialog(algorithm, self)
            elif algorithm.algorithm_type.lower() == "newtonlinesearch":
                dialog = NewtonLineSearchAlgorithmEditDialog(algorithm, self)
            elif algorithm.algorithm_type.lower() == "krylovnewton":
                dialog = KrylovNewtonAlgorithmEditDialog(algorithm, self)
            elif algorithm.algorithm_type.lower() == "secantnewton":
                dialog = SecantNewtonAlgorithmEditDialog(algorithm, self)
            elif algorithm.algorithm_type.lower() == "bfgs":
                dialog = BFGSAlgorithmEditDialog(algorithm, self)
            elif algorithm.algorithm_type.lower() == "broyden":
                dialog = BroydenAlgorithmEditDialog(algorithm, self)
            elif algorithm.algorithm_type.lower() == "expressnewton":
                dialog = ExpressNewtonAlgorithmEditDialog(algorithm, self)
            else:
                QMessageBox.warning(self, "Error", f"No edit dialog available for algorithm type: {algorithm.algorithm_type}")
                return
            
            if dialog.exec() == QDialog.Accepted:
                self.refresh_algorithms_list()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected_algorithm(self):
        """Delete the selected algorithm"""
        tag = self.get_selected_algorithm_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select an algorithm to delete")
            return
        
        self.delete_algorithm(tag)

    def delete_algorithm(self, tag):
        """Delete an algorithm from the system"""
        reply = QMessageBox.question(
            self, 'Delete Algorithm',
            f"Are you sure you want to delete algorithm with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.algorithm_manager.remove_algorithm(tag)
            self.refresh_algorithms_list()


class LinearAlgorithmDialog(QDialog):
    """Dialog for creating a Linear algorithm"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Linear Algorithm")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QVBoxLayout(params_group)
        
        # Initial checkbox
        self.initial_checkbox = QCheckBox("Use Initial Stiffness")
        params_layout.addWidget(self.initial_checkbox)
        
        # Factor Once checkbox
        self.factor_once_checkbox = QCheckBox("Factor Matrix Only Once")
        self.factor_once_checkbox.setToolTip("Set up and factor matrix only once")
        params_layout.addWidget(self.factor_once_checkbox)
        
        layout.addWidget(params_group)
        
        # Info box
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel("The Linear algorithm takes one iteration to solve the system of equations. "
                          "It is ideal for linear elastic systems. Note that convergence is not checked.")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_algorithm(self):
        try:
            # Collect parameters
            initial = self.initial_checkbox.isChecked()
            factor_once = self.factor_once_checkbox.isChecked()
            
            # Create algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "linear",
                initial=initial,
                factor_once=factor_once
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class LinearAlgorithmEditDialog(QDialog):
    """Dialog for editing a Linear algorithm"""
    def __init__(self, algorithm, parent=None):
        super().__init__(parent)
        self.algorithm = algorithm
        self.setWindowTitle(f"Edit Linear Algorithm (Tag: {algorithm.tag})")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QVBoxLayout(params_group)
        
        # Initial checkbox
        self.initial_checkbox = QCheckBox("Use Initial Stiffness")
        self.initial_checkbox.setChecked(algorithm.initial)
        params_layout.addWidget(self.initial_checkbox)
        
        # Factor Once checkbox
        self.factor_once_checkbox = QCheckBox("Factor Matrix Only Once")
        self.factor_once_checkbox.setToolTip("Set up and factor matrix only once")
        self.factor_once_checkbox.setChecked(algorithm.factor_once)
        params_layout.addWidget(self.factor_once_checkbox)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_algorithm(self):
        try:
            # Collect parameters
            initial = self.initial_checkbox.isChecked()
            factor_once = self.factor_once_checkbox.isChecked()
            
            # Remove the old algorithm and create a new one with the same tag
            tag = self.algorithm.tag
            self.algorithm_manager.remove_algorithm(tag)
            
            # Create new algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "linear",
                initial=initial,
                factor_once=factor_once
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NewtonAlgorithmDialog(QDialog):
    """Dialog for creating a Newton algorithm"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Newton Algorithm")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QVBoxLayout(params_group)
        
        # Initial checkbox
        self.initial_checkbox = QCheckBox("Use Initial Stiffness")
        self.initial_checkbox.toggled.connect(self.update_checkboxes)
        params_layout.addWidget(self.initial_checkbox)
        
        # Initial Then Current checkbox
        self.initial_then_current_checkbox = QCheckBox("Use Initial Stiffness Then Current")
        self.initial_then_current_checkbox.setToolTip("Use initial stiffness on first step, then current stiffness")
        self.initial_then_current_checkbox.toggled.connect(self.update_checkboxes)
        params_layout.addWidget(self.initial_then_current_checkbox)
        
        layout.addWidget(params_group)
        
        # Info box
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel("The Newton algorithm uses the Newton-Raphson method to solve the nonlinear residual equation. "
                           "It forms the tangent at the current iteration and solves for the displacement increment.")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def update_checkboxes(self, checked):
        """Ensure only one checkbox can be checked at a time"""
        sender = self.sender()
        if checked:
            if sender == self.initial_checkbox:
                self.initial_then_current_checkbox.setChecked(False)
            elif sender == self.initial_then_current_checkbox:
                self.initial_checkbox.setChecked(False)

    def create_algorithm(self):
        try:
            # Collect parameters
            initial = self.initial_checkbox.isChecked()
            initial_then_current = self.initial_then_current_checkbox.isChecked()
            
            # Create algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "newton",
                initial=initial,
                initial_then_current=initial_then_current
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NewtonAlgorithmEditDialog(QDialog):
    """Dialog for editing a Newton algorithm"""
    def __init__(self, algorithm, parent=None):
        super().__init__(parent)
        self.algorithm = algorithm
        self.setWindowTitle(f"Edit Newton Algorithm (Tag: {algorithm.tag})")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QVBoxLayout(params_group)
        
        # Initial checkbox
        self.initial_checkbox = QCheckBox("Use Initial Stiffness")
        self.initial_checkbox.setChecked(algorithm.initial)
        self.initial_checkbox.toggled.connect(self.update_checkboxes)
        params_layout.addWidget(self.initial_checkbox)
        
        # Initial Then Current checkbox
        self.initial_then_current_checkbox = QCheckBox("Use Initial Stiffness Then Current")
        self.initial_then_current_checkbox.setToolTip("Use initial stiffness on first step, then current stiffness")
        self.initial_then_current_checkbox.setChecked(algorithm.initial_then_current)
        self.initial_then_current_checkbox.toggled.connect(self.update_checkboxes)
        params_layout.addWidget(self.initial_then_current_checkbox)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def update_checkboxes(self, checked):
        """Ensure only one checkbox can be checked at a time"""
        sender = self.sender()
        if checked:
            if sender == self.initial_checkbox:
                self.initial_then_current_checkbox.setChecked(False)
            elif sender == self.initial_then_current_checkbox:
                self.initial_checkbox.setChecked(False)

    def save_algorithm(self):
        try:
            # Collect parameters
            initial = self.initial_checkbox.isChecked()
            initial_then_current = self.initial_then_current_checkbox.isChecked()
            
            # Remove the old algorithm and create a new one with the same tag
            tag = self.algorithm.tag
            self.algorithm_manager.remove_algorithm(tag)
            
            # Create new algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "newton",
                initial=initial,
                initial_then_current=initial_then_current
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ModifiedNewtonAlgorithmDialog(QDialog):
    """Dialog for creating a Modified Newton algorithm"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Modified Newton Algorithm")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QVBoxLayout(params_group)
        
        # Initial checkbox
        self.initial_checkbox = QCheckBox("Use Initial Stiffness")
        params_layout.addWidget(self.initial_checkbox)
        
        # Factor Once checkbox
        self.factor_once_checkbox = QCheckBox("Factor Matrix Only Once")
        params_layout.addWidget(self.factor_once_checkbox)
        
        layout.addWidget(params_group)
        
        # Info box
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel("The Modified Newton algorithm uses the modified Newton-Raphson algorithm to solve nonlinear equations. "
                          "It forms the tangent once and uses it for multiple iterations, which can reduce computational cost but may require more iterations.")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_algorithm(self):
        try:
            # Collect parameters
            initial = self.initial_checkbox.isChecked()
            factor_once = self.factor_once_checkbox.isChecked()
            
            # Create algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "modifiednewton",
                initial=initial,
                factor_once=factor_once
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ModifiedNewtonAlgorithmEditDialog(QDialog):
    """Dialog for editing a Modified Newton algorithm"""
    def __init__(self, algorithm, parent=None):
        super().__init__(parent)
        self.algorithm = algorithm
        self.setWindowTitle(f"Edit Modified Newton Algorithm (Tag: {algorithm.tag})")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QVBoxLayout(params_group)
        
        # Initial checkbox
        self.initial_checkbox = QCheckBox("Use Initial Stiffness")
        self.initial_checkbox.setChecked(algorithm.initial)
        params_layout.addWidget(self.initial_checkbox)
        
        # Factor Once checkbox
        self.factor_once_checkbox = QCheckBox("Factor Matrix Only Once")
        self.factor_once_checkbox.setChecked(algorithm.factor_once)
        params_layout.addWidget(self.factor_once_checkbox)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_algorithm(self):
        try:
            # Collect parameters
            initial = self.initial_checkbox.isChecked()
            factor_once = self.factor_once_checkbox.isChecked()
            
            # Remove the old algorithm and create a new one with the same tag
            tag = self.algorithm.tag
            self.algorithm_manager.remove_algorithm(tag)
            
            # Create new algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "modifiednewton",
                initial=initial,
                factor_once=factor_once
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NewtonLineSearchAlgorithmDialog(QDialog):
    """Dialog for creating a NewtonLineSearch algorithm"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Newton Line Search Algorithm")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Type Search combobox
        self.type_search_combo = QComboBox()
        self.type_search_combo.addItems([
            "InitialInterpolated", "Bisection", "Secant", "RegulaFalsi"
        ])
        params_layout.addRow("Search Type:", self.type_search_combo)
        
        # Tolerance
        self.tol_spin = QDoubleSpinBox()
        self.tol_spin.setDecimals(6)
        self.tol_spin.setRange(0.000001, 1.0)
        self.tol_spin.setValue(0.8)
        params_layout.addRow("Tolerance:", self.tol_spin)
        
        # Max Iterations
        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(1, 100)
        self.max_iter_spin.setValue(10)
        params_layout.addRow("Max Iterations:", self.max_iter_spin)
        
        # Min Eta
        self.min_eta_spin = QDoubleSpinBox()
        self.min_eta_spin.setDecimals(6)
        self.min_eta_spin.setRange(0.000001, 1.0)
        self.min_eta_spin.setValue(0.1)
        params_layout.addRow("Min η:", self.min_eta_spin)
        
        # Max Eta
        self.max_eta_spin = QDoubleSpinBox()
        self.max_eta_spin.setDecimals(6)
        self.max_eta_spin.setRange(1.0, 100.0)
        self.max_eta_spin.setValue(10.0)
        params_layout.addRow("Max η:", self.max_eta_spin)
        
        layout.addWidget(params_group)
        
        # Info box
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel("The Newton Line Search algorithm introduces line search to the Newton-Raphson algorithm to "
                          "improve convergence when standard Newton struggles. It modifies the step size via parameter η.")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_algorithm(self):
        try:
            # Collect parameters
            type_search = self.type_search_combo.currentText()
            tol = self.tol_spin.value()
            max_iter = self.max_iter_spin.value()
            min_eta = self.min_eta_spin.value()
            max_eta = self.max_eta_spin.value()
            
            # Create algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "newtonlinesearch",
                type_search=type_search,
                tol=tol,
                max_iter=max_iter,
                min_eta=min_eta,
                max_eta=max_eta
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NewtonLineSearchAlgorithmEditDialog(QDialog):
    """Dialog for editing a NewtonLineSearch algorithm"""
    def __init__(self, algorithm, parent=None):
        super().__init__(parent)
        self.algorithm = algorithm
        self.setWindowTitle(f"Edit Newton Line Search Algorithm (Tag: {algorithm.tag})")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Type Search combobox
        self.type_search_combo = QComboBox()
        self.type_search_combo.addItems([
            "InitialInterpolated", "Bisection", "Secant", "RegulaFalsi"
        ])
        index = self.type_search_combo.findText(algorithm.type_search)
        if index >= 0:
            self.type_search_combo.setCurrentIndex(index)
        params_layout.addRow("Search Type:", self.type_search_combo)
        
        # Tolerance
        self.tol_spin = QDoubleSpinBox()
        self.tol_spin.setDecimals(6)
        self.tol_spin.setRange(0.000001, 1.0)
        self.tol_spin.setValue(algorithm.tol)
        params_layout.addRow("Tolerance:", self.tol_spin)
        
        # Max Iterations
        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(1, 100)
        self.max_iter_spin.setValue(algorithm.max_iter)
        params_layout.addRow("Max Iterations:", self.max_iter_spin)
        
        # Min Eta
        self.min_eta_spin = QDoubleSpinBox()
        self.min_eta_spin.setDecimals(6)
        self.min_eta_spin.setRange(0.000001, 1.0)
        self.min_eta_spin.setValue(algorithm.min_eta)
        params_layout.addRow("Min η:", self.min_eta_spin)
        
        # Max Eta
        self.max_eta_spin = QDoubleSpinBox()
        self.max_eta_spin.setDecimals(6)
        self.max_eta_spin.setRange(1.0, 100.0)
        self.max_eta_spin.setValue(algorithm.max_eta)
        params_layout.addRow("Max η:", self.max_eta_spin)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def save_algorithm(self):
        try:
            # Collect parameters
            type_search = self.type_search_combo.currentText()
            tol = self.tol_spin.value()
            max_iter = self.max_iter_spin.value()
            min_eta = self.min_eta_spin.value()
            max_eta = self.max_eta_spin.value()
            
            # Remove the old algorithm and create a new one with the same tag
            tag = self.algorithm.tag
            self.algorithm_manager.remove_algorithm(tag)
            
            # Create new algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "newtonlinesearch",
                type_search=type_search,
                tol=tol,
                max_iter=max_iter,
                min_eta=min_eta,
                max_eta=max_eta
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))



class KrylovNewtonAlgorithmDialog(QDialog):
    """Dialog for creating a KrylovNewton algorithm"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Krylov-Newton Algorithm")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Tangent Iteration
        self.tang_iter_combo = QComboBox()
        self.tang_iter_combo.addItems(["current", "initial", "noTangent"])
        params_layout.addRow("Tangent to Iterate On:", self.tang_iter_combo)
        
        # Tangent Increment
        self.tang_incr_combo = QComboBox()
        self.tang_incr_combo.addItems(["current", "initial", "noTangent"])
        params_layout.addRow("Tangent to Increment On:", self.tang_incr_combo)
        
        # Max Dimension
        self.max_dim_spin = QSpinBox()
        self.max_dim_spin.setRange(1, 20)
        self.max_dim_spin.setValue(3)
        params_layout.addRow("Max Dimension:", self.max_dim_spin)
        
        layout.addWidget(params_group)
        
        # Info box
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel("The Krylov-Newton algorithm uses a modified Newton method with Krylov subspace acceleration "
                          "to solve nonlinear equations. Useful for dynamic progressive collapse simulations.")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_algorithm(self):
        try:
            # Collect parameters
            tang_iter = self.tang_iter_combo.currentText()
            tang_incr = self.tang_incr_combo.currentText()
            max_dim = self.max_dim_spin.value()
            
            # Create algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "krylovnewton",
                tang_iter=tang_iter,
                tang_incr=tang_incr,
                max_dim=max_dim
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class KrylovNewtonAlgorithmEditDialog(QDialog):
    """Dialog for editing a KrylovNewton algorithm"""
    def __init__(self, algorithm, parent=None):
        super().__init__(parent)
        self.algorithm = algorithm
        self.setWindowTitle(f"Edit Krylov-Newton Algorithm (Tag: {algorithm.tag})")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Tangent Iteration
        self.tang_iter_combo = QComboBox()
        self.tang_iter_combo.addItems(["current", "initial", "noTangent"])
        index = self.tang_iter_combo.findText(algorithm.tang_iter)
        if index >= 0:
            self.tang_iter_combo.setCurrentIndex(index)
        params_layout.addRow("Tangent to Iterate On:", self.tang_iter_combo)
        
        # Tangent Increment
        self.tang_incr_combo = QComboBox()
        self.tang_incr_combo.addItems(["current", "initial", "noTangent"])
        index = self.tang_incr_combo.findText(algorithm.tang_incr)
        if index >= 0:
            self.tang_incr_combo.setCurrentIndex(index)
        params_layout.addRow("Tangent to Increment On:", self.tang_incr_combo)
        
        # Max Dimension
        self.max_dim_spin = QSpinBox()
        self.max_dim_spin.setRange(1, 20)
        self.max_dim_spin.setValue(algorithm.max_dim)
        params_layout.addRow("Max Dimension:", self.max_dim_spin)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_algorithm(self):
        try:
            # Collect parameters
            tang_iter = self.tang_iter_combo.currentText()
            tang_incr = self.tang_incr_combo.currentText()
            max_dim = self.max_dim_spin.value()
            
            # Remove the old algorithm and create a new one with the same tag
            tag = self.algorithm.tag
            self.algorithm_manager.remove_algorithm(tag)
            
            # Create new algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "krylovnewton",
                tang_iter=tang_iter,
                tang_incr=tang_incr,
                max_dim=max_dim
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class SecantNewtonAlgorithmDialog(QDialog):
    """Dialog for creating a SecantNewton algorithm"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Secant Newton Algorithm")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Tangent Iteration
        self.tang_iter_combo = QComboBox()
        self.tang_iter_combo.addItems(["current", "initial", "noTangent"])
        params_layout.addRow("Tangent to Iterate On:", self.tang_iter_combo)
        
        # Tangent Increment
        self.tang_incr_combo = QComboBox()
        self.tang_incr_combo.addItems(["current", "initial", "noTangent"])
        params_layout.addRow("Tangent to Increment On:", self.tang_incr_combo)
        
        # Max Dimension
        self.max_dim_spin = QSpinBox()
        self.max_dim_spin.setRange(1, 20)
        self.max_dim_spin.setValue(3)
        params_layout.addRow("Max Dimension:", self.max_dim_spin)
        
        layout.addWidget(params_group)
        
        # Info box
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel("The Secant Newton algorithm uses a two-term update to accelerate "
                           "the convergence of the modified Newton method. It uses Crisfield's "
                           "default 'cut-out' values (R1=3.5, R2=0.3).")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_algorithm(self):
        try:
            # Collect parameters
            tang_iter = self.tang_iter_combo.currentText()
            tang_incr = self.tang_incr_combo.currentText()
            max_dim = self.max_dim_spin.value()
            
            # Create algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "secantnewton",
                tang_iter=tang_iter,
                tang_incr=tang_incr,
                max_dim=max_dim
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class SecantNewtonAlgorithmEditDialog(QDialog):
    """Dialog for editing a SecantNewton algorithm"""
    def __init__(self, algorithm, parent=None):
        super().__init__(parent)
        self.algorithm = algorithm
        self.setWindowTitle(f"Edit Secant Newton Algorithm (Tag: {algorithm.tag})")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Tangent Iteration
        self.tang_iter_combo = QComboBox()
        self.tang_iter_combo.addItems(["current", "initial", "noTangent"])
        index = self.tang_iter_combo.findText(algorithm.tang_iter)
        if index >= 0:
            self.tang_iter_combo.setCurrentIndex(index)
        params_layout.addRow("Tangent to Iterate On:", self.tang_iter_combo)
        
        # Tangent Increment
        self.tang_incr_combo = QComboBox()
        self.tang_incr_combo.addItems(["current", "initial", "noTangent"])
        index = self.tang_incr_combo.findText(algorithm.tang_incr)
        if index >= 0:
            self.tang_incr_combo.setCurrentIndex(index)
        params_layout.addRow("Tangent to Increment On:", self.tang_incr_combo)
        
        # Max Dimension
        self.max_dim_spin = QSpinBox()
        self.max_dim_spin.setRange(1, 20)
        self.max_dim_spin.setValue(algorithm.max_dim)
        params_layout.addRow("Max Dimension:", self.max_dim_spin)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_algorithm(self):
        try:
            # Collect parameters
            tang_iter = self.tang_iter_combo.currentText()
            tang_incr = self.tang_incr_combo.currentText()
            max_dim = self.max_dim_spin.value()
            
            # Remove the old algorithm and create a new one with the same tag
            tag = self.algorithm.tag
            self.algorithm_manager.remove_algorithm(tag)
            
            # Create new algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "secantnewton",
                tang_iter=tang_iter,
                tang_incr=tang_incr,
                max_dim=max_dim
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class BFGSAlgorithmDialog(QDialog):
    """Dialog for creating a BFGS algorithm"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create BFGS Algorithm")
        self.algorithm_manager = AlgorithmManager()
        self.int_validator = IntValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Count
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(10)
        params_layout.addRow("Count:", self.count_spin)
        
        layout.addWidget(params_group)
        
        # Info box
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel("The BFGS algorithm performs successive rank-two updates of the tangent. "
                          "It is suitable for symmetric systems. The 'count' parameter represents "
                          "the number of iterations within a time step until a new tangent is formed.")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_algorithm(self):
        try:
            # Collect parameters
            count = self.count_spin.value()
            
            # Create algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "bfgs",
                count=count
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class BFGSAlgorithmEditDialog(QDialog):
    """Dialog for editing a BFGS algorithm"""
    def __init__(self, algorithm, parent=None):
        super().__init__(parent)
        self.algorithm = algorithm
        self.setWindowTitle(f"Edit BFGS Algorithm (Tag: {algorithm.tag})")
        self.algorithm_manager = AlgorithmManager()
        self.int_validator = IntValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Count
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(algorithm.count)
        params_layout.addRow("Count:", self.count_spin)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_algorithm(self):
        try:
            # Collect parameters
            count = self.count_spin.value()
            
            # Remove the old algorithm and create a new one with the same tag
            tag = self.algorithm.tag
            self.algorithm_manager.remove_algorithm(tag)
            
            # Create new algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "bfgs",
                count=count
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class BroydenAlgorithmDialog(QDialog):
    """Dialog for creating a Broyden algorithm"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Broyden Algorithm")
        self.algorithm_manager = AlgorithmManager()
        self.int_validator = IntValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Count
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(10)
        params_layout.addRow("Count:", self.count_spin)
        
        layout.addWidget(params_group)
        
        # Info box
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel("The Broyden algorithm performs successive rank-one updates of the tangent. "
                          "It is suitable for general unsymmetric systems. The 'count' parameter represents "
                          "the number of iterations within a time step until a new tangent is formed.")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_algorithm(self):
        try:
            # Collect parameters
            count = self.count_spin.value()
            
            # Create algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "broyden",
                count=count
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class BroydenAlgorithmEditDialog(QDialog):
    """Dialog for editing a Broyden algorithm"""
    def __init__(self, algorithm, parent=None):
        super().__init__(parent)
        self.algorithm = algorithm
        self.setWindowTitle(f"Edit Broyden Algorithm (Tag: {algorithm.tag})")
        self.algorithm_manager = AlgorithmManager()
        self.int_validator = IntValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Count
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(algorithm.count)
        params_layout.addRow("Count:", self.count_spin)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_algorithm(self):
        try:
            # Collect parameters
            count = self.count_spin.value()
            
            # Remove the old algorithm and create a new one with the same tag
            tag = self.algorithm.tag
            self.algorithm_manager.remove_algorithm(tag)
            
            # Create new algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "broyden",
                count=count
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ExpressNewtonAlgorithmDialog(QDialog):
    """Dialog for creating an ExpressNewton algorithm"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create ExpressNewton Algorithm")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Iteration Count
        self.iter_count_spin = QSpinBox()
        self.iter_count_spin.setRange(1, 100)
        self.iter_count_spin.setValue(2)
        params_layout.addRow("Iteration Count:", self.iter_count_spin)
        
        # K Multiplier
        self.k_multiplier_spin = QDoubleSpinBox()
        self.k_multiplier_spin.setDecimals(3)
        self.k_multiplier_spin.setRange(0.001, 10.0)
        self.k_multiplier_spin.setValue(1.0)
        params_layout.addRow("K Multiplier:", self.k_multiplier_spin)
        
        # Tangent options
        self.initial_tangent_checkbox = QCheckBox()
        self.initial_tangent_checkbox.toggled.connect(self.update_tangent_options)
        params_layout.addRow("Use Initial Tangent:", self.initial_tangent_checkbox)
        
        self.current_tangent_checkbox = QCheckBox()
        self.current_tangent_checkbox.setChecked(True)
        self.current_tangent_checkbox.toggled.connect(self.update_tangent_options)
        params_layout.addRow("Use Current Tangent:", self.current_tangent_checkbox)
        
        # Factor Once
        self.factor_once_checkbox = QCheckBox()
        params_layout.addRow("Factor Matrix Only Once:", self.factor_once_checkbox)
        
        layout.addWidget(params_group)
        
        # Info box
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel("The ExpressNewton algorithm accepts the solution after a constant number of "
                           "Newton-Raphson iterations using a constant system Jacobian matrix. It is "
                           "advised to be used with transient integrators only. Note that there is no "
                           "check on the convergence in this algorithm.")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def update_tangent_options(self, checked):
        """Ensure only one tangent option is checked at a time"""
        sender = self.sender()
        if checked:
            if sender == self.initial_tangent_checkbox:
                self.current_tangent_checkbox.setChecked(False)
            elif sender == self.current_tangent_checkbox:
                self.initial_tangent_checkbox.setChecked(False)

    def create_algorithm(self):
        try:
            # Collect parameters
            iter_count = self.iter_count_spin.value()
            k_multiplier = self.k_multiplier_spin.value()
            initial_tangent = self.initial_tangent_checkbox.isChecked()
            current_tangent = self.current_tangent_checkbox.isChecked()
            factor_once = self.factor_once_checkbox.isChecked()
            
            # Create algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "expressnewton",
                iter_count=iter_count,
                k_multiplier=k_multiplier,
                initial_tangent=initial_tangent,
                current_tangent=current_tangent,
                factor_once=factor_once
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ExpressNewtonAlgorithmEditDialog(QDialog):
    """Dialog for editing an ExpressNewton algorithm"""
    def __init__(self, algorithm, parent=None):
        super().__init__(parent)
        self.algorithm = algorithm
        self.setWindowTitle(f"Edit ExpressNewton Algorithm (Tag: {algorithm.tag})")
        self.algorithm_manager = AlgorithmManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Iteration Count
        self.iter_count_spin = QSpinBox()
        self.iter_count_spin.setRange(1, 100)
        self.iter_count_spin.setValue(algorithm.iter_count)
        params_layout.addRow("Iteration Count:", self.iter_count_spin)
        
        # K Multiplier
        self.k_multiplier_spin = QDoubleSpinBox()
        self.k_multiplier_spin.setDecimals(3)
        self.k_multiplier_spin.setRange(0.001, 10.0)
        self.k_multiplier_spin.setValue(algorithm.k_multiplier)
        params_layout.addRow("K Multiplier:", self.k_multiplier_spin)
        
        # Tangent options
        self.initial_tangent_checkbox = QCheckBox()
        self.initial_tangent_checkbox.setChecked(algorithm.initial_tangent)
        self.initial_tangent_checkbox.toggled.connect(self.update_tangent_options)
        params_layout.addRow("Use Initial Tangent:", self.initial_tangent_checkbox)
        
        self.current_tangent_checkbox = QCheckBox()
        self.current_tangent_checkbox.setChecked(algorithm.current_tangent)
        self.current_tangent_checkbox.toggled.connect(self.update_tangent_options)
        params_layout.addRow("Use Current Tangent:", self.current_tangent_checkbox)
        
        # Factor Once
        self.factor_once_checkbox = QCheckBox()
        self.factor_once_checkbox.setChecked(algorithm.factor_once)
        params_layout.addRow("Factor Matrix Only Once:", self.factor_once_checkbox)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_algorithm)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def update_tangent_options(self, checked):
        """Ensure only one tangent option is checked at a time"""
        sender = self.sender()
        if checked:
            if sender == self.initial_tangent_checkbox:
                self.current_tangent_checkbox.setChecked(False)
            elif sender == self.current_tangent_checkbox:
                self.initial_tangent_checkbox.setChecked(False)

    def save_algorithm(self):
        try:
            # Collect parameters
            iter_count = self.iter_count_spin.value()
            k_multiplier = self.k_multiplier_spin.value()
            initial_tangent = self.initial_tangent_checkbox.isChecked()
            current_tangent = self.current_tangent_checkbox.isChecked()
            factor_once = self.factor_once_checkbox.isChecked()
            
            # Remove the old algorithm and create a new one with the same tag
            tag = self.algorithm.tag
            self.algorithm_manager.remove_algorithm(tag)
            
            # Create new algorithm
            self.algorithm = self.algorithm_manager.create_algorithm(
                "expressnewton",
                iter_count=iter_count,
                k_multiplier=k_multiplier,
                initial_tangent=initial_tangent,
                current_tangent=current_tangent,
                factor_once=factor_once
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == '__main__':
    from qtpy.QtWidgets import QApplication
    import sys
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    window = AlgorithmManagerTab()
    window.show()
    sys.exit(app.exec_())