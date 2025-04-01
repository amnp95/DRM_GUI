from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout,
    QCheckBox, QGroupBox, QDoubleSpinBox, QRadioButton
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
        self.resize(800, 500)
        
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
        self.handlers_table.setColumnCount(4)  # Select, Tag, Type, Parameters
        self.handlers_table.setHorizontalHeaderLabels(["Select", "Tag", "Type", "Parameters"])
        self.handlers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.handlers_table.setSelectionMode(QTableWidget.SingleSelection)
        header = self.handlers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.handlers_table)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_handler)
        
        self.delete_selected_btn = QPushButton("Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_handler)
        
        refresh_btn = QPushButton("Refresh Handlers List")
        refresh_btn.clicked.connect(self.refresh_handlers_list)
        
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_selected_btn)
        buttons_layout.addWidget(refresh_btn)
        
        layout.addLayout(buttons_layout)
        
        # Initial refresh
        self.refresh_handlers_list()
        
        # Disable edit/delete buttons initially
        self.update_button_state()

    def refresh_handlers_list(self):
        """Update the handlers table with current constraint handlers"""
        self.handlers_table.setRowCount(0)
        handlers = self.handler_manager.get_all_handlers()
        
        self.handlers_table.setRowCount(len(handlers))
        self.radio_buttons = []
        
        # Hide vertical header (row indices)
        self.handlers_table.verticalHeader().setVisible(False)
        
        for row, (tag, handler) in enumerate(handlers.items()):
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
            self.handlers_table.setCellWidget(row, 0, radio_cell)
            
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.handlers_table.setItem(row, 1, tag_item)
            
            # Handler Type
            type_item = QTableWidgetItem(handler.handler_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.handlers_table.setItem(row, 2, type_item)
            
            # Parameters
            params = handler.get_values()
            params_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "None"
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.handlers_table.setItem(row, 3, params_item)
        
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

    def get_selected_handler_tag(self):
        """Get the tag of the selected handler"""
        for row, radio_btn in enumerate(self.radio_buttons):
            if radio_btn.isChecked():
                tag_item = self.handlers_table.item(row, 1)
                return int(tag_item.text())
        return None

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

    def edit_selected_handler(self):
        """Edit the selected handler"""
        tag = self.get_selected_handler_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select a handler to edit")
            return
        
        try:
            handler = self.handler_manager.get_handler(tag)
            
            if handler.handler_type.lower() == "plain":
                QMessageBox.information(self, "Info", "Plain constraint handler has no parameters to edit")
                return
            elif handler.handler_type.lower() == "transformation":
                QMessageBox.information(self, "Info", "Transformation constraint handler has no parameters to edit")
                return
            elif handler.handler_type.lower() == "penalty":
                dialog = PenaltyConstraintHandlerEditDialog(handler, self)
            elif handler.handler_type.lower() == "lagrange":
                dialog = LagrangeConstraintHandlerEditDialog(handler, self)
            elif handler.handler_type.lower() == "auto":
                dialog = AutoConstraintHandlerEditDialog(handler, self)
            else:
                QMessageBox.warning(self, "Error", f"No edit dialog available for handler type: {handler.handler_type}")
                return
            
            if dialog.exec() == QDialog.Accepted:
                self.refresh_handlers_list()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected_handler(self):
        """Delete the selected handler"""
        tag = self.get_selected_handler_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select a handler to delete")
            return
        
        self.delete_handler(tag)

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


class PenaltyConstraintHandlerEditDialog(QDialog):
    def __init__(self, handler, parent=None):
        super().__init__(parent)
        self.handler = handler
        self.setWindowTitle(f"Edit Penalty Constraint Handler (Tag: {handler.tag})")
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
        self.alpha_s_spin.setValue(handler.alpha_s)
        params_layout.addRow("Alpha S:", self.alpha_s_spin)
        
        # Alpha M
        self.alpha_m_spin = QDoubleSpinBox()
        self.alpha_m_spin.setDecimals(6)
        self.alpha_m_spin.setRange(1e-12, 1e12)
        self.alpha_m_spin.setValue(handler.alpha_m)
        params_layout.addRow("Alpha M:", self.alpha_m_spin)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_handler)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_handler(self):
        try:
            # Collect parameters
            alpha_s = self.alpha_s_spin.value()
            alpha_m = self.alpha_m_spin.value()
            
            # Remove the old handler and create a new one with the same tag
            tag = self.handler.tag
            self.handler_manager.remove_handler(tag)
            
            # Create new handler
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


