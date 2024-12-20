from qtpy.QtWidgets import QMessageBox
from .surface_wave import SurfaceWaveCreator
from .sv_wave import SvWaveCreator

class DRMManager:
    """Manager class for DRM-related dialogs"""
    
    def __init__(self, parent=None):
        """
        Initialize the DRM Manager.
        
        Args:
            parent: Parent widget for the dialogs
        """
        self.parent = parent
        self.active_dialog = None

    def _show_dialog(self, dialog_class):
        """
        Helper method to show a dialog and manage its lifecycle.
        
        Args:
            dialog_class: The class of the dialog to create
        """
        if self.active_dialog is not None:
            QMessageBox.warning(self.parent, "Warning", "Close the active dialog first.")
            return

        # Create and show the dialog
        dialog = dialog_class(self.parent)
        dialog.show()
        self.active_dialog = dialog

        # Clear the active dialog reference when it's closed
        dialog.finished.connect(self._on_dialog_closed)

    def _on_dialog_closed(self):
        """Callback method when a dialog is closed"""
        self.active_dialog = None

    def create_sv_wave(self):
        """Create and show the SV Wave dialog"""
        self._show_dialog(SvWaveCreator)

    def create_surface_wave(self):
        """Create and show the Surface Wave dialog"""
        self._show_dialog(SurfaceWaveCreator)


    
