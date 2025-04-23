Examples and Tutorials
======================

This section provides practical examples and tutorials to help you understand how to use MeshMaker for various applications.

Basic Examples
--------------

Simple Beam Analysis
~~~~~~~~~~~~~~~~~~~~

Learn how to create and analyze a simple beam model:

.. code-block:: python
   
   import femora as fm
   
   # Initialize MeshMaker
    
   
   # Create material
   fm.material.create_material(
       material_category="nDMaterial",
       material_type="ElasticIsotropic",
       user_name="Steel",
       E=200e9,  # 200 GPa
       nu=0.3,
       rho=7850  # kg/m³
   )
   
   # Create beam geometry (length 5m, height 0.3m)
   length = 5.0
   height = 0.3
   
   # Create a line for the beam
   from femora.components.Geometry.geometryBase import Point, Line
   p1 = Point(0.0, 0.0, 0.0)
   p2 = Point(length, 0.0, 0.0)
   beam_line = Line(p1, p2)
   
   # Create beam region
   beam_region = fm.region.create_region(
       region_type="Beam",
       user_name="BeamRegion",
       geometry=beam_line,
       material_name="Steel",
       mesh_size=0.2,
       section_height=height,
       section_width=0.2
   )
   
   # Fix left end
   fm.boundary.fix_nodes(
       region_name="BeamRegion",
       condition_type="FixedDOF",
       dofs=[1, 2, 3],  # Fix all translations and rotations
       condition_function=lambda x, y, z: x < 0.01
   )
   
   # Apply point load at center
   fm.load.create_load(
       load_type="PointLoad",
       region_name="BeamRegion",
       value=-10000.0,  # 10 kN downward
       direction=2,  # Y-direction
       condition_function=lambda x, y, z: abs(x - length/2) < 0.01
   )
   
   # Generate mesh and visualize
   fm.generate_mesh()
   fm.visualize.plot_mesh()

2D Plane Stress Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

Create a 2D plane stress model:

.. code-block:: python
   
   # Import required libraries
   import femora as fm
   from femora.components.Geometry.geometryBase import Point, Line, Surface
   import numpy as np
   
   # Initialize MeshMaker
    
   
   # Create material
   fm.material.create_material(
       material_category="nDMaterial",
       material_type="ElasticIsotropic",
       user_name="Aluminum",
       E=70e9,  # 70 GPa
       nu=0.33,
       rho=2700  # kg/m³
   )
   
   # Create plate geometry
   width = 1.0
   height = 0.5
   
   p1 = Point(0.0, 0.0, 0.0)
   p2 = Point(width, 0.0, 0.0)
   p3 = Point(width, height, 0.0)
   p4 = Point(0.0, height, 0.0)
   
   l1 = Line(p1, p2)
   l2 = Line(p2, p3)
   l3 = Line(p3, p4)
   l4 = Line(p4, p1)
   
   plate = Surface([l1, l2, l3, l4])
   
   # Create plate region
   plate_region = fm.region.create_region(
       region_type="Quad4Region",
       user_name="PlateRegion",
       geometry=plate,
       material_name="Aluminum",
       mesh_size=0.05
   )
   
   # Fix left edge
   fm.boundary.fix_nodes(
       region_name="PlateRegion",
       condition_type="FixedDOF",
       dofs=[1, 2],  # Fix x and y directions
       condition_function=lambda x, y, z: abs(x) < 0.01
   )
   
   # Apply tensile load on right edge
   fm.load.create_load(
       load_type="SurfaceLoad",
       region_name="PlateRegion",
       value=1e6,  # 1 MPa tensile stress
       direction=1,  # X-direction
       condition_function=lambda x, y, z: abs(x - width) < 0.01
   )
   
   # Generate mesh and visualize
   fm.generate_mesh()
   fm.visualize.plot_mesh()

Advanced Examples
-----------------

Seismic Analysis Example
~~~~~~~~~~~~~~~~~~~~~~~~

This example demonstrates how to perform a basic seismic analysis with MeshMaker:

.. code-block:: python
   
   import femora as fm
   import numpy as np
   
   # Initialize MeshMaker
    
   
   # Define materials
   fm.material.create_material(
       material_category="nDMaterial",
       material_type="ElasticIsotropic",
       user_name="Concrete",
       E=25e9,
       nu=0.2,
       rho=2400
   )
   
   # Create a building frame geometry
   # ... (geometry creation code)
   
   # Apply ground motion record
   fm.load.create_load(
       load_type="UniformExcitation",
       direction=1,
       acceleration_file="examples/Example1/kobe.acc",
       time_file="examples/Example1/kobe.time"
   )
   
   # Set up analysis parameters
   fm.analysis.set_parameters(
       analysis_type="TimeHistory",
       damping_ratio=0.05,
       time_step=0.01,
       num_steps=2000
   )
   
   # Generate mesh and export to OpenSees
   fm.generate_mesh()
   fm.export.to_opensees("seismic_analysis.tcl")

Soil-Structure Interaction Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example of modeling soil-structure interaction:

.. code-block:: python
   
   # Soil-structure interaction example
   # ... (detailed code would be provided here)

Real-World Project Examples
---------------------------

Building Foundation Design
~~~~~~~~~~~~~~~~~~~~~~~~~~

Example of using MeshMaker for foundation design.

Bridge Analysis
~~~~~~~~~~~~~~~

Example of analyzing a bridge structure with MeshMaker.

Tutorial Videos
---------------

For visual learners, we provide a series of tutorial videos:

1. **Getting Started with MeshMaker**: Basic setup and first model
2. **Advanced Meshing Techniques**: How to create complex mesh configurations
3. **Material Modeling in Depth**: Working with various material models
4. **Analysis and Visualization**: Running analyses and visualizing results

Example Files
-------------

You can download complete example files from our GitHub repository:

.. code-block:: bash

   git clone https://github.com/username/meshmaker-examples.git

Alternatively, browse the examples included with your MeshMaker installation in the 'examples' directory:

.. code-block:: bash

   cd /path/to/meshmaker/examples/