class LagrangeConstraintHandlerEditDialog(QDialog):
    def __init__(self, handler, parent=None):
        super().__init__(parent)
        self.handler = handler
        self.setWindowTitle(f"Edit Lagrange Constraint Handler (Tag: {handler.tag})")
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
        self.alpha_s_spin.setValue(handler.alpha_s)
        params_layout.addRow("Alpha S:", self.alpha_s_spin)
        
        # Alpha M
        self.alpha_m_spin = QDoubleSpinBox()
        self.alpha_m_spin.setDecimals(6)
        self.alpha_m_spin.setRange(1e-12, 1e12)
        self.alpha_m_spin.setValue(handler.alpha_m)
        params_layout.addRow("Alpha M:", self.alpha_m_spin)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_handler)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_handler(self):
        try:
            # Collect parameters
            alpha_s = self.alpha_s_spin.value()
            alpha_m = self.alpha_m_spin.value()
            
            # Remove the old handler and create a new one with the same tag
            tag = self.handler.tag
            self.handler_manager.remove_handler(tag)
            
            # Create new handler
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


class AutoConstraintHandlerEditDialog(QDialog):
    def __init__(self, handler, parent=None):
        super().__init__(parent)
        self.handler = handler
        self.setWindowTitle(f"Edit Auto Constraint Handler (Tag: {handler.tag})")
        self.handler_manager = ConstraintHandlerManager()
        self.double_validator = DoubleValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Parameters group
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)
        
        # Verbose
        self.verbose_checkbox = QCheckBox()
        self.verbose_checkbox.setChecked(handler.verbose)
        params_layout.addRow("Verbose Output:", self.verbose_checkbox)
        
        # Auto Penalty
        self.auto_penalty_spin = QDoubleSpinBox()
        self.auto_penalty_spin.setDecimals(6)
        self.auto_penalty_spin.setRange(1e-12, 1e12)
        if handler.auto_penalty is not None:
            self.auto_penalty_spin.setValue(handler.auto_penalty)
        else:
            self.auto_penalty_spin.setValue(1e-12)  # Use minimum value to represent None
        self.auto_penalty_spin.setSpecialValueText("None")
        params_layout.addRow("Auto Penalty:", self.auto_penalty_spin)
        
        # User Penalty
        self.user_penalty_spin = QDoubleSpinBox()
        self.user_penalty_spin.setDecimals(6)
        self.user_penalty_spin.setRange(1e-12, 1e12)
        if handler.user_penalty is not None:
            self.user_penalty_spin.setValue(handler.user_penalty)
        else:
            self.user_penalty_spin.setValue(1e-12)  # Use minimum value to represent None
        self.user_penalty_spin.setSpecialValueText("None")
        params_layout.addRow("User Penalty:", self.user_penalty_spin)
        
        layout.addWidget(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_handler)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_handler(self):
        try:
            # Collect parameters
            verbose = self.verbose_checkbox.isChecked()
            auto_penalty = self.auto_penalty_spin.value() if self.auto_penalty_spin.value() != 1e-12 else None
            user_penalty = self.user_penalty_spin.value() if self.user_penalty_spin.value() != 1e-12 else None
            
            # Remove the old handler and create a new one with the same tag
            tag = self.handler.tag
            self.handler_manager.remove_handler(tag)
            
            # Create new handler
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