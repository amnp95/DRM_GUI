Quick Start Guide
================

This quick start guide will help you create your first mesh model using MeshMaker. Follow these simple steps to get started.

Setting Up Your Environment
--------------------------

Before you begin, make sure you have:

1. Installed MeshMaker (see :doc:`installation` for details)
2. Imported the necessary components:

.. code-block:: python

   from meshmaker.components.MeshMaker import MeshMaker
   from meshmaker.components.Geometry.geometryBase import Point, Line, Surface
   import numpy as np

Creating Your First Model
------------------------

Let's create a simple 2D mesh model:

Step 1: Initialize MeshMaker
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a MeshMaker instance
   mk = MeshMaker()

Step 2: Define Materials
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create an elastic isotropic material
   mk.material.create_material(
       material_category="nDMaterial",
       material_type="ElasticIsotropic",
       user_name="Concrete",
       E=30e6,  # Young's modulus (Pa)
       nu=0.2,  # Poisson's ratio
       rho=2400  # Density (kg/m³)
   )

Step 3: Create Geometry
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Define corner points of a rectangular domain
   p1 = Point(0.0, 0.0, 0.0)
   p2 = Point(10.0, 0.0, 0.0)
   p3 = Point(10.0, 5.0, 0.0)
   p4 = Point(0.0, 5.0, 0.0)
   
   # Create lines connecting the points
   l1 = Line(p1, p2)
   l2 = Line(p2, p3)
   l3 = Line(p3, p4)
   l4 = Line(p4, p1)
   
   # Create a surface from the lines
   surface = Surface([l1, l2, l3, l4])

Step 4: Create a Region
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a meshed region from the surface
   region = mk.region.create_region(
       region_type="Quad4Region",
       user_name="MainRegion",
       geometry=surface,
       material_name="Concrete",
       mesh_size=0.5  # Element size
   )

Step 5: Apply Boundary Conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Fix the bottom edge (lines with y=0)
   mk.boundary.fix_nodes(
       region_name="MainRegion",
       condition_type="FixedDOF",
       dofs=[1, 2],  # Fix x and y directions
       condition_function=lambda x, y, z: abs(y) < 1e-6
   )

Step 6: Apply Loads
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Apply a distributed load on the top edge
   mk.load.create_load(
       load_type="SurfaceLoad",
       region_name="MainRegion",
       value=-10000.0,  # N/m² (negative for compression)
       direction=2,  # Y-direction
       condition_function=lambda x, y, z: abs(y - 5.0) < 1e-6
   )

Step 7: Generate the Mesh
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Generate the mesh
   mk.generate_mesh()

Step 8: Visualize the Model
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Visualize the mesh
   mk.visualize.plot_mesh(
       show_nodes=True,
       show_elements=True
   )

Step 9: Export the Model
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Export to OpenSees Tcl file
   mk.export.to_opensees(
       filename="my_first_model.tcl",
       analysis_type="Static"
   )

Complete Example
--------------

Here's the complete code for this quick start example:

.. code-block:: python

   from meshmaker.components.MeshMaker import MeshMaker
   from meshmaker.components.Geometry.geometryBase import Point, Line, Surface
   import numpy as np
   
   # Create a MeshMaker instance
   mk = MeshMaker()
   
   # Create material
   mk.material.create_material(
       material_category="nDMaterial",
       material_type="ElasticIsotropic",
       user_name="Concrete",
       E=30e6,
       nu=0.2,
       rho=2400
   )
   
   # Create geometry
   p1 = Point(0.0, 0.0, 0.0)
   p2 = Point(10.0, 0.0, 0.0)
   p3 = Point(10.0, 5.0, 0.0)
   p4 = Point(0.0, 5.0, 0.0)
   
   l1 = Line(p1, p2)
   l2 = Line(p2, p3)
   l3 = Line(p3, p4)
   l4 = Line(p4, p1)
   
   surface = Surface([l1, l2, l3, l4])
   
   # Create region
   region = mk.region.create_region(
       region_type="Quad4Region",
       user_name="MainRegion",
       geometry=surface,
       material_name="Concrete",
       mesh_size=0.5
   )
   
   # Apply boundary conditions
   mk.boundary.fix_nodes(
       region_name="MainRegion",
       condition_type="FixedDOF",
       dofs=[1, 2],
       condition_function=lambda x, y, z: abs(y) < 1e-6
   )
   
   # Apply loads
   mk.load.create_load(
       load_type="SurfaceLoad",
       region_name="MainRegion",
       value=-10000.0,
       direction=2,
       condition_function=lambda x, y, z: abs(y - 5.0) < 1e-6
   )
   
   # Generate mesh
   mk.generate_mesh()
   
   # Visualize
   mk.visualize.plot_mesh(
       show_nodes=True,
       show_elements=True
   )
   
   # Export
   mk.export.to_opensees(
       filename="my_first_model.tcl",
       analysis_type="Static"
   )

Next Steps
---------

Now that you've created your first model with MeshMaker, you can:

* Explore more complex geometries
* Try different materials (see :ref:`elastic-isotropic-material` for more options)
* Learn about advanced meshing techniques
* Check out the :doc:`examples` for more inspiration