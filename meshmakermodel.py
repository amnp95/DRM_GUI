from meshmaker.components.MeshMaker import MeshMaker
import os 

# change the direcotto the current file
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Layer properties as a dictionary
layers = [
    {"layer": 1, "rho": 2142.1, "vp": 669.1, "vs": 353.1, "xi_s": 0.0296, "xi_p": 0.0148, "thickness": 8},
    {"layer": 2, "rho": 2146.2, "vp": 785.3, "vs": 414.4, "xi_s": 0.0269, "xi_p": 0.0134, "thickness": 8},
    {"layer": 3, "rho": 2150.4, "vp": 886.1, "vs": 467.6, "xi_s": 0.0249, "xi_p": 0.0125, "thickness": 8},
    {"layer": 4, "rho": 2154.5, "vp": 976.4, "vs": 515.3, "xi_s": 0.0234, "xi_p": 0.0117, "thickness": 8},
    {"layer": 5, "rho": 2158.6, "vp": 1059.1, "vs": 559.0, "xi_s": 0.0221, "xi_p": 0.0111, "thickness": 8},
    {"layer": 6, "rho": 2162.8, "vp": 1135.7, "vs": 599.4, "xi_s": 0.0211, "xi_p": 0.0105, "thickness": 8}
]

mk = MeshMaker()
pi = 3.1415926
f1 = 15; # Hz
f2 = 3; # Hz
w1 = 2*pi*f1
w2 = 2*pi*f2


index = 0
for layer in layers[::-1]:
    rho = layer["rho"]
    vp = layer["vp"]
    vs = layer["vs"]
    xi_s = layer["xi_s"]
    xi_p = layer["xi_p"]
    thickness = layer["thickness"]
    vp_vs_ratio = (vp / vs) ** 2
    nu  = (vp_vs_ratio - 2) / (2 * (vp_vs_ratio - 1))
    E = 2 * rho * (vs ** 2) * (1 + nu)
    E = E / 1000
    rho = rho / 1000
    mat = mk.material.create_material("nDMaterial", "ElasticIsotropic", 
                                user_name=f"Layer{layer['layer']}", 
                                E=E, nu=nu, rho=rho)
    ele = mk.element.create_element(element_type="stdBrick",
                                    ndof=3,
                                    material=mat,
                                    b1=0,
                                    b2=0,
                                    b3=-9.81*rho)
    
    damp = mk.damping.create_damping("frequency rayleigh", dampingFactor=xi_s, f1=3, f2=15)
    # reg = mk.region.create_region("elementRegion", damping=damp)

    zmin = -48 + index * thickness
    zmax = zmin + thickness
    dx = 4.0
    dy = 4.0
    dz = 4.0
    Nx = int(128 / dx)
    Ny = int(128 / dy)
    Nz = int(thickness / dz)

    mk.meshPart.create_mesh_part("Volume mesh", "Uniform Rectangular Grid",
                            user_name=f"Layer{layer['layer']}",
                            element=ele,
                            region=mk.region.create_region("elementRegion", damping=damp),
                            **{'X Min': -64, 'X Max': 64,
                                'Y Min': -64, 'Y Max': 64,
                                'Z Min': zmin, 'Z Max': zmax,
                                'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': Nz})
    index += 1


# create a list of mesh parts
mesh_parts = []
for layer in layers:
    mesh_parts.append(f"Layer{layer['layer']}")

mk.assembler.create_section(mesh_parts, num_partitions=4)

mk.assembler.Assemble()
mk.addAbsorbingLayer(numLayers=5,
                        numPartitions=4,
                        partitionAlgo="kd-tree",
                        geometry="Rectangular",
                        matchDamping=True,
                        type="PML",
                        )


# mk.export_to_vtk("mesh.vtk")
mk.export_to_tcl("mesh.tcl")