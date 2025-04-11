from meshmaker.components.MeshMaker import MeshMaker 

mk = MeshMaker()
mk.material.create_material(material_category="nDMaterial", material_type="ElasticIsotropic", user_name="Dense Ottawa", E=2.0e7, nu=0.3, rho=2.02)
mk.material.create_material(material_category="nDMaterial", material_type="ElasticIsotropic", user_name="Loose Ottawa", E=2.0e7, nu=0.3, rho=1.94)
mk.material.create_material(material_category="nDMaterial", material_type="ElasticIsotropic", user_name="Dense Montrey", E=2.0e7, nu=0.3, rho=2.018)

DensOttawaEle = mk.element.create_element(element_type="stdBrick", ndof=3, material="Dense Ottawa", b1=0.0, b2=0.0, b3=-9.81 * 2.02)
LooseOttawaEle = mk.element.create_element(element_type="stdBrick", ndof=3, material="Loose Ottawa", b1=0.0, b2=0.0, b3=-9.81 * 1.94)
MontreyEle = mk.element.create_element(element_type="stdBrick", ndof=3, material="Dense Montrey", b1=0.0, b2=0.0, b3=-9.81 * 2.018)


Xmin = -60
Xmax = 60
Ymin = -60
Ymax = 60
Zmin = -13
thick1 = 2.6
thick2 = 2.4
thick3 = 5.0 
thick4 = 6.0
thick5 = 2.0
dx = 1.0
dy = 1.0
dz1 = 1.3
dz2 = 1.2
dz3 = 1.0
dz4 = 0.5
dz5 = 0.5
Nx = int((Xmax - Xmin)/dx)
Ny = int((Ymax - Ymin)/dy)

mk.meshPart.create_mesh_part(category="Volume mesh",
                             mesh_part_type="Uniform Rectangular Grid",
                             user_name="DensOttawa1",
                             element=DensOttawaEle,
                             region=mk.region.get_region(0),
                             **{'X Min': Xmin, 'X Max': Xmax, 
                                'Y Min': Ymin, 'Y Max': Ymax, 
                                'Z Min': Zmin, 'Z Max': Zmin + thick1, 
                                'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick1/dz1)})
Zmin += thick1
mk.meshPart.create_mesh_part(category="Volume mesh",
                             mesh_part_type="Uniform Rectangular Grid",
                             user_name="DensOttawa2",
                            element=DensOttawaEle,
                            region=mk.region.get_region(0),
                            **{'X Min': Xmin, 'X Max': Xmax, 
                                'Y Min': Ymin, 'Y Max': Ymax, 
                                'Z Min': Zmin, 'Z Max': Zmin + thick2, 
                                'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick2/dz2)})

Zmin += thick2
mk.meshPart.create_mesh_part(category="Volume mesh",
                                mesh_part_type="Uniform Rectangular Grid",
                                user_name="DensOttawa3",
                                element=DensOttawaEle,
                                region=mk.region.get_region(0),
                                **{'X Min': Xmin, 'X Max': Xmax,
                                'Y Min': Ymin, 'Y Max': Ymax,
                                'Z Min': Zmin, 'Z Max': Zmin + thick3,
                                'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick3/dz3)})
Zmin += thick3
mk.meshPart.create_mesh_part(category="Volume mesh",
                                mesh_part_type="Uniform Rectangular Grid",
                                user_name="LooseOttawa",
                                element=LooseOttawaEle,
                                region=mk.region.get_region(0),
                                **{'X Min': Xmin, 'X Max': Xmax,
                                'Y Min': Ymin, 'Y Max': Ymax,
                                'Z Min': Zmin, 'Z Max': Zmin + thick4,
                                'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick4/dz4)})
Zmin += thick4
mk.meshPart.create_mesh_part(category="Volume mesh",
                                mesh_part_type="Uniform Rectangular Grid",
                                user_name="Montrey",
                                element=MontreyEle,
                                region=mk.region.get_region(0),
                                **{'X Min': Xmin, 'X Max': Xmax,
                                'Y Min': Ymin, 'Y Max': Ymax,
                                'Z Min': Zmin, 'Z Max': Zmin + thick5,  
                                'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick5/dz5)})


mk.assembler.create_section(meshparts=["DensOttawa1", "DensOttawa2", "DensOttawa3"], num_partitions=2)
mk.assembler.create_section(["LooseOttawa"], num_partitions=2)
mk.assembler.create_section(["Montrey"], num_partitions=2)
timeseries = mk.timeSeries.create_time_series(series_type="path",filePath="kobe.acc",fileTime="kobe.time")
mk.pattern.create_pattern(pattern_type="uniformexcitation",dof=1, time_series=timeseries)
mk.gui()
