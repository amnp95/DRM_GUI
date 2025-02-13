
import os
os.environ["QT_API"] = "pyside6"
import sys
from qtpy.QtWidgets import QApplication
from meshmaker.gui.main_window import MainWindow


DEBUG = True

def main():
    # # ========================================
    # if DEBUG:
    #     from meshmaker.components.Material.materialsOpenSees import ElasticIsotropicMaterial, J2CyclicBoundingSurfaceMaterial
    #     from meshmaker.components.Element.elementsOpenSees import stdBrickElement
    #     from meshmaker.components.Mesh.meshPartInstance import StructuredRectangular3D
    #     from meshmaker.components.Assemble.Assembler import AssemblySection, Assembler
    #     # elastic2  = ElasticIsotropicMaterial(user_name="Steel2", E=200e3, ν=0.3,  ρ=7.85e-9)
    #     # elsatic3  = ElasticIsotropicMaterial(user_name="Steel3", E=400e3, ν=0.25, ρ=7.85e-9)
    #     # stdbrik2 = stdBrickElement(ndof=3, material=elastic2, b1=0, b2=0, b3=-10)
    #     # stdbrik3 = stdBrickElement(ndof=3, material=elastic2, b1=0, b2=0, b3=-10)

    #     elastic1  = ElasticIsotropicMaterial(user_name="Elastic", E=6812817120.00, ν=0.2616328,  ρ=2400)
    #     elastic2  = ElasticIsotropicMaterial(user_name="Steel", E=200e9, ν=0.3,  ρ=7.85e-9)
    #     J2plastic = J2CyclicBoundingSurfaceMaterial(user_name="J2Plastic", G=270e6, K=500e6, Su=30e3, Den=2000, h=54e6, m=0.5, h0=0.2, chi=0.0, beta=0)
    #     stdbrik1  = stdBrickElement(ndof=3, material=elastic1, b1=0, b2=0, b3=-9.81)
    #     stdbrik2  = stdBrickElement(ndof=3, material=elastic2, b1=0, b2=0, b3=-9.81)
    #     stdbrik3  = stdBrickElement(ndof=3, material=J2plastic, b1=0, b2=0, b3=-9.81)


    #     # inner region
    #     StructuredRectangular3D(user_name="layer1",   element=stdbrik1, **{'X Min': -60, 'X Max': 60, 'Y Min': -60, 'Y Max': 60, 'Z Min': -35, 'Z Max': -20, 'Nx Cells': int(120/2.5), 'Ny Cells': int(120/2.5), 'Nz Cells': int(15/2.5)})
    #     StructuredRectangular3D(user_name="layer2",   element=stdbrik2, **{'X Min': -60, 'X Max': 60, 'Y Min': -60, 'Y Max': 60, 'Z Min': -20, 'Z Max': -10, 'Nx Cells': int(120/2.5), 'Ny Cells': int(120/2.5), 'Nz Cells': int(10/2.5)})
    #     StructuredRectangular3D(user_name="layer3",   element=stdbrik3, **{'X Min': -60, 'X Max': 60, 'Y Min': -60, 'Y Max': 60, 'Z Min': -10, 'Z Max':  0, 'Nx Cells': int(120/2.5), 'Ny Cells': int(120/2.5), 'Nz Cells': int(10/2.5)})
     

    #     AssemblySection(['layer1', 'layer2', 'layer3'], num_partitions=4)
    #     Assembler = Assembler.get_instance()
    #     Assembler.Assemble()





    #     import qtpy
    #     print(f"Using Qt bindings: {qtpy.API_NAME}")


    # app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # sys.exit(app.exec())

    if DEBUG:
        from meshmaker.components.Material.materialsOpenSees import ElasticIsotropicMaterial, J2CyclicBoundingSurfaceMaterial
        from meshmaker.components.Element.elementsOpenSees import stdBrickElement
        from meshmaker.components.Mesh.meshPartInstance import StructuredRectangular3D
        from meshmaker.components.Assemble.Assembler import AssemblySection, Assembler
        from meshmaker.components.MeshMaker import MeshMaker
        
        # elastic2  = ElasticIsotropicMaterial(user_name="Steel2", E=200e3, ν=0.3,  ρ=7.85e-9)
        # elsatic3  = ElasticIsotropicMaterial(user_name="Steel3", E=400e3, ν=0.25, ρ=7.85e-9)
        # stdbrik2 = stdBrickElement(ndof=3, material=elastic2, b1=0, b2=0, b3=-10)
        # stdbrik3 = stdBrickElement(ndof=3, material=elastic2, b1=0, b2=0, b3=-10)

        #        G [Pa]	    K[Pa]	       Density[kg/m3] Layer_Name	Thickness[m]    Depth      Vs[m/s]  Vp [m/s]	rho[kg/m3]	  Su [kN/m2]  hG	m	    ho	    Chi
        #    1	25000000.0	616666666.7	    2065		  Clay 1	    1.0	            1.0        110.0	   561.0	2065.0	      22964.0	  0.6	0.97	0.00	0.005
        #*   2	29062500.0	716875000.0	    2058		  Clay 2	    1.0	            2.0        118.8	   606.0	2057.5	      26695.6	  0.63	0.97	0.00	0.005
        #    3	33125000.0	817083333.3	    2050		  Clay 1	    1.0	            3.0        127.1	   648.2	2050.0	      30427.3	  0.63	0.97	0.00	0.005 
        #    4	37187500.0	917291666.7	    2043		  Clay 1	    1.0	            4.0        134.9	   688.0	2042.5	      34158.9	  0.63	0.97	0.00	0.005
        #*   5	41250000.0	1017500000.0	2035		  Clay 1	    1.0	            5.0        142.4	   726.0	2035.0	      37890.5	  0.63	0.97	0.00	0.005
        #    6	45312500.0	1117708333.3	2028		  Clay 1	    1.0	            6.0        149.5	   762.3	2027.5	      41622.2	  0.63	0.97	0.00	0.005 
        #*   7	49375000.0	1217916666.7	2020		  Clay 1	    1.0	            7.0        156.3	   797.2	2020.0	      45353.8	  0.63	0.97	0.00	0.005
        #    8	53437500.0	1318125000.0	2013		  Clay 1	    1.0	            8.0        163.0	   830.9	2012.5	      49085.5	  0.63	0.97	0.00	0.005
        #    9	57500000.0	1418333333.3	2005		  Clay 1	    1.0	            9.0        169.3	   863.5	2005.0	      52817.1	  0.63	0.97	0.00	0.005 
        #*   10	61562500.0	1518541666.7	1998		  Clay 1	    1.0	            10.        175.6	   895.2	1997.5	      56548.8	  0.63	0.97	0.00	0.005
        #    11	65625000.0	1618750000.0	1990		  Clay 1	    1.0	            11         181.6	   926.0	1990.0	      60280.4	  0.63	0.97	0.00	0.005
        #*   12	69687500.0	1718958333.3	1983		  Clay 1	    1.0	            12         187.5	   956.0	1982.5	      64012.1	  0.63	0.97	0.00	0.005 
        #    13	73750000.0	1819166666.7	1975		  Clay 1	    1.0	            13         193.2	   985.3	1975.0	      67743.7	  0.63	0.97	0.00	0.005
        #    14	77812500.0	1919375000.0	1968		  Clay 1	    1.0	            14         198.9	   1014.0	1967.5	      71475.3	  0.63	0.97	0.00	0.005
        #*   15	81875000.0	2019583333.3	1960		  Clay 1	    1.0	            15         204.4	   1042.2	1960.0	      75207.0	  0.63	0.97	0.00	0.005 
        #    16	85937500.0	2119791666.7	1953		  Clay 1	    1.0	            16         209.8	   1069.8	1952.5	      78938.6	  0.63	0.97	0.00	0.005
        #*   17	90000000.0	2220000000.0	1945		  Clay 1	    1.0	            17         215.1	   1096.9	1945.0	      82670.3	  0.63	0.97	0.00	0.005
        #*   18	115000000.0	2836666666.7	1840		  Clay 1	    6.0	            23         250.0	   1274.8	1840.0	      105634.2    0.63	0.97	0.00	0.005 
        #    19	100000000.0	2466666666.7	1736		  Clay 1	    6.0	            28         240.0	   1223.8	1736.0	      91855.9	  0.63	0.97	0.00	0.005
        #    20	180000000.0	4440000000.0	1873		  Clay 1	    6.0	            34         310.0	   1580.7	1873.0	      165340.6    0.63	0.97	0.00	0.005
        
        # ========================================
        # materials
        E = 6812817120.00/1000
        rho = 2400/1000.
        nu = 0.2616328
        elastic1  = ElasticIsotropicMaterial(user_name="Elastic", E=E, nu=nu,  rho=rho)


        Param_G = E / (2 * (1 + nu))
        Param_K = E / (3 * (1 - 2 * nu))
        Param_h = 0.63 * Param_G
        Param_Su = 1056.3422 # kN/m2
        Param_m = 0.97
        print(f"Param_G: {Param_G}, Param_K: {Param_K}, Param_h: {Param_h}, Param_Su: {Param_Su}")
        J2plastic1 = J2CyclicBoundingSurfaceMaterial(user_name="J2Plastic1", G=Param_G, K=Param_K, Su=Param_Su, 
                                                     Den=rho, h=Param_h, m=Param_m, h0=0.0, chi=0.005, beta=0)
        
        # ========================================
        # elements
        
        stdbrikE   = stdBrickElement(ndof=3, material=elastic1, b1=0, b2=0, b3=-9.81*2.4)
        stdbrikJ1  = stdBrickElement(ndof=3, material=J2plastic1, b1=0, b2=0, b3=-9.81*2.4)

        # inner region
        dx = 2.5
        dy = 2.5
        dz1 = 2.5
        dz2 = 2.5

        StructuredRectangular3D(user_name="base",   element=stdbrikE, **{'X Min': -60, 'X Max': 60, 'Y Min': -60, 'Y Max': 60, 'Z Min': -35, 'Z Max': -30, 'Nx Cells': int(120/dx), 'Ny Cells': int(120/dy), 'Nz Cells': int(5/dz1)})
        StructuredRectangular3D(user_name="right",  element=stdbrikE, **{'X Min':  52.5, 'X Max': 60, 'Y Min': -60, 'Y Max': 60, 'Z Min': -30, 'Z Max':  0,  'Nx Cells': int(7.5/dx),  'Ny Cells': int(120/dy), 'Nz Cells': int(30/dz2)})
        StructuredRectangular3D(user_name="left",   element=stdbrikE, **{'X Min': -60, 'X Max':-52.5, 'Y Min': -60, 'Y Max': 60, 'Z Min': -30, 'Z Max':  0,  'Nx Cells': int(7.5/dx),  'Ny Cells': int(120/dy), 'Nz Cells': int(30/dz2)})
        StructuredRectangular3D(user_name="front",  element=stdbrikE, **{'X Min': -52.5, 'X Max': 52.5, 'Y Min':  52.5, 'Y Max': 60, 'Z Min': -30, 'Z Max':  0,  'Nx Cells': int(105/dx),  'Ny Cells': int(7.5/dy),  'Nz Cells': int(30/dz2)})
        StructuredRectangular3D(user_name="back",   element=stdbrikE, **{'X Min': -52.5, 'X Max': 52.5, 'Y Min': -60, 'Y Max':-52.5, 'Z Min': -30, 'Z Max':  0,  'Nx Cells': int(105/dx),  'Ny Cells': int(7.5/dy),  'Nz Cells': int(30/dz2)})
        StructuredRectangular3D(user_name="core1",  element=stdbrikJ1, **{'X Min': -52.5, 'X Max': 52.5, 'Y Min': -52.5, 'Y Max': 52.5, 'Z Min': -30, 'Z Max': 0, 'Nx Cells': int(105/2.5), 'Ny Cells': int(105/2.5),  'Nz Cells': int(30/dz2)})

        
        mk = MeshMaker.get_instance()
        # d1 = mk.damping.create_damping("rayleigh", alphaM=0.1, betaK=0.0)
        # d2 = mk.damping.create_damping("frequency rayleigh", dampingFactor=0.95)
        # d3 = mk.damping.create_damping("rayleigh", alphaM=0.4, betaK=0.0)
        # d4 = mk.damping.create_damping("uniform", dampingRatio=0.05, freql=1.0, freq2=100.0)
        # d5 = mk.damping.create_damping("secant stiffness proportional", dampingFactor=0.05)
        
        # gr = mk.region.create_region("elementRegion", damping=d1)
        # er1 = mk.region.create_region("elementRegion", damping=d2)
        # er2 = mk.region.create_region("elementRegion", damping=d3)
        # nr1 = mk.region.create_region("nodeRegion", damping=d4)
        # nr2 = mk.region.create_region("nodeRegion", damping=d5)
        # nr3 = mk.region.create_region("nodeRegion", damping=d1)




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

        # StructuredRectangular3D(user_name="outer_base",   element=stdbrikE, region=er1 ,**{'X Min': xmin,    'X Max': xmax,    'Y Min': ymin,    'Y Max': ymax,    'Z Min': zmin,    'Z Max': zminorg, 'Nx Cells': int((xmax-xmin)/2.5), 'Ny Cells': int((ymax-ymin)/2.5), 'Nz Cells': int(thickness/dz1)})
        # StructuredRectangular3D(user_name="outer_right1", element=stdbrikE, region=er2 ,**{'X Min': xmaxorg, 'X Max': xmax,    'Y Min': ymin,    'Y Max': ymax,    'Z Min': zminorg, 'Z Max': -20,     'Nx Cells': int(thickness/2.5),   'Ny Cells': int((ymax-ymin)/2.5), 'Nz Cells': int((-20-zminorg)/dz1)})
        # StructuredRectangular3D(user_name="outer_right2", element=stdbrikE, region=er1 ,**{'X Min': xmaxorg, 'X Max': xmax,    'Y Min': ymin,    'Y Max': ymax,    'Z Min': -20,     'Z Max': 0,       'Nx Cells': int(thickness/2.5),   'Ny Cells': int((ymax-ymin)/2.5), 'Nz Cells': int(20/dz2)})
        # StructuredRectangular3D(user_name="outer_left1",  element=stdbrikE, region=er2 ,**{'X Min': xmin,    'X Max': xminorg, 'Y Min': ymin,    'Y Max': ymax,    'Z Min': zminorg, 'Z Max': -20,     'Nx Cells': int(thickness/2.5),   'Ny Cells': int((ymax-ymin)/2.5), 'Nz Cells': int((-20-zminorg)/dz1)})
        # StructuredRectangular3D(user_name="outer_left2",  element=stdbrikE, region=er1 ,**{'X Min': xmin,    'X Max': xminorg, 'Y Min': ymin,    'Y Max': ymax,    'Z Min': -20,     'Z Max': 0,       'Nx Cells': int(thickness/2.5),   'Ny Cells': int((ymax-ymin)/2.5), 'Nz Cells': int(20/dz2)})
        # StructuredRectangular3D(user_name="outer_front1", element=stdbrikE, region=gr ,**{'X Min': xminorg, 'X Max': xmaxorg, 'Y Min': ymin,    'Y Max': yminorg, 'Z Min': zminorg, 'Z Max': -20,     'Nx Cells': int((xmaxorg-xminorg)/2.5), 'Ny Cells': int(thickness/2.5), 'Nz Cells': int((-20-zminorg)/dz1)})
        # StructuredRectangular3D(user_name="outer_front2", element=stdbrikE, region=er2 ,**{'X Min': xminorg, 'X Max': xmaxorg, 'Y Min': ymin,    'Y Max': yminorg, 'Z Min': -20,     'Z Max': 0,       'Nx Cells': int((xmaxorg-xminorg)/2.5), 'Ny Cells': int(thickness/2.5), 'Nz Cells': int(20/dz2)})
        # StructuredRectangular3D(user_name="outer_back1",  element=stdbrikE, region=er1 ,**{'X Min': xminorg, 'X Max': xmaxorg, 'Y Min': ymaxorg, 'Y Max': ymax,    'Z Min': zminorg, 'Z Max': -20,     'Nx Cells': int((xmaxorg-xminorg)/2.5), 'Ny Cells': int(thickness/2.5), 'Nz Cells': int((-20-zminorg)/dz1)})
        # StructuredRectangular3D(user_name="outer_back2",  element=stdbrikE, region=gr ,**{'X Min': xminorg, 'X Max': xmaxorg, 'Y Min': ymaxorg, 'Y Max': ymax,    'Z Min': -20,     'Z Max': 0,       'Nx Cells': int((xmaxorg-xminorg)/2.5), 'Ny Cells': int(thickness/2.5), 'Nz Cells': int(20/dz2)})
        
        
        AssemblySection(["base", "right", "left", "front", "back"], num_partitions=1)
        AssemblySection(["core1"], num_partitions=2)
        # AssemblySection(["outer_base", "outer_right1", "outer_right2", "outer_left1", "outer_left2", "outer_front1", "outer_front2", "outer_back1", "outer_back2"], num_partitions=4)
        # ========================================
        Assembler().Assemble()

        #      'modal': ModalDamping,
        # 'uniform': UniformDamping,
        # 'secant stiffness proportional':
        # mk.export_to_vtk("mesh.vtk")
        # mk.export_to_tcl("mesh.tcl")


        import qtpy
        print(f"Using Qt bindings: {qtpy.API_NAME}")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':

    main()