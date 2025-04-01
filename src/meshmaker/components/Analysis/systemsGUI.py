from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout,
    QCheckBox, QGroupBox, QDoubleSpinBox, QRadioButton, QSpinBox
)

from meshmaker.utils.validator import DoubleValidator, IntValidator
from meshmaker.components.Analysis.systems import (
    System, SystemManager, 
    FullGeneralSystem, BandGeneralSystem,
    BandSPDSystem, ProfileSPDSystem,
    SuperLUSystem, UmfpackSystem, MumpsSystem
)

class SystemManagerTab(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup dialog properties
        self.setWindowTitle("System Manager")
        self.resize(800, 500)
        
        # Get the system manager instance
        self.system_manager = SystemManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # System type selection
        type_layout = QGridLayout()
        
        # System type dropdown
        self.system_type_combo = QComboBox()
        self.system_type_combo.addItems(self.system_manager.get_available_types())
        
        create_system_btn = QPushButton("Create New System")
        create_system_btn.clicked.connect(self.open_system_creation_dialog)
        
        type_layout.addWidget(QLabel("System Type:"), 0, 0)
        type_layout.addWidget(self.system_type_combo, 0, 1)
        type_layout.addWidget(create_system_btn, 1, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Systems table
        self.systems_table = QTableWidget()
        self.systems_table.setColumnCount(4)  # Select, Tag, Type, Parameters
        self.systems_table.setHorizontalHeaderLabels(["Select", "Tag", "Type", "Parameters"])
        self.systems_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.systems_table.setSelectionMode(QTableWidget.SingleSelection)
        header = self.systems_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.systems_table)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_system)
        
        self.delete_selected_btn = QPushButton("Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_system)
        
        refresh_btn = QPushButton("Refresh Systems List")
        refresh_btn.clicked.connect(self.refresh_systems_list)
        
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_selected_btn)
        buttons_layout.addWidget(refresh_btn)
        
        layout.addLayout(buttons_layout)
        
        # Initial refresh
        self.refresh_systems_list()
        
        # Disable edit/delete buttons initially
        self.update_button_state()

    def refresh_systems_list(self):
        """Update the systems table with current systems"""
        self.systems_table.setRowCount(0)
        systems = self.system_manager.get_all_systems()
        
        self.systems_table.setRowCount(len(systems))
        self.radio_buttons = []
        
        # Hide vertical header (row indices)
        self.systems_table.verticalHeader().setVisible(False)
        
        for row, (tag, system) in enumerate(systems.items()):
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
            self.systems_table.setCellWidget(row, 0, radio_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.systems_table.setItem(row, 1, tag_item)
            
            # System Type
            type_item = QTableWidgetItem(system.system_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.systems_table.setItem(row, 2, type_item)
            
            # Parameters
            params = system.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.systems_table.setItem(row, 3, params_item)
        
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

    def get_selected_system_tag(self):
        """Get the tag of the selected system"""
        for row, radio_btn in enumerate(self.radio_buttons):
            if radio_btn.isChecked():
                tag_item = self.systems_table.item(row, 1)
                return int(tag_item.text())
        return None

    def open_system_creation_dialog(self):
        """Open dialog to create a new system of selected type"""
        system_type = self.system_type_combo.currentText()
        
        if system_type.lower() == "fullgeneral":
            dialog = FullGeneralSystemDialog(self)
        elif system_type.lower() == "bandgeneral":
            dialog = BandGeneralSystemDialog(self)
        elif system_type.lower() == "bandspd":
            dialog = BandSPDSystemDialog(self)
        elif system_type.lower() == "profilespd":
            dialog = ProfileSPDSystemDialog(self)
        elif system_type.lower() == "superlu":
            dialog = SuperLUSystemDialog(self)
        elif system_type.lower() == "umfpack":
            dialog = UmfpackSystemDialog(self)
        elif system_type.lower() == "mumps":
            dialog = MumpsSystemDialog(self)
        else:
            QMessageBox.warning(self, "Error", f"No creation dialog available for system type: {system_type}")
            return
        
        if dialog.exec() == QDialog.Accepted:
            self.refresh_systems_list()

    def edit_selected_system(self):
        """Edit the selected system"""
        tag = self.get_selected_system_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select a system to edit")
            return
        
        try:
            system = self.system_manager.get_system(tag)
            
            if system.system_type.lower() in ["fullgeneral", "bandgeneral", "bandspd", "profilespd", "superlu"]:
                QMessageBox.information(self, "Info", f"{system.system_type} system has no parameters to edit")
                return
            elif system.system_type.lower() == "umfpack":
                dialog = UmfpackSystemEditDialog(system, self)
            elif system.system_type.lower() == "mumps":
                dialog = MumpsSystemEditDialog(system, self)
            else:
                QMessageBox.warning(self, "Error", f"No edit dialog available for system type: {system.system_type}")
                return
            
            if dialog.exec() == QDialog.Accepted:
                self.refresh_systems_list()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected_system(self):
        """Delete the selected system"""
        tag = self.get_selected_system_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select a system to delete")
            return
        
        self.delete_system(tag)

    def delete_system(self, tag):
        """Delete a system from the system of equations"""
        reply = QMessageBox.question(
            self, 'Delete System',
            f"Are you sure you want to delete system with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.system_manager.remove_system(tag)
            self.refresh_systems_list()


class FullGeneralSystemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Full General System")
        self.system_manager = SystemManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("Full General System is NOT optimized, uses all the matrix.\nIt has no additional parameters.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_system)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_system(self):
        try:
            # Create system
            self.system = self.system_manager.create_system("fullgeneral")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class BandGeneralSystemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Band General System")
        self.system_manager = SystemManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("Band General System uses banded matrix storage.\nIt has no additional parameters.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_system)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_system(self):
        try:
            # Create system
            self.system = self.system_manager.create_system("bandgeneral")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class BandSPDSystemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Band SPD System")
        self.system_manager = SystemManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("Band SPD System is for symmetric positive definite matrices, uses banded profile storage.\nIt has no additional parameters.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_system)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_system(self):
        try:
            # Create system
            self.system = self.system_manager.create_system("bandspd")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class ProfileSPDSystemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Profile SPD System")
        self.system_manager = SystemManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("Profile SPD System is for symmetric positive definite matrices, uses skyline storage.\nIt has no additional parameters.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_system)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_system(self):
        try:
            # Create system
            self.system = self.system_manager.create_system("profilespd")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class SuperLUSystemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create SuperLU System")
        self.system_manager = SystemManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("SuperLU System is a sparse system solver.\nIt has no additional parameters.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_system)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_system(self):
        try:
            # Create system
            self.system = self.system_manager.create_system("superlu")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class UmfpackSystemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Umfpack System")
        self.system_manager = SystemManager()
        self.double_validator = DoubleValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # lvalue_fact
        self.lvalue_fact_checkbox = QCheckBox("Use lvalue factor")
        params_layout.addRow(self.lvalue_fact_checkbox)
        
        self.lvalue_fact_spin = QDoubleSpinBox()
        self.lvalue_fact_spin.setDecimals(6)
        self.lvalue_fact_spin.setRange(1e-12, 1e12)
        self.lvalue_fact_spin.setValue(1.0)
        self.lvalue_fact_spin.setEnabled(False)
        params_layout.addRow("lvalue factor:", self.lvalue_fact_spin)
        
        # Connect checkbox to enable/disable spin box
        self.lvalue_fact_checkbox.toggled.connect(self.lvalue_fact_spin.setEnabled)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("Umfpack System is a sparse system solver.\n"
                     "- lvalue factor: Factor used in the matrix factorization")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_system)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_system(self):
        try:
            # Collect parameters
            lvalue_fact = None
            if self.lvalue_fact_checkbox.isChecked():
                lvalue_fact = self.lvalue_fact_spin.value()
            
            # Create system
            self.system = self.system_manager.create_system("umfpack", lvalue_fact=lvalue_fact)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class UmfpackSystemEditDialog(QDialog):
    def __init__(self, system, parent=None):
        super().__init__(parent)
        self.system = system
        self.setWindowTitle(f"Edit Umfpack System (Tag: {system.tag})")
        self.system_manager = SystemManager()
        self.double_validator = DoubleValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # lvalue_fact
        self.lvalue_fact_checkbox = QCheckBox("Use lvalue factor")
        self.lvalue_fact_checkbox.setChecked(system.lvalue_fact is not None)
        params_layout.addRow(self.lvalue_fact_checkbox)
        
        self.lvalue_fact_spin = QDoubleSpinBox()
        self.lvalue_fact_spin.setDecimals(6)
        self.lvalue_fact_spin.setRange(1e-12, 1e12)
        if system.lvalue_fact is not None:
            self.lvalue_fact_spin.setValue(system.lvalue_fact)
        else:
            self.lvalue_fact_spin.setValue(1.0)
        self.lvalue_fact_spin.setEnabled(system.lvalue_fact is not None)
        params_layout.addRow("lvalue factor:", self.lvalue_fact_spin)
        
        # Connect checkbox to enable/disable spin box
        self.lvalue_fact_checkbox.toggled.connect(self.lvalue_fact_spin.setEnabled)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_system)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_system(self):
        try:
            # Collect parameters
            lvalue_fact = None
            if self.lvalue_fact_checkbox.isChecked():
                lvalue_fact = self.lvalue_fact_spin.value()
            
            # Remove the old system and create a new one with the same tag
            tag = self.system.tag
            self.system_manager.remove_system(tag)
            
            # Create new system
            self.system = self.system_manager.create_system("umfpack", lvalue_fact=lvalue_fact)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class MumpsSystemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Mumps System")
        self.system_manager = SystemManager()
        self.double_validator = DoubleValidator()
        self.int_validator = IntValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # ICNTL14
        self.icntl14_checkbox = QCheckBox("Use ICNTL14")
        params_layout.addRow(self.icntl14_checkbox)
        
        self.icntl14_spin = QDoubleSpinBox()
        self.icntl14_spin.setDecimals(6)
        self.icntl14_spin.setRange(1e-12, 1e12)
        self.icntl14_spin.setValue(20.0)  # Default value
        self.icntl14_spin.setEnabled(False)
        params_layout.addRow("ICNTL14 (workspace increase %):", self.icntl14_spin)
        
        # Connect checkbox to enable/disable spin box
        self.icntl14_checkbox.toggled.connect(self.icntl14_spin.setEnabled)
        
        # ICNTL7
        self.icntl7_checkbox = QCheckBox("Use ICNTL7")
        params_layout.addRow(self.icntl7_checkbox)
        
        self.icntl7_combo = QComboBox()
        self.icntl7_combo.addItems([
            "0 - AMD",
            "1 - User defined",
            "2 - AMF",
            "3 - SCOTCH",
            "4 - PORD",
            "5 - Metis",
            "6 - AMD with QADM",
            "7 - Automatic"
        ])
        self.icntl7_combo.setEnabled(False)
        params_layout.addRow("ICNTL7 (ordering method):", self.icntl7_combo)
        
        # Connect checkbox to enable/disable combo box
        self.icntl7_checkbox.toggled.connect(self.icntl7_combo.setEnabled)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("Mumps System is a sparse direct solver.\n"
                     "- ICNTL14: Controls the percentage increase in the estimated working space\n"
                     "- ICNTL7: Computes a symmetric permutation (ordering) for factorization")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_system)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_system(self):
        try:
            # Collect parameters
            icntl14 = None
            if self.icntl14_checkbox.isChecked():
                icntl14 = self.icntl14_spin.value()
            
            icntl7 = None
            if self.icntl7_checkbox.isChecked():
                icntl7 = int(self.icntl7_combo.currentText().split(' ')[0])
            
            # Create system
            self.system = self.system_manager.create_system("mumps", icntl14=icntl14, icntl7=icntl7)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class MumpsSystemEditDialog(QDialog):
    def __init__(self, system, parent=None):
        super().__init__(parent)
        self.system = system
        self.setWindowTitle(f"Edit Mumps System (Tag: {system.tag})")
        self.system_manager = SystemManager()
        self.double_validator = DoubleValidator()
        self.int_validator = IntValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # ICNTL14
        self.icntl14_checkbox = QCheckBox("Use ICNTL14")
        self.icntl14_checkbox.setChecked(system.icntl14 is not None)
        params_layout.addRow(self.icntl14_checkbox)
        
        self.icntl14_spin = QDoubleSpinBox()
        self.icntl14_spin.setDecimals(6)
        self.icntl14_spin.setRange(1e-12, 1e12)
        if system.icntl14 is not None:
            self.icntl14_spin.setValue(system.icntl14)
        else:
            self.icntl14_spin.setValue(20.0)  # Default value
        self.icntl14_spin.setEnabled(system.icntl14 is not None)
        params_layout.addRow("ICNTL14 (workspace increase %):", self.icntl14_spin)
        
        # Connect checkbox to enable/disable spin box
        self.icntl14_checkbox.toggled.connect(self.icntl14_spin.setEnabled)
        
        # ICNTL7
        self.icntl7_checkbox = QCheckBox("Use ICNTL7")
        self.icntl7_checkbox.setChecked(system.icntl7 is not None)
        params_layout.addRow(self.icntl7_checkbox)
        
        self.icntl7_combo = QComboBox()
        self.icntl7_combo.addItems([
            "0 - AMD",
            "1 - User defined",
            "2 - AMF",
            "3 - SCOTCH",
            "4 - PORD",
            "5 - Metis",
            "6 - AMD with QADM",
            "7 - Automatic"
        ])
        if system.icntl7 is not None:
            # Find and select the correct item in the combo box
            for i in range(self.icntl7_combo.count()):
                if self.icntl7_combo.itemText(i).startswith(str(system.icntl7)):
                    self.icntl7_combo.setCurrentIndex(i)
                    break
        self.icntl7_combo.setEnabled(system.icntl7 is not None)
        params_layout.addRow("ICNTL7 (ordering method):", self.icntl7_combo)
        
        # Connect checkbox to enable/disable combo box
        self.icntl7_checkbox.toggled.connect(self.icntl7_combo.setEnabled)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_system)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_system(self):
        try:
            # Collect parameters
            icntl14 = None
            if self.icntl14_checkbox.isChecked():
                icntl14 = self.icntl14_spin.value()
            
            icntl7 = None
            if self.icntl7_checkbox.isChecked():
                icntl7 = int(self.icntl7_combo.currentText().split(' ')[0])
            
            # Remove the old system and create a new one with the same tag
            tag = self.system.tag
            self.system_manager.remove_system(tag)
            
            # Create new system
            self.system = self.system_manager.create_system("mumps", icntl14=icntl14, icntl7=icntl7)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == '__main__':
    from qtpy.QtWidgets import QApplication
    import sys
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    window = SystemManagerTab()
    window.show()
    sys.exit(app.exec_())