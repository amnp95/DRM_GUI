from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout,
    QCheckBox, QGroupBox, QDoubleSpinBox, QRadioButton, QSpinBox
)

from meshmaker.utils.validator import DoubleValidator, IntValidator
from meshmaker.components.Analysis.convergenceTests import (
    Test, TestManager, 
    NormUnbalanceTest, NormDispIncrTest,
    EnergyIncrTest, RelativeNormUnbalanceTest,
    RelativeNormDispIncrTest, RelativeTotalNormDispIncrTest,
    RelativeEnergyIncrTest, FixedNumIterTest,
    NormDispAndUnbalanceTest, NormDispOrUnbalanceTest
)

class TestManagerTab(QDialog):
    """
    Main dialog for managing convergence tests
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup dialog properties
        self.setWindowTitle("Convergence Test Manager")
        self.resize(800, 500)
        
        # Get the test manager instance
        self.test_manager = TestManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Test type selection
        type_layout = QGridLayout()
        
        # Test type dropdown
        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems(self.test_manager.get_available_types())
        
        create_test_btn = QPushButton("Create New Test")
        create_test_btn.clicked.connect(self.open_test_creation_dialog)
        
        type_layout.addWidget(QLabel("Test Type:"), 0, 0)
        type_layout.addWidget(self.test_type_combo, 0, 1)
        type_layout.addWidget(create_test_btn, 1, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Info box for test description
        info_group = QGroupBox("Test Description")
        info_layout = QVBoxLayout(info_group)
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        layout.addWidget(info_group)
        
        # Update info label when test type changes
        self.test_type_combo.currentTextChanged.connect(self.update_info_text)
        # Initialize with the first test type
        self.update_info_text(self.test_type_combo.currentText())
        
        # Tests table
        self.tests_table = QTableWidget()
        self.tests_table.setColumnCount(4)  # Select, Tag, Type, Parameters
        self.tests_table.setHorizontalHeaderLabels(["Select", "Tag", "Type", "Parameters"])
        self.tests_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tests_table.setSelectionMode(QTableWidget.SingleSelection)
        header = self.tests_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.tests_table)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_test)
        
        self.delete_selected_btn = QPushButton("Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_test)
        
        refresh_btn = QPushButton("Refresh Tests List")
        refresh_btn.clicked.connect(self.refresh_tests_list)
        
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_selected_btn)
        buttons_layout.addWidget(refresh_btn)
        
        layout.addLayout(buttons_layout)
        
        # Initial refresh
        self.refresh_tests_list()
        
        # Disable edit/delete buttons initially
        self.update_button_state()

    def update_info_text(self, test_type: str):
        """Update the info text based on the selected test type"""
        descriptions = {
            "normunbalance": "Checks the norm of the right-hand side (unbalanced forces) vector against a tolerance. "
                            "Useful for checking overall system equilibrium, but sensitive to large penalty constraint forces.",
            
            "normdispincr": "Checks the norm of the displacement increment vector against a tolerance. "
                           "Measures displacement change and useful for tracking solution convergence.",
            
            "energyincr": "Checks the energy increment (0.5 * x^T * b) against a tolerance. "
                         "Provides energy-based convergence assessment, useful for problems with energy-critical behaviors.",
            
            "relativenormunbalance": "Compares current unbalance norm to initial unbalance norm. "
                                    "Requires at least two iterations and can be sensitive to initial conditions.",
            
            "relativenormdispincr": "Compares current displacement increment norm to initial norm. "
                                   "Tracks relative changes in displacement.",
            
            "relativetotalnormdispincr": "Uses ratio of current norm to total norm (sum of norms since last convergence). "
                                        "Tracks cumulative displacement changes and provides more comprehensive tracking.",
            
            "relativeenergyincr": "Compares energy increment relative to first iteration. "
                                 "Provides energy-based relative convergence assessment.",
            
            "fixednumiter": "Runs a fixed number of iterations with no convergence check. "
                           "Useful for specific analytical requirements.",
            
            "normdispandunbalance": "Simultaneously checks displacement increment and unbalanced force norms. "
                                   "Requires BOTH displacement and unbalance norms to converge.",
            
            "normdisporunbalance": "Convergence achieved if EITHER displacement OR unbalance norm criterion is met. "
                                  "More flexible than the AND condition."
        }
        
        test_type = test_type.lower()
        if test_type in descriptions:
            self.info_label.setText(descriptions[test_type])
        else:
            self.info_label.setText("No description available for this test type.")

    def refresh_tests_list(self):
        """Update the tests table with current tests"""
        self.tests_table.setRowCount(0)
        tests = self.test_manager.get_all_tests()
        
        self.tests_table.setRowCount(len(tests))
        self.radio_buttons = []
        
        # Hide vertical header (row indices)
        self.tests_table.verticalHeader().setVisible(False)
        
        for row, (tag, test) in enumerate(tests.items()):
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
            self.tests_table.setCellWidget(row, 0, radio_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.tests_table.setItem(row, 1, tag_item)
            
            # Test Type
            type_item = QTableWidgetItem(test.test_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.tests_table.setItem(row, 2, type_item)
            
            # Parameters
            params = test.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.tests_table.setItem(row, 3, params_item)
        
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

    def get_selected_test_tag(self):
        """Get the tag of the selected test"""
        for row, radio_btn in enumerate(self.radio_buttons):
            if radio_btn.isChecked():
                tag_item = self.tests_table.item(row, 1)
                return int(tag_item.text())
        return None

    def open_test_creation_dialog(self):
        """Open dialog to create a new test of selected type"""
        test_type = self.test_type_combo.currentText().lower()
        
        dialog = None
        
        if test_type == "normunbalance":
            dialog = NormUnbalanceTestDialog(self)
        elif test_type == "normdispincr":
            dialog = NormDispIncrTestDialog(self)
        elif test_type == "energyincr":
            dialog = EnergyIncrTestDialog(self)
        elif test_type == "relativenormunbalance":
            dialog = RelativeNormUnbalanceTestDialog(self)
        elif test_type == "relativenormdispincr":
            dialog = RelativeNormDispIncrTestDialog(self)
        elif test_type == "relativetotalnormdispincr":
            dialog = RelativeTotalNormDispIncrTestDialog(self)
        elif test_type == "relativeenergyincr":
            dialog = RelativeEnergyIncrTestDialog(self)
        elif test_type == "fixednumiter":
            dialog = FixedNumIterTestDialog(self)
        elif test_type == "normdispandunbalance":
            dialog = NormDispAndUnbalanceTestDialog(self)
        elif test_type == "normdisporunbalance":
            dialog = NormDispOrUnbalanceTestDialog(self)
        else:
            QMessageBox.warning(self, "Error", f"No creation dialog available for test type: {test_type}")
            return
        
        if dialog.exec() == QDialog.Accepted:
            self.refresh_tests_list()

    def edit_selected_test(self):
        """Edit the selected test"""
        tag = self.get_selected_test_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select a test to edit")
            return
        
        try:
            test = self.test_manager.get_test(tag)
            
            dialog = None
            test_type = test.test_type.lower()
            
            if test_type == "normunbalance":
                dialog = NormUnbalanceTestEditDialog(test, self)
            elif test_type == "normdispincr":
                dialog = NormDispIncrTestEditDialog(test, self)
            elif test_type == "energyincr":
                dialog = EnergyIncrTestEditDialog(test, self)
            elif test_type == "relativenormunbalance":
                dialog = RelativeNormUnbalanceTestEditDialog(test, self)
            elif test_type == "relativenormdispincr":
                dialog = RelativeNormDispIncrTestEditDialog(test, self)
            elif test_type == "relativetotalnormdispincr":
                dialog = RelativeTotalNormDispIncrTestEditDialog(test, self)
            elif test_type == "relativeenergyincr":
                dialog = RelativeEnergyIncrTestEditDialog(test, self)
            elif test_type == "fixednumiter":
                dialog = FixedNumIterTestEditDialog(test, self)
            elif test_type == "normdispandunbalance":
                dialog = NormDispAndUnbalanceTestEditDialog(test, self)
            elif test_type == "normdisporunbalance":
                dialog = NormDispOrUnbalanceTestEditDialog(test, self)
            else:
                QMessageBox.warning(self, "Error", f"No edit dialog available for test type: {test_type}")
                return
            
            if dialog.exec() == QDialog.Accepted:
                self.refresh_tests_list()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected_test(self):
        """Delete the selected test"""
        tag = self.get_selected_test_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select a test to delete")
            return
        
        self.delete_test(tag)

    def delete_test(self, tag):
        """Delete a test from the system"""
        reply = QMessageBox.question(
            self, 'Delete Test',
            f"Are you sure you want to delete test with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.test_manager.remove_test(tag)
            self.refresh_tests_list()

#------------------------------------------------------
# Base Test Dialog Classes
#------------------------------------------------------

class BaseTestDialog(QDialog):
    """Base dialog for creating and editing tests with common fields"""
    def __init__(self, parent=None, title="Test Dialog"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.test_manager = TestManager()
        
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Parameters group
        self.params_group = QGroupBox("Parameters")
        self.params_layout = QFormLayout(self.params_group)
        self.layout.addWidget(self.params_group)
        
        # Buttons
        self.btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_test)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.btn_layout.addWidget(self.save_btn)
        self.btn_layout.addWidget(self.cancel_btn)
        
        # Add button layout at the end after subclass adds its fields
    
    def add_button_layout(self):
        """Add button layout to main layout - call this after adding all fields"""
        self.layout.addLayout(self.btn_layout)
    
    def save_test(self):
        """Placeholder for save method to be implemented by subclasses"""
        pass


class BaseNormTestDialog(BaseTestDialog):
    """Base dialog for tests that use norm type and print flag"""
    def __init__(self, parent=None, title="Norm Test Dialog"):
        super().__init__(parent, title)
        
        # Tolerance parameter
        self.tol_spin = QDoubleSpinBox()
        self.tol_spin.setDecimals(6)
        self.tol_spin.setRange(1e-12, 1.0)
        self.tol_spin.setValue(1e-6)
        self.params_layout.addRow("Tolerance:", self.tol_spin)
        
        # Max iterations parameter
        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(1, 1000)
        self.max_iter_spin.setValue(25)
        self.params_layout.addRow("Max Iterations:", self.max_iter_spin)
        
        # Print flag parameter
        self.print_flag_combo = QComboBox()
        self.print_flag_combo.addItems([
            "0: Print nothing",
            "1: Print norm information each iteration",
            "2: Print norms and iterations at successful test",
            "4: Print norms, displacement vector, and residual vector",
            "5: Print error message but return successful test"
        ])
        self.params_layout.addRow("Print Flag:", self.print_flag_combo)
        
        # Norm type parameter
        self.norm_type_combo = QComboBox()
        self.norm_type_combo.addItems([
            "0: Max-norm",
            "1: 1-norm",
            "2: 2-norm (default)"
        ])
        self.norm_type_combo.setCurrentIndex(2)  # Set default to 2-norm
        self.params_layout.addRow("Norm Type:", self.norm_type_combo)
        
        # Add button layout
        self.add_button_layout()
    
    def get_params(self):
        """Get common parameters from the dialog"""
        tol = self.tol_spin.value()
        max_iter = self.max_iter_spin.value()
        print_flag = int(self.print_flag_combo.currentText().split(":")[0])
        norm_type = int(self.norm_type_combo.currentText().split(":")[0])
        
        return {
            "tol": tol,
            "max_iter": max_iter,
            "print_flag": print_flag,
            "norm_type": norm_type
        }


class BaseEnergyTestDialog(BaseTestDialog):
    """Base dialog for energy tests"""
    def __init__(self, parent=None, title="Energy Test Dialog"):
        super().__init__(parent, title)
        
        # Tolerance parameter
        self.tol_spin = QDoubleSpinBox()
        self.tol_spin.setDecimals(6)
        self.tol_spin.setRange(1e-12, 1.0)
        self.tol_spin.setValue(1e-6)
        self.params_layout.addRow("Tolerance:", self.tol_spin)
        
        # Max iterations parameter
        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(1, 1000)
        self.max_iter_spin.setValue(25)
        self.params_layout.addRow("Max Iterations:", self.max_iter_spin)
        
        # Print flag parameter
        self.print_flag_combo = QComboBox()
        self.print_flag_combo.addItems([
            "0: Print nothing",
            "1: Print norm information each iteration",
            "2: Print norms and iterations at successful test",
            "4: Print norms, displacement vector, and residual vector",
            "5: Print error message but return successful test"
        ])
        self.params_layout.addRow("Print Flag:", self.print_flag_combo)
        
        # Add button layout
        self.add_button_layout()
    
    def get_params(self):
        """Get common parameters from the dialog"""
        tol = self.tol_spin.value()
        max_iter = self.max_iter_spin.value()
        print_flag = int(self.print_flag_combo.currentText().split(":")[0])
        
        return {
            "tol": tol,
            "max_iter": max_iter,
            "print_flag": print_flag
        }


class BaseCombinedNormTestDialog(BaseTestDialog):
    """Base dialog for tests that use two tolerances"""
    def __init__(self, parent=None, title="Combined Norm Test Dialog"):
        super().__init__(parent, title)
        
        # Displacement tolerance parameter
        self.tol_incr_spin = QDoubleSpinBox()
        self.tol_incr_spin.setDecimals(6)
        self.tol_incr_spin.setRange(1e-12, 1.0)
        self.tol_incr_spin.setValue(1e-6)
        self.params_layout.addRow("Displacement Tolerance:", self.tol_incr_spin)
        
        # Residual tolerance parameter
        self.tol_r_spin = QDoubleSpinBox()
        self.tol_r_spin.setDecimals(6)
        self.tol_r_spin.setRange(1e-12, 1.0)
        self.tol_r_spin.setValue(1e-6)
        self.params_layout.addRow("Residual Tolerance:", self.tol_r_spin)
        
        # Max iterations parameter
        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(1, 1000)
        self.max_iter_spin.setValue(25)
        self.params_layout.addRow("Max Iterations:", self.max_iter_spin)
        
        # Print flag parameter
        self.print_flag_combo = QComboBox()
        self.print_flag_combo.addItems([
            "0: Print nothing",
            "1: Print norm information each iteration",
            "2: Print norms and iterations at successful test",
            "4: Print norms, displacement vector, and residual vector",
            "5: Print error message but return successful test"
        ])
        self.params_layout.addRow("Print Flag:", self.print_flag_combo)
        
        # Norm type parameter
        self.norm_type_combo = QComboBox()
        self.norm_type_combo.addItems([
            "0: Max-norm",
            "1: 1-norm",
            "2: 2-norm (default)"
        ])
        self.norm_type_combo.setCurrentIndex(2)  # Set default to 2-norm
        self.params_layout.addRow("Norm Type:", self.norm_type_combo)
        
        # Max increment parameter
        self.max_incr_spin = QSpinBox()
        self.max_incr_spin.setRange(-1, 1000)
        self.max_incr_spin.setValue(-1)
        self.params_layout.addRow("Max Error Increase (-1 for default):", self.max_incr_spin)
        
        # Add button layout
        self.add_button_layout()
    
    def get_params(self):
        """Get common parameters from the dialog"""
        tol_incr = self.tol_incr_spin.value()
        tol_r = self.tol_r_spin.value()
        max_iter = self.max_iter_spin.value()
        print_flag = int(self.print_flag_combo.currentText().split(":")[0])
        norm_type = int(self.norm_type_combo.currentText().split(":")[0])
        max_incr = self.max_incr_spin.value()
        
        return {
            "tol_incr": tol_incr,
            "tol_r": tol_r,
            "max_iter": max_iter,
            "print_flag": print_flag,
            "norm_type": norm_type,
            "max_incr": max_incr
        }


#------------------------------------------------------
# Test Dialog Classes - Creation
#------------------------------------------------------

class NormUnbalanceTestDialog(BaseNormTestDialog):
    """Dialog for creating a Norm Unbalance test"""
    def __init__(self, parent=None):
        super().__init__(parent, "Create Norm Unbalance Test")
        
        # Additional info
        info = QLabel("The NormUnbalance test checks the norm of the right-hand side (unbalanced forces) vector "
                     "against a tolerance. Useful for checking overall system equilibrium.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Create test
            self.test = self.test_manager.create_test(
                "normunbalance",
                tol=params["tol"],
                max_iter=params["max_iter"],
                print_flag=params["print_flag"],
                norm_type=params["norm_type"]
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NormDispIncrTestDialog(BaseNormTestDialog):
    """Dialog for creating a Norm Displacement Increment test"""
    def __init__(self, parent=None):
        super().__init__(parent, "Create Norm Displacement Increment Test")
        
        # Additional info
        info = QLabel("The NormDispIncr test checks the norm of the displacement increment vector "
                     "against a tolerance. Useful for tracking solution convergence.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Create test
            self.test = self.test_manager.create_test(
                "normdispincr",
                tol=params["tol"],
                max_iter=params["max_iter"],
                print_flag=params["print_flag"],
                norm_type=params["norm_type"]
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class EnergyIncrTestDialog(BaseEnergyTestDialog):
    """Dialog for creating an Energy Increment test"""
    def __init__(self, parent=None):
        super().__init__(parent, "Create Energy Increment Test")
        
        # Additional info
        info = QLabel("The EnergyIncr test checks the energy increment (0.5 * x^T * b) against a tolerance. "
                     "Useful for problems with energy-critical behaviors.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Create test
            self.test = self.test_manager.create_test(
                "energyincr",
                tol=params["tol"],
                max_iter=params["max_iter"],
                print_flag=params["print_flag"]
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class RelativeNormUnbalanceTestDialog(BaseNormTestDialog):
    """Dialog for creating a Relative Norm Unbalance test"""
    def __init__(self, parent=None):
        super().__init__(parent, "Create Relative Norm Unbalance Test")
        
        # Additional info
        info = QLabel("The RelativeNormUnbalance test compares current unbalance to initial unbalance. "
                     "Requires at least two iterations and can be sensitive to initial conditions.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Create test
            self.test = self.test_manager.create_test(
                "relativenormunbalance",
                tol=params["tol"],
                max_iter=params["max_iter"],
                print_flag=params["print_flag"],
                norm_type=params["norm_type"]
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class RelativeNormDispIncrTestDialog(BaseNormTestDialog):
    """Dialog for creating a Relative Norm Displacement Increment test"""
    def __init__(self, parent=None):
        super().__init__(parent, "Create Relative Norm Displacement Increment Test")
        
        # Additional info
        info = QLabel("The RelativeNormDispIncr test compares current displacement increment to initial. "
                     "Tracks relative changes in displacement.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Create test
            self.test = self.test_manager.create_test(
                "relativenormdispincr",
                tol=params["tol"],
                max_iter=params["max_iter"],
                print_flag=params["print_flag"],
                norm_type=params["norm_type"]
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class RelativeTotalNormDispIncrTestDialog(BaseNormTestDialog):
    """Dialog for creating a Relative Total Norm Displacement Increment test"""
    def __init__(self, parent=None):
        super().__init__(parent, "Create Relative Total Norm Displacement Increment Test")
        
        # Additional info
        info = QLabel("The RelativeTotalNormDispIncr test uses ratio of current norm to total norm "
                     "(sum of norms since last convergence). Tracks cumulative displacement changes.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Create test
            self.test = self.test_manager.create_test(
                "relativetotalnormdispincr",
                tol=params["tol"],
                max_iter=params["max_iter"],
                print_flag=params["print_flag"],
                norm_type=params["norm_type"]
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class RelativeEnergyIncrTestDialog(BaseEnergyTestDialog):
    """Dialog for creating a Relative Energy Increment test"""
    def __init__(self, parent=None):
        super().__init__(parent, "Create Relative Energy Increment Test")
        
        # Additional info
        info = QLabel("The RelativeEnergyIncr test compares energy increment relative to first iteration. "
                     "Provides energy-based relative convergence assessment.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Create test
            self.test = self.test_manager.create_test(
                "relativeenergyincr",
                tol=params["tol"],
                max_iter=params["max_iter"],
                print_flag=params["print_flag"]
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class FixedNumIterTestDialog(BaseTestDialog):
    """Dialog for creating a Fixed Number of Iterations test"""
    def __init__(self, parent=None):
        super().__init__(parent, "Create Fixed Number of Iterations Test")
        
        # Additional info
        info = QLabel("The FixedNumIter test runs a fixed number of iterations with no convergence check. "
                     "Useful for specific analytical requirements.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
        
        # Number of iterations parameter
        self.num_iter_spin = QSpinBox()
        self.num_iter_spin.setRange(1, 1000)
        self.num_iter_spin.setValue(10)
        self.params_layout.addRow("Number of Iterations:", self.num_iter_spin)
        
        # Add button layout
        self.add_button_layout()
    
    def save_test(self):
        try:
            # Create test
            self.test = self.test_manager.create_test(
                "fixednumiter",
                num_iter=self.num_iter_spin.value()
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NormDispAndUnbalanceTestDialog(BaseCombinedNormTestDialog):
    """Dialog for creating a Norm Displacement AND Unbalance test"""
    def __init__(self, parent=None):
        super().__init__(parent, "Create Norm Displacement AND Unbalance Test")
        
        # Additional info
        info = QLabel("The NormDispAndUnbalance test simultaneously checks displacement increment and unbalanced force norms. "
                      "Requires BOTH displacement and unbalance norms to converge.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Create test
            self.test = self.test_manager.create_test(
                "normdispandunbalance",
                tol_incr=params["tol_incr"],
                tol_r=params["tol_r"],
                max_iter=params["max_iter"],
                print_flag=params["print_flag"],
                norm_type=params["norm_type"],
                max_incr=params["max_incr"]
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NormDispOrUnbalanceTestDialog(BaseCombinedNormTestDialog):
    """Dialog for creating a Norm Displacement OR Unbalance test"""
    def __init__(self, parent=None):
        super().__init__(parent, "Create Norm Displacement OR Unbalance Test")
        
        # Additional info
        info = QLabel("The NormDispOrUnbalance test checks displacement increment or unbalanced force norms. "
                      "Convergence achieved if EITHER displacement OR unbalance norm criterion is met.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Create test
            self.test = self.test_manager.create_test(
                "normdisporunbalance",
                tol_incr=params["tol_incr"],
                tol_r=params["tol_r"],
                max_iter=params["max_iter"],
                print_flag=params["print_flag"],
                norm_type=params["norm_type"],
                max_incr=params["max_incr"]
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


#------------------------------------------------------
# Test Dialog Classes - Editing Existing Tests
#------------------------------------------------------

class NormUnbalanceTestEditDialog(BaseNormTestDialog):
    """Dialog for editing a Norm Unbalance test"""
    def __init__(self, test: NormUnbalanceTest, parent=None):
        super().__init__(parent, "Edit Norm Unbalance Test")
        self.test = test
        
        # Fill in existing values
        self.tol_spin.setValue(test.tol)
        self.max_iter_spin.setValue(test.max_iter)
        self.print_flag_combo.setCurrentIndex(min(test.print_flag, self.print_flag_combo.count()-1))
        self.norm_type_combo.setCurrentIndex(min(test.norm_type, self.norm_type_combo.count()-1))
        
        # Additional info
        info = QLabel("The NormUnbalance test checks the norm of the right-hand side (unbalanced forces) vector "
                     "against a tolerance. Useful for checking overall system equilibrium.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Update test parameters
            self.test.tol = params["tol"]
            self.test.max_iter = params["max_iter"]
            self.test.print_flag = params["print_flag"]
            self.test.norm_type = params["norm_type"]
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NormDispIncrTestEditDialog(BaseNormTestDialog):
    """Dialog for editing a Norm Displacement Increment test"""
    def __init__(self, test: NormDispIncrTest, parent=None):
        super().__init__(parent, "Edit Norm Displacement Increment Test")
        self.test = test
        
        # Fill in existing values
        self.tol_spin.setValue(test.tol)
        self.max_iter_spin.setValue(test.max_iter)
        self.print_flag_combo.setCurrentIndex(min(test.print_flag, self.print_flag_combo.count()-1))
        self.norm_type_combo.setCurrentIndex(min(test.norm_type, self.norm_type_combo.count()-1))
        
        # Additional info
        info = QLabel("The NormDispIncr test checks the norm of the displacement increment vector "
                     "against a tolerance. Useful for tracking solution convergence.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Update test parameters
            self.test.tol = params["tol"]
            self.test.max_iter = params["max_iter"]
            self.test.print_flag = params["print_flag"]
            self.test.norm_type = params["norm_type"]
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class EnergyIncrTestEditDialog(BaseEnergyTestDialog):
    """Dialog for editing an Energy Increment test"""
    def __init__(self, test: EnergyIncrTest, parent=None):
        super().__init__(parent, "Edit Energy Increment Test")
        self.test = test
        
        # Fill in existing values
        self.tol_spin.setValue(test.tol)
        self.max_iter_spin.setValue(test.max_iter)
        self.print_flag_combo.setCurrentIndex(min(test.print_flag, self.print_flag_combo.count()-1))
        
        # Additional info
        info = QLabel("The EnergyIncr test checks the energy increment (0.5 * x^T * b) against a tolerance. "
                     "Useful for problems with energy-critical behaviors.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Update test parameters
            self.test.tol = params["tol"]
            self.test.max_iter = params["max_iter"]
            self.test.print_flag = params["print_flag"]
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class RelativeNormUnbalanceTestEditDialog(BaseNormTestDialog):
    """Dialog for editing a Relative Norm Unbalance test"""
    def __init__(self, test: RelativeNormUnbalanceTest, parent=None):
        super().__init__(parent, "Edit Relative Norm Unbalance Test")
        self.test = test
        
        # Fill in existing values
        self.tol_spin.setValue(test.tol)
        self.max_iter_spin.setValue(test.max_iter)
        self.print_flag_combo.setCurrentIndex(min(test.print_flag, self.print_flag_combo.count()-1))
        self.norm_type_combo.setCurrentIndex(min(test.norm_type, self.norm_type_combo.count()-1))
        
        # Additional info
        info = QLabel("The RelativeNormUnbalance test compares current unbalance to initial unbalance. "
                     "Requires at least two iterations and can be sensitive to initial conditions.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Update test parameters
            self.test.tol = params["tol"]
            self.test.max_iter = params["max_iter"]
            self.test.print_flag = params["print_flag"]
            self.test.norm_type = params["norm_type"]
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class RelativeNormDispIncrTestEditDialog(BaseNormTestDialog):
    """Dialog for editing a Relative Norm Displacement Increment test"""
    def __init__(self, test: RelativeNormDispIncrTest, parent=None):
        super().__init__(parent, "Edit Relative Norm Displacement Increment Test")
        self.test = test
        
        # Fill in existing values
        self.tol_spin.setValue(test.tol)
        self.max_iter_spin.setValue(test.max_iter)
        self.print_flag_combo.setCurrentIndex(min(test.print_flag, self.print_flag_combo.count()-1))
        self.norm_type_combo.setCurrentIndex(min(test.norm_type, self.norm_type_combo.count()-1))
        
        # Additional info
        info = QLabel("The RelativeNormDispIncr test compares current displacement increment to initial. "
                     "Tracks relative changes in displacement.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Update test parameters
            self.test.tol = params["tol"]
            self.test.max_iter = params["max_iter"]
            self.test.print_flag = params["print_flag"]
            self.test.norm_type = params["norm_type"]
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class RelativeTotalNormDispIncrTestEditDialog(BaseNormTestDialog):
    """Dialog for editing a Relative Total Norm Displacement Increment test"""
    def __init__(self, test: RelativeTotalNormDispIncrTest, parent=None):
        super().__init__(parent, "Edit Relative Total Norm Displacement Increment Test")
        self.test = test
        
        # Fill in existing values
        self.tol_spin.setValue(test.tol)
        self.max_iter_spin.setValue(test.max_iter)
        self.print_flag_combo.setCurrentIndex(min(test.print_flag, self.print_flag_combo.count()-1))
        self.norm_type_combo.setCurrentIndex(min(test.norm_type, self.norm_type_combo.count()-1))
        
        # Additional info
        info = QLabel("The RelativeTotalNormDispIncr test uses ratio of current norm to total norm "
                     "(sum of norms since last convergence). Tracks cumulative displacement changes.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Update test parameters
            self.test.tol = params["tol"]
            self.test.max_iter = params["max_iter"]
            self.test.print_flag = params["print_flag"]
            self.test.norm_type = params["norm_type"]
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class RelativeEnergyIncrTestEditDialog(BaseEnergyTestDialog):
    """Dialog for editing a Relative Energy Increment test"""
    def __init__(self, test: RelativeEnergyIncrTest, parent=None):
        super().__init__(parent, "Edit Relative Energy Increment Test")
        self.test = test
        
        # Fill in existing values
        self.tol_spin.setValue(test.tol)
        self.max_iter_spin.setValue(test.max_iter)
        self.print_flag_combo.setCurrentIndex(min(test.print_flag, self.print_flag_combo.count()-1))
        
        # Additional info
        info = QLabel("The RelativeEnergyIncr test compares energy increment relative to first iteration. "
                     "Provides energy-based relative convergence assessment.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Update test parameters
            self.test.tol = params["tol"]
            self.test.max_iter = params["max_iter"]
            self.test.print_flag = params["print_flag"]
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class FixedNumIterTestEditDialog(BaseTestDialog):
    """Dialog for editing a Fixed Number of Iterations test"""
    def __init__(self, test: FixedNumIterTest, parent=None):
        super().__init__(parent, "Edit Fixed Number of Iterations Test")
        self.test = test
        
        # Number of iterations parameter
        self.num_iter_spin = QSpinBox()
        self.num_iter_spin.setRange(1, 1000)
        self.num_iter_spin.setValue(test.num_iter)
        self.params_layout.addRow("Number of Iterations:", self.num_iter_spin)
        
        # Additional info
        info = QLabel("The FixedNumIter test runs a fixed number of iterations with no convergence check. "
                     "Useful for specific analytical requirements.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
        
        # Add button layout
        self.add_button_layout()
    
    def save_test(self):
        try:
            # Update test parameters
            self.test.num_iter = self.num_iter_spin.value()
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NormDispAndUnbalanceTestEditDialog(BaseCombinedNormTestDialog):
    """Dialog for editing a Norm Displacement AND Unbalance test"""
    def __init__(self, test: NormDispAndUnbalanceTest, parent=None):
        super().__init__(parent, "Edit Norm Displacement AND Unbalance Test")
        self.test = test
        
        # Fill in existing values
        self.tol_incr_spin.setValue(test.tol_incr)
        self.tol_r_spin.setValue(test.tol_r)
        self.max_iter_spin.setValue(test.max_iter)
        self.print_flag_combo.setCurrentIndex(min(test.print_flag, self.print_flag_combo.count()-1))
        self.norm_type_combo.setCurrentIndex(min(test.norm_type, self.norm_type_combo.count()-1))
        self.max_incr_spin.setValue(test.max_incr)
        
        # Additional info
        info = QLabel("The NormDispAndUnbalance test simultaneously checks displacement increment and unbalanced force norms. "
                      "Requires BOTH displacement and unbalance norms to converge.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Update test parameters
            self.test.tol_incr = params["tol_incr"]
            self.test.tol_r = params["tol_r"]
            self.test.max_iter = params["max_iter"]
            self.test.print_flag = params["print_flag"]
            self.test.norm_type = params["norm_type"]
            self.test.max_incr = params["max_incr"]
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NormDispOrUnbalanceTestEditDialog(BaseCombinedNormTestDialog):
    """Dialog for editing a Norm Displacement OR Unbalance test"""
    def __init__(self, test: NormDispOrUnbalanceTest, parent=None):
        super().__init__(parent, "Edit Norm Displacement OR Unbalance Test")
        self.test = test
        
        # Fill in existing values
        self.tol_incr_spin.setValue(test.tol_incr)
        self.tol_r_spin.setValue(test.tol_r)
        self.max_iter_spin.setValue(test.max_iter)
        self.print_flag_combo.setCurrentIndex(min(test.print_flag, self.print_flag_combo.count()-1))
        self.norm_type_combo.setCurrentIndex(min(test.norm_type, self.norm_type_combo.count()-1))
        self.max_incr_spin.setValue(test.max_incr)
        
        # Additional info
        info = QLabel("The NormDispOrUnbalance test checks displacement increment or unbalanced force norms. "
                      "Convergence achieved if EITHER displacement OR unbalance norm criterion is met.")
        info.setWordWrap(True)
        self.layout.insertWidget(1, info)
    
    def save_test(self):
        try:
            params = self.get_params()
            
            # Update test parameters
            self.test.tol_incr = params["tol_incr"]
            self.test.tol_r = params["tol_r"]
            self.test.max_iter = params["max_iter"]
            self.test.print_flag = params["print_flag"]
            self.test.norm_type = params["norm_type"]
            self.test.max_incr = params["max_incr"]
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = TestManagerTab()
    window.show()
    sys.exit(app.exec_())
    
    sys.exit(app.exec_())