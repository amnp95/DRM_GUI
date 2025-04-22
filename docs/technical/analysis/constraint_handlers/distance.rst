Distance constraint handler
========================

The Distance constraint handler enforces distance constraints between pairs of nodes, maintaining fixed distances during deformation.

Parameters
----------

``handler_type`` : str, default="Penalty"
    The type of constraint handler to use for enforcing distance constraints. Options are "Penalty" or "Lagrange".

``alpha`` : float, default=1.0e6
    The penalty factor applied to constraint violations when using the Penalty handler.

Usage Example
-------------

.. code-block:: python

    # Create a MeshMaker instance
    mk = MeshMaker()
    
    # Create a Distance constraint handler with default parameters
    mk.analysis.constraint.create_handler("Distance")
    
    # Create a Distance constraint handler with custom parameters
    mk.analysis.constraint.create_handler("Distance", handler_type="Lagrange", alpha=1.0e9) 