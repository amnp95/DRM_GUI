from PySide6.QtWidgets import QMessageBox
from .surface_wave import SurfaceWaveCreator
from .sv_wave import SvWaveCreator

class DRMManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.active_dialog = None


    def create_sv_wave(self):
        dialog = SvWaveCreator(self.parent)
        # show the dialog if there is no active dialog
        if self.active_dialog is None:
            dialog.show()
            self.active_dialog = dialog
        else:
            # show a message box if there is already an active dialog
            QMessageBox.warning(self.parent, "Warning", "Close the active dialog first.")
        
        # make the self.active_dialog None when the dialog is closed
        dialog.finished.connect(lambda: setattr(self, 'active_dialog', None))
    


    def create_surface_wave(self):
        dialog = SurfaceWaveCreator(self.parent)
        # show the dialog if there is no active dialog
        if self.active_dialog is None:
            dialog.show()
            self.active_dialog = dialog
        else:
            # show a message box if there is already an active dialog
            QMessageBox.warning(self.parent, "Warning", "Close the active dialog first.")
        
        # make the self.active_dialog None when the dialog is closed
        dialog.finished.connect(lambda: setattr(self, 'active_dialog', None))


    
