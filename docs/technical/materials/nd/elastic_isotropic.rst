.. _elastic-isotropic-material:

ElasticIsotropicMaterial
========================

A 3D isotropic elastic material defined by:

- **E**: Young's modulus (required)
- **nu**: Poisson's ratio (required)
- **rho**: Mass density (default = 0.0)

.. admonition:: Usage Examples
   :class: note

   **Direct Creation:**

   .. code-block:: python

      # Create material directly
      elastic_material = ElasticIsotropicMaterial(
          user_name="Concrete",
          E=30e6,  # Young's modulus (Pa)
          nu=0.2,  # Poisson's ratio
          rho=2400  # Mass density (kg/m³)
      )

   **Via MeshMaker:**

   .. code-block:: python

      from meshmaker.components.MeshMaker import MeshMaker
      
      mk = MeshMaker()
      mk.material.create_material(
          material_category="nDMaterial",
          material_type="ElasticIsotropic", 
          user_name="Concrete", 
          E=30e6, nu=0.2, rho=2400
      )

