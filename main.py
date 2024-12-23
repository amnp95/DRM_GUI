
import os
os.environ["QT_API"] = "pyside6"
import sys
from qtpy.QtWidgets import QApplication
from meshmaker.gui.main_window import MainWindow


DEBUG = True

def main():
    # ========================================
    if DEBUG:
        from meshmaker.components.Material.materialsOpenSees import ElasticIsotropicMaterial, J2CyclicBoundingSurfaceMaterial
        from meshmaker.components.Element.elementsOpenSees import stdBrickElement
        from meshmaker.components.Mesh.meshPartInstance import StructuredRectangular3D
        # elastic2  = ElasticIsotropicMaterial(user_name="Steel2", E=200e3, ν=0.3,  ρ=7.85e-9)
        # elsatic3  = ElasticIsotropicMaterial(user_name="Steel3", E=400e3, ν=0.25, ρ=7.85e-9)
        # stdbrik2 = stdBrickElement(ndof=3, material=elastic2, b1=0, b2=0, b3=-10)
        # stdbrik3 = stdBrickElement(ndof=3, material=elastic2, b1=0, b2=0, b3=-10)

        elastic1  = ElasticIsotropicMaterial(user_name="Elastic", E=6812817120.00, ν=0.2616328,  ρ=2400)
        J2plastic = J2CyclicBoundingSurfaceMaterial(user_name="J2Plastic", G=270e6, K=500e6, Su=30e3, Den=2000, h=54e6, m=0.5, h0=0.2, chi=0.0, beta=0)
        stdbrik1  = stdBrickElement(ndof=3, material=elastic1, b1=0, b2=0, b3=-9.81)
        stdbrik2  = stdBrickElement(ndof=3, material=J2plastic, b1=0, b2=0, b3=-9.81)


        # inner region
        StructuredRectangular3D(user_name="base",   element=stdbrik1, **{'X Min': -60, 'X Max': 60, 'Y Min': -60, 'Y Max': 60, 'Z Min': -35, 'Z Max': -10, 'Nx Cells': int(120/2.5), 'Ny Cells': int(120/2.5), 'Nz Cells': int(25/2.5)})
        StructuredRectangular3D(user_name="core",   element=stdbrik2, **{'X Min': -30, 'X Max': 30, 'Y Min': -30, 'Y Max': 30, 'Z Min': -10, 'Z Max':  0, 'Nx Cells': int(60/2.5), 'Ny Cells': int(60/2.5), 'Nz Cells': int(10/2.5)}) 
        StructuredRectangular3D(user_name="right",  element=stdbrik1, **{'X Min':  30, 'X Max': 60, 'Y Min': -60, 'Y Max': 60, 'Z Min': -10, 'Z Max':  0, 'Nx Cells': int(30/2.5), 'Ny Cells': int(120/2.5), 'Nz Cells': int(10/2.5)})
        StructuredRectangular3D(user_name="left",   element=stdbrik1, **{'X Min': -60, 'X Max':-30, 'Y Min': -60, 'Y Max': 60, 'Z Min': -10, 'Z Max':  0, 'Nx Cells': int(30/2.5), 'Ny Cells': int(120/2.5), 'Nz Cells': int(10/2.5)})
        StructuredRectangular3D(user_name="front",  element=stdbrik1, **{'X Min': -30, 'X Max': 30, 'Y Min':  30, 'Y Max': 60, 'Z Min': -10, 'Z Max':  0, 'Nx Cells': int(60/2.5), 'Ny Cells': int(30/2.5), 'Nz Cells': int(10/2.5)})
        StructuredRectangular3D(user_name="back",   element=stdbrik1, **{'X Min': -30, 'X Max': 30, 'Y Min': -60, 'Y Max':-30, 'Z Min': -10, 'Z Max':  0, 'Nx Cells': int(60/2.5), 'Ny Cells': int(30/2.5), 'Nz Cells': int(10/2.5)})

        # outer region 
        numlayer = 5
        thickness = 5 * 2.5
        zminorg = -35
        zmaxorg = 0
        xminorg = -60
        xmaxorg = 60
        yminorg = -60
        ymaxorg = 60
        xmin = xminorg - thickness
        xmax = xmaxorg + thickness
        ymin = yminorg - thickness
        ymax = ymaxorg + thickness
        zmin = zminorg - thickness

        StructuredRectangular3D(user_name="outer_base", element=stdbrik1, **{'X Min': xmin, 'X Max': xmax, 'Y Min': ymin, 'Y Max': ymax, 'Z Min': zmin, 'Z Max': zminorg, 'Nx Cells': int((xmax-xmin)/2.5), 'Ny Cells': int((ymax-ymin)/2.5), 'Nz Cells': int(thickness/2.5)})
        StructuredRectangular3D(user_name="outer_right", element=stdbrik1, **{'X Min': xmaxorg, 'X Max': xmax, 'Y Min': ymin, 'Y Max': ymax, 'Z Min': zminorg, 'Z Max': zmaxorg, 'Nx Cells': int(thickness/2.5), 'Ny Cells': int((ymax-ymin)/2.5), 'Nz Cells': int((zmaxorg-zminorg)/2.5)})
        StructuredRectangular3D(user_name="outer_left", element=stdbrik1, **{'X Min': xmin, 'X Max': xminorg, 'Y Min': ymin, 'Y Max': ymax, 'Z Min': zminorg, 'Z Max': zmaxorg, 'Nx Cells': int(thickness/2.5), 'Ny Cells': int((ymax-ymin)/2.5), 'Nz Cells': int((zmaxorg-zminorg)/2.5)})
        StructuredRectangular3D(user_name="outer_front", element=stdbrik1, **{'X Min': xminorg, 'X Max': xmaxorg, 'Y Min': ymin, 'Y Max': yminorg, 'Z Min': zminorg, 'Z Max': zmaxorg, 'Nx Cells': int((xmaxorg-xminorg)/2.5), 'Ny Cells': int(thickness/2.5), 'Nz Cells': int((zmaxorg-zminorg)/2.5)})
        StructuredRectangular3D(user_name="outer_back", element=stdbrik1, **{'X Min': xminorg, 'X Max': xmaxorg, 'Y Min': ymaxorg, 'Y Max': ymax, 'Z Min': zminorg, 'Z Max': zmaxorg, 'Nx Cells': int((xmaxorg-xminorg)/2.5), 'Ny Cells': int(thickness/2.5), 'Nz Cells': int((zmaxorg-zminorg)/2.5)})
        # StructuredRectangular3D(user_name="outer_base", element=stdbrik1, **{'X Min': -70, 'X Max': 70, 'Y Min': -70, 'Y Max': 70, 'Z Min': -45, 'Z Max': -35, 'Nx Cells': int(140/2.5), 'Ny Cells': int(140/2.5), 'Nz Cells': int(10/2.5)})
        # StructuredRectangular3D(user_name="outer_right", element=stdbrik1, **{'X Min': 60, 'X Max': 70, 'Y Min': -70, 'Y Max': 70, 'Z Min': -35, 'Z Max': 0, 'Nx Cells': int(10/2.5), 'Ny Cells': int(140/2.5), 'Nz Cells': int(35/2.5)}) 
        # StructuredRectangular3D(user_name="outer_left", element=stdbrik1, **{'X Min': -70, 'X Max': -60, 'Y Min': -70, 'Y Max': 70, 'Z Min': -35, 'Z Max': 0, 'Nx Cells': int(10/2.5), 'Ny Cells': int(140/2.5), 'Nz Cells': int(35/2.5)})
        # StructuredRectangular3D(user_name="outer_front", element=stdbrik1, **{'X Min': -60, 'X Max': 60, 'Y Min': -70, 'Y Max': -60, 'Z Min': -35, 'Z Max': 0, 'Nx Cells': int(120/2.5), 'Ny Cells': int(10/2.5), 'Nz Cells': int(35/2.5)})
        # StructuredRectangular3D(user_name="outer_back", element=stdbrik1, **{'X Min': -60, 'X Max': 60, 'Y Min': 60, 'Y Max': 70, 'Z Min': -35, 'Z Max': 0, 'Nx Cells': int(120/2.5), 'Ny Cells': int(10/2.5), 'Nz Cells': int(35/2.5)})
        # ========================================
        import qtpy
        print(f"Using Qt bindings: {qtpy.API_NAME}")


    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':

    main()