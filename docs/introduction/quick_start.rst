Quick Start Guide
=================

This quick start guide will help you create your first 3D soil layer model using FEMORA. We'll walk through Example1, which demonstrates how to create a multi-layered soil profile for seismic analysis.

Setting Up Your Environment
---------------------------

Before you begin, make sure you have:

1. Installed FEMORA (see :doc:`installation` for details)
2. Imported the necessary components:

.. code-block:: python

   import os
   import femora as fm
   import numpy as np

Creating Your First 3D Soil Layer Model
---------------------------------------

Example1 demonstrates how to create a 3D soil model with multiple layers of different soil materials, apply boundary conditions, and perform a seismic analysis using an earthquake record (Kobe earthquake).

The model consists of a 20m × 20m soil column (-10m to 10m in both X and Y directions) with a total depth of 18m, divided into 5 distinct soil layers:

1. Three layers of "Dense Ottawa" sand (total 10m thick)
2. One layer of "Loose Ottawa" sand (6m thick)
3. One layer of "Dense Montrey" sand (2m thick) at the surface

This stratified soil profile allows for realistic modeling of wave propagation through different soil materials during seismic events.

Step 1: Initialize FEMORA
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Set working directory to the location of your model files
   os.chdir(os.path.dirname(__file__))

Step 2: Define Materials
~~~~~~~~~~~~~~~~~~~~~~~~

In this step, we define the three soil materials used in our layered profile:

.. code-block:: python

   # Define materials
   fm.material.create_material(material_category="nDMaterial", 
                              material_type="ElasticIsotropic", 
                              user_name="Dense Ottawa", 
                              E=2.0e7,    # Young's modulus (Pa)
                              nu=0.3,     # Poisson's ratio
                              rho=2.02)   # Density (ton/m³)
   
   fm.material.create_material(material_category="nDMaterial", 
                              material_type="ElasticIsotropic", 
                              user_name="Loose Ottawa", 
                              E=2.0e7, 
                              nu=0.3, 
                              rho=1.94)

   fm.material.create_material(material_category="nDMaterial", 
                              material_type="ElasticIsotropic", 
                              user_name="Dense Montrey", 
                              E=2.0e7, 
                              nu=0.3, 
                              rho=2.018)

**Note**: We're using ElasticIsotropic materials with different densities to represent different soil types. In more advanced models, you might use more complex constitutive models like PressureDependMultiYield or other nonlinear materials.

Step 3: Create Elements
~~~~~~~~~~~~~~~~~~~~~~~

Now we define the element types for each soil material. We use 3D brick elements (stdBrick) with body forces to account for gravity:

.. code-block:: python

   # Create elements using the defined materials
   DensOttawaEle = fm.element.create_element(element_type="stdBrick", 
                                            ndof=3,             # 3 degrees of freedom per node
                                            material="Dense Ottawa", 
                                            b1=0.0,             # Body force in x-direction
                                            b2=0.0,             # Body force in y-direction
                                            b3=-9.81 * 2.02)    # Body force in z-direction (gravity * density)
   
   LooseOttawaEle = fm.element.create_element(element_type="stdBrick", 
                                             ndof=3, 
                                             material="Loose Ottawa", 
                                             b1=0.0, 
                                             b2=0.0, 
                                             b3=-9.81 * 1.94)   # Note the different gravity force due to different density
   
   MontreyEle = fm.element.create_element(element_type="stdBrick", 
                                         ndof=3, 
                                         material="Dense Montrey", 
                                         b1=0.0, 
                                         b2=0.0, 
                                         b3=-9.81 * 2.018)      # Gravity force for Montrey sand

**Note**: The `b3` parameter represents the gravitational body force in the vertical direction, calculated as the acceleration due to gravity (-9.81 m/s²) multiplied by the material density.

Step 4: Create Mesh Parts
~~~~~~~~~~~~~~~~~~~~~~~~~

In this step, we define the dimensions and discretization of our 3D soil profile, creating five distinct layers:

