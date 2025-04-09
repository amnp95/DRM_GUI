# tapis_integration.py
from qtpy.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox,
    QDialogButtonBox
)
from qtpy.QtCore import Qt, QThread, Signal
import os

class TapisWorker(QThread):
    """Worker thread for Tapis API operations"""
    files_loaded = Signal(list)
    error_occurred = Signal(str)
    
    def __init__(self, base_url, username, password, path=None):
        super().__init__()
        self.base_url = base_url
        self.username = username
        self.password = password
        self.path = path
        
    def run(self):
        try:
            # Import here to avoid requiring tapipy for regular usage
            from tapipy.tapis import Tapis
            
            # Initialize Tapis client
            t = Tapis(base_url=self.base_url, username=self.username, password=self.password)
            t.get_tokens()
            
            # List files in the specified path or user's home
            path_to_use = self.path if self.path else f"./{self.username}"
            files = t.files.listFiles(systemId="designsafe.storage.default", path=path_to_use)
            
            # Emit the result
            self.files_loaded.emit(files)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class TACCFileBrowserDialog(QDialog):
    """Dialog for browsing files on TACC systems via Tapis API"""
    
    def __init__(self, parent=None, file_type="h5drm"):
        super().__init__(parent)
        self.setWindowTitle("Browse TACC Files")
        self.resize(600, 400)
        self.file_type = file_type  # "h5drm" or "csv"
        self.selected_file_path = None
        self.tapis_client = None
        self.current_path = None
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Connection details group
        connection_group = QGroupBox("TACC Connection")
        connection_layout = QGridLayout(connection_group)
        
        # Base URL
        connection_layout.addWidget(QLabel("Base URL:"), 0, 0)
        self.base_url_edit = QLineEdit("https://designsafe.tapis.io")
        connection_layout.addWidget(self.base_url_edit, 0, 1)
        
        # Username
        connection_layout.addWidget(QLabel("Username:"), 1, 0)
        self.username_edit = QLineEdit()
        connection_layout.addWidget(self.username_edit, 1, 1)
        
        # Password
        connection_layout.addWidget(QLabel("Password:"), 2, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        connection_layout.addWidget(self.password_edit, 2, 1)
        
        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_tacc)
        connection_layout.addWidget(self.connect_button, 3, 0, 1, 2)
        
        layout.addWidget(connection_group)
        
        # File browser group
        browser_group = QGroupBox("File Browser")
        browser_layout = QVBoxLayout(browser_group)
        
        # Current path display
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Path:"))
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit)
        
        # Go up button
        self.up_button = QPushButton("Up")
        self.up_button.clicked.connect(self.go_up)
        self.up_button.setEnabled(False)
        path_layout.addWidget(self.up_button)
        
        browser_layout.addLayout(path_layout)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.item_double_clicked)
        browser_layout.addWidget(self.file_list)
        
        layout.addWidget(browser_group)
        
        # File type filter display - update the text to be more informative
        filter_text = f"Showing all files (preferring {'H5DRM' if self.file_type == 'h5drm' else 'CSV'} files)"
        filter_label = QLabel(filter_text)
        layout.addWidget(filter_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        layout.addWidget(button_box)
        
        # Initially disable the file browser
        browser_group.setEnabled(False)
        self.browser_group = browser_group
    
    def connect_to_tacc(self):
        """Connect to TACC using the provided credentials"""
        # Disable connect button during connection
        self.connect_button.setEnabled(False)
        self.connect_button.setText("Connecting...")
        
        # Get connection details
        base_url = self.base_url_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()
        
        # Validate inputs
        if not (base_url and username and password):
            QMessageBox.warning(self, "Missing Information", "Please provide all connection details.")
            self.connect_button.setEnabled(True)
            self.connect_button.setText("Connect")
            return
        
        # Create and start worker thread
        self.worker = TapisWorker(base_url, username, password)
        self.worker.files_loaded.connect(self.on_files_loaded)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
    
    def on_files_loaded(self, files):
        """Handle the list of files returned from Tapis"""
        # Re-enable connect button
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Connect")
        
        # Enable file browser
        self.browser_group.setEnabled(True)
        self.up_button.setEnabled(True)
        
        # Clear the file list
        self.file_list.clear()
        
        # Get the current path from the first file (they all share the same parent path)
        if files and len(files) > 0:
            # Extract the path from the first file
            first_file = files[0]
            file_path = first_file.path
            
            # Get the parent directory path
            parent_path = os.path.dirname(file_path)
            self.current_path = parent_path
            self.path_edit.setText(parent_path)
        
        # Add files to the list
        for file in files:
            if file.type == "dir":
                # Always show directories
                item = QListWidgetItem(f"📁 {file.name}")
                item.setData(Qt.UserRole, file)
                self.file_list.addItem(item)
            elif file.type == "file":
                # Show all files, but highlight those with the target extension
                if ((self.file_type == "h5drm" and file.name.lower().endswith(".h5drm")) or
                    (self.file_type == "csv" and file.name.lower().endswith(".csv"))):
                    item = QListWidgetItem(f"📄 {file.name} ✓")  # Add a checkmark to indicate preferred files
                else:
                    item = QListWidgetItem(f"📄 {file.name}")
                item.setData(Qt.UserRole, file)
                self.file_list.addItem(item)
    
    def on_error(self, error_message):
        """Handle errors from Tapis API"""
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Connect")
        
        QMessageBox.critical(self, "Connection Error", f"Error connecting to TACC: {error_message}")
    
    def item_double_clicked(self, item):
        """Handle double-clicking an item in the file list"""
        file_data = item.data(Qt.UserRole)
        
        if file_data.type == "dir":
            # Navigate into the directory
            self.navigate_to(file_data.path)
        else:
            # Select the file
            self.selected_file_path = file_data.path
            self.ok_button.setEnabled(True)
    
    def navigate_to(self, path):
        """Navigate to a specific directory"""
        # Get connection details
        base_url = self.base_url_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()
        
        # Create and start worker thread
        self.worker = TapisWorker(base_url, username, password, path)
        self.worker.files_loaded.connect(self.on_files_loaded)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
    
    def go_up(self):
        """Navigate up one directory level"""
        if self.current_path:
            parent_path = os.path.dirname(self.current_path)
            if parent_path:
                self.navigate_to(parent_path)
    
    def get_selected_file(self):
        """Return the selected file path"""
        return self.selected_file_path
    
    def get_connection_info(self):
        """Return the connection information"""
        return {
            "base_url": self.base_url_edit.text(),
            "username": self.username_edit.text(),
            "password": self.password_edit.text()
        }