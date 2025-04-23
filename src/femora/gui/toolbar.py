from qtpy.QtGui import QAction
from qtpy.QtWidgets import QMenuBar, QFileDialog, QMessageBox, QProgressDialog,QApplication
from qtpy.QtCore import Qt


class ToolbarManager:
    def __init__(self, main_window):
        """
        Initialize the ToolbarManager.
        
        Args:
            main_window: Reference to the MainWindow instance
        """
        self.main_window = main_window
        self.menubar = main_window.menuBar()
        self.setup_menus()

    def setup_menus(self):
        """Set up all menus in the menubar"""
        self.create_file_menu()
        self.create_view_menu()
        self.create_theme_menu()
        self.create_tools_menu()

    def create_file_menu(self):
        """Create the File menu and its items"""
        file_menu = self.menubar.addMenu("File")
        export_menu = file_menu.addMenu("Export")

        export_tcl_action = QAction("Export TCL", self.main_window)
        export_tcl_action.triggered.connect(self.export_to_tcl)
        export_menu.addAction(export_tcl_action)

        export_vtk_action = QAction("Export VTK", self.main_window)
        export_vtk_action.triggered.connect(self.export_to_vtk)
        export_menu.addAction(export_vtk_action)
        

    def export_to_tcl(self):
        """Handle the export to TCL action"""
        try:
            # Get file path from user
            filename, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export TCL File",
                "",
                "TCL Files (*.tcl);;All Files (*)"
            )
            
            if filename:
                # Create and show progress dialog
                progress = QProgressDialog("Exporting...", "Cancel", 0, 100, self.main_window)
                progress.setWindowModality(Qt.WindowModal)
                progress.setAutoClose(True)
                progress.setAutoReset(True)
                progress.show()  # Explicitly show the dialog
                def progress_callback(value, message):
                    progress.setValue(int(value))
                    progress.setLabelText(message)  # Update the message in the progress dialog
                    # Process events to ensure UI updates
                    QApplication.processEvents()
                    if progress.wasCanceled():
                        raise Exception("Export canceled by user")

                try:
                    success = self.main_window.meshMaker.export_to_tcl(filename, progress_callback)
                    
                    if success:
                        QMessageBox.information(
                            self.main_window,
                            "Success",
                            "File exported successfully!"
                        )
                    else:
                        QMessageBox.warning(
                            self.main_window,
                            "Export Failed",
                            "Failed to export the file. Please check the console for details."
                        )
                finally:
                    # Ensure progress dialog is closed even if export fails
                    progress.close()
                    
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"An error occurred while exporting: {str(e)}"
            )
    def export_to_vtk(self):
        """Handle the export to VTK action"""
        try:
            # Get file path from user
            filename, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Export VTK File",
                "",
                "VTK Files (*.vtk);;All Files (*)"
            )
            
            if filename:
                # Export the file
                success = self.main_window.meshMaker.export_to_vtk(filename)
                
                if success:
                    QMessageBox.information(
                        self.main_window,
                        "Success",
                        "File exported successfully!"
                    )
                else:
                    QMessageBox.warning(
                        self.main_window,
                        "Export Failed",
                        "Failed to export the file. Please check the console for details."
                    )
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"An error occurred while exporting: {str(e)}"
            )

    def create_view_menu(self):
        """Create the View menu and its items"""
        view_menu = self.menubar.addMenu("View")
        
        increase_size_action = QAction("Increase Size", self.main_window)
        increase_size_action.setShortcut("Ctrl+=")
        increase_size_action.triggered.connect(self.main_window.increase_font_size)
        view_menu.addAction(increase_size_action)

        decrease_size_action = QAction("Decrease Size", self.main_window)
        decrease_size_action.setShortcut("Ctrl+-")
        decrease_size_action.triggered.connect(self.main_window.decrease_font_size)
        view_menu.addAction(decrease_size_action)

    def create_theme_menu(self):
        """Create the Theme menu and its items"""
        theme_menu = self.menubar.addMenu("Theme")
        
        dark_theme_action = QAction("Dark Theme", self.main_window)
        dark_theme_action.triggered.connect(lambda: self.main_window.switch_theme("Dark"))
        theme_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction("Light Theme", self.main_window)
        light_theme_action.triggered.connect(lambda: self.main_window.switch_theme("Light"))
        theme_menu.addAction(light_theme_action)

        brown_theme_action = QAction("Brown Theme", self.main_window)
        brown_theme_action.triggered.connect(lambda: self.main_window.switch_theme("Brown"))
        theme_menu.addAction(brown_theme_action)

    def create_tools_menu(self):
        """Create the Tools menu and its items"""
        tools_menu = self.menubar.addMenu("Tools")
        drm_menu = tools_menu.addMenu("DRM Generator")

        sv_wave_action = QAction("SV Wave", self.main_window)
        sv_wave_action.triggered.connect(self.main_window.drm_manager.create_sv_wave)
        drm_menu.addAction(sv_wave_action)

        surface_wave_action = QAction("Surface Wave", self.main_window)
        surface_wave_action.triggered.connect(self.main_window.drm_manager.create_surface_wave)
        drm_menu.addAction(surface_wave_action)