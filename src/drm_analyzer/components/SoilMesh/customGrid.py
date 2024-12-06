# drm_analyzer/components/soil/custom_grid.py
from PySide6.QtWidgets import QLabel
from .baseGrid import BaseGridTab

class CustomGridTab(BaseGridTab):
    def setup_specific_fields(self):
        self.form_layout.addWidget(QLabel("Custom grid implementation pending"), 1, 0, 1, 2)

    def get_data(self):
        data = super().get_data()
        data.update({'type': 'custom'})
        return data