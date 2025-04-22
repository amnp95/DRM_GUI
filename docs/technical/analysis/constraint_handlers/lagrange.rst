Lagrange constraint handler
========================

The Lagrange constraint handler enforces constraints exactly by introducing additional Lagrange multiplier degrees of freedom to the system.

Parameters
----------

``alpha_s`` : float, default=1.0
    The alpha value for single-point constraints.

``alpha_m`` : float, default=1.0
    The alpha value for multi-point constraints.

Usage Example
-------------

.. code-block:: python

    # Create a MeshMaker instance
    mk = MeshMaker()
    
    # Create a Lagrange constraint handler with default parameters
    mk.analysis.constraint.create_handler("Lagrange")
    
    # Create a Lagrange constraint handler with custom parameters
    mk.analysis.constraint.create_handler("Lagrange", alpha_s=0.5, alpha_m=0.8) 