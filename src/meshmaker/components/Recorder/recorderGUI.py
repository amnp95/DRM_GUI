from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QDialog, QFormLayout, QMessageBox, QHeaderView, QGridLayout, 
    QStackedWidget, QCheckBox, QScrollArea, QFrame, QTextEdit,
    QFileDialog, QGroupBox
)

from meshmaker.components.Recorder.recorderBase import (
    Recorder, RecorderManager, RecorderRegistry,
    NodeRecorder, VTKHDFRecorder
)
from meshmaker.utils.validator import DoubleValidator, IntValidator


class RecorderManagerTab(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup dialog properties
        self.setWindowTitle("Recorder Manager")
        self.resize(800, 600)
        
        # Get the recorder manager instance
        self.recorder_manager = RecorderManager()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Recorder type selection
        type_layout = QGridLayout()
        
        # Recorder type dropdown
        self.recorder_type_combo = QComboBox()
        self.recorder_type_combo.addItems(self.recorder_manager.get_available_types())
        
        create_recorder_btn = QPushButton("Create New Recorder")
        create_recorder_btn.clicked.connect(self.open_recorder_creation_dialog)
        
        type_layout.addWidget(QLabel("Recorder Type:"), 0, 0)
        type_layout.addWidget(self.recorder_type_combo, 0, 1)
        type_layout.addWidget(create_recorder_btn, 1, 0, 1, 2)
        
        layout.addLayout(type_layout)
        
        # Recorders table
        self.recorders_table = QTableWidget()
        self.recorders_table.setColumnCount(3)  # Tag, Type, Parameters
        self.recorders_table.setHorizontalHeaderLabels(["Tag", "Type", "Parameters"])
        self.recorders_table.setSelectionBehavior(QTableWidget.SelectRows)  # Select entire rows
        self.recorders_table.setSelectionMode(QTableWidget.SingleSelection)  # Single row selection
        header = self.recorders_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Stretch all columns
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Except for the first one
        
        layout.addWidget(self.recorders_table)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_recorder)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected_recorder)
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_recorders_list)
        
        actions_layout.addWidget(self.edit_btn)
        actions_layout.addWidget(self.delete_btn)
        actions_layout.addWidget(refresh_btn)
        
        layout.addLayout(actions_layout)
        
        # Initial refresh
        self.refresh_recorders_list()
        
        # Enable/disable Edit and Delete buttons based on selection
        self.recorders_table.itemSelectionChanged.connect(self.update_button_state)
        self.update_button_state()  # Initial state

    def update_button_state(self):
        """Enable/disable buttons based on whether a row is selected"""
        has_selection = len(self.recorders_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def get_selected_recorder_tag(self):
        """Get the tag of the selected recorder"""
        selected_rows = self.recorders_table.selectedItems()
        if not selected_rows:
            return None
        
        # Get the tag from the first column of the selected row
        tag_item = self.recorders_table.item(selected_rows[0].row(), 0)
        if tag_item:
            return int(tag_item.text())
        return None

    def open_recorder_creation_dialog(self):
        """Open dialog to create a new recorder of selected type"""
        recorder_type = self.recorder_type_combo.currentText()
        
        if recorder_type.lower() == "node":
            dialog = NodeRecorderCreationDialog(self)
        elif recorder_type.lower() == "vtkhdf":
            dialog = VTKHDFRecorderCreationDialog(self)
        else:
            QMessageBox.warning(self, "Error", f"No creation dialog available for recorder type: {recorder_type}")
            return
        
        if dialog.exec() == QDialog.Accepted:
            self.refresh_recorders_list()

    def edit_selected_recorder(self):
        """Edit the selected recorder"""
        tag = self.get_selected_recorder_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select a recorder to edit")
            return
        
        try:
            recorder = self.recorder_manager.get_recorder(tag)
            
            if recorder.recorder_type == "Node":
                dialog = NodeRecorderEditDialog(recorder, self)
            elif recorder.recorder_type == "VTKHDF":
                dialog = VTKHDFRecorderEditDialog(recorder, self)
            else:
                QMessageBox.warning(self, "Error", f"No edit dialog available for recorder type: {recorder.recorder_type}")
                return
            
            if dialog.exec() == QDialog.Accepted:
                self.refresh_recorders_list()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected_recorder(self):
        """Delete the selected recorder"""
        tag = self.get_selected_recorder_tag()
        if tag is None:
            QMessageBox.warning(self, "Warning", "Please select a recorder to delete")
            return
        
        reply = QMessageBox.question(
            self, 'Delete Recorder',
            f"Are you sure you want to delete recorder with tag {tag}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.recorder_manager.remove_recorder(tag)
                self.refresh_recorders_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def refresh_recorders_list(self):
        """Update the recorders table with current recorders"""
        self.recorders_table.setRowCount(0)
        recorders = Recorder.get_all_recorders()
        
        self.recorders_table.setRowCount(len(recorders))
        
        for row, (tag, recorder) in enumerate(recorders.items()):
            # Tag
            tag_item = QTableWidgetItem(str(tag))
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
            self.recorders_table.setItem(row, 0, tag_item)
            
            # Recorder Type
            type_item = QTableWidgetItem(recorder.recorder_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.recorders_table.setItem(row, 1, type_item)
            
            # Parameters
            params_dict = recorder.get_values()
            if recorder.recorder_type == "Node":
                params_str = self._format_node_recorder_params(params_dict)
            elif recorder.recorder_type == "VTKHDF":
                params_str = self._format_vtkhdf_recorder_params(params_dict)
            else:
                params_str = str(params_dict)
                
            params_item = QTableWidgetItem(params_str)
            params_item.setFlags(params_item.flags() & ~Qt.ItemIsEditable)
            self.recorders_table.setItem(row, 2, params_item)
        
        # Update button state after refresh
        self.update_button_state()

    def _format_node_recorder_params(self, params_dict):
        """Format Node recorder parameters for display"""
        parts = []
        
        # Output destination
        if params_dict.get("file_name"):
            parts.append(f"File: {params_dict['file_name']}")
        elif params_dict.get("xml_file"):
            parts.append(f"XML: {params_dict['xml_file']}")
        elif params_dict.get("binary_file"):
            parts.append(f"Binary: {params_dict['binary_file']}")
        elif params_dict.get("inet_addr") and params_dict.get("port"):
            parts.append(f"TCP: {params_dict['inet_addr']}:{params_dict['port']}")
        
        # Node selection
        if params_dict.get("nodes"):
            parts.append(f"Nodes: {params_dict['nodes']}")
        elif params_dict.get("node_range"):
            parts.append(f"Node Range: {params_dict['node_range']}")
        elif params_dict.get("region"):
            parts.append(f"Region: {params_dict['region']}")
        
        # Response
        parts.append(f"DOFs: {params_dict['dofs']}")
        parts.append(f"Response: {params_dict['resp_type']}")
        
        return ", ".join(parts)

    def _format_vtkhdf_recorder_params(self, params_dict):
        """Format VTKHDF recorder parameters for display"""
        parts = []
        
        if params_dict.get("file_base_name"):
            parts.append(f"File: {params_dict['file_base_name']}")
        
        if params_dict.get("resp_types"):
            parts.append(f"Responses: {', '.join(params_dict['resp_types'])}")
        
        if params_dict.get("delta_t"):
            parts.append(f"dT: {params_dict['delta_t']}")
        
        if params_dict.get("r_tol_dt"):
            parts.append(f"rTolDt: {params_dict['r_tol_dt']}")
        
        return ", ".join(parts)


class NodeRecorderCreationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Node Recorder")
        self.recorder_manager = RecorderManager()
        self.int_validator = IntValidator()
        self.double_validator = DoubleValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create a tabbed interface for different sections
        self.tabs = QStackedWidget()
        
        # Create tabs
        self.setup_output_tab()
        self.setup_nodes_tab()
        self.setup_response_tab()
        self.setup_options_tab()
        
        # Add navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_tab)
        self.prev_btn.setEnabled(False)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_tab)
        
        self.create_btn = QPushButton("Create")
        self.create_btn.clicked.connect(self.create_recorder)
        self.create_btn.setVisible(False)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.create_btn)
        nav_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(self.tabs)
        layout.addLayout(nav_layout)
        
        # Initialize tab navigation
        self.current_tab = 0
        self.update_navigation()

    def setup_output_tab(self):
        """Setup the output destination tab"""
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setSpacing(10)
        
        # Output destination group
        output_group = QGroupBox("Output Destination")
        output_group_layout = QVBoxLayout(output_group)
        
        # File output
        self.file_radio = QCheckBox("File")
        self.file_radio.setChecked(True)
        self.file_input = QLineEdit()
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_radio)
        file_layout.addWidget(self.file_input)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        output_group_layout.addLayout(file_layout)
        
        # XML output
        self.xml_radio = QCheckBox("XML File")
        self.xml_input = QLineEdit()
        xml_layout = QHBoxLayout()
        xml_layout.addWidget(self.xml_radio)
        xml_layout.addWidget(self.xml_input)
        xml_browse_btn = QPushButton("Browse")
        xml_browse_btn.clicked.connect(self.browse_xml)
        xml_layout.addWidget(xml_browse_btn)
        output_group_layout.addLayout(xml_layout)
        
        # Binary output
        self.binary_radio = QCheckBox("Binary File")
        self.binary_input = QLineEdit()
        binary_layout = QHBoxLayout()
        binary_layout.addWidget(self.binary_radio)
        binary_layout.addWidget(self.binary_input)
        binary_browse_btn = QPushButton("Browse")
        binary_browse_btn.clicked.connect(self.browse_binary)
        binary_layout.addWidget(binary_browse_btn)
        output_group_layout.addLayout(binary_layout)
        
        # TCP output
        self.tcp_radio = QCheckBox("TCP/IP")
        tcp_layout = QHBoxLayout()
        tcp_layout.addWidget(self.tcp_radio)
        tcp_layout.addWidget(QLabel("IP Address:"))
        self.inet_addr_input = QLineEdit()
        tcp_layout.addWidget(self.inet_addr_input)
        tcp_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit()
        self.port_input.setValidator(self.int_validator)
        tcp_layout.addWidget(self.port_input)
        output_group_layout.addLayout(tcp_layout)
        
        # Connect radio buttons to ensure only one is checked
        self.file_radio.clicked.connect(lambda: self.update_output_selection("file"))
        self.xml_radio.clicked.connect(lambda: self.update_output_selection("xml"))
        self.binary_radio.clicked.connect(lambda: self.update_output_selection("binary"))
        self.tcp_radio.clicked.connect(lambda: self.update_output_selection("tcp"))
        
        output_layout.addWidget(output_group)
        
        # Add notes
        notes_label = QLabel("Note: Only one output destination may be specified.")
        notes_label.setWordWrap(True)
        output_layout.addWidget(notes_label)
        
        output_layout.addStretch()
        self.tabs.addWidget(output_widget)

    def setup_nodes_tab(self):
        """Setup the nodes selection tab"""
        nodes_widget = QWidget()
        nodes_layout = QVBoxLayout(nodes_widget)
        nodes_layout.setSpacing(10)
        
        # Node selection group
        node_group = QGroupBox("Node Selection")
        node_group_layout = QVBoxLayout(node_group)
        
        # Node list
        self.node_radio = QCheckBox("Node List")
        self.node_radio.setChecked(True)
        self.node_input = QLineEdit()
        node_layout = QHBoxLayout()
        node_layout.addWidget(self.node_radio)
        node_layout.addWidget(QLabel("Nodes (comma separated):"))
        node_layout.addWidget(self.node_input)
        node_group_layout.addLayout(node_layout)
        
        # Node range
        self.node_range_radio = QCheckBox("Node Range")
        node_range_layout = QHBoxLayout()
        node_range_layout.addWidget(self.node_range_radio)
        node_range_layout.addWidget(QLabel("Start Node:"))
        self.start_node_input = QLineEdit()
        self.start_node_input.setValidator(self.int_validator)
        node_range_layout.addWidget(self.start_node_input)
        node_range_layout.addWidget(QLabel("End Node:"))
        self.end_node_input = QLineEdit()
        self.end_node_input.setValidator(self.int_validator)
        node_range_layout.addWidget(self.end_node_input)
        node_group_layout.addLayout(node_range_layout)
        
        # Region
        self.region_radio = QCheckBox("Region")
        region_layout = QHBoxLayout()
        region_layout.addWidget(self.region_radio)
        region_layout.addWidget(QLabel("Region Tag:"))
        self.region_input = QLineEdit()
        self.region_input.setValidator(self.int_validator)
        region_layout.addWidget(self.region_input)
        node_group_layout.addLayout(region_layout)
        
        # Connect radio buttons to ensure only one is checked
        self.node_radio.clicked.connect(lambda: self.update_node_selection("node"))
        self.node_range_radio.clicked.connect(lambda: self.update_node_selection("node_range"))
        self.region_radio.clicked.connect(lambda: self.update_node_selection("region"))
        
        nodes_layout.addWidget(node_group)
        
        # Add notes
        notes_label = QLabel("Note: Only one node selection method may be specified.")
        notes_label.setWordWrap(True)
        nodes_layout.addWidget(notes_label)
        
        nodes_layout.addStretch()
        self.tabs.addWidget(nodes_widget)

    def setup_response_tab(self):
        """Setup the response tab"""
        response_widget = QWidget()
        response_layout = QVBoxLayout(response_widget)
        response_layout.setSpacing(10)
        
        # DOF selection
        dof_group = QGroupBox("Degrees of Freedom")
        dof_layout = QHBoxLayout(dof_group)
        dof_layout.addWidget(QLabel("DOFs (space separated):"))
        self.dof_input = QLineEdit()
        dof_layout.addWidget(self.dof_input)
        response_layout.addWidget(dof_group)
        
        # Response type selection
        resp_group = QGroupBox("Response Type")
        resp_layout = QVBoxLayout(resp_group)
        
        self.resp_type_combo = QComboBox()
        self.resp_type_combo.addItems([
            "disp", "vel", "accel", "incrDisp", "reaction", "rayleighForces"
        ])
        
        # Special case for eigen
        eigen_layout = QHBoxLayout()
        self.eigen_radio = QCheckBox("Eigen Mode")
        self.mode_input = QLineEdit()
        self.mode_input.setValidator(self.int_validator)
        eigen_layout.addWidget(self.eigen_radio)
        eigen_layout.addWidget(QLabel("Mode:"))
        eigen_layout.addWidget(self.mode_input)
        
        resp_layout.addWidget(self.resp_type_combo)
        resp_layout.addLayout(eigen_layout)
        
        # Connect eigen radio to update response type
        self.eigen_radio.clicked.connect(self.update_response_type)
        self.resp_type_combo.currentIndexChanged.connect(lambda: self.eigen_radio.setChecked(False))
        
        response_layout.addWidget(resp_group)
        
        # Add notes
        notes_label = QLabel("Note: Specify the DOFs to record (e.g., '1 2 3' for X, Y, Z displacements) and the type of response to record.")
        notes_label.setWordWrap(True)
        response_layout.addWidget(notes_label)
        
        response_layout.addStretch()
        self.tabs.addWidget(response_widget)

    def setup_options_tab(self):
        """Setup the options tab"""
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)
        options_layout.setSpacing(10)
        
        # Options group
        options_group = QGroupBox("Additional Options")
        options_group_layout = QFormLayout(options_group)
        
        # Precision
        self.precision_input = QLineEdit("6")
        self.precision_input.setValidator(self.int_validator)
        options_group_layout.addRow("Precision:", self.precision_input)
        
        # Time Series
        self.time_series_input = QLineEdit()
        self.time_series_input.setValidator(self.int_validator)
        options_group_layout.addRow("Time Series Tag:", self.time_series_input)
        
        # Time option
        self.time_checkbox = QCheckBox()
        options_group_layout.addRow("Include Time:", self.time_checkbox)
        
        # Delta T
        self.delta_t_input = QLineEdit()
        self.delta_t_input.setValidator(self.double_validator)
        options_group_layout.addRow("Time Interval (dT):", self.delta_t_input)
        
        # Close on write
        self.close_on_write_checkbox = QCheckBox()
        options_group_layout.addRow("Close on Write:", self.close_on_write_checkbox)
        
        options_layout.addWidget(options_group)
        
        # Add notes
        notes_text = QTextEdit()
        notes_text.setReadOnly(True)
        notes_text.setPlainText(
            "Notes:\n"
            "- Precision: Number of significant digits (default: 6)\n"
            "- Time Series: Tag of previously constructed TimeSeries\n"
            "- Include Time: Places domain time in first output column\n"
            "- Time Interval: Record only when time step is greater than specified interval\n"
            "- Close on Write: Opens and closes file on each write (slows down execution)"
        )
        options_layout.addWidget(notes_text)
        
        options_layout.addStretch()
        self.tabs.addWidget(options_widget)

    def update_output_selection(self, selection):
        """Update output selection to ensure only one is checked"""
        self.file_radio.setChecked(selection == "file")
        self.xml_radio.setChecked(selection == "xml")
        self.binary_radio.setChecked(selection == "binary")
        self.tcp_radio.setChecked(selection == "tcp")

    def update_node_selection(self, selection):
        """Update node selection to ensure only one is checked"""
        self.node_radio.setChecked(selection == "node")
        self.node_range_radio.setChecked(selection == "node_range")
        self.region_radio.setChecked(selection == "region")

    def update_response_type(self):
        """Update response type when eigen mode is checked"""
        if self.eigen_radio.isChecked():
            # Disable the combo box
            self.resp_type_combo.setEnabled(False)
        else:
            # Enable the combo box
            self.resp_type_combo.setEnabled(True)

    def browse_file(self):
        """Browse for output file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select Output File", "", "All Files (*)"
        )
        if filename:
            self.file_input.setText(filename)
            self.update_output_selection("file")

    def browse_xml(self):
        """Browse for XML output file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select XML Output File", "", "XML Files (*.xml);;All Files (*)"
        )
        if filename:
            self.xml_input.setText(filename)
            self.update_output_selection("xml")

    def browse_binary(self):
        """Browse for binary output file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select Binary Output File", "", "All Files (*)"
        )
        if filename:
            self.binary_input.setText(filename)
            self.update_output_selection("binary")

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
        self.create_btn.setVisible(self.current_tab == self.tabs.count() - 1)

    def create_recorder(self):
        try:
            # Collect parameters
            params = {}
            
            # Output destination
            if self.file_radio.isChecked():
                params["file_name"] = self.file_input.text().strip()
                if not params["file_name"]:
                    raise ValueError("Please specify an output file name")
            elif self.xml_radio.isChecked():
                params["xml_file"] = self.xml_input.text().strip()
                if not params["xml_file"]:
                    raise ValueError("Please specify an XML output file name")
            elif self.binary_radio.isChecked():
                params["binary_file"] = self.binary_input.text().strip()
                if not params["binary_file"]:
                    raise ValueError("Please specify a binary output file name")
            elif self.tcp_radio.isChecked():
                params["inet_addr"] = self.inet_addr_input.text().strip()
                params["port"] = int(self.port_input.text()) if self.port_input.text() else None
                if not params["inet_addr"] or not params["port"]:
                    raise ValueError("Please specify both IP address and port for TCP output")
            else:
                raise ValueError("Please select an output destination")
            
            # Node selection
            if self.node_radio.isChecked():
                node_text = self.node_input.text().strip()
                if not node_text:
                    raise ValueError("Please specify node list")
                params["nodes"] = [int(n.strip()) for n in node_text.split(",")]
            elif self.node_range_radio.isChecked():
                start_node = self.start_node_input.text().strip()
                end_node = self.end_node_input.text().strip()
                if not start_node or not end_node:
                    raise ValueError("Please specify both start and end nodes")
                params["node_range"] = [int(start_node), int(end_node)]
            elif self.region_radio.isChecked():
                region = self.region_input.text().strip()
                if not region:
                    raise ValueError("Please specify region tag")
                params["region"] = int(region)
            else:
                raise ValueError("Please select a node selection method")
            
            # DOFs and response type
            dof_text = self.dof_input.text().strip()
            if not dof_text:
                raise ValueError("Please specify DOFs")
            params["dofs"] = [int(d.strip()) for d in dof_text.split()]
            
            if self.eigen_radio.isChecked():
                mode = self.mode_input.text().strip()
                if not mode:
                    raise ValueError("Please specify eigen mode")
                params["resp_type"] = f"eigen {mode}"
            else:
                params["resp_type"] = self.resp_type_combo.currentText()
            
            # Additional options
            precision = self.precision_input.text().strip()
            if precision:
                params["precision"] = int(precision)
            
            time_series = self.time_series_input.text().strip()
            if time_series:
                params["time_series"] = int(time_series)
            
            params["time"] = self.time_checkbox.isChecked()
            
            delta_t = self.delta_t_input.text().strip()
            if delta_t:
                params["delta_t"] = float(delta_t)
            
            params["close_on_write"] = self.close_on_write_checkbox.isChecked()
            
            # Create recorder
            self.recorder = self.recorder_manager.create_recorder("node", **params)
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class NodeRecorderEditDialog(QDialog):
    def __init__(self, recorder, parent=None):
        super().__init__(parent)
        self.recorder = recorder
        self.setWindowTitle(f"Edit Node Recorder (Tag: {recorder.tag})")
        self.recorder_manager = RecorderManager()
        self.int_validator = IntValidator()
        self.double_validator = DoubleValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create a tabbed interface for different sections
        self.tabs = QStackedWidget()
        
        # Create tabs
        self.setup_output_tab()
        self.setup_nodes_tab()
        self.setup_response_tab()
        self.setup_options_tab()
        
        # Initialize with current values
        self.load_current_values()
        
        # Add navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_tab)
        self.prev_btn.setEnabled(False)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_tab)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_recorder)
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

    def setup_output_tab(self):
        """Setup the output destination tab"""
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setSpacing(10)
        
        # Output destination group
        output_group = QGroupBox("Output Destination")
        output_group_layout = QVBoxLayout(output_group)
        
        # File output
        self.file_radio = QCheckBox("File")
        self.file_input = QLineEdit()
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_radio)
        file_layout.addWidget(self.file_input)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        output_group_layout.addLayout(file_layout)
        
        # XML output
        self.xml_radio = QCheckBox("XML File")
        self.xml_input = QLineEdit()
        xml_layout = QHBoxLayout()
        xml_layout.addWidget(self.xml_radio)
        xml_layout.addWidget(self.xml_input)
        xml_browse_btn = QPushButton("Browse")
        xml_browse_btn.clicked.connect(self.browse_xml)
        xml_layout.addWidget(xml_browse_btn)
        output_group_layout.addLayout(xml_layout)
        
        # Binary output
        self.binary_radio = QCheckBox("Binary File")
        self.binary_input = QLineEdit()
        binary_layout = QHBoxLayout()
        binary_layout.addWidget(self.binary_radio)
        binary_layout.addWidget(self.binary_input)
        binary_browse_btn = QPushButton("Browse")
        binary_browse_btn.clicked.connect(self.browse_binary)
        binary_layout.addWidget(binary_browse_btn)
        output_group_layout.addLayout(binary_layout)
        
        # TCP output
        self.tcp_radio = QCheckBox("TCP/IP")
        tcp_layout = QHBoxLayout()
        tcp_layout.addWidget(self.tcp_radio)
        tcp_layout.addWidget(QLabel("IP Address:"))
        self.inet_addr_input = QLineEdit()
        tcp_layout.addWidget(self.inet_addr_input)
        tcp_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit()
        self.port_input.setValidator(self.int_validator)
        tcp_layout.addWidget(self.port_input)
        output_group_layout.addLayout(tcp_layout)
        
        # Connect radio buttons to ensure only one is checked
        self.file_radio.clicked.connect(lambda: self.update_output_selection("file"))
        self.xml_radio.clicked.connect(lambda: self.update_output_selection("xml"))
        self.binary_radio.clicked.connect(lambda: self.update_output_selection("binary"))
        self.tcp_radio.clicked.connect(lambda: self.update_output_selection("tcp"))
        
        output_layout.addWidget(output_group)
        
        # Add notes
        notes_label = QLabel("Note: Only one output destination may be specified.")
        notes_label.setWordWrap(True)
        output_layout.addWidget(notes_label)
        
        output_layout.addStretch()
        self.tabs.addWidget(output_widget)

    def setup_nodes_tab(self):
        """Setup the nodes selection tab"""
        nodes_widget = QWidget()
        nodes_layout = QVBoxLayout(nodes_widget)
        nodes_layout.setSpacing(10)
        
        # Node selection group
        node_group = QGroupBox("Node Selection")
        node_group_layout = QVBoxLayout(node_group)
        
        # Node list
        self.node_radio = QCheckBox("Node List")
        self.node_input = QLineEdit()
        node_layout = QHBoxLayout()
        node_layout.addWidget(self.node_radio)
        node_layout.addWidget(QLabel("Nodes (comma separated):"))
        node_layout.addWidget(self.node_input)
        node_group_layout.addLayout(node_layout)
        
        # Node range
        self.node_range_radio = QCheckBox("Node Range")
        node_range_layout = QHBoxLayout()
        node_range_layout.addWidget(self.node_range_radio)
        node_range_layout.addWidget(QLabel("Start Node:"))
        self.start_node_input = QLineEdit()
        self.start_node_input.setValidator(self.int_validator)
        node_range_layout.addWidget(self.start_node_input)
        node_range_layout.addWidget(QLabel("End Node:"))
        self.end_node_input = QLineEdit()
        self.end_node_input.setValidator(self.int_validator)
        node_range_layout.addWidget(self.end_node_input)
        node_group_layout.addLayout(node_range_layout)
        
        # Region
        self.region_radio = QCheckBox("Region")
        region_layout = QHBoxLayout()
        region_layout.addWidget(self.region_radio)
        region_layout.addWidget(QLabel("Region Tag:"))
        self.region_input = QLineEdit()
        self.region_input.setValidator(self.int_validator)
        region_layout.addWidget(self.region_input)
        node_group_layout.addLayout(region_layout)
        
        # Connect radio buttons to ensure only one is checked
        self.node_radio.clicked.connect(lambda: self.update_node_selection("node"))
        self.node_range_radio.clicked.connect(lambda: self.update_node_selection("node_range"))
        self.region_radio.clicked.connect(lambda: self.update_node_selection("region"))
        
        nodes_layout.addWidget(node_group)
        
        # Add notes
        notes_label = QLabel("Note: Only one node selection method may be specified.")
        notes_label.setWordWrap(True)
        nodes_layout.addWidget(notes_label)
        
        nodes_layout.addStretch()
        self.tabs.addWidget(nodes_widget)

    def setup_response_tab(self):
        """Setup the response tab"""
        response_widget = QWidget()
        response_layout = QVBoxLayout(response_widget)
        response_layout.setSpacing(10)
        
        # DOF selection
        dof_group = QGroupBox("Degrees of Freedom")
        dof_layout = QHBoxLayout(dof_group)
        dof_layout.addWidget(QLabel("DOFs (space separated):"))
        self.dof_input = QLineEdit()
        dof_layout.addWidget(self.dof_input)
        response_layout.addWidget(dof_group)
        
        # Response type selection
        resp_group = QGroupBox("Response Type")
        resp_layout = QVBoxLayout(resp_group)
        
        self.resp_type_combo = QComboBox()
        self.resp_type_combo.addItems([
            "disp", "vel", "accel", "incrDisp", "reaction", "rayleighForces"
        ])
        
        # Special case for eigen
        eigen_layout = QHBoxLayout()
        self.eigen_radio = QCheckBox("Eigen Mode")
        self.mode_input = QLineEdit()
        self.mode_input.setValidator(self.int_validator)
        eigen_layout.addWidget(self.eigen_radio)
        eigen_layout.addWidget(QLabel("Mode:"))
        eigen_layout.addWidget(self.mode_input)
        
        resp_layout.addWidget(self.resp_type_combo)
        resp_layout.addLayout(eigen_layout)
        
        # Connect eigen radio to update response type
        self.eigen_radio.clicked.connect(self.update_response_type)
        self.resp_type_combo.currentIndexChanged.connect(lambda: self.eigen_radio.setChecked(False))
        
        response_layout.addWidget(resp_group)
        
        # Add notes
        notes_label = QLabel("Note: Specify the DOFs to record (e.g., '1 2 3' for X, Y, Z displacements) and the type of response to record.")
        notes_label.setWordWrap(True)
        response_layout.addWidget(notes_label)
        
        response_layout.addStretch()
        self.tabs.addWidget(response_widget)

    def setup_options_tab(self):
        """Setup the options tab"""
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)
        options_layout.setSpacing(10)
        
        # Options group
        options_group = QGroupBox("Additional Options")
        options_group_layout = QFormLayout(options_group)
        
        # Precision
        self.precision_input = QLineEdit()
        self.precision_input.setValidator(self.int_validator)
        options_group_layout.addRow("Precision:", self.precision_input)
        
        # Time Series
        self.time_series_input = QLineEdit()
        self.time_series_input.setValidator(self.int_validator)
        options_group_layout.addRow("Time Series Tag:", self.time_series_input)
        
        # Time option
        self.time_checkbox = QCheckBox()
        options_group_layout.addRow("Include Time:", self.time_checkbox)
        
        # Delta T
        self.delta_t_input = QLineEdit()
        self.delta_t_input.setValidator(self.double_validator)
        options_group_layout.addRow("Time Interval (dT):", self.delta_t_input)
        
        # Close on write
        self.close_on_write_checkbox = QCheckBox()
        options_group_layout.addRow("Close on Write:", self.close_on_write_checkbox)
        
        options_layout.addWidget(options_group)
        
        # Add notes
        notes_text = QTextEdit()
        notes_text.setReadOnly(True)
        notes_text.setPlainText(
            "Notes:\n"
            "- Precision: Number of significant digits (default: 6)\n"
            "- Time Series: Tag of previously constructed TimeSeries\n"
            "- Include Time: Places domain time in first output column\n"
            "- Time Interval: Record only when time step is greater than specified interval\n"
            "- Close on Write: Opens and closes file on each write (slows down execution)"
        )
        options_layout.addWidget(notes_text)
        
        options_layout.addStretch()
        self.tabs.addWidget(options_widget)

    def load_current_values(self):
        """Load current recorder values into the dialog"""
        values = self.recorder.get_values()
        
        # Output destination
        if values.get("file_name"):
            self.file_radio.setChecked(True)
            self.file_input.setText(values["file_name"])
        elif values.get("xml_file"):
            self.xml_radio.setChecked(True)
            self.xml_input.setText(values["xml_file"])
        elif values.get("binary_file"):
            self.binary_radio.setChecked(True)
            self.binary_input.setText(values["binary_file"])
        elif values.get("inet_addr") and values.get("port"):
            self.tcp_radio.setChecked(True)
            self.inet_addr_input.setText(values["inet_addr"])
            self.port_input.setText(str(values["port"]))
        
        # Node selection
        if values.get("nodes"):
            self.node_radio.setChecked(True)
            self.node_input.setText(", ".join(map(str, values["nodes"])))
        elif values.get("node_range"):
            self.node_range_radio.setChecked(True)
            self.start_node_input.setText(str(values["node_range"][0]))
            self.end_node_input.setText(str(values["node_range"][1]))
        elif values.get("region"):
            self.region_radio.setChecked(True)
            self.region_input.setText(str(values["region"]))
        
        # DOFs and response type
        if values.get("dofs"):
            self.dof_input.setText(" ".join(map(str, values["dofs"])))
        
        resp_type = values.get("resp_type", "")
        if resp_type.startswith("eigen "):
            self.eigen_radio.setChecked(True)
            self.mode_input.setText(resp_type.split()[1])
            self.resp_type_combo.setEnabled(False)
        else:
            index = self.resp_type_combo.findText(resp_type)
            if index >= 0:
                self.resp_type_combo.setCurrentIndex(index)
        
        # Additional options
        if values.get("precision"):
            self.precision_input.setText(str(values["precision"]))
        
        if values.get("time_series"):
            self.time_series_input.setText(str(values["time_series"]))
        
        self.time_checkbox.setChecked(values.get("time", False))
        
        if values.get("delta_t"):
            self.delta_t_input.setText(str(values["delta_t"]))
        
        self.close_on_write_checkbox.setChecked(values.get("close_on_write", False))

    def update_output_selection(self, selection):
        """Update output selection to ensure only one is checked"""
        self.file_radio.setChecked(selection == "file")
        self.xml_radio.setChecked(selection == "xml")
        self.binary_radio.setChecked(selection == "binary")
        self.tcp_radio.setChecked(selection == "tcp")

    def update_node_selection(self, selection):
        """Update node selection to ensure only one is checked"""
        self.node_radio.setChecked(selection == "node")
        self.node_range_radio.setChecked(selection == "node_range")
        self.region_radio.setChecked(selection == "region")

    def update_response_type(self):
        """Update response type when eigen mode is checked"""
        if self.eigen_radio.isChecked():
            # Disable the combo box
            self.resp_type_combo.setEnabled(False)
        else:
            # Enable the combo box
            self.resp_type_combo.setEnabled(True)

    def browse_file(self):
        """Browse for output file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select Output File", "", "All Files (*)"
        )
        if filename:
            self.file_input.setText(filename)
            self.update_output_selection("file")

    def browse_xml(self):
        """Browse for XML output file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select XML Output File", "", "XML Files (*.xml);;All Files (*)"
        )
        if filename:
            self.xml_input.setText(filename)
            self.update_output_selection("xml")

    def browse_binary(self):
        """Browse for binary output file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select Binary Output File", "", "All Files (*)"
        )
        if filename:
            self.binary_input.setText(filename)
            self.update_output_selection("binary")

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

    def save_recorder(self):
        try:
            # Collect parameters
            params = {}
            
            # Output destination
            if self.file_radio.isChecked():
                params["file_name"] = self.file_input.text().strip()
                if not params["file_name"]:
                    raise ValueError("Please specify an output file name")
            elif self.xml_radio.isChecked():
                params["xml_file"] = self.xml_input.text().strip()
                if not params["xml_file"]:
                    raise ValueError("Please specify an XML output file name")
            elif self.binary_radio.isChecked():
                params["binary_file"] = self.binary_input.text().strip()
                if not params["binary_file"]:
                    raise ValueError("Please specify a binary output file name")
            elif self.tcp_radio.isChecked():
                params["inet_addr"] = self.inet_addr_input.text().strip()
                params["port"] = int(self.port_input.text()) if self.port_input.text() else None
                if not params["inet_addr"] or not params["port"]:
                    raise ValueError("Please specify both IP address and port for TCP output")
            else:
                raise ValueError("Please select an output destination")
            
            # Node selection
            if self.node_radio.isChecked():
                node_text = self.node_input.text().strip()
                if not node_text:
                    raise ValueError("Please specify node list")
                params["nodes"] = [int(n.strip()) for n in node_text.split(",")]
            elif self.node_range_radio.isChecked():
                start_node = self.start_node_input.text().strip()
                end_node = self.end_node_input.text().strip()
                if not start_node or not end_node:
                    raise ValueError("Please specify both start and end nodes")
                params["node_range"] = [int(start_node), int(end_node)]
            elif self.region_radio.isChecked():
                region = self.region_input.text().strip()
                if not region:
                    raise ValueError("Please specify region tag")
                params["region"] = int(region)
            else:
                raise ValueError("Please select a node selection method")
            
            # DOFs and response type
            dof_text = self.dof_input.text().strip()
            if not dof_text:
                raise ValueError("Please specify DOFs")
            params["dofs"] = [int(d.strip()) for d in dof_text.split()]
            
            if self.eigen_radio.isChecked():
                mode = self.mode_input.text().strip()
                if not mode:
                    raise ValueError("Please specify eigen mode")
                params["resp_type"] = f"eigen {mode}"
            else:
                params["resp_type"] = self.resp_type_combo.currentText()
            
            # Additional options
            precision = self.precision_input.text().strip()
            if precision:
                params["precision"] = int(precision)
            
            time_series = self.time_series_input.text().strip()
            if time_series:
                params["time_series"] = int(time_series)
            
            params["time"] = self.time_checkbox.isChecked()
            
            delta_t = self.delta_t_input.text().strip()
            if delta_t:
                params["delta_t"] = float(delta_t)
            
            params["close_on_write"] = self.close_on_write_checkbox.isChecked()
            
            # Update recorder
            # First remove the old recorder
            tag = self.recorder.tag
            self.recorder_manager.remove_recorder(tag)
            
            # Create a new recorder with the same tag
            self.recorder = self.recorder_manager.create_recorder("node", **params)
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class VTKHDFRecorderCreationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create VTKHDF Recorder")
        self.recorder_manager = RecorderManager()
        self.double_validator = DoubleValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # File base name
        file_group = QGroupBox("Output File")
        file_layout = QHBoxLayout(file_group)
        file_layout.addWidget(QLabel("File Base Name:"))
        self.file_base_name_input = QLineEdit()
        file_layout.addWidget(self.file_base_name_input)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        layout.addWidget(file_group)
        
        # Response types
        resp_group = QGroupBox("Response Types")
        resp_layout = QVBoxLayout(resp_group)
        
        # Checkboxes for response types
        self.resp_checkboxes = {}
        resp_types = ["disp", "vel", "accel", "stress3D6", "strain3D6", "stress2D3", "strain2D3"]
        for resp_type in resp_types:
            checkbox = QCheckBox(resp_type)
            self.resp_checkboxes[resp_type] = checkbox
            resp_layout.addWidget(checkbox)
        
        layout.addWidget(resp_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QFormLayout(options_group)
        
        # Time interval
        self.delta_t_input = QLineEdit()
        self.delta_t_input.setValidator(self.double_validator)
        options_layout.addRow("Time Interval (dT):", self.delta_t_input)
        
        # Relative tolerance
        self.r_tol_dt_input = QLineEdit()
        self.r_tol_dt_input.setValidator(self.double_validator)
        options_layout.addRow("Relative Tolerance (rTolDt):", self.r_tol_dt_input)
        
        layout.addWidget(options_group)
        
        # Add notes
        notes_text = QTextEdit()
        notes_text.setReadOnly(True)
        notes_text.setPlainText(
            "Notes:\n"
            "- File Base Name: Output will be generated as <base_name>.h5 and can be visualized with ParaView\n"
            "- Response Types: Select the types of response to record\n"
            "- Time Interval: Record only at specified intervals\n"
            "- Relative Tolerance: Tolerance for time step matching"
        )
        layout.addWidget(notes_text)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_recorder)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_file(self):
        """Browse for output file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select Output File Base", "", "All Files (*)"
        )
        if filename:
            # Remove .h5 extension if present, as it will be added by OpenSees
            if filename.lower().endswith(".h5"):
                filename = filename[:-3]
            self.file_base_name_input.setText(filename)

    def create_recorder(self):
        try:
            # Collect parameters
            params = {}
            
            # File base name
            file_base_name = self.file_base_name_input.text().strip()
            if not file_base_name:
                raise ValueError("Please specify a file base name")
            params["file_base_name"] = file_base_name
            
            # Response types
            resp_types = []
            for resp_type, checkbox in self.resp_checkboxes.items():
                if checkbox.isChecked():
                    resp_types.append(resp_type)
            
            if not resp_types:
                raise ValueError("Please select at least one response type")
            params["resp_types"] = resp_types
            
            # Options
            delta_t = self.delta_t_input.text().strip()
            if delta_t:
                params["delta_t"] = float(delta_t)
            
            r_tol_dt = self.r_tol_dt_input.text().strip()
            if r_tol_dt:
                params["r_tol_dt"] = float(r_tol_dt)
            
            # Create recorder
            self.recorder = self.recorder_manager.create_recorder("vtkhdf", **params)
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class VTKHDFRecorderEditDialog(QDialog):
    def __init__(self, recorder, parent=None):
        super().__init__(parent)
        self.recorder = recorder
        self.setWindowTitle(f"Edit VTKHDF Recorder (Tag: {recorder.tag})")
        self.recorder_manager = RecorderManager()
        self.double_validator = DoubleValidator()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # File base name
        file_group = QGroupBox("Output File")
        file_layout = QHBoxLayout(file_group)
        file_layout.addWidget(QLabel("File Base Name:"))
        self.file_base_name_input = QLineEdit()
        file_layout.addWidget(self.file_base_name_input)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        layout.addWidget(file_group)
        
        # Response types
        resp_group = QGroupBox("Response Types")
        resp_layout = QVBoxLayout(resp_group)
        
        # Checkboxes for response types
        self.resp_checkboxes = {}
        resp_types = ["disp", "vel", "accel", "stress3D6", "strain3D6", "stress2D3", "strain2D3"]
        for resp_type in resp_types:
            checkbox = QCheckBox(resp_type)
            self.resp_checkboxes[resp_type] = checkbox
            resp_layout.addWidget(checkbox)
        
        layout.addWidget(resp_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QFormLayout(options_group)
        
        # Time interval
        self.delta_t_input = QLineEdit()
        self.delta_t_input.setValidator(self.double_validator)
        options_layout.addRow("Time Interval (dT):", self.delta_t_input)
        
        # Relative tolerance
        self.r_tol_dt_input = QLineEdit()
        self.r_tol_dt_input.setValidator(self.double_validator)
        options_layout.addRow("Relative Tolerance (rTolDt):", self.r_tol_dt_input)
        
        layout.addWidget(options_group)
        
        # Load current values
        self.load_current_values()
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_recorder)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_current_values(self):
        """Load current recorder values into the dialog"""
        values = self.recorder.get_values()
        
        # File base name
        if values.get("file_base_name"):
            self.file_base_name_input.setText(values["file_base_name"])
        
        # Response types
        resp_types = values.get("resp_types", [])
        for resp_type, checkbox in self.resp_checkboxes.items():
            checkbox.setChecked(resp_type in resp_types)
        
        # Options
        if values.get("delta_t") is not None:
            self.delta_t_input.setText(str(values["delta_t"]))
        
        if values.get("r_tol_dt") is not None:
            self.r_tol_dt_input.setText(str(values["r_tol_dt"]))

    def browse_file(self):
        """Browse for output file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select Output File Base", "", "All Files (*)"
        )
        if filename:
            # Remove .h5 extension if present, as it will be added by OpenSees
            if filename.lower().endswith(".h5"):
                filename = filename[:-3]
            self.file_base_name_input.setText(filename)

    def save_recorder(self):
        try:
            # Collect parameters
            params = {}
            
            # File base name
            file_base_name = self.file_base_name_input.text().strip()
            if not file_base_name:
                raise ValueError("Please specify a file base name")
            params["file_base_name"] = file_base_name
            
            # Response types
            resp_types = []
            for resp_type, checkbox in self.resp_checkboxes.items():
                if checkbox.isChecked():
                    resp_types.append(resp_type)
            
            if not resp_types:
                raise ValueError("Please select at least one response type")
            params["resp_types"] = resp_types
            
            # Options
            delta_t = self.delta_t_input.text().strip()
            if delta_t:
                params["delta_t"] = float(delta_t)
            
            r_tol_dt = self.r_tol_dt_input.text().strip()
            if r_tol_dt:
                params["r_tol_dt"] = float(r_tol_dt)
            
            # Update recorder
            # First remove the old recorder
            tag = self.recorder.tag
            self.recorder_manager.remove_recorder(tag)
            
            # Create a new recorder with the same tag
            self.recorder = self.recorder_manager.create_recorder("vtkhdf", **params)
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == '__main__':
    from qtpy.QtWidgets import QApplication
    import sys
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    window = RecorderManagerTab()
    window.show()
    sys.exit(app.exec_())