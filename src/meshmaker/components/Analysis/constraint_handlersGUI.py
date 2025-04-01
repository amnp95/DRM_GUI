from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout,
    QCheckBox, QGroupBox, QDoubleSpinBox
)

from meshmaker.utils.validator import DoubleValidator
from meshmaker.components.Analysis.constraint_handlers import (
    ConstraintHandler, ConstraintHandlerManager, 
    PlainConstraintHandler, TransformationConstraintHandler,
    PenaltyConstraintHandler, LagrangeConstraintHandler, 
    AutoConstraintHandler
)

class ConstraintHandlerManagerTab(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup dialog properties
        self.setWindowTitle("Constraint Handler Manager")
        self.resize(700, 500)
        
        # Get the constraint handler manager instance
        self.handler_manager = ConstraintHandlerManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Handler type selection
        type_layout = QGridLayout()
        
        # Handler type dropdown
        self.handler_type_combo = QComboBox()
        self.handler_type_combo.addItems(self.handler_manager.get_available_types())
        
        create_handler_btn = QPushButton("Create New Handler")
        create_handler_btn.clicked.connect(self.open_handler_creation_dialog)
        
        type_layout.addWidget(QLabel("Handler Type:"), 0, 0)
        type_layout.addWidget(self.handler_type_combo, 0, 1)
        type_layout.addWidget(create_handler_btn, 1, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Handlers table
        self.handlers_table = QTableWidget()
        self.handlers_table.setColumnCount(4)  # Tag, Type, Parameters, Delete
        self.handlers_table.setHorizontalHeaderLabels(["Tag", "Type", "Parameters", "Delete"])
        header = self.handlers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.handlers_table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Handlers List")
        refresh_btn.clicked.connect(self.refresh_handlers_list)
        layout.addWidget(refresh_btn)
        
        # Initial refresh
        self.refresh_handlers_list()

    def refresh_handlers_list(self):
        """Update the handlers table with current constraint handlers"""
        self.handlers_table.setRowCount(0)
        handlers = self.handler_manager.get_all_handlers()
        
        self.handlers_table.setRowCount(len(handlers))
        for row, (tag, handler) in enumerate(handlers.items()):
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.handlers_table.setItem(row, 0, tag_item)
            
            # Handler Type
            type_item = QTableWidgetItem(handler.handler_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.handlers_table.setItem(row, 1, type_item)
            
            # Parameters
            params = handler.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.handlers_table.setItem(row, 2, params_item)
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, t=tag: self.delete_handler(t))
            self.handlers_table.setCellWidget(row, 3, delete_btn)

    def open_handler_creation_dialog(self):
        """Open dialog to create a new constraint handler of selected type"""
        handler_type = self.handler_type_combo.currentText()
        
        if handler_type.lower() == "plain":
            dialog = PlainConstraintHandlerDialog(self)
        elif handler_type.lower() == "transformation":
            dialog = TransformationConstraintHandlerDialog(self)
        elif handler_type.lower() == "penalty":
            dialog = PenaltyConstraintHandlerDialog(self)
        elif handler_type.lower() == "lagrange":
            dialog = LagrangeConstraintHandlerDialog(self)
        elif handler_type.lower() == "auto":
            dialog = AutoConstraintHandlerDialog(self)
        else:
            QMessageBox.warning(self, "Error", f"No creation dialog available for handler type: {handler_type}")
            return
        
        if dialog.exec() == QDialog.Accepted:
            self.refresh_handlers_list()

    def delete_handler(self, tag):
        """Delete a constraint handler from the system"""
        reply = QMessageBox.question(
            self, 'Delete Constraint Handler',
            f"Are you sure you want to delete constraint handler with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.handler_manager.remove_handler(tag)
            self.refresh_handlers_list()


class PlainConstraintHandlerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Plain Constraint Handler")
        self.handler_manager = ConstraintHandlerManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("Plain constraint handler does not follow the constraint definitions across the model evolution.\nIt has no additional parameters.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_handler)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_handler(self):
        try:
            # Create handler
            self.handler = self.handler_manager.create_handler("plain")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class TransformationConstraintHandlerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Transformation Constraint Handler")
        self.handler_manager = ConstraintHandlerManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("Transformation constraint handler performs static condensation of the constraint degrees of freedom.\nIt has no additional parameters.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_handler)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_handler(self):
        try:
            # Create handler
            self.handler = self.handler_manager.create_handler("transformation")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class PenaltyConstraintHandlerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Penalty Constraint Handler")
        self.handler_manager = ConstraintHandlerManager()
        self.double_validator = DoubleValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Alpha S
        self.alpha_s_spin = QDoubleSpinBox()
        self.alpha_s_spin.setDecimals(6)
        self.alpha_s_spin.setRange(1e-12, 1e12)
        self.alpha_s_spin.setValue(1.0)
        params_layout.addRow("Alpha S:", self.alpha_s_spin)
        
        # Alpha M
        self.alpha_m_spin = QDoubleSpinBox()
        self.alpha_m_spin.setDecimals(6)
        self.alpha_m_spin.setRange(1e-12, 1e12)
        self.alpha_m_spin.setValue(1.0)
        params_layout.addRow("Alpha M:", self.alpha_m_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("Penalty constraint handler uses penalty numbers to enforce constraints.\n"
                     "- Alpha S: Penalty value for single-point constraints\n"
                     "- Alpha M: Penalty value for multi-point constraints")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_handler)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_handler(self):
        try:
            # Collect parameters
            alpha_s = self.alpha_s_spin.value()
            alpha_m = self.alpha_m_spin.value()
            
            # Create handler
            self.handler = self.handler_manager.create_handler("penalty", alpha_s=alpha_s, alpha_m=alpha_m)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class LagrangeConstraintHandlerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Lagrange Constraint Handler")
        self.handler_manager = ConstraintHandlerManager()
        self.double_validator = DoubleValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Alpha S
        self.alpha_s_spin = QDoubleSpinBox()
        self.alpha_s_spin.setDecimals(6)
        self.alpha_s_spin.setRange(1e-12, 1e12)
        self.alpha_s_spin.setValue(1.0)
        params_layout.addRow("Alpha S:", self.alpha_s_spin)
        
        # Alpha M
        self.alpha_m_spin = QDoubleSpinBox()
        self.alpha_m_spin.setDecimals(6)
        self.alpha_m_spin.setRange(1e-12, 1e12)
        self.alpha_m_spin.setValue(1.0)
        params_layout.addRow("Alpha M:", self.alpha_m_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("Lagrange multipliers constraint handler uses Lagrange multipliers to enforce constraints.\n"
                     "- Alpha S: Scaling factor for single-point constraints\n"
                     "- Alpha M: Scaling factor for multi-point constraints")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_handler)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_handler(self):
        try:
            # Collect parameters
            alpha_s = self.alpha_s_spin.value()
            alpha_m = self.alpha_m_spin.value()
            
            # Create handler
            self.handler = self.handler_manager.create_handler("lagrange", alpha_s=alpha_s, alpha_m=alpha_m)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class AutoConstraintHandlerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Auto Constraint Handler")
        self.handler_manager = ConstraintHandlerManager()
        self.double_validator = DoubleValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Verbose
        self.verbose_checkbox = QCheckBox()
        params_layout.addRow("Verbose Output:", self.verbose_checkbox)
        
        # Auto Penalty
        self.auto_penalty_spin = QDoubleSpinBox()
        self.auto_penalty_spin.setDecimals(6)
        self.auto_penalty_spin.setRange(1e-12, 1e12)
        self.auto_penalty_spin.setValue(1.0)
        self.auto_penalty_spin.setSpecialValueText("None")
        params_layout.addRow("Auto Penalty:", self.auto_penalty_spin)
        
        # User Penalty
        self.user_penalty_spin = QDoubleSpinBox()
        self.user_penalty_spin.setDecimals(6)
        self.user_penalty_spin.setRange(1e-12, 1e12)
        self.user_penalty_spin.setValue(1.0)
        self.user_penalty_spin.setSpecialValueText("None")
        params_layout.addRow("User Penalty:", self.user_penalty_spin)
        
        layout.addWidget(params_group)
        
        # Info label
        info = QLabel("Auto constraint handler automatically selects the penalty value for compatibility constraints.\n"
                     "- Verbose: Output extra information during analysis\n"
                     "- Auto Penalty: Value for automatically calculated penalty\n"
                     "- User Penalty: Value for user-defined penalty")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_handler)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_handler(self):
        try:
            # Collect parameters
            verbose = self.verbose_checkbox.isChecked()
            auto_penalty = self.auto_penalty_spin.value() if self.auto_penalty_spin.value() != 1e-12 else None
            user_penalty = self.user_penalty_spin.value() if self.user_penalty_spin.value() != 1e-12 else None
            
            # Create handler
            self.handler = self.handler_manager.create_handler("auto", 
                                                             verbose=verbose, 
                                                             auto_penalty=auto_penalty, 
                                                             user_penalty=user_penalty)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == '__main__':
    from qtpy.QtWidgets import QApplication
    import sys
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    window = ConstraintHandlerManagerTab()
    window.show()
    sys.exit(app.exec_())