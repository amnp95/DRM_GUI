from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QMessageBox, QHeaderView, QGridLayout,
    QFrame, QTextBrowser, QCheckBox
)
from qtpy.QtCore import Qt
from meshmaker.components.Damping.dampingBase import DampingBase
from meshmaker.components.Region.regionBase import RegionBase, GlobalRegion, ElementRegion, NodeRegion

class DampingSelectorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.damping_combo = QComboBox()
        self.refresh_dampings()
        
        self.create_damping_btn = QPushButton("Manage Dampings")
        self.create_damping_btn.clicked.connect(self.open_damping_dialog)
        
        layout.addWidget(QLabel("Damping:"))
        layout.addWidget(self.damping_combo, stretch=1)
        layout.addWidget(self.create_damping_btn)
    
    def refresh_dampings(self):
        self.damping_combo.clear()
        self.damping_combo.addItem("None", None)
        for tag, damping in DampingBase._dampings.items():
            self.damping_combo.addItem(f"{damping.name} (Tag: {tag}, Type: {damping.get_Type()})", damping)
    
    def open_damping_dialog(self):
        from meshmaker.components.Damping.dampingGUI import DampingManagerTab
        dialog = DampingManagerTab(self)
        dialog.exec()
        self.refresh_dampings()
    
    def get_selected_damping(self):
        return self.damping_combo.currentData()
    
    def set_selected_damping(self, damping):
        index = self.damping_combo.findData(damping)
        self.damping_combo.setCurrentIndex(max(index, 0))

