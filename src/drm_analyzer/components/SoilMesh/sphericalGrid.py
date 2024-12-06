from PyQt5.QtWidgets import QLabel, QLineEdit
import numpy as np
import pyvista as pv
from .baseGrid import BaseGridTab

class SphericalGridTab(BaseGridTab):
    def setup_specific_fields(self):
        fields = [
            ("Radius (m):", "radius"),
            ("Number of Radial Elements:", "num_r"),
            ("Number of Azimuthal Elements:", "num_theta"),
            ("Number of Polar Elements:", "num_phi")
        ]
        
        for i, (label, attr_name) in enumerate(fields):
            self.form_layout.addWidget(QLabel(label), i + 1, 0)
            line_edit = QLineEdit()
            setattr(self, attr_name, line_edit)
            self.form_layout.addWidget(line_edit, i + 1, 1)
            
            if 'num' in attr_name:
                line_edit.setValidator(self.int_validator)
            else:
                line_edit.setValidator(self.double_validator)

    def create_grid(self):
        try:
            radius = float(self.radius.text() or 0)
            num_r = int(self.num_r.text() or 0)
            num_theta = int(self.num_theta.text() or 0)
            num_phi = int(self.num_phi.text() or 0)
            
            if any(v == 0 for v in [radius, num_r, num_theta, num_phi]):
                return None
                
            r = np.linspace(0, radius, num_r)
            theta = np.linspace(0, 2*np.pi, num_theta)
            phi = np.linspace(0, np.pi, num_phi)
            
            r_grid, theta_grid, phi_grid = np.meshgrid(r, theta, phi)
            
            x = r_grid * np.sin(phi_grid) * np.cos(theta_grid)
            y = r_grid * np.sin(phi_grid) * np.sin(theta_grid)
            z = r_grid * np.cos(phi_grid)
            
            grid = pv.StructuredGrid(x, y, z)
            return grid
        except ValueError:
            return None

    def get_data(self):
        data = super().get_data()
        data.update({
            'type': 'spherical',
            'radius': self.radius.text(),
            'num_r': self.num_r.text(),
            'num_theta': self.num_theta.text(),
            'num_phi': self.num_phi.text()
        })
        return data

