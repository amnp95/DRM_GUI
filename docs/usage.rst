Usage
=====

To use MeshMaker in your project, follow these steps:

1. Import the `MeshMaker` class from the `meshmaker.components.MeshMaker` module:

   .. code-block:: python

      from meshmaker.components.MeshMaker import MeshMaker

2. Create an instance of the `MeshMaker` class:

   .. code-block:: python

      mk = MeshMaker()

3. Define materials using the `material` manager:

   .. code-block:: python

      mk.material.create_material(material_category="nDMaterial", material_type="ElasticIsotropic",
                                  user_name="Dense Ottawa", E=2.0e7, nu=0.3, rho=2.02)

4. Create elements and assign materials to them:

   .. code-block:: python

      DensOttawaEle = mk.element.create_element(element_type="stdBrick", ndof=3,
                                                material="Dense Ottawa", b1=0.0, b2=0.0, b3=-9.81 * 2.02)

5. Define mesh parts using the `meshPart` manager:

   .. code-block:: python

      mk.meshPart.create_mesh_part(category="Volume mesh", mesh_part_type="Uniform Rectangular Grid",
                                   user_name="DensOttawa1", element=DensOttawaEle, region=mk.region.get_region(0),
                                   **{'X Min': Xmin, 'X Max': Xmax, 'Y Min': Ymin, 'Y Max': Ymax,
                                      'Z Min': Zmin, 'Z Max': Zmin + thick1,
                                      'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick1/dz1)})

6. Assemble the mesh parts using the `assembler` manager:

   .. code-block:: python

      mk.assembler.create_section(meshparts=["DensOttawa1", "DensOttawa2", "DensOttawa3"], num_partitions=2)
      mk.assembler.Assemble()

7. Export the mesh to TCL format:

   .. code-block:: python

      mk.export_to_tcl("mesh.tcl")

For more detailed information on the available classes and methods, refer to the API documentation.