.. _drucker-prager-material:

DruckerPragerMaterial
=====================

A material model implementing the Drucker-Prager plasticity model, which is widely used for modeling pressure-dependent materials such as soils, rock, and concrete.

Parameters
---------

Required Parameters:
^^^^^^^^^^^^^^^^^^

- **k**: Bulk modulus (required)
- **G**: Shear modulus (required)
- **sigmaY**: Yield stress (required)
- **rho**: Frictional strength parameter (required)

Optional Parameters:
^^^^^^^^^^^^^^^^^

- **rhoBar**: Controls evolution of plastic volume change: 0 ≤ rhoBar ≤ rho (default = rho)
- **Kinf**: Nonlinear isotropic strain hardening parameter: Kinf ≥ 0 (default = 0.0)
- **Ko**: Nonlinear isotropic strain hardening parameter: Ko ≥ 0 (default = 0.0)
- **delta1**: Nonlinear isotropic strain hardening parameter: delta1 ≥ 0 (default = 0.0)
- **delta2**: Tension softening parameter: delta2 ≥ 0 (default = 0.0)
- **H**: Linear strain hardening parameter: H ≥ 0 (default = 0.0)
- **theta**: Controls relative proportions of isotropic and kinematic hardening: 0 ≤ theta ≤ 1 (default = 0.0)
- **density**: Mass density of the material (default = 0.0)
- **atmPressure**: Atmospheric pressure for updating elastic bulk and shear moduli (default = 101 kPa)

.. admonition:: Usage Examples
   :class: note

   **Direct Creation:**

   .. code-block:: python

      # Create material directly
      dp_material = DruckerPragerMaterial(
          user_name="Sand",
          k=8.33e6,      # Bulk modulus (Pa)
          G=3.85e6,      # Shear modulus (Pa)
          sigmaY=3000,   # Yield stress (Pa)
          rho=0.45,      # Frictional strength parameter
          rhoBar=0.4,    # Plastic volume evolution control
          Kinf=0.0,      # Isotropic hardening parameter
          Ko=0.0,        # Isotropic hardening parameter
          delta1=0.0,    # Isotropic hardening parameter
          delta2=0.0,    # Tension softening parameter
          H=500,         # Linear hardening parameter
          theta=0.5,     # Isotropic/kinematic hardening proportion
          density=1650   # Mass density (kg/m³)
      )

   **Via MeshMaker:**

   .. code-block:: python

      from meshmaker.components.MeshMaker import MeshMaker
      
      mk = MeshMaker()
      mk.material.create_material(
          material_category="nDMaterial",
          material_type="DruckerPrager", 
          user_name="Sand", 
          k=8.33e6, 
          G=3.85e6, 
          sigmaY=3000, 
          rho=0.45,
          H=500,
          density=1650
      )