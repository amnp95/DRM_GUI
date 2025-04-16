.. _j2-cyclic-bounding-surface-material:

J2CyclicBoundingSurfaceMaterial
===============================

A material model that implements the J2 Cyclic Bounding Surface plasticity model, useful for modeling cyclical response in soil and other materials with complex hardening behavior.

Parameters
----------

- **G**: Shear modulus (required)
- **K**: Bulk modulus (required)
- **Su**: Undrained shear strength (required)
- **Den**: Mass density (required)
- **h**: Hardening parameter (required)
- **m**: Hardening exponent (required)
- **h0**: Initial hardening parameter (required)
- **chi**: Initial damping (viscous). chi = 2*dr_o/omega (dr_o = damping ratio at zero strain, omega = angular frequency) (required)
- **beta**: Integration variable (0 = explicit, 1 = implicit, 0.5 = midpoint rule) (default = 0.5)

Material State Control
----------------------

This material supports switching between elastic and plastic states using the ``updateMaterialStage`` method:

- ``'elastic'`` - Sets material to behave elastically
- ``'plastic'`` - Sets material to elasto-plastic behavior

.. admonition:: Usage Examples
   :class: note

   **Direct Creation:**

   .. code-block:: python

      # Create material directly
      j2_material = J2CyclicBoundingSurfaceMaterial(
          user_name="Clay",
          G=1.3e6,       # Shear modulus (Pa)
          K=2.6e6,       # Bulk modulus (Pa)
          Su=18000,      # Undrained shear strength (Pa)
          Den=1800,      # Mass density (kg/m³)
          h=1.5,         # Hardening parameter
          m=0.6,         # Hardening exponent
          h0=0.5,        # Initial hardening parameter
          chi=0.1,       # Initial damping
          beta=0.5       # Integration variable (midpoint rule)
      )

   **Via MeshMaker:**

   .. code-block:: python

      from meshmaker.components.MeshMaker import MeshMaker
      
      mk = MeshMaker()
      mk.material.create_material(
          material_category="nDMaterial",
          material_type="J2CyclicBoundingSurface", 
          user_name="Clay", 
          G=1.3e6, 
          K=2.6e6, 
          Su=18000, 
          Den=1800, 
          h=1.5, 
          m=0.6, 
          h0=0.5, 
          chi=0.1
      )