class RegionManagerTab(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Region type selection
        type_layout = QGridLayout()
        self.region_type_combo = QComboBox()
        self.region_type_combo.addItems(["ElementRegion", "NodeRegion"])
        
        create_region_btn = QPushButton("Create New Region")
        create_region_btn.clicked.connect(self.open_region_creation_dialog)
        
        type_layout.addWidget(QLabel("Region Type:"), 0, 0)
        type_layout.addWidget(self.region_type_combo, 0, 1, 1, 2)
        type_layout.addWidget(create_region_btn, 1, 0, 1, 3)
        
        layout.addLayout(type_layout)
        
        # Regions table
        self.regions_table = QTableWidget()
        self.regions_table.setColumnCount(7)  # Tag, Type, Name, Damping, Edit, Delete
        self.regions_table.setHorizontalHeaderLabels(["Tag", "Type", "Name", "Damping", "Edit", "info" ,"Delete"])
        header = self.regions_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # dont show the index column
        self.regions_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.regions_table)
        
        # Refresh regions button
        refresh_btn = QPushButton("Refresh Regions List")
        refresh_btn.clicked.connect(self.refresh_regions_list)
        layout.addWidget(refresh_btn)
        
        # Initial refresh
        self.refresh_regions_list()

    def refresh_regions_list(self):
        self.regions_table.setRowCount(0)
        regions = RegionBase.get_all_regions()
        
        self.regions_table.setRowCount(len(regions))
        for row, (tag, region) in enumerate(regions.items()):
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.regions_table.setItem(row, 0, tag_item)
            
            # Region Type
            type_item = QTableWidgetItem(region.get_type())
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.regions_table.setItem(row, 1, type_item)
            
            # Name
            name_item = QTableWidgetItem(region.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.regions_table.setItem(row, 2, name_item)
            
            # Damping
            damping_text = region.damping.name if region.damping else "None"
            damping_item = QTableWidgetItem(damping_text)
            damping_item.setFlags(damping_item.flags() & ~Qt.ItemIsEditable)
            self.regions_table.setItem(row, 3, damping_item)
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, r=region: self.open_region_edit_dialog(r))
            self.regions_table.setCellWidget(row, 4, edit_btn)
            
            # Delete button (disabled for global region)
            delete_btn = QPushButton("Delete")
            delete_btn.setEnabled(tag != 0)
            delete_btn.clicked.connect(lambda checked, t=tag: self.delete_region(t))
            self.regions_table.setCellWidget(row, 6, delete_btn)

            # info button
            info_btn = QPushButton("Info")
            info_btn.clicked.connect(lambda checked, r=region: self.show_region_info(r))
            self.regions_table.setCellWidget(row, 5, info_btn)

    def open_region_creation_dialog(self):
        region_type = self.region_type_combo.currentText()
        dialog = RegionCreationDialog(region_type, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_regions_list()

    def open_region_edit_dialog(self, region):
        dialog = RegionEditDialog(region, self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_regions_list()

    def show_region_info(self, region):
        QMessageBox.information(self, f"{region.get_type()} Info", str(region))

    def delete_region(self, tag):
        reply = QMessageBox.question(
            self, 'Delete Region',
            f"Are you sure you want to delete region with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            RegionBase.remove_region(tag)
            self.refresh_regions_list()

class RegionCreationDialog(QDialog):
    def __init__(self, region_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Create {region_type}")
        self.region_type = region_type
        
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Parameters
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Get region class
        self.region_class = globals()[region_type]
        
        # Parameter inputs
        self.param_inputs = {}
        parameters = self.region_class.get_Parameters()
        
        # Create a grid layout for parameters
        params_group = QGridLayout()
        row = 0
        
        # Add damping selector
        self.damping_selector = DampingSelectorWidget()
        params_group.addWidget(QLabel("Damping:"), row, 0, 1, 3)
        row += 1
        params_group.addWidget(self.damping_selector, row, 0, 1, 3)
        row += 1
        
        # Add other parameters
        for param, input_type in parameters.items():
            if input_type == "checkbox":
                input_field = QCheckBox()
                params_group.addWidget(QLabel(param), row, 0)
                params_group.addWidget(input_field, row, 1, 1, 2)
            else:  # lineEdit
                input_field = QLineEdit()
                params_group.addWidget(QLabel(param), row, 0)
                params_group.addWidget(input_field, row, 1, 1, 2)
            
            self.param_inputs[param] = input_field
            row += 1
        
        left_layout.addLayout(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create Region")
        create_btn.clicked.connect(self.create_region)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        left_layout.addLayout(btn_layout)
        left_layout.addStretch()
        
        # Add left widget to main layout
        main_layout.addWidget(left_widget)
        
        # Vertical line separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # Right side - Notes
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        notes_display = QTextBrowser()
        notes_display.setHtml(f"<b>Notes:</b><br>")
        info = self.region_class.getNotes()
        for i, note in enumerate(info["Notes"]):
            notes_display.append(f"<b>{i+1}</b>) {note}")
        notes_display.append(f"<br><b>References:</b>")
        for i, ref in enumerate(info["References"]):
            notes_display.append(f"<b>{i+1}</b>) {ref}")

        right_layout.addWidget(notes_display)
        right_layout.addStretch()
        
        main_layout.addWidget(right_widget)
        
        # Set layout proportions
        main_layout.setStretch(0, 3)
        main_layout.setStretch(2, 2)

    def create_region(self):
        try:
            params = {}
            for param, input_field in self.param_inputs.items():
                if isinstance(input_field, QCheckBox):
                    value = input_field.isChecked()
                else:
                    text = input_field.text().strip()
                    if not text:
                        continue
                    if param in ['elements', 'nodes']:
                        value = [int(x) for x in text.split(',')]
                    elif param in ['element_range', 'node_range']:
                        value = [int(x) for x in text.split(',')][:2]
                    else:
                        value = text
                params[param] = value
            
            damping = self.damping_selector.get_selected_damping()
            region = self.region_class(damping=damping, **params)
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class RegionEditDialog(QDialog):
    def __init__(self, region, parent=None):
        super().__init__(parent)
        self.region = region
        self.setWindowTitle(f"Edit {region.get_type()} (Tag: {region.tag})")
        
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Parameters
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Parameter inputs
        self.param_inputs = {}
        parameters = region.__class__.get_Parameters()
        
        # Create a grid layout for parameters
        params_group = QGridLayout()
        row = 0
        
        # Add damping selector
        self.damping_selector = DampingSelectorWidget()
        self.damping_selector.set_selected_damping(region.damping)
        params_group.addWidget(QLabel("Damping:"), row, 0, 1, 3)
        row += 1
        params_group.addWidget(self.damping_selector, row, 0, 1, 3)
        row += 1
        
        # Add other parameters
        for param, input_type in parameters.items():
            if input_type == "checkbox":
                input_field = QCheckBox()
                input_field.setChecked(getattr(region, param, False))
                params_group.addWidget(QLabel(param), row, 0)
                params_group.addWidget(input_field, row, 1, 1, 2)
            else:  # lineEdit
                input_field = QLineEdit()
                value = getattr(region, param, [])
                if value:
                    input_field.setText(','.join(map(str, value)))
                params_group.addWidget(QLabel(param), row, 0)
                params_group.addWidget(input_field, row, 1, 1, 2)
            
            self.param_inputs[param] = input_field
            row += 1
        
        left_layout.addLayout(params_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        left_layout.addLayout(btn_layout)
        left_layout.addStretch()
        
        # Add left widget to main layout
        main_layout.addWidget(left_widget)
        
        # Vertical line separator
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # Right side - Notes
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        notes_display = QTextBrowser()
        notes_display.setHtml(f"<b>Notes:</b><br>")
        info = region.getNotes()
        for i, note in enumerate(info["Notes"]):
            notes_display.append(f"<b>{i+1}</b>) {note}")
        notes_display.append(f"<br><b>References:</b>")
        for i, ref in enumerate(info["References"]):
            notes_display.append(f"<b>{i+1}</b>) {ref}")
        right_layout.addWidget(notes_display)
        right_layout.addStretch()
        
        main_layout.addWidget(right_widget)
        
        # Set layout proportions
        main_layout.setStretch(0, 3)
        main_layout.setStretch(2, 2)

    def save_changes(self):
        try:
            # Update damping
            self.region.damping = self.damping_selector.get_selected_damping()
            
            # Update other parameters
            params = {}
            for param, input_field in self.param_inputs.items():
                if isinstance(input_field, QCheckBox):
                    setattr(self.region, param, input_field.isChecked())
                else:
                    text = input_field.text().strip()
                    if text:
                        if param in ['elements', 'nodes']:
                            value = [int(x) for x in text.split(',')]
                        elif param in ['element_range', 'node_range']:
                            value = [int(x) for x in text.split(',')][:2]
                        else:
                            value = text
                        setattr(self.region, param, value)
            
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication
    from meshmaker.components.Damping.dampingBase import RayleighDamping, ModalDamping
    
    # Create some sample dampings
    RayleighDamping1 = RayleighDamping(alphaM=0.1, betaK=0.2, betaKInit=0.3, betaKComm=0.4)
    RayleighDamping2 = RayleighDamping(alphaM=0.5, betaK=0.6, betaKInit=0.7, betaKComm=0.8)
    ModalDamping1 = ModalDamping(numberofModes=2, dampingFactors="0.1,0.2")
    
    # Initialize global region
    global_region = GlobalRegion(damping=RayleighDamping1)
    
    # Create some sample regions
    element_region = ElementRegion(damping=ModalDamping1, elements=[1, 2, 3], element_only=True)
    node_region = NodeRegion(damping=RayleighDamping2, nodes=[1, 2, 3, 4])
    
    # Create and show the application
    app = QApplication(sys.argv)
    window = RegionManagerTab()
    window.show()
    sys.exit(app.exec_())