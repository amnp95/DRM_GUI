import sys
from PySide6.QtWidgets import QApplication
from drm_analyzer.gui.main_window import MainWindow

DEBUG = True


def main():
    # ========================================
    if DEBUG:
        from drm_analyzer.components.Material.materialsOpenSees import ElasticIsotropicMaterial
        from drm_analyzer.components.Element.elementsOpenSees import stdBrickElement
        from drm_analyzer.components.Mesh.meshPartInstance import StructuredRectangular3D


        elastic  = ElasticIsotropicMaterial(user_name="Steel", E=200e3, ν=0.3,  ρ=7.85e-9)
        stdbrik1 = stdBrickElement(ndof=3, material=elastic, b1=0, b2=0, b3=-10)
        stdbrik2 = stdBrickElement(ndof=3, material=elastic, b1=0, b2=0, b3=-10)
        stdbrik3 = stdBrickElement(ndof=3, material=elastic, b1=0, b2=0, b3=-10)
        StructuredRectangular3D(user_name="base",    element=stdbrik1, **{'X Min': -50, 'X Max': 50, 'Y Min': -50, 'Y Max': 50, 'Z Min': -30, 'Z Max': -20, 'Nx Cells': 100, 'Ny Cells': 100, 'Nz Cells': 10})
        StructuredRectangular3D(user_name="middle",  element=stdbrik2, **{'X Min': -50, 'X Max': 50, 'Y Min': -50, 'Y Max': 50, 'Z Min': -20, 'Z Max': -10, 'Nx Cells': 100, 'Ny Cells': 100, 'Nz Cells': 10})
        StructuredRectangular3D(user_name="top",     element=stdbrik3, **{'X Min': -50, 'X Max': 50, 'Y Min': -50, 'Y Max': 50, 'Z Min': -10, 'Z Max':   0, 'Nx Cells': 100, 'Ny Cells': 100, 'Nz Cells': 10})
    # ========================================
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()