.. code-block:: python

   # Define mesh dimensions and discretization parameters
   Xmin = -10.0
   Xmax = 10.0
   Ymin = -10.0
   Ymax = 10.0
   Zmin = -18.0  # Bottom of the model
   
   # Layer thicknesses (from bottom to top)
   thick1 = 2.6  # First layer (Dense Ottawa)
   thick2 = 2.4  # Second layer (Dense Ottawa)
   thick3 = 5.0  # Third layer (Dense Ottawa)
   thick4 = 6.0  # Fourth layer (Loose Ottawa)
   thick5 = 2.0  # Fifth layer (Montrey)
   
   # Mesh discretization (element sizes)
   dx = 1.0    # Element size in x-direction
   dy = 1.0    # Element size in y-direction
   dz1 = 1.3   # Element size in z-direction for layer 1
   dz2 = 1.2   # Element size in z-direction for layer 2
   dz3 = 1.0   # Element size in z-direction for layer 3
   dz4 = 0.5   # Element size in z-direction for layer 4
   dz5 = 0.5   # Element size in z-direction for layer 5
   
   # Calculate number of elements in x and y directions
   Nx = int((Xmax - Xmin)/dx)  # 20 elements in x-direction
   Ny = int((Ymax - Ymin)/dy)  # 20 elements in y-direction
   
   # Create first layer (Dense Ottawa) at the bottom
   fm.meshPart.create_mesh_part(category="Volume mesh",
                               mesh_part_type="Uniform Rectangular Grid",
                               user_name="DensOttawa1",
                               element=DensOttawaEle,
                               region=fm.region.get_region(0),
                               **{'X Min': Xmin, 'X Max': Xmax, 
                                  'Y Min': Ymin, 'Y Max': Ymax, 
                                  'Z Min': Zmin, 'Z Max': Zmin + thick1, 
                                  'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick1/dz1)})
   
   # Update Zmin to the top of the previous layer
   Zmin += thick1
   
   # Create second layer (Dense Ottawa)
   fm.meshPart.create_mesh_part(category="Volume mesh",
                               mesh_part_type="Uniform Rectangular Grid",
                               user_name="DensOttawa2",
                               element=DensOttawaEle,
                               region=fm.region.get_region(0),
                               **{'X Min': Xmin, 'X Max': Xmax, 
                                  'Y Min': Ymin, 'Y Max': Ymax, 
                                  'Z Min': Zmin, 'Z Max': Zmin + thick2, 
                                  'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick2/dz2)})
   
   # Update Zmin to the top of the previous layer
   Zmin += thick2
   
   # Create third layer (Dense Ottawa)
   fm.meshPart.create_mesh_part(category="Volume mesh",
                               mesh_part_type="Uniform Rectangular Grid",
                               user_name="DensOttawa3",
                               element=DensOttawaEle,
                               region=fm.region.get_region(0),
                               **{'X Min': Xmin, 'X Max': Xmax, 
                                  'Y Min': Ymin, 'Y Max': Ymax, 
                                  'Z Min': Zmin, 'Z Max': Zmin + thick3, 
                                  'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick3/dz3)})
   
   # Update Zmin to the top of the previous layer
   Zmin += thick3
   
   # Create fourth layer (Loose Ottawa)
   fm.meshPart.create_mesh_part(category="Volume mesh",
                               mesh_part_type="Uniform Rectangular Grid",
                               user_name="LooseOttawa",
                               element=LooseOttawaEle,
                               region=fm.region.get_region(0),
                               **{'X Min': Xmin, 'X Max': Xmax, 
                                  'Y Min': Ymin, 'Y Max': Ymax, 
                                  'Z Min': Zmin, 'Z Max': Zmin + thick4, 
                                  'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick4/dz4)})
   
   # Update Zmin to the top of the previous layer
   Zmin += thick4
   
   # Create fifth layer (Montrey) at the top
   fm.meshPart.create_mesh_part(category="Volume mesh",
                               mesh_part_type="Uniform Rectangular Grid",
                               user_name="Montrey",
                               element=MontreyEle,
                               region=fm.region.get_region(0),
                               **{'X Min': Xmin, 'X Max': Xmax, 
                                  'Y Min': Ymin, 'Y Max': Ymax, 
                                  'Z Min': Zmin, 'Z Max': Zmin + thick5, 
                                  'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick5/dz5)})

**Note**: This creates a 3D soil column with different mesh refinement in the vertical direction for each layer. The lower layers (which are deeper) have coarser mesh (dz1=1.3m, dz2=1.2m, dz3=1.0m), while the upper layers have finer mesh (dz4=dz5=0.5m). This is a common practice in geotechnical modeling to have finer mesh near the surface where more detailed results are typically needed.

Step 5: Assemble Mesh Parts
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we need to assemble the five mesh parts into a complete model for analysis:

.. code-block:: python

   # Create assembly sections (grouping mesh parts for parallel processing)
   fm.assembler.create_section(meshparts=["DensOttawa1", "DensOttawa2", "DensOttawa3"], 
                              num_partitions=2)  # Group all Dense Ottawa layers with 2 parallel partitions
   
   fm.assembler.create_section(["LooseOttawa"], 
                              num_partitions=2)  # Loose Ottawa layer with 2 parallel partitions
   
   fm.assembler.create_section(["Montrey"], 
                              num_partitions=2)  # Montrey layer with 2 parallel partitions

   # Assemble the mesh parts into a complete mesh
   fm.assembler.Assemble()

Step 6: Define Time Series and Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we define the seismic loading by creating a time series and excitation pattern:

.. code-block:: python

   # Create a TimeSeries for excitation using the Kobe earthquake record
   timeseries = fm.timeSeries.create_time_series(series_type="path",
                                               filePath="kobe.acc",  # Acceleration file
                                               fileTime="kobe.time") # Time steps file

   # Create a pattern for the uniform excitation (base shaking)
   kobe = fm.pattern.create_pattern(pattern_type="uniformexcitation",
                                  dof=1,  # X-direction excitation
                                  time_series=timeseries)

**Note**: This applies the Kobe earthquake record as a uniform base excitation in the X-direction (dof=1). The acceleration data is read from "kobe.acc" and the corresponding time values from "kobe.time". This simulates the propagation of seismic waves from the bottom of the model upward through the different soil layers.

Step 7: Apply Boundary Conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, we apply appropriate boundary conditions for a seismic analysis:

.. code-block:: python

   # Apply laminar boundary conditions
   fm.constraint.mp.create_laminar_boundary(dofs=[1,2], direction=3)
   
   # Fix the bottom of the model
   fm.constraint.sp.fixMacroZmin(dofs=[1,2,3])

**Note**: The laminar boundary conditions ensure that nodes at the same elevation (z-coordinate) will move together in the horizontal directions (dofs=[1,2]), which simulates the behavior of soil in a shear box test. The `fixMacroZmin` function fixes all degrees of freedom (x, y, z translations) at the bottom of the model, effectively creating a rigid base where the earthquake motion will be applied.

Step 8: Create Recorders and Analysis Steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we define how to record the results and set up the analysis:

.. code-block:: python

   # Create a recorder for the whole model
   recorder = fm.recorder.create_recorder("vtkhdf",                    # VTK HDF format for ParaView visualization
                                        file_base_name="result.vtkhdf", # Base name for output files
                                        resp_types=["disp", "vel", "accel", "stress3D6", "strain3D6"], # Response quantities to record
                                        delta_t=0.02)                  # Time interval between recordings (seconds)

   # Create a gravity analysis step (initialize the model under gravitational forces)
   gravity = fm.analysis.create_default_transient_analysis(username="gravity", 
                                                         dt=0.01,      # Time step size (seconds)
                                                         num_steps=50) # Total number of time steps

   # Add components to the process in sequence
   fm.process.add_step(kobe, description="Uniform Excitation (Kobe record)")
   fm.process.add_step(recorder, description="Recorder of the whole model")
   fm.process.add_step(gravity, description="Gravity Analysis Step")

**Note**: The recorder captures displacements, velocities, accelerations, and 3D stresses and strains at 0.02-second intervals. The gravity analysis applies the gravitational forces gradually over 50 time steps (0.5 seconds total) to establish the initial stress state before applying the earthquake excitation.

Step 9: Export and Visualize the Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Export to OpenSees Tcl file
   fm.export_to_tcl("mesh.tcl")
   
   # Launch the GUI for visualization
   fm.gui()

Complete Example
----------------

Here's the complete code for this quick start example:

.. code-block:: python

   import os
   import femora as fm
   import numpy as np
   
   # Set working directory to the location of your model files
   os.chdir(os.path.dirname(__file__))
   
   # Define materials
   fm.material.create_material(material_category="nDMaterial", 
                              material_type="ElasticIsotropic", 
                              user_name="Dense Ottawa", 
                              E=2.0e7,    # Young's modulus (Pa)
                              nu=0.3,     # Poisson's ratio
                              rho=2.02)   # Density (ton/m³)
   
   fm.material.create_material(material_category="nDMaterial", 
                              material_type="ElasticIsotropic", 
                              user_name="Loose Ottawa", 
                              E=2.0e7, 
                              nu=0.3, 
                              rho=1.94)

   fm.material.create_material(material_category="nDMaterial", 
                              material_type="ElasticIsotropic", 
                              user_name="Dense Montrey", 
                              E=2.0e7, 
                              nu=0.3, 
                              rho=2.018)

   # Create elements using the defined materials
   DensOttawaEle = fm.element.create_element(element_type="stdBrick", 
                                            ndof=3,             # 3 degrees of freedom per node
                                            material="Dense Ottawa", 
                                            b1=0.0,             # Body force in x-direction
                                            b2=0.0,             # Body force in y-direction
                                            b3=-9.81 * 2.02)    # Body force in z-direction (gravity * density)
   
   LooseOttawaEle = fm.element.create_element(element_type="stdBrick", 
                                             ndof=3, 
                                             material="Loose Ottawa", 
                                             b1=0.0, 
                                             b2=0.0, 
                                             b3=-9.81 * 1.94)   # Note the different gravity force due to different density
   
   MontreyEle = fm.element.create_element(element_type="stdBrick", 
                                         ndof=3, 
                                         material="Dense Montrey", 
                                         b1=0.0, 
                                         b2=0.0, 
                                         b3=-9.81 * 2.018)      # Gravity force for Montrey sand
   
   # Define mesh dimensions and discretization parameters
   Xmin = -10.0
   Xmax = 10.0
   Ymin = -10.0
   Ymax = 10.0
   Zmin = -18.0  # Bottom of the model
   
   # Layer thicknesses (from bottom to top)
   thick1 = 2.6  # First layer (Dense Ottawa)
   thick2 = 2.4  # Second layer (Dense Ottawa)
   thick3 = 5.0  # Third layer (Dense Ottawa)
   thick4 = 6.0  # Fourth layer (Loose Ottawa)
   thick5 = 2.0  # Fifth layer (Montrey)
   
   # Mesh discretization (element sizes)
   dx = 1.0    # Element size in x-direction
   dy = 1.0    # Element size in y-direction
   dz1 = 1.3   # Element size in z-direction for layer 1
   dz2 = 1.2   # Element size in z-direction for layer 2
   dz3 = 1.0   # Element size in z-direction for layer 3
   dz4 = 0.5   # Element size in z-direction for layer 4
   dz5 = 0.5   # Element size in z-direction for layer 5
   
   # Calculate number of elements in x and y directions
   Nx = int((Xmax - Xmin)/dx)  # 20 elements in x-direction
   Ny = int((Ymax - Ymin)/dy)  # 20 elements in y-direction
   
   # Create first layer (Dense Ottawa) at the bottom
   fm.meshPart.create_mesh_part(category="Volume mesh",
                               mesh_part_type="Uniform Rectangular Grid",
                               user_name="DensOttawa1",
                               element=DensOttawaEle,
                               region=fm.region.get_region(0),
                               **{'X Min': Xmin, 'X Max': Xmax, 
                                  'Y Min': Ymin, 'Y Max': Ymax, 
                                  'Z Min': Zmin, 'Z Max': Zmin + thick1, 
                                  'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick1/dz1)})
   
   # Update Zmin to the top of the previous layer
   Zmin += thick1
   
   # Create second layer (Dense Ottawa)
   fm.meshPart.create_mesh_part(category="Volume mesh",
                               mesh_part_type="Uniform Rectangular Grid",
                               user_name="DensOttawa2",
                               element=DensOttawaEle,
                               region=fm.region.get_region(0),
                               **{'X Min': Xmin, 'X Max': Xmax, 
                                  'Y Min': Ymin, 'Y Max': Ymax, 
                                  'Z Min': Zmin, 'Z Max': Zmin + thick2, 
                                  'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick2/dz2)})
   
   # Update Zmin to the top of the previous layer
   Zmin += thick2
   
   # Create third layer (Dense Ottawa)
   fm.meshPart.create_mesh_part(category="Volume mesh",
                               mesh_part_type="Uniform Rectangular Grid",
                               user_name="DensOttawa3",
                               element=DensOttawaEle,
                               region=fm.region.get_region(0),
                               **{'X Min': Xmin, 'X Max': Xmax, 
                                  'Y Min': Ymin, 'Y Max': Ymax, 
                                  'Z Min': Zmin, 'Z Max': Zmin + thick3, 
                                  'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick3/dz3)})
   
   # Update Zmin to the top of the previous layer
   Zmin += thick3
   
   # Create fourth layer (Loose Ottawa)
   fm.meshPart.create_mesh_part(category="Volume mesh",
                               mesh_part_type="Uniform Rectangular Grid",
                               user_name="LooseOttawa",
                               element=LooseOttawaEle,
                               region=fm.region.get_region(0),
                               **{'X Min': Xmin, 'X Max': Xmax, 
                                  'Y Min': Ymin, 'Y Max': Ymax, 
                                  'Z Min': Zmin, 'Z Max': Zmin + thick4, 
                                  'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick4/dz4)})
   
   # Update Zmin to the top of the previous layer
   Zmin += thick4
   
   # Create fifth layer (Montrey) at the top
   fm.meshPart.create_mesh_part(category="Volume mesh",
                               mesh_part_type="Uniform Rectangular Grid",
                               user_name="Montrey",
                               element=MontreyEle,
                               region=fm.region.get_region(0),
                               **{'X Min': Xmin, 'X Max': Xmax, 
                                  'Y Min': Ymin, 'Y Max': Ymax, 
                                  'Z Min': Zmin, 'Z Max': Zmin + thick5, 
                                  'Nx Cells': Nx, 'Ny Cells': Ny, 'Nz Cells': int(thick5/dz5)})
   
   # Create assembly sections (grouping mesh parts for parallel processing)
   fm.assembler.create_section(meshparts=["DensOttawa1", "DensOttawa2", "DensOttawa3"], 
                              num_partitions=2)  # Group all Dense Ottawa layers with 2 parallel partitions
   
   fm.assembler.create_section(["LooseOttawa"], 
                              num_partitions=2)  # Loose Ottawa layer with 2 parallel partitions
   
   fm.assembler.create_section(["Montrey"], 
                              num_partitions=2)  # Montrey layer with 2 parallel partitions

   # Assemble the mesh parts into a complete mesh
   fm.assembler.Assemble()

   # Create a TimeSeries for excitation using the Kobe earthquake record
   timeseries = fm.timeSeries.create_time_series(series_type="path",
                                               filePath="kobe.acc",  # Acceleration file
                                               fileTime="kobe.time") # Time steps file

   # Create a pattern for the uniform excitation (base shaking)
   kobe = fm.pattern.create_pattern(pattern_type="uniformexcitation",
                                  dof=1,  # X-direction excitation
                                  time_series=timeseries)

   # Apply laminar boundary conditions
   fm.constraint.mp.create_laminar_boundary(dofs=[1,2], direction=3)
   
   # Fix the bottom of the model
   fm.constraint.sp.fixMacroZmin(dofs=[1,2,3])

   # Create a recorder for the whole model
   recorder = fm.recorder.create_recorder("vtkhdf",                    # VTK HDF format for ParaView visualization
                                        file_base_name="result.vtkhdf", # Base name for output files
                                        resp_types=["disp", "vel", "accel", "stress3D6", "strain3D6"], # Response quantities to record
                                        delta_t=0.02)                  # Time interval between recordings (seconds)

   # Create a gravity analysis step (initialize the model under gravitational forces)
   gravity = fm.analysis.create_default_transient_analysis(username="gravity", 
                                                         dt=0.01,      # Time step size (seconds)
                                                         num_steps=50) # Total number of time steps

   # Add components to the process in sequence
   fm.process.add_step(kobe, description="Uniform Excitation (Kobe record)")
   fm.process.add_step(recorder, description="Recorder of the whole model")
   fm.process.add_step(gravity, description="Gravity Analysis Step")
   
   # Export to OpenSees Tcl file
   fm.export_to_tcl("mesh.tcl")
   
   # Launch the GUI for visualization
   fm.gui()

Next Steps
----------

Now that you've created your first model with FEMORA, you can:

* Explore more complex geometries
* Try different materials 
* Learn about advanced meshing techniques
* Check out the :doc:`examples` for more inspiration